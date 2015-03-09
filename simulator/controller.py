import cpu
import threading
import thread
from FIFOAlgorithm import FIFO
from LRUAlgorithm import LRU
from LFUAlgorithm import LFU
from OptimalAlgorithm import Optimal
from Switcher import Switcher



class Controller(object):
    
    def __init__(self, simulation_values):        
        self.simulation_values=simulation_values
        self.simulation_values["page_num_stream"] = []  # Each List Entry: [pid, virtual_page_number]
        self.simulation_values["event_page_stream"] = threading.Event()  # Used to wait for an address to be 
                                                    # available in page_num_stream
        self.simulation_values["switching_event"] = threading.Event()
        self.simulation_values["switching_event"].set()
        self.simulation_values["read_lock"] = threading.Lock()                                 
        self.simulation_values["process_size"] = simulation_values["vas"] * (2 ** 30)  # GB 

        self.read_from_file=simulation_values["read_from_file"]

        self.simulation_values["number_pr_threads"] = 4  # No of page replacement algorithms
        self.threads = []  # Array of PR started. Used to wait on them
        self.simulation_values["thread_set"] = set()  # Global set; Used to indicate reading of an elem by all algos.


        if(self.read_from_file):
            self.simulation_values["page_num_stream"]=simulation_values["page_accesses"]
            self.simulation_values["event_page_stream"].set()

        self.lru = LRU(self.simulation_values)
        self.optimal = Optimal(self.simulation_values)
        self.lfu = LFU(self.simulation_values)
        self.fifo = FIFO(self.simulation_values)
        self.current_algorithm = self.lfu
        self.other_algorithms = [self.lfu,self.lru,self.fifo]

        self.switcher = Switcher(self.current_algorithm, self.other_algorithms, self.optimal)



    def start_simulation(self):
        try:


            if(not self.read_from_file):

                thread = threading.Thread(target=lambda : cpu.start_CPU(self.simulation_values), args=())
                self.threads.append(thread)
                thread.start()

            while(len(self.simulation_values["page_num_stream"]) < self.simulation_values["window"]):
                print len(self.simulation_values["page_num_stream"])
                self.simulation_values["progress_bar"].grid(column=1, row=5)
                self.simulation_values["progress_bar"].config(maximum=self.simulation_values["window"], value=len(self.simulation_values["page_num_stream"]))
                pass
            self.simulation_values["progress_bar"].grid_forget()

            print "sim_win filled"
            print len(self.simulation_values["page_num_stream"])
            
            
            thread_optimal = threading.Thread(target=self.optimal, args=(self.switcher,))
            self.threads.append(thread_optimal)
            thread_optimal.start()
            
            thread_lru = threading.Thread(target=self.lru, args=(self.switcher,))
            self.threads.append(thread_lru)
            thread_lru.start()
            
            thread_lfu = threading.Thread(target=self.lfu, args=(self.switcher,))
            self.threads.append(thread_lfu)
            thread_lfu.start()
            
            thread_fifo = threading.Thread(target=self.fifo, args=(self.switcher,))
            self.threads.append(thread_fifo)
            thread_fifo.start()



        except Exception as e:
            print "Failed to start thread:", e


        for thread in self.threads:
            thread.join()

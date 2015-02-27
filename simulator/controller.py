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
        self.page_num_stream = []  # Each List Entry: [pid, virtual_page_number]
        self.event_page_stream = threading.Event()  # Used to wait for an address to be 
                                                    # available in page_num_stream
        self.switching_event = threading.Event()
        self.switching_event.set()
        self.lock = threading.Lock()                                 
        self.number_processes = simulation_values["num_processes"] 
        self.main_memory_size = simulation_values["memory"] * (2 ** 30)  # GB
        self.page_size = simulation_values["page_size"] * (2 ** 10)  # KB
        #self.number_frames = self.main_memory_size / self.page_size
        self.number_frames = 5
        self.simulation_window_size = simulation_values["window"]
        self.process_size = simulation_values["vas"] * (2 ** 30)  # GB 
        self.number_virtual_pages = self.process_size / self.page_size

        self.number_pr_threads = 4  # No of page replacement algorithms
        self.threads = []  # Array of PR started. Used to wait on them
        self.thread_set = set()  # Global set; Used to indicate reading of an elem by all algos.

        self.lru = LRU(self.number_virtual_pages, self.number_frames, self.number_pr_threads, self.page_num_stream, self.event_page_stream, self.lock, self.thread_set,self.simulation_window_size, self.switching_event)
        self.optimal = Optimal(self.number_virtual_pages, self.number_frames, self.number_pr_threads, self.page_num_stream, 
             self.event_page_stream, self.lock,self.thread_set, self.simulation_window_size, self.switching_event)
        self.lfu = LFU(self.number_virtual_pages, self.number_frames, self.number_pr_threads, self.page_num_stream, self.event_page_stream, self.lock, self.thread_set,self.simulation_window_size, self.switching_event)
        self.fifo = FIFO(self.number_virtual_pages, self.number_frames, self.number_pr_threads, self.page_num_stream, self.event_page_stream, self.lock, self.thread_set,self.simulation_window_size, self.switching_event)
        self.current_algorithm = self.lfu
        self.other_algorithms = [self.lfu,self.lru,self.fifo]

        self.switcher = Switcher(self.current_algorithm, self.other_algorithms, self.optimal)

    def start_simulation(self):
        try:
            thread = threading.Thread(target=lambda : cpu.start_CPU(self.number_processes, 
                                        self.page_num_stream, self.event_page_stream, self.lock, self.simulation_window_size), args=())
            self.threads.append(thread)
            thread.start()

            while(len(self.page_num_stream) < self.simulation_window_size):
                print len(self.page_num_stream)
                pass

            print "sim_win filled"
            print len(self.page_num_stream)
            
            
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

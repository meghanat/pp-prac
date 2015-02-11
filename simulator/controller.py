import cpu
import threading
import thread
from LRUAlgorithm import LRU
from LFUAlgorithm import LFU
from OptimalAlgorithm import Optimal


class Controller(object):
    
    def __init__(self, simulation_values):        
        self.page_num_stream = []  # Each List Entry
                              # [pid, virtual_page_number, set of threads that have
                              #  read from this entry]
        self.event_page_stream = threading.Event()  # Used to wait for an address to be 
                                               # available on page_num_stream
        self.lock = threading.Lock()                                     
        self.number_processes = simulation_values["num_processes"] 
        self.main_memory_size = simulation_values["memory"] * (2 ** 30)  # GB
        self.page_size = simulation_values["page_size"] * (2 ** 10)  # KB
        self.number_frames = self.main_memory_size / self.page_size
        self.simulation_window_size = simulation_values["window"]
        self.process_size = simulation_values["vas"] * (2 ** 30)  # GB 
        self.number_virtual_pages = self.process_size / self.page_size

        self.number_pr_threads = 3  # No of page replacement algorithms
        self.threads = []  # Array of PR started. Used to wait on them

    def start_simulation(self):
        try:
            thread = threading.Thread(target=lambda : cpu.start_CPU(self.number_processes, 
                                        self.page_num_stream, self.event_page_stream, self.lock), args=())
            self.threads.append(thread)
            thread.start()

            while(len(self.page_num_stream) < self.simulation_window_size):
                pass

            print "sim_win filled"
            print len(self.page_num_stream)
            
            optimal = Optimal(self.number_virtual_pages, self.number_frames, self.number_pr_threads, self.page_num_stream, 
                self.event_page_stream, self.lock, self.simulation_window_size)
            thread_optimal = threading.Thread(target=optimal, args=())
            self.threads.append(thread_optimal)
            thread_optimal.start()

                
            lru = LRU(self.number_virtual_pages, self.number_frames, self.number_pr_threads, self.page_num_stream, self.event_page_stream, self.lock)
            thread_lru = threading.Thread(target=lru, args=())
            self.threads.append(thread_lru)
            thread_lru.start()
        
            lfu = LFU(self.number_virtual_pages, self.number_frames, self.number_pr_threads, self.page_num_stream, self.event_page_stream, self.lock)
            thread_lfu = threading.Thread(target=lfu, args=())
            self.threads.append(thread_lfu)
            thread_lfu.start()
        

        except Exception as e:
            print "Failed to start thread:", e


        for thread in self.threads:
            thread.join()

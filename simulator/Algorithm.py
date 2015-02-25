import thread
import time
class Algorithm:

    def __init__(self, number_virtual_pages, number_frames, number_pr_threads, 
                       page_num_stream, event_page_stream, read_lock, thread_set,name,simulation_window_size=10):
        self.number_virtual_pages = number_virtual_pages
        self.number_pr_threads = number_pr_threads
        self.page_tables = { }  # Structure: PID => Page Table
                                # { virtual_page_no : 
                                #        { frame_no: #, present_bit: 1/0 } }
                                # index of page table is the virtual page number
        self.page_num_stream = page_num_stream
        self.event = event_page_stream
        self.simulating = True
        self.read_lock = read_lock
        self.page_fault_count = 0
        self.thread_set = thread_set
        self.simulation_window_size=simulation_window_size
        self.pages_accessed=0
        self.logs = []
        self.name=name

    def get_current_memory_mappings(self):
        virtual_addresses = []
        for frame in self.memory:      
            virtual_addresses.append(frame["virtual_page_no"])
        return virtual_addresses

    def get_next_log(self):
        if len(self.logs) > 0:
            return self.logs.pop(0)
        else:
            return ""

    def get_page_fault_count(self):
        print "In Algorithm :",self.name
        return self.page_fault_count

     #return page table for process    
    def get_page_table(self,pid):
        if pid not in self.page_tables:
            self.page_tables[pid] = {}
        page_table = self.page_tables[pid]
        return page_table

    def stop_algorithm(self):
        self.simulating = False


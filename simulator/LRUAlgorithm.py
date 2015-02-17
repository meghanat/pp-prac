import thread
import time


class LRU(object):
    def __init__(self, number_virtual_pages, number_frames, number_pr_threads, 
                       page_num_stream, event_page_stream, read_lock, thread_set,simulation_window_size=10, switching_window=10000):
        self.number_virtual_pages = number_virtual_pages
        self.number_pr_threads = number_pr_threads
        self.page_tables = { }  # Structure: PID => Page Table
                                # { virtual_page_no : 
                                #        { frame_no: #, present_bit: 1/0 } }
                                # index of page table is the virtual page number
        self.memory = [{"time" : 0, "pid": -1, "virtual_page_no": -1} for i in range(number_frames)]
        self.page_num_stream = page_num_stream
        self.event = event_page_stream
        self.simulating = True
        self.read_lock = read_lock
        self.page_fault_count = 0
        self.thread_set = thread_set
        self.simulation_window_size=simulation_window_size
        self.pages_accessed=0
        self.switching_window = switching_window
        self.name = "LRU"
        

    def reset_memory(self,current_memory):
        self.memory=[{"time" : 0, "pid": i["pid"], "virtual_page_no": i["virtual_page_no"]} for i in current_memory]


    def get_current_memory_mappings(self):
        virtual_addresses = []
        for frame in self.memory:      
            virtual_addresses.append(frame["virtual_page_no"])
        return virtual_addresses

    def stop_lru(self):
        self.simulating = False

    def get_page_fault_count(self):
        return self.page_fault_count

    #fill empty frame
    def fill_frame(self,virtual_page_no,pid,frame_no):
        print "LRU replace"
        page_table=self.page_tables[pid]
        #  Update the page table of this process
        if virtual_page_no not in page_table:
            page_table[virtual_page_no] = {}
        page_table[virtual_page_no]["frame_no"] = frame_no
        page_table[virtual_page_no]["present_bit"] = 1

        #  Update the frame entry also
        self.memory[frame_no]["pid"] = pid
        self.memory[frame_no]["time"] = time.time()#time.clock()
        self.memory[frame_no]["virtual_page_no"] = virtual_page_no
        self.page_fault_count += 1


    #swap out page from memory
    def replace_frame(self,virtual_page_no,pid):
        #print "here"
        print "LRU replace"
        frame_to_replace = min(self.memory, key=lambda x: x["time"])
        frame_no_to_replace = self.memory.index(frame_to_replace)

        # For the frame which is being replaced, make it's process'
        # page table's page table entry's present bit 1
        self.page_tables[frame_to_replace["pid"]]\
        [frame_to_replace["virtual_page_no"]]["present_bit"] = 0

        # For the current process' page table
        page_table=self.page_tables[pid]
        if virtual_page_no not in page_table:
            page_table[virtual_page_no] = {}

        page_table[virtual_page_no]["frame_no"] = frame_no_to_replace
        page_table[virtual_page_no]["present_bit"] = 1

        # Update the frame entry's PID and time stamp
        self.memory[frame_no_to_replace]["pid"] = pid
        self.memory[frame_no_to_replace]["time"] = time.time()#time.clock()
        self.memory[frame_no_to_replace]["virtual_page_no"] = virtual_page_no
        self.page_fault_count += 1

    #return page table for process    
    def get_page_table(self,pid):
        if pid not in self.page_tables:
            self.page_tables[pid] = {}
        page_table = self.page_tables[pid]
        return page_table
        
    def __call__(self,switcher):
        self.switcher=switcher
        while self.simulating:

            while(self.pages_accessed == self.switching_window):
                pass
            
            thread_id = thread.get_ident()

            if thread_id not in self.thread_set:  # Only if the thread hasn't already
                                             # read this address

                self.read_lock.acquire()
                #print " lru before event.wait",self.event.is_set()
                self.event.wait()
                #print " lru after event.wait",self.event.is_set()
                pid, virtual_page_no = self.page_num_stream[0]
                self.read_lock.release()
                self.pages_accessed+=1
                #get page table for process
                page_table=self.get_page_table(pid)

                if virtual_page_no in page_table:
                    pte = page_table[virtual_page_no]
                else:
                    pte = None

                if pte and pte["present_bit"]:
                    #  Update main memory time stamp
                    self.memory[pte["frame_no"]]["time"] = time.time()#time.clock()
                
                else:   #page not in memory
                    for frame_no, frame_entry in enumerate(self.memory):
                        if frame_entry["pid"] == -1:  # Empty Frame
                            self.fill_frame(virtual_page_no,pid,frame_no)
                            break
                    else:  # If all of the previous iterations went through,
                           # ie. if no frames are free
                        self.replace_frame(virtual_page_no,pid)

                self.thread_set.add(thread_id)  # This thread has read the address
            self.read_lock.acquire()
            #print thread_id, " LRU in 1"
            if(len(self.page_num_stream) != 0 and len(self.thread_set) == self.number_pr_threads):  # If all threads have read the value
                #print "Popped"
                self.page_num_stream.pop(0)
                self.thread_set.clear()
                if(len(self.page_num_stream) < self.simulation_window_size):  # Wait for an access to be made
                    self.event.clear() 

                if(self.pages_accessed == self.switching_window):
                    self.switcher.switch()
                
            self.read_lock.release()
            #print thread_id, " LRU out 1"

            
# TODO: Call a function from within a thread? This function is too long

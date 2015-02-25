import Algorithm
import thread


class LFU(Algorithm.Algorithm):
    def __init__(self, number_virtual_pages, number_frames, number_pr_threads, 
                       page_num_stream, event_page_stream, read_lock, thread_set,simulation_window_size=10):

        Algorithm.Algorithm.__init__(self, number_virtual_pages, number_frames, number_pr_threads, 
                       page_num_stream, event_page_stream, read_lock, thread_set,"LFU",simulation_window_size)

        self.memory = [{"frequency" : 0, "pid": -1, "virtual_page_no": -1} for i in range(number_frames)]
        


    def reset_memory(self,current_memory):
        self.memory=[{"frequency" : 0, "pid": i["pid"], "virtual_page_no": i["virtual_page_no"]} for i in current_memory]


    #fill empty frame
    def fill_frame(self,virtual_page_no,pid,frame_no):
        self.logs.append("Fill frame " + str(frame_no) + " with " + str(virtual_page_no) + "\n")
        page_table=self.page_tables[pid]

        #  Update the page table of this process
        if virtual_page_no not in page_table:
            page_table[virtual_page_no] = {}
        page_table[virtual_page_no]["frame_no"] = frame_no
        page_table[virtual_page_no]["present_bit"] = 1

        #  Update the frame entry also
        self.memory[frame_no]["pid"] = pid
        self.memory[frame_no]["frequency"] = 0
        self.memory[frame_no]["virtual_page_no"] = virtual_page_no
        self.page_fault_count += 1


    #swap out page from memory
    def replace_frame(self,virtual_page_no,pid):
        frame_to_replace = min(self.memory, key=lambda x: x["frequency"])
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

        self.logs.append("Replace page " + str(self.memory[frame_no_to_replace]["virtual_page_no"]) +
              " in frame " + str(frame_no_to_replace) + " with page " + str(virtual_page_no) + " of process " + str(pid) + "\n")

        # Update the frame entry's PID and frequency
        self.memory[frame_no_to_replace]["pid"] = pid
        self.memory[frame_no_to_replace]["frequency"] = 0
        self.memory[frame_no_to_replace]["virtual_page_no"] = virtual_page_no
        self.page_fault_count += 1

    def update_frame_in_memory(self, pte):
        self.memory[pte["frame_no"]]["frequency"] += 1
        
    def __call__(self,switcher):
        self.switcher=switcher
        while True:
            while(self.pages_accessed == self.simulation_window_size):
                pass
            thread_id = thread.get_ident()

            if thread_id not in self.thread_set:  # Only if the thread hasn't already
                                             # read this address
                #get page table for process

                self.read_lock.acquire()  
                #print " lru before event.wait",self.event.is_set()
                self.event.wait()
                #print " lru after event.wait",self.event.is_set()
                pid, virtual_page_no = self.page_num_stream[0]
                self.read_lock.release()
                self.pages_accessed+=1

                page_table=self.get_page_table(pid)

                if virtual_page_no in page_table:
                    pte = page_table[virtual_page_no]
                else:
                    pte = None

                if pte and pte["present_bit"]:
                    #  Update frequency of page
                    self.update_frame_in_memory(pte)
                
                else:   #page not in memory
                    for frame_no, frame_entry in enumerate(self.memory):
                        if frame_entry["pid"] == -1:  # Empty Frame
                            self.fill_frame(virtual_page_no,pid,frame_no)
                            break
                    else:  # If all of the previous iterations went through,
                           # ie. if no frames are free
                        self.replace_frame(virtual_page_no,pid)
                #print "LFU in"
                self.thread_set.add(thread_id)  # This thread has read the address
                #print "LFU out"

            self.read_lock.acquire()
            #print "LFU in 1"            
            if(len(self.page_num_stream) != 0 and len(self.thread_set) == self.number_pr_threads):  # If all threads have read the value

                self.page_num_stream.pop(0)
                self.thread_set.clear()
                
                if(len(self.page_num_stream) < self.simulation_window_size):  # Wait for an access to be made
                    self.event.clear() 

                if(self.pages_accessed == self.simulation_window_size):
                    self.switcher.switch()
                
            self.read_lock.release()
            #print "LFU out 1"

            

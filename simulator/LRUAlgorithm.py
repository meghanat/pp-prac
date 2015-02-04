import thread
import time

class LRU(object):
    def __init__(self, number_virtual_pages, number_frames, number_pr_threads, 
                       page_num_stream, event_page_stream):
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

    def get_current_memory_mappings(self):
        virtual_addresses = []
        for frame in self.memory:      
            virtual_addresses.append(frame["virtual_page_no"])
        return virtual_addresses

    def stop_lru(self):
        self.simulating = False

        
    def __call__(self):
        while self.simulating:
            if(len(self.page_num_stream) == 0):  # Wait for an access to be made
                self.event.clear()
            self.event.wait()

            print self.page_num_stream[0]
            pid, virtual_page_no, thread_set = self.page_num_stream[0]
            thread_id = thread.get_ident()

            if thread_id not in thread_set:  # Only if the thread hasn't already
                                             # read this address
                if pid not in self.page_tables:
                    self.page_tables[pid] = {}
                
                page_table = self.page_tables[pid]
                if virtual_page_no in page_table:
                    pte = page_table[virtual_page_no]
                else:
                    pte = None

                if pte and pte["present_bit"]:
                    #  Update main memory time stamp
                    self.memory[pte["frame_no"]]["time"] = time.clock()
                else:
                    for frame_no, frame_entry in enumerate(self.memory):
                        if frame_entry["pid"] == -1:  # Empty Frame
                            #  Update the page table of this process
                            if virtual_page_no not in page_table:
                                page_table[virtual_page_no] = {}
                            page_table[virtual_page_no]["frame_no"] = frame_no
                            page_table[virtual_page_no]["present_bit"] = 1

                            #  Update the frame entry also
                            self.memory[frame_no]["pid"] = pid
                            self.memory[frame_no]["time"] = time.clock()
                            self.memory[frame_no]["virtual_page_no"] = virtual_page_no

                            #print page_table
                            #print self.memory[frame_no]
                            break
                    else:  # If all of the previous iterations went through,
                           # ie. if no frames are free
                        frame_to_replace = min(self.memory, key=lambda x: x["time"])
                        frame_no_to_replace = self.memory.index(frame_to_replace)

                        # For the frame which is being replaced, make it's process'
                        # page table's page table entry's present bit 1
                        self.page_tables[frame_to_replace["pid"]]\
                        [frame_to_replace["virtual_page_no"]]["present_bit"] = 0

                        # For the current process' page table
                        if virtual_page_no not in page_table:
                            page_table[virtual_page_no] = {}

                        page_table[virtual_page_no]["frame_no"] = frame_no_to_replace
                        page_table[virtual_page_no]["present_bit"] = 1

                        # Update the frame entry's PID and time stamp
                        self.memory[frame_no_to_replace]["pid"] = pid
                        self.memory[frame_no_to_replace]["time"] = time.clock()
                        self.memory[frame_no_to_replace]["virtual_page_no"] = virtual_page_no

                self.page_num_stream[0][2].add(thread_id)  # This thread has read the address
            
            if(len(self.page_num_stream[0][2]) == self.number_pr_threads):  # If all threads have read the value
                #print "Popped"
                self.page_num_stream.pop(0)
            
# TODO: Call a function from within a thread? This function is too long

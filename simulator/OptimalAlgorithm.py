import thread



class Optimal(object):

    def __init__(self, number_virtual_pages, number_frames, number_pr_threads, 
                       page_num_stream, event_page_stream, read_lock, simulation_window_size):
        self.number_virtual_pages = number_virtual_pages
        self.number_pr_threads = number_pr_threads
        self.page_tables = { }  # Structure: PID => Page Table
                                # { virtual_page_no : 
                                #        { frame_no: #, present_bit: 1/0 } }
                                # index of page table is the virtual page number
        self.memory = [{"pid": -1, "virtual_page_no": -1} for i in range(number_frames)]
        self.page_num_stream = page_num_stream
        self.event = event_page_stream
        self.simulating = True
        self.simulation_window_size = simulation_window_size
        self.read_lock = read_lock


    def get_current_memory_mappings(self):
        virtual_addresses = []
        for frame in self.memory:      
            virtual_addresses.append(frame["virtual_page_no"])
        return virtual_addresses

    def stop_optimal(self):
        self.simulating = False

    #fill empty frame
    def fill_frame(self,virtual_page_no,pid,frame_no):
        page_table=self.page_tables[pid]
        #  Update the page table of this process
        if virtual_page_no not in page_table:
            page_table[virtual_page_no] = {}
        page_table[virtual_page_no]["frame_no"] = frame_no
        page_table[virtual_page_no]["present_bit"] = 1

        #  Update the frame entry also
        self.memory[frame_no]["pid"] = pid
        self.memory[frame_no]["virtual_page_no"] = virtual_page_no


    #swap out page from memory
    def replace_frame(self,virtual_page_no,pid):
        #print "here"
        
        #frame_to_replace = min(self.memory, key=lambda x: x["time"])
    
        next_access=-1
        frame_to_replace={}

        for frame_no,frame in enumerate(self.memory):
            try:
                i=self.page_num_stream.index(frame["virtual_page_no"],0,self.simulation_window_size)
                if i> next_access:
                    next_access=i
                    frame_to_replace=frame
                    frame_no_to_replace=frame_no

            except ValueError: # not in the simulation_window
                frame_to_replace=frame
                frame_no_to_replace=frame_no
                break
                

        #print frame_to_replace


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
        self.memory[frame_no_to_replace]["virtual_page_no"] = virtual_page_no

    #return page table for process    
    def get_page_table(self,pid):
        if pid not in self.page_tables:
            self.page_tables[pid] = {}
        page_table = self.page_tables[pid]
        return page_table
        
    def __call__(self):
        while self.simulating:
            if(len(self.page_num_stream) == 0):  # Wait for an access to be made
                self.event.clear() 

            self.event.wait()
            
            self.read_lock.acquire()
            pid, virtual_page_no, thread_set = self.page_num_stream[0]
            self.read_lock.release()
            
            thread_id = thread.get_ident()

            if thread_id not in thread_set:  # Only if the thread hasn't already
                                             # read this address
                #get page table for process
                page_table=self.get_page_table(pid)

                if virtual_page_no in page_table:
                    pte = page_table[virtual_page_no]
                else:
                    pte = None
                if pte and pte["present_bit"]:
                    pass
                else:   #page not in memory
                    for frame_no, frame_entry in enumerate(self.memory):
                        if frame_entry["pid"] == -1:  # Empty Frame
                            self.fill_frame(virtual_page_no,pid,frame_no)
                            break
                    else:  # If all of the previous iterations went through,
                           # ie. if no frames are free
                        self.replace_frame(virtual_page_no,pid)
                        
                self.page_num_stream[0][2].add(thread_id)  # This thread has read the address
            
            self.read_lock.acquire()
            if(len(self.page_num_stream[0][2]) == self.number_pr_threads):  # If all threads have read the value
                #print "Popped"
                self.page_num_stream.pop(0)
            self.read_lock.release()
            

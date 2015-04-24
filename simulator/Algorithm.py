import thread
import time
import copy
import tkMessageBox



class Algorithm:
    def __init__(self,simulation_values):
        self.number_pr_threads = simulation_values["number_pr_threads"]
        self.page_tables = { }  # Structure: PID => Page Table
                                # { virtual_page_no : 
                                #        { frame_no: #, present_bit: 1/0 } }
                                # index of page table is the virtual page number


        self.page_num_stream = simulation_values["page_num_stream"]
        self.event = simulation_values["event_page_stream"]
        
        self.read_lock = simulation_values["read_lock"]
        self.page_fault_count = 0
        self.thread_set = simulation_values["thread_set"]
        self.switcher_size=simulation_values["window"]
        self.pages_accessed=0
        self.logs = []
        self.name=simulation_values["name"]
        #print self.name, simulation_values
        self.switching_event = simulation_values["switching_event"]
        self.simulation_values=simulation_values

    def get_current_memory_mappings(self):
        virtual_addresses = []
        for frame in self.memory:      
            virtual_addresses.append(frame["virtual_page_no"])
        return virtual_addresses

    def reset_page_tables(self, current_page_table):
        self.page_tables = copy.deepcopy(current_page_table)

    def get_next_log(self):
        if len(self.logs) > 0:
            return self.logs.pop(0)
        else:
            return ""

    def get_page_fault_count(self):
        return self.page_fault_count

     #return page table for process    
    def get_page_table(self,pid):
        if pid not in self.page_tables:
            self.page_tables[pid] = {}
        page_table = self.page_tables[pid]
        return page_table

    def stop_algorithm(self):
        self.simulating = False

    # This method *must* be overidden in the subclass algorithms
    def update_frame_in_memory(self, pte):
        pass

    def __call__(self,switcher):
        self.switcher=switcher
        no_wins = 1
        while self.simulation_values["simulating"]:

            self.switching_event.wait()            
            thread_id = thread.get_ident()

            if thread_id not in self.thread_set:  # Only if the thread hasn't already
                                             # read this address

                self.read_lock.acquire()
                self.event.wait()
                
                pid, virtual_page_no = self.page_num_stream[0]
                # if(self.name=="Random"):
                #     print "pid: ",pid," virtual_page_no: ",virtual_page_no,"\n"

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
                    self.update_frame_in_memory(pte)
                
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

            if(len(self.page_num_stream) != 0 and len(self.thread_set) == self.number_pr_threads):  # If all threads have read the value
                #print "Popped"
                self.page_num_stream.pop(0)
                self.thread_set.clear()
                if(len(self.page_num_stream) < self.switcher_size):  # Wait for an access to be made
                    if(self.simulation_values["read_from_file"]):
                        self.simulation_values["simulating"]=False
                        #print "Sim stopped"
                        tkMessageBox.showerror("Alert","Simulation stopped")

                    self.event.clear() 

                if(self.pages_accessed == self.switcher_size):
                    self.switcher.switch(self.switching_event)
                    
                
            self.read_lock.release()

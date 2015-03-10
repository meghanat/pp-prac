import Algorithm
import itertools
import thread
import time


class Optimal(Algorithm.Algorithm):
    def __init__(self, simulation_values):
        
       
        simulation_values["name"]="Optimal"
        Algorithm.Algorithm.__init__(self,simulation_values)
        self.memory = []

        for i in itertools.count(0):
            if i == simulation_values["number_frames"]:
                break
            self.memory.append({"pid": -1, "virtual_page_no": -1})
        self.name = "Optimal"


    def reset_memory(self,current_memory):
        self.memory=[{"pid": i["pid"], "virtual_page_no": i["virtual_page_no"]} for i in current_memory]



    #fill empty frame
    def fill_frame(self,virtual_page_no, pid, frame_no):
        self.logs.append("Fill frame " +  str(frame_no) + " with " + str(virtual_page_no) + "\n")
        page_table=self.page_tables[pid]
        #  Update the page table of this process
        if virtual_page_no not in page_table:
            page_table[virtual_page_no] = {}
        page_table[virtual_page_no]["frame_no"] = frame_no
        page_table[virtual_page_no]["present_bit"] = 1

        #  Update the frame entry also
        self.memory[frame_no]["pid"] = pid
        self.memory[frame_no]["virtual_page_no"] = virtual_page_no
        self.page_fault_count += 1


     #swap out page from memory
    def replace_frame(self,virtual_page_no,pid):
        next_access=-1
        frame_to_replace={}

        for frame_no,frame in enumerate(self.memory):
            try:
                i=self.page_num_stream.index([frame["pid"],frame["virtual_page_no"]],0,self.simulation_window_size-self.pages_accessed)
                #print frame_no," index: ",i
                if i> next_access:
                    next_access=i
                    frame_to_replace=frame
                    frame_no_to_replace=frame_no

            except ValueError: # not in the simulation_window
                frame_to_replace=frame
                frame_no_to_replace=frame_no
                break
                
        self.page_fault_count += 1

        # For the frame which is being replaced, make it's process'
        # page table's page table entry's present bit 0
        self.page_tables[frame_to_replace["pid"]]\
        [frame_to_replace["virtual_page_no"]]["present_bit"] = 0

        # For the current process' page table
        page_table=self.page_tables[pid]
        if virtual_page_no not in page_table:
            page_table[virtual_page_no] = {}

        page_table[virtual_page_no]["frame_no"] = frame_no_to_replace
        page_table[virtual_page_no]["present_bit"] = 1

        self.logs.append("Optimal: Replace page " + str(self.memory[frame_no_to_replace]["virtual_page_no"]) +
              " in frame " + str(frame_no_to_replace) + " with page " + str(virtual_page_no) + " of process " + str(pid) + "\n")
        # Update the frame entry's PID and time stamp
        self.memory[frame_no_to_replace]["pid"] = pid
        self.memory[frame_no_to_replace]["virtual_page_no"] = virtual_page_no


    #return page table for process    
    def get_page_table(self,pid):
        if pid not in self.page_tables:
            self.page_tables[pid] = {}
        page_table = self.page_tables[pid]
        return page_table

    def update_frame_in_memory(self, pte):
        pass

            

import Algorithm
import thread
import time


class FIFO(Algorithm.Algorithm):
    def __init__(self, simulation_values):

        simulation_values["name"]="FIFO"
        Algorithm.Algorithm.__init__(self,simulation_values)
        
        self.memory = [{"pid": -1, "virtual_page_no": -1} for i in range(simulation_values["number_frames"])]
        self.name = "FIFO"
        self.i = -1
        

    def reset_memory(self,current_memory):
        self.memory=[{"pid": i["pid"], "virtual_page_no": i["virtual_page_no"]} for i in current_memory]


    
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
        self.memory[frame_no]["virtual_page_no"] = virtual_page_no
        self.page_fault_count += 1


    #swap out page from memory
    def replace_frame(self,virtual_page_no,pid):
        self.i = (self.i + 1) % len(self.memory)
        frame_to_replace = self.memory[self.i]
        frame_no_to_replace = self.i

        # For the frame which is being replaced, make it's process'
        # page table's page table entry's present bit 1
        self.page_tables[frame_to_replace["pid"]]\
        [frame_to_replace["virtual_page_no"]]["present_bit"] = 0

        # For the current process' page table
        page_table=self.page_tables[pid]
        if virtual_page_no not in page_table:
            page_table[virtual_page_no] = {}

        self.logs.append("Replace page " + str(self.memory[frame_no_to_replace]["virtual_page_no"]) +
             " in frame " + str(frame_no_to_replace) + " with page " +  str(virtual_page_no) + " of process " + str(pid) +"\n")

        page_table[virtual_page_no]["frame_no"] = frame_no_to_replace
        page_table[virtual_page_no]["present_bit"] = 1

        # Update the frame entry's PID and time stamp
        self.memory[frame_no_to_replace]["pid"] = pid
        self.memory[frame_no_to_replace]["virtual_page_no"] = virtual_page_no
        self.page_fault_count += 1

    def update_frame_in_memory(self, pte):
        pass
            
        

import Algorithm
import itertools
import thread
import time


class Clock(Algorithm.Algorithm):    
    def __init__(self,  simulation_values):
        simulation_values["name"] = "CLOCK"
        Algorithm.Algorithm.__init__(self, simulation_values)
        self.memory = []
        self.next_frame_pointer = 0
        self.number_frames = simulation_values["number_frames"]

        for i in itertools.count(0):
            if i == simulation_values["number_frames"]:
                break
            self.memory.append({"use_bit" : 0, "pid": -1, "virtual_page_no": -1})

    def reset_memory(self,current_memory):
        self.memory=[{"use_bit" : 0, "pid": i["pid"], "virtual_page_no": i["virtual_page_no"]} for i in current_memory]


    #fill empty frame
    def fill_frame(self,virtual_page_no,pid,frame_no):
        self.logs.append("Fill frame " + str(frame_no) + " with " + str(virtual_page_no) + "\n")

        page_table = self.page_tables[pid]

        #  Update the page table of this process
        if virtual_page_no not in page_table:
            page_table[virtual_page_no] = {}
        page_table[virtual_page_no]["frame_no"] = frame_no
        page_table[virtual_page_no]["present_bit"] = 1

        #  Update the frame entry also
        self.memory[frame_no]["pid"] = pid
        self.memory[frame_no]["use_bit"] = 1
        self.memory[frame_no]["virtual_page_no"] = virtual_page_no
        self.page_fault_count += 1
        self.next_frame_pointer = (self.next_frame_pointer + 1) % self.number_frames

    def check_next_frame_use_bit(self):

    def get_frame_to_replace(self):
        current = self.next_frame_pointer

        # increment next frame and check use bit; if it is 0, return else clear it
        self.next_frame_pointer = (self.next_frame_pointer + 1) % self.number_frames
        if self.memory[self.next_frame_pointer]["use_bit"] == 0:
            return self.next_frame_pointer
        # clear it
        self.memory[self.next_frame_pointer]["use_bit"] = 0
        self.next_frame_pointer = (self.next_frame_pointer + 1) % self.number_frames

        while self.next_frame_pointer != current:
            if self.memory[self.next_frame_pointer]["use_bit"] == 0:
                return self.next_frame_pointer
            self.memory[self.next_frame_pointer]["use_bit"] = 0  
            self.next_frame_pointer = (self.next_frame_pointer + 1) % self.number_frames

        # Reached the initial position of the pointer and all use_bits found to be 1
        else:
            self.next_frame_pointer = (self.next_frame_pointer + 1) % self.number_frames
            return current

    #swap out page from memory
    def replace_frame(self,virtual_page_no,pid):
        frame_no_to_replace = self.get_frame_to_replace()
        frame_to_replace = self.memory[frame_no_to_replace]

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

        self.logs.append("Replace page " + str(self.memory[frame_no_to_replace]["virtual_page_no"]) +
             " in frame " + str(frame_no_to_replace) + " with page " +  str(virtual_page_no) + " of process " + str(pid) +"\n")

        # Update the frame entry's PID and time stamp
        self.memory[frame_no_to_replace]["pid"] = pid
        self.memory[frame_no_to_replace]["use_bit"] = 1
        self.memory[frame_no_to_replace]["virtual_page_no"] = virtual_page_no
        self.page_fault_count += 1

    def update_frame_in_memory(self, pte):
        self.memory[pte["frame_no"]]["time"] = time.time()
        self.memory[pte["frame_no"]]["use_bit"] = 1


        

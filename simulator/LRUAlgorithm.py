import thread
import time
import Algorithm

class LRU(Algorithm.Algorithm):
    def __init__(self, number_virtual_pages, number_frames, number_pr_threads, 
                       page_num_stream, event_page_stream, read_lock, thread_set,simulation_window_size=10):
        
        Algorithm.Algorithm.__init__(self, number_virtual_pages, number_frames, number_pr_threads, 
                       page_num_stream, event_page_stream, read_lock, thread_set,simulation_window_size=10)

        self.memory = [{"time" : 0, "pid": -1, "virtual_page_no": -1} for i in range(number_frames)]
        self.name = "LRU"
        

    def reset_memory(self,current_memory):
        self.memory=[{"time" : 0, "pid": i["pid"], "virtual_page_no": i["virtual_page_no"]} for i in current_memory]


    def stop_lru(self):
        self.simulating = False

    #fill empty frame
    def fill_frame(self,virtual_page_no,pid,frame_no):
        self.logs.append("LRU: Fill frame " + str(frame_no) + " with " + str(virtual_page_no) + "\n")

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

        self.logs.append("Replace page " + str(self.memory[frame_no_to_replace]["virtual_page_no"]) +
             " in frame " + str(frame_no_to_replace) + " with page " +  str(virtual_page_no) + " of process " + str(pid) +"\n")

        # Update the frame entry's PID and time stamp
        self.memory[frame_no_to_replace]["pid"] = pid
        self.memory[frame_no_to_replace]["time"] = time.time()#time.clock()
        self.memory[frame_no_to_replace]["virtual_page_no"] = virtual_page_no
        self.page_fault_count += 1
        

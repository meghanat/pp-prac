import threading
import unittest
import time
import cpu


#def __init__(self,simulation_values):

class TestCPU(unittest.TestCase):
    

    def setUp(self):
        
        self.simulation_values = {}
        self.simulation_values["number_frames"] = 3
        self.simulation_values["vas"] = 4
        self.simulation_values["event_page_stream"] = threading.Event()  
        self.simulation_values["event_page_stream"].set()
        self.simulation_values["switching_event"] = threading.Event()
        self.simulation_values["switching_event"].set()
        self.simulation_values["read_lock"] = threading.Lock()                                 
        self.simulation_values["process_size"] = self.simulation_values["vas"] * (2 ** 30)  # GB 
        self.simulation_values["number_pr_threads"] = 1 # No of page replacement algorithms
        self.simulation_values["thread_set"] = set()  # Global set; Used to indicate reading of an elem by all algos.
        self.simulation_values["window"] = 10  
        self.simulation_values["simulating"] = True      
        self.simulation_values["read_from_file"] = False  
        self.simulation_values['page_num_stream']=[]
        
    def test_one_process(self):
    	self.simulation_values["number_processes"] = 1
        
        cpuobj=cpu.CPU(self.simulation_values)
        thread_cpu = threading.Thread(target=cpuobj.page_access_stream)
        thread_cpu.start()
        time.sleep(5)
        self.assertTrue(len(cpuobj.page_num_stream)>0)

    def test_hundred_processes(self):
        self.simulation_values["number_processes"] = 100
        
        cpuobj=cpu.CPU(self.simulation_values)
        thread_cpu = threading.Thread(target=cpuobj.page_access_stream)
        thread_cpu.start()
        time.sleep(5)
        self.assertTrue(len(cpuobj.page_num_stream)>0)



    def tearDown(self):
    	self.simulation_values["simulating"]=False

    
if __name__ == '__main__':
    unittest.main(verbosity=2)

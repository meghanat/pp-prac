import OptimalAlgorithm as opt
import LRUAlgorithm as lru
import FIFOAlgorithm as fifo
import LFUAlgorithm as lfu
import threading
import unittest


class TestAlgorithmPageFaultCounts(unittest.TestCase):

    def setUp(self):
        self.simulation_values = {}
        self.simulation_values["number_frames"] = 3
        self.simulation_values["vas"] = 4
        self.simulation_values["number_processes"] = 1

        self.simulation_values["page_num_stream"] = [[1, 2], [1, 3], [1, 2], [1, 1], [1, 5], [1, 2], [1, 4], [1, 5], [1, 3]]
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

    def test_lru_page_fault_count(self):
        expected_faults = 6
        lruob = lru.LRU(self.simulation_values)
        thread_lru = threading.Thread(target=lruob, args=(None,))
        thread_lru.start()
        while len(self.simulation_values["page_num_stream"]) > 0:
            self.simulation_values["event_page_stream"].set()
            self.simulation_values["switching_event"].set()

        thread_lru._Thread__stop()
        self.assertEqual(expected_faults, lruob.get_page_fault_count())

    def test_optimal_page_fault_count(self):
        expected_faults = 5
        opt_ob = opt.Optimal(self.simulation_values)
        thread_opt = threading.Thread(target=opt_ob, args=(None,))
        thread_opt.start()
        while len(self.simulation_values["page_num_stream"]) > 0:
            self.simulation_values["event_page_stream"].set()
            self.simulation_values["switching_event"].set()
        thread_opt._Thread__stop()
        self.assertEqual(expected_faults, opt_ob.get_page_fault_count())

    def test_fifo_page_fault_count(self):
        expected_faults = 7
        fifo_ob = fifo.FIFO(self.simulation_values)
        thread_fifo = threading.Thread(target=fifo_ob, args=(None,))
        thread_fifo.start()
        while len(self.simulation_values["page_num_stream"]) > 0:
            self.simulation_values["event_page_stream"].set()
            self.simulation_values["switching_event"].set()
        thread_fifo._Thread__stop()
        self.assertEqual(expected_faults, fifo_ob.get_page_fault_count())        

    def test_lfu_page_fault_count(self):
        expected_faults = 7
        lfuob = lfu.LFU(self.simulation_values)
        thread_lfu = threading.Thread(target=lfuob, args=(None,))
        thread_lfu.start()
        while len(self.simulation_values["page_num_stream"]) > 0:
            self.simulation_values["event_page_stream"].set()
            self.simulation_values["switching_event"].set()
        thread_lfu._Thread__stop()
        self.assertEqual(expected_faults, lfuob.get_page_fault_count())        

if __name__ == '__main__':
    unittest.main()

import threading
import unittest
import time
import Generator as gen


#def __init__(self,simulation_values, address_stream, event, prob_dist=[0.6, 0.3, 0.1], process_size=1 << 32,switcher_size=10):

class TestGenerator(unittest.TestCase):

    def setUp(self):
        self.simulation_values = {"simulating":True}
        self.address_stream=[]
        self.event=threading.Event()

        
    def test_default_values(self):

    	genobj=gen.VirtualAddressGenerator(self.simulation_values,self.address_stream,self.event)
    	time.sleep(5)
    	self.assertTrue(len(genobj.address_stream)>0)


    def test_process_size_zero(self):
    	with self.assertRaises(ValueError):
    		genobj=gen.VirtualAddressGenerator(self.simulation_values,self.address_stream,self.event,process_size=0)

    def test_normal_values(self):

    	genobj=gen.VirtualAddressGenerator(self.simulation_values,self.address_stream,self.event,process_size=4<<32,switcher_size=1000)
    	time.sleep(5)
    	self.assertTrue(len(genobj.address_stream)>0)


    def tearDown(self):
    	self.simulation_values["simulating"]=False

    
if __name__ == '__main__':
    unittest.main(verbosity=2)

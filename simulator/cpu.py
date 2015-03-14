import threading
import thread
import Generator


class CPU:
    def __init__(self,simulation_values):
        print "In CPU,", simulation_values
        self.simulation_values=simulation_values
        self.num_processes = simulation_values["number_processes"]
        self.addr_access_stream = []
        self.page_num_stream = simulation_values["page_num_stream"]
        self.event_access_stream = threading.Event()
        self.event_page_stream = simulation_values["event_page_stream"]
        self.PAGE_SHIFT = 12 # Get page size log to the base 2 of this
        self.lock = simulation_values["read_lock"]
        self.switcher_size = simulation_values["window"]
        try:
            self.objects = [Generator.VirtualAddressGenerator(self.simulation_values,self.addr_access_stream, self.event_access_stream, switcher_size=self.switcher_size) for i in range(self.num_processes)]
        except Exception as e:
            print e

    def page_access_stream(self):
        while(self.simulation_values["simulating"]):
            if(len(self.addr_access_stream) == 0):
                print "empty"
                self.event_access_stream.clear()
            self.event_access_stream.wait()

            pid, virt_addr = self.addr_access_stream.pop(0)
            virt_page = virt_addr >> self.PAGE_SHIFT
            self.page_num_stream.append([pid, virt_page])
            self.event_page_stream.set()

def start_CPU(simulation_values):
    print "here"
    mCPU = CPU(simulation_values)
    try:
        mCPU.page_access_stream()

    except Exception as e:
        print e

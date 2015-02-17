import threading
import thread
import Generator


class CPU:
    def __init__(self, num_processes, page_num_stream, event_page_stream, lock,simulation_window_size):
        self.num_processes = num_processes
        self.addr_access_stream = []
        self.page_num_stream =  page_num_stream
        self.event_access_stream = threading.Event()
        self.event_page_stream = event_page_stream
        self.PAGE_SHIFT = 12 # Get page size log to the base 2 of this
        self.lock = lock
        self.simulation_window_size = simulation_window_size
        try:
            self.objects = [Generator.VirtualAddressGenerator(self.addr_access_stream, self.event_access_stream, simulation_window_size=self.simulation_window_size) for i in range(self.num_processes)]
        except Exception as e:
            print e

    def page_access_stream(self):
        while(True):
            if(len(self.addr_access_stream) == 0):
                self.event_access_stream.clear()
            self.event_access_stream.wait()

            pid, virt_addr = self.addr_access_stream.pop(0)
            virt_page = virt_addr >> self.PAGE_SHIFT
            self.page_num_stream.append([pid, virt_page])
            self.event_page_stream.set()

def start_CPU(num_processes, page_num_stream, event_page_stream, lock,simulation_window_size):
    mCPU = CPU(num_processes, page_num_stream, event_page_stream, lock,simulation_window_size)
    try:
        mCPU.page_access_stream()

    except Exception as e:
        print e

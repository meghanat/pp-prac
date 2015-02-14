import threading
import thread
import Generator


class CPU:
    def __init__(self, num_processes, page_num_stream, event_page_stream, lock):
        self.num_processes = num_processes
        self.addr_access_stream = []
        self.page_num_stream =  page_num_stream  # [[page_num,access_count]] # Removing this because we are moving it to the higher controller
        self.event_access_stream = threading.Event()
        self.event_page_stream = event_page_stream
        self.PAGE_SHIFT = 12
        self.lock = lock
        try:
            self.objects = [Generator.VirtualAddressGenerator(self.addr_access_stream, self.event_access_stream) for i in range(self.num_processes)]
        except Exception as e:
            print e

    def page_access_stream(self):
        while(True):
            if(len(self.addr_access_stream) == 0):
                self.event_access_stream.clear()
            self.event_access_stream.wait()

            pid, virt_addr = self.addr_access_stream.pop(0)
            virt_page = virt_addr >> self.PAGE_SHIFT
            self.page_num_stream.append([pid, virt_page, set()])
            self.event_page_stream.set()

def start_CPU(num_processes, page_num_stream, event_page_stream, lock):
    mCPU = CPU(num_processes, page_num_stream, event_page_stream, lock)
    try:
        mCPU.page_access_stream()

    except Exception as e:
        print e

import threading
import thread
import Generator

class CPU:

    def __init__(self,num_processes,virt_addr_size):
        self.num_processes=num_processes
        self.virt_addr_size=virt_addr_size
        self.addr_access_stream=[]
        self.page_num_stream=[] #[[page_num,access_count]]
        self.event=threading.Event()
        self.PAGE_SHIFT=12
        self.objects = [Generator.VirtualAddressGenerator(self.addr_access_stream, self.event) for i in range(self.num_processes)]

    def page_access_stream(self):
        while(True):
            if(len(self.addr_access_stream)==0):
                self.event.clear()
            self.event.wait()
            
            #print self.addr_access_stream
            #print self.event.is_set()
            virt_addr=self.addr_access_stream.pop(0)

            virt_page=virt_addr>>self.PAGE_SHIFT
            print virt_page,"\n"
            self.page_num_stream.append([virt_page,0])
            
    """
    def gen_random(self):
        while (True):
            self.addr_access_stream.append(1<<32)
            self.event.set()
    """


mCPU=CPU(2,4)
try:
    mCPU.page_access_stream()
    
except Exception as e:
    print e

            





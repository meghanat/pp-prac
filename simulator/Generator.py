import random
import numpy.random
import thread
import threading


class VirtualAddressGenerator:
    pid = 0
    def __init__(self,simulation_values, address_stream, event, prob_dist=[0.3, 0.3, 0.4], process_size=1 << 32,switcher_size=10):
        self.process_size = process_size
        self.kernel_space = 1 << 30  # Remove this hard coded value
        self.prob_dist = prob_dist
        self.values = [1, 2, 3]
        self.current_address = random.randrange(self.kernel_space, self.process_size, 4)
        self.address_stream = address_stream
        self.event = event
        self.switcher_size = switcher_size
        self.simulation_values=simulation_values
        try:
            thread = threading.Thread(target=self.generate_virtual_address, args=())
            thread.start()
        except Exception as e:
            print e

    def increment_address(self, pid):
        #print "Increment ", pid, "\n"
        self.current_address += 4
        # print self.current_address
        self.address_stream.append((pid, self.current_address))
        if(len(self.address_stream) >= self.switcher_size):
            self.event.set()

    def generate_loop_addresses(self, pid):
        #print "Loop ", pid, "\n"
        num_iterations = random.randrange(10, 100)
        offset = random.randrange(4, 4000, 4)  # one to thousand instructions per iteration
        
        if self.current_address+offset > self.process_size:
            offset=self.process_size - self.current_address
            
        for i in range(num_iterations):
            for j in range(self.current_address, self.current_address + offset, 4):
                #print "Address: ", j, "; Process: ", pid, "\n"
                self.address_stream.append((pid, j))
                if(len(self.address_stream) >= self.switcher_size):
                    self.event.set()

        self.current_address += offset + 4
        #print "Address: ", self.current_address, "; Process: ", pid, "\n"
        self.address_stream.append((pid, self.current_address))
        if(len(self.address_stream) >= self.switcher_size):
            self.event.set()


    def generate_jump_addresses(self, pid):
        #print "Jump: ", pid, "\n"
        jump_to = random.randrange(self.kernel_space, self.process_size-4000, 4)
        #print " jump_to :",jump_to,"\n"
        offset = random.randrange(4, 4000, 4)
        
        for j in range(jump_to, jump_to + offset, 4):
            #print "Address: ", j, "; Process: ", pid, "\n"
            self.address_stream.append((pid, j))
            if(len(self.address_stream) >= self.switcher_size):
                self.event.set()

        self.current_address += 4
        #print "Address: ", self.current_address, "; Process: ", pid, "\n"
        self.address_stream.append((pid, self.current_address))
        if(len(self.address_stream) >= self.switcher_size):
            self.event.set()

    def generate_virtual_address(self):
        VirtualAddressGenerator.pid += 1
        pid = VirtualAddressGenerator.pid
        while (self.simulation_values["simulating"]):

            gen_value = numpy.random.choice(self.values, None, self.prob_dist)
        
            if(gen_value == 1):
                self.increment_address(pid)
                
            elif (gen_value == 2):
                self.generate_loop_addresses(pid)

            elif (gen_value == 3):
                # print "Jump\n"
                self.generate_jump_addresses(pid)
                

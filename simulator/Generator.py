import random
import numpy.random
import thread
import threading


class VirtualAddressGenerator:
    pid = 0
    def __init__(self, address_stream, event, prob_dist=[0.6, 0.3, 0.1], process_size=1 << 32):
        self.process_size = process_size
        self.kernel_space = 1 << 30
        self.prob_dist = prob_dist
        self.values = [1, 2, 3]
        self.current_address = random.randrange(self.kernel_space, self.process_size, 4)
        self.address_stream = address_stream
        self.event = event
        try:
            thread = threading.Thread(target=self.generate_virtual_address, args=())
            thread.start()
            #  TODO : Need to join these threads somewhere :}
        except Exception as e:
            print e

    def increment_address(self):
        # print "Increment\n"
        self.current_address += 4
        # print self.current_address
        self.address_stream.append((VirtualAddressGenerator.pid, self.current_address))
        self.event.set()

    def generate_loop_addresses(self):
        num_iterations = random.randrange(10, 10000)

        offset = random.randrange(4, 4000, 4)  # one to thousand instructions per iteration
        
        if self.current_address+offset > self.process_size:
            offset=self.process_size-self.current_address
            
        for i in range(num_iterations):
            for j in range(self.current_address, self.current_address + offset, 4):
                # print j, "\n"
                self.address_stream.append((VirtualAddressGenerator.pid, j))
                self.event.set()

        self.current_address += offset + 4
        self.address_stream.append((VirtualAddressGenerator.pid, self.current_address))
        self.event.set()

    def generate_jump_addresses(self):

        jump_to = random.randrange(self.kernel_space, self.process_size-4000, 4)
        offset = random.randrange(4, 4000, 4)
        for j in range(jump_to, jump_to + offset, 4):
            # print j, "\n"
            self.address_stream.append((VirtualAddressGenerator.pid, j))
            self.event.set()
        self.current_address += 4
        self.address_stream.append((VirtualAddressGenerator.pid, self.current_address))
        self.event.set()

    def generate_virtual_address(self):
        VirtualAddressGenerator.pid += 1
        while (True):
            gen_value = numpy.random.choice(self.values, None, self.prob_dist)
            if(gen_value == 1):
                self.increment_address()
                
            elif (gen_value == 2):
                # print "Loop\n"
                self.generate_loop_addresses()

            elif (gen_value == 3):
                # print "Jump\n"
                self.generate_jump_addresses()
                

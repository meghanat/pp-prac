import time
class Switcher(object):
	def __init__(self,current_algorithm,other_algorithms):
		self.current_algorithm=current_algorithm
		self.other_algorithms=other_algorithms

	def switch(self):
		print "SWITChER"
		time.sleep(5)
		for i in self.other_algorithms:
			i.reset_memory(self.current_algorithm.memory)
			i.page_tables=dict(self.current_algorithm.page_tables)
			i.page_fault_count=0
		
		self.current_algorithm=min(self.other_algorithms,key=lambda x: x.get_page_fault_count)
		print self.current_algorithm.name

		for i in self.other_algorithms:
			i.pages_accessed=0





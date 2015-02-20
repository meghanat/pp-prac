import time
class Switcher(object):
	def __init__(self,current_algorithm,other_algorithms,optimal):
		self.current_algorithm=current_algorithm
		self.other_algorithms=other_algorithms
		self.optimal=optimal

	def switch(self):
		print "Switch"
		best = min(self.other_algorithms, key=lambda x: x.get_page_fault_count())
		print self.best.name

		for i in self.other_algorithms:
			i.reset_memory(self.current_algorithm.memory)
			i.page_tables=dict(self.current_algorithm.page_tables)
			i.page_fault_count=0
		self.optimal.page_fault_count=0 # since optimal is also passed but isnt part of other_algorithms[]
	
		for i in self.other_algorithms:
			i.pages_accessed=0
		self.optimal.pages_accessed=0 # since the pages being accessed must be the same across all algorithms	

		self.current_algorithm = best



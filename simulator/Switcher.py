import time
class Switcher(object):
	def __init__(self,current_algorithm,other_algorithms,optimal):
		self.current_algorithm=current_algorithm
		self.other_algorithms=other_algorithms
		self.optimal=optimal
		self.total_count = 0

	def switch(self, swithing_event):
		swithing_event.clear()
		# print "Switch"
		best = min(self.other_algorithms, key=lambda x: x.get_page_fault_count())
		#print best.name
		# for i in self.other_algorithms:
		# 	print i.name, i.get_page_fault_count()
		# 	print i.name, i.pages_accessed
		# print self.optimal.get_page_fault_count()
		# print self.optimal.pages_accessed

		self.total_count += self.current_algorithm.get_page_fault_count()

		for i in self.other_algorithms:
			i.reset_memory(self.current_algorithm.memory)
			i.reset_page_tables(self.current_algorithm.page_tables)
			i.page_fault_count=0
		self.optimal.page_fault_count=0 # since optimal is also passed but isnt part of other_algorithms[]
		self.optimal.reset_memory(self.current_algorithm.memory)
		self.optimal.reset_page_tables(self.current_algorithm.page_tables)
	
		for i in self.other_algorithms:
			i.pages_accessed=0
		self.optimal.pages_accessed=0 # since the pages being accessed must be the same across all algorithms	

		self.current_algorithm = best
		swithing_event.set()

	def get_total_count(self):
		return self.total_count


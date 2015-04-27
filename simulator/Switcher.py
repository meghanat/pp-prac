import time
import operator
class Switcher(object):
	def __init__(self,current_algorithm,other_algorithms,optimal, lru_standalone):
		self.current_algorithm=current_algorithm
		self.other_algorithms=other_algorithms
		self.optimal=optimal
		self.total_count = 0
		self.number_windows=0
		self.performance={}
		self.lru_standalone = lru_standalone
		for i in self.other_algorithms:
			self.performance[i.name]=0

	def switch(self, switching_event):
		
		self.number_windows+=1

		switching_event.clear()
		best = min(self.other_algorithms, key=lambda x: x.get_page_fault_count())
		self.performance[best.name]+=1
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
		self.lru_standalone.pages_accessed = 0	

		self.current_algorithm = best
		switching_event.set()

	def get_total_count(self):
		return self.total_count

	def get_total_windows(self):
		return self.number_windows

	def get_best_performing_algorithm(self):
		return max(self.performance.iteritems(), key=operator.itemgetter(1))[0]


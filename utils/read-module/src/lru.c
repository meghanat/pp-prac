#include "algo.h" 

int is_in_set(algorithm* algo, int id) {
	int i = 0;
	for(i = 0; i < algo->no_threads; ++i) {
		if(algo->thread_set[i] == id) {
			return 1;
		}
	}
	return 0;
}





void call(void * arg) {
	algorithm * algo = (algorithm *) arg;
	struct page_stream_entry* entry;
	table_entry_t pte;
	
	while(*(algo->simulating)) {
		// switching event wait
		if(!is_in_set) {
			// Acquire Read Lock
			// Event wait
			entry = TAILQ_FIRST(algo->que);
			
		}
	}
}
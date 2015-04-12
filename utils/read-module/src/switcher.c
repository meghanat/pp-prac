#include "algo.h"
#include "common.h"

void do_switch(switcher* algo_switcher) {
	atomic_set(algo_switcher->current_algo->is_switching, 1);

	int i = 0;
	algorithm* best = NULL;
	algorithm** others = algo_switcher->other_algos;
	int min = 0;

	// Make sure all the algorithms have finished 
	// Any outstanding fill_frame, replace_frame or update_frame operations
	for (i = 0; i < NO_PR_THREADS; ++i)
	{
		while(atomic_read(&(others[i]->frame_operation))) {
			printk("Waiting");
		}
	}

	printk(KERN_INFO "Switch begin\n");

	// Find the algorithm with the lowest page fault count
	min = others[0]->page_fault_count;
	best = others[0];
	for (i = 1; i < NO_PR_THREADS; ++i) {
		if(others[i]->page_fault_count < min){
			min = others[i]->page_fault_count;
			best = others[i];
		}
	}

	algo_switcher->total_count += algo_switcher->current_algo->page_fault_count;
	
	// Reset page fault counts, pages accessed
	// Set other algorithms' page tables and memory to that of current
	for (i = 0; i < NO_PR_THREADS; ++i) {
		printk(KERN_INFO "%s: %d\n", others[i]->name, others[i]->page_fault_count);
		others[i]->page_fault_count = 0;
		others[i]->pages_accessed = 0;


		set_page_tables(others[i], algo_switcher->current_algo);
		set_memory(others[i], algo_switcher->current_algo);
	}
	
	printk(KERN_INFO "Best: %s\n", best->name);
	printk(KERN_INFO "Switch End\n");
	printk(KERN_INFO "Switched Algo Total: %d\n", algo_switcher->total_count);

	// Switch to the algorithm with the lowest page fault count
	algo_switcher->current_algo = best;

	atomic_set(algo_switcher->current_algo->is_switching, 0);

}
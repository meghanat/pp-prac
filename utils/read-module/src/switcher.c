#include "algo.h"

void do_switch(switcher* algo_switcher) {

	atomic_set(algo_switcher->current_algo->is_switching, 1);

	printk(KERN_INFO "switcher\n");

	atomic_set(algo_switcher->current_algo->is_switching, 0);

}
#include <linux/time.h>

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

void add_to_page_table(algorithm* algo, struct page_stream_entry* entry) {
	table_entry_t* pte;
	pte = (table_entry_t*)kmalloc(sizeof(table_entry_t), GFP_ATOMIC);
    memset(pte, 0, sizeof(table_entry_t));
    pte->key.pid = entry->pid;
    pte->key.virtual_page_no = entry->virt_page_no;
    HASH_ADD(hh, algo->page_tables, key, sizeof(table_key_t), pte);
}

table_entry_t* find_in_page_table(algorithm* algo, struct page_stream_entry* entry) {
	table_entry_t local;
	table_entry_t* result;
	memset(&local, 0, sizeof(table_entry_t));
    local.key.pid = entry->pid;
    local.key.virtual_page_no = entry->virt_page_no;
    HASH_FIND(hh, algo->page_tables, &local.key, sizeof(table_key_t), result);
    return result;
}

void update_frame_in_memory(algorithm* algo, int frame_no) {
	struct timespec cur_time;
	cur_time = current_kernel_time();
	algo->memory[frame_no].param.time_stamp = cur_time.tv_usec; // nanoseconds
}

void fill_frame(algorithm* algo, struct page_stream_entry* stream_entry, long frame_no) {
	table_entry_t* entry = kmalloc(sizeof(table_entry_t), GFP_ATOMIC);
	table_entry_t* found;

	memset(entry, 0, sizeof(table_entry_t));
	entry->key.pid = stream_entry->pid;
	entry->key.virtual_page_no = stream_entry->virt_page_no;
	entry->frame_no = frame_no;
	entry->present_bit = 1;

	HASH_FIND(hh, algo->page_tables, &(entry->key), sizeof(table_key_t), found);

	if(found) {
		// HASH_UPDATE
	}
	else {
		// HASH_ADD
	}


}


void call(void * arg) {
	algorithm * algo = (algorithm *) arg;
	struct page_stream_entry* entry;
	table_entry_t* pte;
	
	while(*(algo->simulating)) {
		// switching event wait
		if(!is_in_set) {
			// Acquire Read Lock
			// Event wait
			entry = TAILQ_FIRST(algo->que);

			if((pte = is_in_page_table(algo, entry))) {
				if(pte->present_bit){
					update_frame_in_memory(algo, pte->frame_no);
				}
			}
			else {
				// free frame availabe

				// replace
			}

			

		}
	}
}
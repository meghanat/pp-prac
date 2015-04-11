#ifndef __ALGO__H
#define __ALGO__H

#include "page_num_structure.h"
#include "uthash.h"

#undef uthash_malloc
#undef uthash_free
#define uthash_malloc(sz) kmalloc(sz, GFP_ATOMIC)
#define uthash_free(ptr,sz) kfree(ptr)

#define WINDOW 100
#define NO_FRAMES 3
#define NO_PR_THREADS 1

typedef struct {
    long pid;
    long virtual_page_no;
} table_key_t;

typedef struct {
    table_key_t key;
    long frame_no;
    long present_bit;
    UT_hash_handle hh;
} table_entry_t;

typedef struct {
	long virtual_page_no;
	long pid;
	union {
		long freq;
		long time_stamp;
	 	long used;
	} param;  
} memory_cell;


struct algorithm_struct{
	memory_cell * memory;
	table_entry_t * page_tables;
	struct page_stream_entry_q * que;
	// Add sem* for event
	// Add sem* for switching
	// Add read lock for reading
	int page_fault_count;
	int * thread_set;
	int pages_accessed;
	int switching_window;
	volatile int *simulating;
	int id;
	int no_threads;
	void (*update_frame)(struct algorithm_struct* algo, int frame_no);
	void (*replace_frame)(struct algorithm_struct* algo, struct  page_stream_entry* entry);
	void (*fill_frame)(struct algorithm_struct* algo, struct page_stream_entry* stream_entry, long frame_no);

};

typedef struct algorithm_struct algorithm;

int call_algo(void * arg);
int print_msg(void* message);
#endif


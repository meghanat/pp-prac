#ifndef __ALGO__H
#define __ALGO__H

#include "page_num_structure.h"
#include "uthash.h"

#undef uthash_malloc
#undef uthash_free
#define uthash_malloc(sz) kmalloc(sz, GFP_ATOMIC)
#define uthash_free(ptr,sz) kfree(ptr)

#define WINDOW 5
#define NO_FRAMES 3
#define NO_PR_THREADS 4

#include <linux/completion.h>
#include <linux/semaphore.h>

typedef struct {
    long pid;
    long virtual_page_no;
} table_key_t;

typedef struct {
	struct page_stream_entry_q* que;
	struct completion* completion;
	atomic_t* read_event;
} read_args;

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
	int use_bit;  
} memory_cell;

struct algorithm_struct;

typedef struct {
	int total_count;
	struct algorithm_struct* current_algo;
	struct algorithm_struct* other_algos[NO_PR_THREADS];
} switcher;

struct algorithm_struct{
	char* name;
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
	struct semaphore* set_sem;
	struct semaphore* tailq_sem;
	struct completion* completion;
	int next_frame_pointer; // This is only relevant to the clock algorithm
	switcher* algo_switcher;

	atomic_t* is_switching;
	atomic_t* read_event;
	atomic_t frame_operation;
};

typedef struct algorithm_struct algorithm;

int call_algo(void * arg);
int print_msg(void* message);
#endif


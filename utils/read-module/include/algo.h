#ifndef __ALGO__H
#define __ALGO__H

#include "page_num_structure.h"
#include "uthash.h"

#undef uthash_malloc
#undef uthash_free
#define uthash_malloc(sz) kmalloc(sz, GFP_ATOMIC)
#define uthash_free(ptr,sz) kfree(ptr)

typedef struct {
    int pid;
    int virtual_page_no;
} table_key_t;

typedef struct {
    table_key_t key;
    int frame_no;
    int present_bit;
    UT_hash_handle hh;
} table_entry_t;

typedef struct {
	long virtual_page_no;
	long pid;
	union {
		int freq;
		int time_stamp;
	 	int used;
	} param;  
} memory_cell;


typedef struct {
	memory_cell * memory;
	table_entry_t * page_tables;
	struct page_stream_entry_q * que;
} algorithm;	
#endif


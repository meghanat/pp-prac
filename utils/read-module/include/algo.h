#ifndef __ALGO__H
#define __ALGO__H

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
#endif

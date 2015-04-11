#ifndef __COMMON_H__
#define __COMMON_H__

int call_algo(void * arg);
int is_in_set(algorithm* algo);
void add_to_set(algorithm* algo);
int is_set_full(algorithm* algo);
void clear_set(algorithm* algo);
void add_to_page_table(algorithm* algo, struct page_stream_entry* entry);
table_entry_t* find_in_page_table(algorithm* algo, struct page_stream_entry* entry);

#endif
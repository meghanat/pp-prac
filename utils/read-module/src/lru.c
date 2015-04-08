#include <linux/time.h>
#include <linux/slab.h>
#include <linux/kthread.h>
#include "algo.h"


int is_in_set(algorithm* algo) {
    int i = 0;
    // put lock
    for(i = 0; i < algo->no_threads; ++i) {
        if(algo->thread_set[i] == algo->id) {
            return 1;
        }
    }
    //unlock
    return 0;
}

void add_to_set(algorithm* algo) {
    int i = 0;
    // get lock
    for(i = 0; i < algo->no_threads; ++i) {

        if(algo->thread_set[i] == 0) {
            algo->thread_set[i] = algo->id;
            return;
        }
    }
    // unlock
}

void add_to_page_table(algorithm* algo, struct page_stream_entry* entry) {
    table_entry_t* pte;
    pte = (table_entry_t*)kmalloc(sizeof(table_entry_t), GFP_ATOMIC);
    memset(pte, 0, sizeof(table_entry_t));
    pte->key.pid = entry->pid;
    pte->key.virtual_page_no = entry->virt_page_no;
    HASH_ADD(hh, algo->page_tables, key, sizeof(table_key_t), pte);
    return;
}

table_entry_t* find_in_page_table(algorithm* algo, struct page_stream_entry* entry) {
    table_entry_t* result = NULL;
    table_entry_t local;

    memset(&local, 0, sizeof(table_entry_t));
    local.key.pid = entry->pid;
    local.key.virtual_page_no = entry->virt_page_no;
    HASH_FIND(hh, algo->page_tables, &(local.key), sizeof(table_key_t), result);
    return result;
}

void lru_update_frame_in_memory(algorithm* algo, int frame_no) {
    struct timespec cur_time;
    cur_time = current_kernel_time();
    algo->memory[frame_no].param.time_stamp = cur_time.tv_nsec; // nanoseconds
}

void lru_fill_frame(algorithm* algo, struct page_stream_entry* stream_entry, long frame_no) {
    table_entry_t* entry = kmalloc(sizeof(table_entry_t), GFP_ATOMIC);
    table_entry_t* found = NULL;
    table_entry_t* temp = NULL;

    memset(entry, 0, sizeof(table_entry_t));
    entry->key.pid = stream_entry->pid;
    entry->key.virtual_page_no = stream_entry->virt_page_no;
    entry->frame_no = frame_no;
    entry->present_bit = 1;

    HASH_FIND(hh, algo->page_tables, &(entry->key), sizeof(table_key_t), found);

    if(found) {
        HASH_UPDATE(hh, algo->page_tables, key, sizeof(table_key_t), found, entry, temp);
        kfree(entry);
    }
    else {
        HASH_ADD(hh, algo->page_tables, key, sizeof(table_key_t), entry);
    }

    // Update memory cell
    algo->update_frame(algo, frame_no);
    algo->memory[frame_no].pid = stream_entry->pid;
    algo->memory[frame_no].virtual_page_no = stream_entry->virt_page_no;
    algo->page_fault_count++;
    return;
}



void lru_replace_frame(algorithm* algo, struct  page_stream_entry* entry) {
    struct timespec cur_time;
    long min = 0;
    int i = 0;
    int frame_no = 0;
    memory_cell* replacee = NULL;
    table_entry_t* found;
    table_entry_t* search;
    table_entry_t* temp;

    cur_time = current_kernel_time();
    min = cur_time.tv_nsec;

    for(i = 0; i < NO_FRAMES; ++i) {
        if(algo->memory[i].param.time_stamp < min) {
            min = algo->memory[i].param.time_stamp;
            frame_no = i;
            replacee = &algo->memory[i];
        }
    }

    search = kmalloc(sizeof(table_entry_t), GFP_ATOMIC);
    memset(search, 0, sizeof(table_entry_t));
    search->key.pid = replacee->pid;
    search->key.virtual_page_no = replacee->virtual_page_no;
    search->frame_no = frame_no;
    search->present_bit = 0;

    HASH_FIND(hh, algo->page_tables, &(search->key), sizeof(table_key_t), found);

    if(found) {
        HASH_UPDATE(hh, algo->page_tables, key, sizeof(table_key_t), found, search, temp);
    }
    else{
        printk(KERN_DEBUG "Replacing frame that doesn't exist");
    }

    search->key.pid = entry->pid;
    search->key.virtual_page_no = entry->virt_page_no;
    search->frame_no = frame_no;
    search->present_bit = 1;

    HASH_FIND(hh, algo->page_tables, &(search->key), sizeof(table_key_t), found);
    if(found) {
        HASH_UPDATE(hh, algo->page_tables, key, sizeof(table_key_t), found, search, temp);
        kfree(search);
    }
    else {
        HASH_ADD(hh, algo->page_tables, key, sizeof(table_key_t), search);
    }

    replacee->virtual_page_no = entry->virt_page_no;
    replacee->pid = entry->pid;
    algo->update_frame(algo, frame_no);
    return;
}

int call_algo(void * arg){
    algorithm * algo = (algorithm *) arg;
    struct page_stream_entry* entry = NULL;
    table_entry_t* pte = NULL;
    int i = 0;
    int flag = 0;

    while(*(algo->simulating)) {
        
        if(!is_in_set(algo)) {
            entry = TAILQ_FIRST(algo->que);
            if(entry){
                pte = find_in_page_table(algo, entry);

                // Page already in memory
                if(pte != NULL && pte->present_bit) {
                    algo->update_frame(algo, pte->frame_no);
                }
                else {
                    // free frame availabe
                    for(i = 0; i < NO_FRAMES; ++i) {
                        if(algo->memory[i].pid == 0) {
                            algo->fill_frame(algo, entry, i);
                            flag = 1;
                            break;
                        }
                    }

                    // No free frame available
                    if(!flag) {
                        algo->replace_frame(algo, entry);
                    }
                }

                // Add thread id to set
                add_to_set(algo);

            }
        }

        *(algo->simulating) = 0;
    }
    printk(KERN_INFO "%d\n", algo->page_fault_count);
}



int callold(void * arg) {
    algorithm * algo = (algorithm *) arg;
    struct page_stream_entry* entry;
    table_entry_t* pte;
    int i = 500000;
    int flag = 0;
    
    while(i--) {
        // switching event wait
        if(!is_in_set(algo)) {//TODO FIX THIS0
            // Acquire Read Lock
            // Event wait
            entry = TAILQ_FIRST(algo->que);
            //printk(KERN_DEBUG "ENTRY %d", entry == NULL);
            printk(KERN_INFO "Hello");
            /*if((pte = find_in_page_table(algo, entry)) && (pte->present_bit)) {
                algo->update_frame(algo, pte->frame_no);
            }
            else {
                // free frame availabe
                for(i = 0; i < NO_FRAMES; ++i) {
                    if(algo->memory[i].pid == 0) {
                        algo->fill_frame(algo, entry, i);
                        flag = 1;
                        break;
                    }
                }

                // replace
                if(!flag) {
                    algo->replace_frame(algo, entry);
                }
            }*/

            *(algo->simulating) = 0;
            
        }
    }
}

int print_msg(void* message) {
    printk(KERN_DEBUG "HIIIIIIIIIIIII\n");
}

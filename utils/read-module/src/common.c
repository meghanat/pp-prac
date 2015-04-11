#include <linux/time.h>
#include <linux/slab.h>
#include <linux/kthread.h>
#include "algo.h"

int is_in_set(algorithm* algo) {
    int i = 0;
    down(algo->set_sem);
    for(i = 0; i < algo->no_threads; ++i) {
        if(algo->thread_set[i] == algo->id) {
            up(algo->set_sem);
            return 1;
        }
    }
    up(algo->set_sem);
    return 0;
}

void add_to_set(algorithm* algo) {
    int i = 0;
    down(algo->set_sem);
    for(i = 0; i < algo->no_threads; ++i) {

        if(algo->thread_set[i] == 0) {
            algo->thread_set[i] = algo->id;
            up(algo->set_sem);
            return;
        }
    }
    up(algo->set_sem);
}

int is_set_full(algorithm* algo) {
    int i = 0;
    down(algo->set_sem);
    for(i = 0; i < algo->no_threads; ++i){
        if(algo->thread_set[i] == 0) {
            up(algo->set_sem);
            return 0;
        }
    }
    up(algo->set_sem);
    return 1;
}

void clear_set(algorithm* algo) {
    int i = 0;
    down(algo->set_sem);
    for (i = 0; i < algo->no_threads; ++i) {
            algo->thread_set[i] = 0;
    }
    up(algo->set_sem);
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
    table_entry_t* result = NULL;
    table_entry_t local;

    memset(&local, 0, sizeof(table_entry_t));
    local.key.pid = entry->pid;
    local.key.virtual_page_no = entry->virt_page_no;
    HASH_FIND(hh, algo->page_tables, &(local.key), sizeof(table_key_t), result);
    return result;
}

int call_algo(void * arg){
    algorithm * algo = (algorithm *) arg;
    struct page_stream_entry* entry = NULL;
    table_entry_t* pte = NULL;
    int i = 0;
    int flag = 0;

    while(*(algo->simulating)) {
        flag = 0;
        printk(KERN_INFO "Simulating\n");
        if(!is_in_set(algo)) {
            entry = TAILQ_FIRST(algo->que);
            
            if(entry){
                printk(KERN_INFO "%ld %ld\n", entry->pid, entry->virt_page_no);
                pte = find_in_page_table(algo, entry);

                // Page already in memory
                if(pte != NULL && pte->present_bit) {
                    printk(KERN_INFO "Updating\n");
                    algo->update_frame(algo, pte->frame_no);
                }
                else {
                    // free frame availabe
                    for(i = 0; i < NO_FRAMES; ++i) {
                        if(algo->memory[i].pid == 0) {
                            printk(KERN_INFO "Filling\n");
                            algo->fill_frame(algo, entry, i);
                            flag = 1;
                            break;
                        }
                    }
                    printk(KERN_INFO "FLag: %d\n", flag);
                    // No free frame available
                    if(!flag) {
                        printk(KERN_INFO "Replacing\n");
                        algo->replace_frame(algo, entry);
                    }
                }

                // Add thread id to set
                add_to_set(algo);

                if(is_set_full(algo))
                {    
                    if(!TAILQ_EMPTY(algo->que)) {
                        TAILQ_REMOVE(algo->que, entry, tailq);
                    }
                    clear_set(algo);
                    if(TAILQ_EMPTY(algo->que)) {
                    *(algo->simulating) = 0;
                    }
                    
                }

            }
        }       
    }
    printk(KERN_INFO "%d\n", algo->page_fault_count);
    return 0;
}
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

void fill_frame(algorithm* algo, struct page_stream_entry* stream_entry, long frame_no) {
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

int call_algo(void * arg){
    algorithm * algo = (algorithm *) arg;
    struct page_stream_entry* entry = NULL;
    table_entry_t* pte = NULL;
    int i = 0;
    int flag = 0;

    while(*(algo->simulating)) {
        flag = 0;
        if(!is_in_set(algo)) {

            down(algo->tailq_sem);
            entry = TAILQ_FIRST(algo->que);
            up(algo->tailq_sem);
            
            if(entry){
                printk(KERN_INFO "%s read: %ld %ld\n", algo->name, entry->pid, entry->virt_page_no);
                pte = find_in_page_table(algo, entry);

                // Page already in memory
                if(pte != NULL && pte->present_bit) {
                    printk(KERN_INFO "%s: Updating\n", algo->name);
                    algo->update_frame(algo, pte->frame_no);
                }
                else {
                    // free frame availabe
                    for(i = 0; i < NO_FRAMES; ++i) {
                        if(algo->memory[i].pid == 0) {
                            printk(KERN_INFO "%s: Filling\n", algo->name);
                            fill_frame(algo, entry, i);
                            flag = 1;
                            break;
                        }
                    }
                    //printk(KERN_INFO "FLag: %d\n", flag);
                    // No free frame available
                    if(!flag) {
                        printk(KERN_INFO "%s: Replacing\n", algo->name);
                        algo->replace_frame(algo, entry);
                    }
                }

                // Add thread id to set
                add_to_set(algo);

                if(is_set_full(algo))
                {   
                    down(algo->tailq_sem);
                    if(!TAILQ_EMPTY(algo->que)) {
                        TAILQ_REMOVE(algo->que, entry, tailq);
                    }
                    clear_set(algo);
                    if(TAILQ_EMPTY(algo->que)) {
                    *(algo->simulating) = 0;
                    }
                    up(algo->tailq_sem);
                }

            }
        }       
    }
    printk(KERN_INFO "%s Page fault count: %d\n", algo->name, algo->page_fault_count);
    complete(algo->completion);
}
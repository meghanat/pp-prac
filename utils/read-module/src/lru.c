#include <linux/time.h>
#include <linux/slab.h>
#include <linux/kthread.h>
#include "algo.h"

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
    table_entry_t* found = NULL;
    table_entry_t* search = NULL;
    table_entry_t* temp = NULL;

    cur_time = current_kernel_time();
    min = cur_time.tv_nsec;

    for(i = 0; i < NO_FRAMES; ++i) {
        if(algo->memory[i].param.time_stamp <= min) {
            min = algo->memory[i].param.time_stamp;
            frame_no = i;
            replacee = &(algo->memory[i]);
        }
    }

    if(replacee != NULL)
    {   
        // Look for the page table entry for the frame being replaced
        // Set it's present bit to 0
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

        // Look for the page table entry for the incoming virtual page no + pid
        // Set it's present bit to 1
        // Set the frame number to the number of the frame in memory being evicted
        search->key.pid = entry->pid;
        search->key.virtual_page_no = entry->virt_page_no;
        search->frame_no = frame_no;
        search->present_bit = 1;
        HASH_FIND(hh, algo->page_tables, &(search->key), sizeof(table_key_t), found);

        // If there is a PTE, update the frame number and present bit
        // If not, add a new PTE
        if(found) {
            HASH_UPDATE(hh, algo->page_tables, key, sizeof(table_key_t), found, search, temp);
            kfree(search);
        }
        else {
            HASH_ADD(hh, algo->page_tables, key, sizeof(table_key_t), search);
        }

        // Update the memory frame also
        // Set it's virtual page number and pid
        // To that of the incoming entry
        replacee->virtual_page_no = entry->virt_page_no;
        replacee->pid = entry->pid;
        algo->update_frame(algo, frame_no);
        algo->page_fault_count++;
    }
    else
    {
        printk(KERN_INFO "ERR");

    }


}
#include <linux/time.h>
#include <linux/slab.h>
#include <linux/kthread.h>
#include "algo.h"

#define LARGE_INT 2147483647

void lfu_update_frame_in_memory(algorithm* algo, int frame_no) {
    atomic_set(&(algo->frame_operation), 1);
    algo->memory[frame_no].param.freq += 1;
    atomic_set(&(algo->frame_operation), 0);
}

void lfu_replace_frame(algorithm* algo, struct  page_stream_entry* entry) {
    atomic_set(&(algo->frame_operation), 1);
    long min = 0;
    int i = 0;
    int frame_no = 0;
    memory_cell* replacee = NULL;
    table_entry_t* found = NULL;
    table_entry_t* search = NULL;
    table_entry_t* temp = NULL;

    min = LARGE_INT;

    for(i = 0; i < NO_FRAMES; ++i) {
        if(algo->memory[i].param.freq <= min) {
            min = algo->memory[i].param.freq;
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
            printk(KERN_DEBUG "%s:Replacing frame that doesn't exist\n", algo->name);
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
    atomic_set(&(algo->frame_operation), 0);
}   
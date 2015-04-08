#include <linux/module.h>  // Needed by all modules
#include <linux/kernel.h>  // Needed for KERN_INFO
#include <linux/fs.h>      // Needed by filp
#include <asm/uaccess.h>   // Needed by segment descriptors
#include <linux/kthread.h>

#include <linux/slab.h>
#include <linux/gfp.h>

#include "algo.h"
#include "page_num_structure.h"
#include "lru.h"

void init_algo(algorithm * algo, struct page_stream_entry_q * que, int* set, volatile int* simulating,void (*update_func_ptr)(algorithm* algo, int frame_no),
    void (*replace_func_ptr)(algorithm* algo, struct  page_stream_entry* entry),
    void (*fill_func_ptr)(algorithm* algo, struct page_stream_entry* stream_entry, long frame_no)) {
    static int identifier = 1;
    algo->memory = kmalloc(sizeof(memory_cell) * NO_FRAMES, GFP_ATOMIC);
    memset(algo->memory, 0, sizeof(memory_cell) * NO_FRAMES); // PID 0 => Empty Frame
    algo->que = que;
    algo->page_fault_count = 0;
    algo->thread_set = set;
    algo->pages_accessed = 0;
    algo->switching_window = WINDOW;
    algo->simulating = simulating;
    algo->id = identifier;
    algo->no_threads = NO_PR_THREADS;
    algo->fill_frame=fill_func_ptr;
    algo->update_frame=update_func_ptr;
    algo->replace_frame=replace_func_ptr;
    algo->page_tables = NULL;

    identifier++;
}

void destroy(algorithm * algo) {
    // Free memory and page_tables
}

struct task_struct *ts = NULL;

int init_module(void)
{
    // Create variables
    struct file *f = NULL;
    char buf[128];
    int i = 0;
    long page_no = 0;
    long pid = 0;
    char cur[1];
    mm_segment_t fs;
    volatile int simulating = 1;
    
    struct page_stream_entry_q que;
    struct page_stream_entry *p = NULL;
    struct page_stream_entry *entry = NULL;

    int count = 0;
    int set[NO_PR_THREADS] = {0};
    algorithm lru;

    TAILQ_INIT(&que);

    for(i = 0;i < 128; i++)
        buf[i] = 0;
    
    printk(KERN_INFO "Module is loaded\n");
    
    f = filp_open("/home/deborah/file", O_RDONLY, 0);
    if(f == NULL)
        printk(KERN_ALERT "filp_open error.\n");
    else{
        // Get current segment descriptor
        fs = get_fs();
        // Set segment descriptor associated to kernel space
        set_fs(get_ds());
    
        i = 0;

        while(f->f_op->read(f, cur, 1, &f->f_pos) == 1)
        {   
            i = 0;
            while(cur[0] != ',')
            {
                buf[i++] = cur[0];
                f->f_op->read(f, cur, 1, &f->f_pos);
            }
            buf[i] = '\0';
            kstrtoul(buf, 16, &page_no);
            f->f_op->read(f, cur, 1, &f->f_pos);
            i = 0;
            while(cur[0] != '\n')
            {
                buf[i++] = cur[0];
                f->f_op->read(f, cur, 1, &f->f_pos);
            }
            buf[i] = '\0';
            kstrtoul(buf, 10, &pid);
        
            entry = kmalloc(sizeof(struct  page_stream_entry), GFP_ATOMIC);
            entry->pid = pid;
            entry->virt_page_no = page_no;
            TAILQ_INSERT_TAIL(&que, entry, tailq);  
            //printk(KERN_INFO "Page no: %ld\n Pid:%ld\n", page_no, pid);

        }   
        /*p = TAILQ_FIRST(&que);
        printk("Pointer:%p\nPID:%ld\nPage No:%ld\n", p, p->pid, p->virt_page_no);

        p = TAILQ_LAST(&que,page_stream_entry_q);
        printk("Pointer:%p\nPID:%ld\nPage No:%ld\n",p, p->pid, p->virt_page_no);*/
        
        TAILQ_COUNT(p, &que, tailq, count);
        printk("Count: %d\n", count);

        // Restore segment descriptor
        set_fs(fs);
    }
    filp_close(f, NULL);

    init_algo(&lru, &que, set, &simulating, &lru_update_frame_in_memory, &lru_replace_frame, &lru_fill_frame);
    
    ts = kthread_run(call_algo, &lru , "LRU");
    if(ts == NULL){
        printk(KERN_INFO "Bad");
    }

    return 0;
}

void cleanup_module(void)
{
    printk(KERN_INFO "Module is unloaded\n");
}

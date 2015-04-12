#include <asm/uaccess.h>   // Needed by segment descriptors

#include <linux/completion.h>
#include <linux/fs.h>      // Needed by filp
#include <linux/gfp.h>
#include <linux/kernel.h>  // Needed for KERN_INFO
#include <linux/kthread.h>
#include <linux/module.h>  // Needed by all modules
#include <linux/semaphore.h> // For mutual exclusion
#include <linux/slab.h>

#include "algo.h"
#include "clock.h"
#include "common.h"
#include "fifo.h"
#include "lfu.h"
#include "lru.h"
#include "page_num_structure.h"

int init_algo(char* name, algorithm * algo, struct page_stream_entry_q * que, int* set, volatile int* simulating,
    void (*update_func_ptr)(algorithm* algo, int frame_no),
    void (*replace_func_ptr)(algorithm* algo, struct  page_stream_entry* entry),
    struct semaphore* set_sem, struct semaphore* tailq_sem, struct completion* completion, switcher* algo_switcher, 
    atomic_t* is_switching) {

    static int identifier = 1;
    algo->memory = kmalloc(sizeof(memory_cell) * NO_FRAMES, GFP_ATOMIC);
    if(algo->memory == NULL) {
        printk(KERN_ALERT "kmalloc Failed\n");
        return -1;
    }
    memset(algo->memory, 0, sizeof(memory_cell) * NO_FRAMES); // PID 0 => Empty Frame
    algo->name = name;
    algo->que = que;
    algo->page_fault_count = 0;
    algo->thread_set = set;
    algo->pages_accessed = 0;
    algo->switching_window = WINDOW;
    algo->simulating = simulating;
    algo->id = identifier;
    algo->no_threads = NO_PR_THREADS;
    algo->update_frame=update_func_ptr;
    algo->replace_frame=replace_func_ptr;
    algo->page_tables = NULL;
    algo->set_sem = set_sem;
    algo->tailq_sem = tailq_sem;
    algo->completion = completion;
    algo->next_frame_pointer = 0;
    algo->algo_switcher = algo_switcher;
    algo->is_switching = is_switching;
    atomic_set(&(algo->frame_operation), 0);

    identifier++;
    return 0;
}

void destroy(algorithm * algo) {
    table_entry_t* p = NULL;
    table_entry_t* tmp = NULL;

    // Free algorithm memory
    kfree(algo->memory);

    // Free algorithm page tables
    HASH_ITER(hh, algo->page_tables, p, tmp) {
      HASH_DEL(algo->page_tables, p);
      kfree(p);
    }

}

void init_switcher(switcher* algo_switcher, algorithm* lru, algorithm* fifo, algorithm* lfu, algorithm* clock) {
    algo_switcher->total_count = 0;
    algo_switcher->current_algo = lru;
    algo_switcher->other_algos[0] = lru;
    algo_switcher->other_algos[1] = fifo;
    algo_switcher->other_algos[2] = lfu;
    algo_switcher->other_algos[3] = clock;
}

int init_module(void)
{
    // Create variables
    struct task_struct *ts = NULL;
    struct file *f = NULL;

    char buf[128];
    int i = 0;
    long page_no = 0;
    long pid = 0;
    char cur[1];
    mm_segment_t fs;
    int count = 0;
    int result = 0;
    
    struct page_stream_entry_q que;
    struct page_stream_entry *p = NULL;
    struct page_stream_entry *entry = NULL;

    struct semaphore set_sem;
    struct semaphore tailq_sem;

    struct completion lru_completion;
    struct completion fifo_completion;
    struct completion lfu_completion;
    struct completion clock_completion;

    int set[NO_PR_THREADS] = {0};
    volatile int simulating = 1;
    atomic_t is_switching = ATOMIC_INIT(0);

    algorithm lru;
    algorithm fifo;
    algorithm lfu;
    algorithm clock;

    switcher algo_switcher;

    // Initialize semaphores
    sema_init(&set_sem, 1);
    sema_init(&tailq_sem, 1);

    // Initialize completion
    init_completion(&lru_completion);
    init_completion(&fifo_completion);
    init_completion(&lfu_completion);
    init_completion(&clock_completion);

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

    result = init_algo("LRU", &lru, &que, set, &simulating, &lru_update_frame_in_memory, &lru_replace_frame,  
                       &set_sem, &tailq_sem, &lru_completion, &algo_switcher, &is_switching);
    if(result != 0) {
        return -1;
    }

    result = init_algo("FIFO", &fifo, &que, set, &simulating, &fifo_update_frame_in_memory, &fifo_replace_frame, 
                       &set_sem, &tailq_sem, &fifo_completion, &algo_switcher, &is_switching);
    if(result != 0) {
        return -1;
    }

    result = init_algo("LFU", &lfu, &que, set, &simulating, &lfu_update_frame_in_memory, &lfu_replace_frame, 
                       &set_sem, &tailq_sem, &lfu_completion, &algo_switcher, &is_switching);
    if(result != 0) {
        return -1;
    }

    result = init_algo("CLOCK", &clock, &que, set, &simulating, &clock_update_frame_in_memory, &clock_replace_frame, 
                       &set_sem, &tailq_sem, &clock_completion, &algo_switcher, &is_switching);
    if(result != 0) {
        return -1;
    }
    
    init_switcher(&algo_switcher, &lru, &fifo, &lfu, &clock);

    ts = kthread_run(call_algo, &lru , "LRU");
    if(ts == NULL){
        printk(KERN_INFO "Bad");
    }
    
    ts = kthread_run(call_algo, &fifo , "FIFO");
    if(ts == NULL){
        printk(KERN_INFO "Bad");
    }

    ts = kthread_run(call_algo, &lfu , "LFU");
    if(ts == NULL){
        printk(KERN_INFO "Bad");
    }

    ts = kthread_run(call_algo, &clock , "CLOCK");
    if(ts == NULL){
        printk(KERN_INFO "Bad");
    }

    wait_for_completion(&lru_completion);
    wait_for_completion(&fifo_completion);
    wait_for_completion(&lfu_completion);
    wait_for_completion(&clock_completion);
    
    destroy(&lru);
    destroy(&fifo);
    destroy(&lfu);
    destroy(&clock);
    return 0;
}

void cleanup_module(void)
{
    printk(KERN_INFO "Module is unloaded\n");
}

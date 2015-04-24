#include <asm/uaccess.h>   // Needed by segment descriptors

#include <linux/completion.h>
#include <linux/fs.h>      // Needed by filp
#include <linux/gfp.h>
#include <linux/kernel.h>  // Needed for KERN_INFO
#include <linux/module.h>  // Needed by all modules
#include <linux/slab.h>


#include "algo.h"
#include "page_num_structure.h"

int read_entries_from_file(void * args) {
    read_args* arg = (read_args* ) args;
    struct completion* read_completion = arg->completion;
    struct page_stream_entry_q* que = arg->que;

    struct file *f = NULL;
    char buf[128];
    int i = 0;
    long page_no = 0;
    long pid = 0;
    char cur[1];
    mm_segment_t fs;
    int count = 0;

    struct page_stream_entry *entry = NULL;
    struct page_stream_entry *p = NULL;

    for(i = 0;i < 128; i++)
        buf[i] = 0;

    f = filp_open("/home/deborah/file1", O_RDONLY, 0);

    if(f == NULL)
        printk(KERN_ALERT "filp_open error.\n");
    else{

        TAILQ_COUNT(p, que, tailq, count);
        while(count > 10) {
            printk(KERN_INFO "Waiting in Read");
            TAILQ_COUNT(p, que, tailq, count);
        }

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
            TAILQ_INSERT_TAIL(que, entry, tailq);
            atomic_set(arg->read_event, 1);
            //printk(KERN_INFO "Page no: %ld\n Pid:%ld\n", page_no, pid);
        }   
        /*p = TAILQ_FIRST(&que);
        printk("Pointer:%p\nPID:%ld\nPage No:%ld\n", p, p->pid, p->virt_page_no);

        p = TAILQ_LAST(&que,page_stream_entry_q);
        printk("Pointer:%p\nPID:%ld\nPage No:%ld\n",p, p->pid, p->virt_page_no);*/
        
        TAILQ_COUNT(p, que, tailq, count);
        printk("Count: %d\n", count);

        // Restore segment descriptor
        set_fs(fs);
    }
    filp_close(f, NULL);
    complete(read_completion);
}

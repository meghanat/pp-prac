#include <linux/module.h>  // Needed by all modules
#include <linux/kernel.h>  // Needed for KERN_INFO
#include <linux/fs.h>      // Needed by filp
#include <asm/uaccess.h>   // Needed by segment descriptors
#include <linux/slab.h>
#include <linux/gfp.h>

#define WINDOW 100
#define NO_FRAMES 100

#include "algo.h"
#include "page_num_structure.h"

void init_algo(algorithm * algo, struct page_stream_entry_q * que, int* set) {
    algo->memory = kmalloc(sizeof(memory_cell) * NO_FRAMES, GFP_ATOMIC);
    memset(algo->memory, 0, sizeof(memory_cell) * NO_FRAMES); // PID 0 => Empty Frame
    algo->que = que;
    algo->page_fault_count = 0;
    algo->thread_set = set;
    algo->pages_accessed = 0;
    algo->switching_window = WINDOW;
}

void destroy(algorithm * algo) {
    // Free memory and page_tables
}

int init_module(void)
{
    // Create variables
    struct file *f;
    char buf[128];
    int i =0;
    long page_no = 0;
    long pid = 0;
    char cur[1];
    mm_segment_t fs;

    struct page_stream_entry_q que;
    struct page_stream_entry* p;
    struct page_stream_entry *entry;
    
    algorithm lru;
    int set[1] = {0};

    TAILQ_INIT(&que);

    // Init the buffer with 0
    for(i=0;i<128;i++)
        buf[i] = 0;
    // To see in /var/log/messages that the module is operating
    printk(KERN_INFO "My module is loaded\n");
    // I am using Fedora and for the test I have chosen following file
    // Obviously it is much smaller than the 128 bytes, but hell with it =)
    f = filp_open("/home/deborah/file", O_RDONLY, 0);
    if(f == NULL)
        printk(KERN_ALERT "filp_open error!!.\n");
    else{
        // Get current segment descriptor
        fs = get_fs();
        // Set segment descriptor associated to kernel space
        set_fs(get_ds());
	
	i = 0;
        // Read the file
	printk(" Before Read \n");
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
                kstrtoul(buf, 16, &pid);
	
		entry = kmalloc(sizeof(struct  page_stream_entry), GFP_ATOMIC);
		entry->pid = pid;
		entry->virt_page_no = page_no;
		TAILQ_INSERT_TAIL(&que, entry, tailq);	
	 	//printk(KERN_INFO "Page no: %ld\n Pid:%ld\n", page_no, pid);

	}	
	p = TAILQ_FIRST(&que);
	printk("Pointer:%p\nPID:%ld\nPage No:%ld\n", p, p->pid, p->virt_page_no);

	p = TAILQ_LAST(&que,page_stream_entry_q);
	printk("Pointer:%p\nPID:%ld\nPage No:%ld\n",p, p->pid, p->virt_page_no);

  

        // Restore segment descriptor
        set_fs(fs);
        // See what we read from file
        printk(KERN_INFO "buf:%s\n",buf);
    }
    filp_close(f,NULL);

    init_algo(&lru, &que, set);

    return 0;
}

void cleanup_module(void)
{
    printk(KERN_INFO "My module is unloaded\n");
}

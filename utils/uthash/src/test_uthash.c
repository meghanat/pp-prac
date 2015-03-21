#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
# include <linux/sched.h>
# include <linux/tty.h>
# include <linux/io.h>
# include <asm/pgtable.h>
# include <asm/highmem.h>

# include "uthash.h"


MODULE_LICENSE("GPL");
MODULE_AUTHOR("Deborah-Digges");
MODULE_DESCRIPTION("A hello world module");

typedef struct {
  int pid;
  int virtual_page_no;
} table_key_t;

typedef struct {
    table_key_t key;
    int frame_no;
    int present_bit;
    UT_hash_handle hh;
} table_entry_t;

void test_uthash()
{
    printk(KERN_DEBUG "Testing uthash\n");
}

static int __init uthash_init(void)
{
    printk(KERN_DEBUG "Init module\n");
    test_uthash();
    return 0;
}

static void __exit uthash_cleanup(void)
{
	printk(KERN_DEBUG "Cleaning up module\n");
}

module_init(uthash_init);
module_exit(uthash_cleanup);

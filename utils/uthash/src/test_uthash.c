#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/tty.h>
#include <linux/io.h>
#include <asm/pgtable.h>
#include <asm/highmem.h>

#include <linux/slab.h>
#include <linux/gfp.h>
#include "uthash.h"

#undef uthash_malloc
#undef uthash_free
#define uthash_malloc(sz) kmalloc(sz, GFP_ATOMIC)
#define uthash_free(ptr,sz) kfree(ptr)

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

int test_uthash(void)
{
    table_entry_t l, *p, *q, *r, *tmp, *records = NULL;
    printk(KERN_DEBUG "Testing uthash\n");

    q = (table_entry_t*)kmalloc( sizeof(table_entry_t), GFP_ATOMIC );
    memset(q, 0, sizeof(table_entry_t));
    q->key.pid = 1;
    q->key.virtual_page_no = 100;
    q->frame_no = 10000;
    q->present_bit = 0;

    r = (table_entry_t*)kmalloc( sizeof(table_entry_t), GFP_ATOMIC );
    memset(r, 0, sizeof(table_entry_t));
    r->key.pid = 1;
    r->key.virtual_page_no = 100;
    HASH_ADD(hh, records, key, sizeof(table_key_t), r);

    memset(&l, 0, sizeof(table_entry_t));
    l.key.pid = 1;
    l.key.virtual_page_no = 100;
    HASH_FIND(hh, records, &l.key, sizeof(table_key_t), p);

    if (p) printk(KERN_DEBUG "found %d %d\n", p->key.pid, p->key.virtual_page_no);


    HASH_UPDATE(hh, records, key, sizeof(table_key_t), p, q, tmp);
    printk("P: %d %d\n", p->key.pid, p->key.virtual_page_no);
    if(q){
	printk("Q: %d %d\n", q->key.pid, q->key.virtual_page_no);
    }

    memset(&l, 0, sizeof(table_entry_t));
    l.key.pid = 1;
    l.key.virtual_page_no = 100;
    HASH_FIND(hh, records, &l.key, sizeof(table_key_t), p);


    //kfree(r);	
    //HASH_FIND(hh, records, &(q->key), sizeof(table_key_t), p);
    if (p) printk(KERN_DEBUG "found %d %d\n", p->frame_no, p->present_bit);
    

    HASH_ITER(hh, records, p, tmp) {
      printk(KERN_DEBUG "-----------\n");
      printk(KERN_DEBUG "%d %d\n", p->key.pid, p->key.virtual_page_no);
      HASH_DEL(records, p);
      kfree(p);
    }
    return 0;
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

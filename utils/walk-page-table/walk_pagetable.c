#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
# include <linux/sched.h>
# include <linux/tty.h>
# include <linux/io.h>
# include <asm/pgtable.h>
# include <asm/highmem.h>


MODULE_LICENSE("GPL");
MODULE_AUTHOR("Deborah-Digges");
MODULE_DESCRIPTION("A hello world module");

struct task_struct * current_process;

void  walk_page_table(unsigned long addr, pid_t pid)
{
    
    struct mm_struct * mm;
    struct page * page = NULL;
    pgd_t *pgd = NULL;
    pte_t *ptep, pte;
    pud_t *pud = NULL;
    pmd_t *pmd = NULL;
    current_process = pid_task(find_vpid(pid), PIDTYPE_PID); // Retrieve task structure
    mm = current_process->mm;

   if(!mm){
        printk(KERN_DEBUG "No mm structure for process %ld", (unsigned long)current_process->pid);
        return;
   }

   pgd = pgd_offset(mm, addr);
   if (pgd_none(*pgd) || pgd_bad(*pgd)){
        printk(KERN_NOTICE "No pgd");
        return;
   }

    pud = pud_offset(pgd, addr);
    if (pud_none(*pud) || pud_bad(*pud)){
        printk(KERN_NOTICE "No pud");
        return;
    }

    pmd = pmd_offset(pud, addr);
    if (pmd_none(*pmd) || pmd_bad(*pmd)){
        printk(KERN_NOTICE "InValid pmd");
	return;
    }

    ptep = pte_offset_map(pmd, addr);
    if (!ptep){
        printk(KERN_NOTICE "No PTE");        
	return;
    }
    pte = *ptep;

    page = pte_page(pte);
    if (page)
        printk(KERN_INFO "page frame struct is @ %p\n", page);
    else
        printk(KERN_INFO "Virtual page not mapped\n");
    
}

static int __init hello_init(void)
{
    walk_page_table(0xbfb773fc, 2537);

	return 0;
}

static void __exit hello_cleanup(void)
{
	printk(KERN_DEBUG "Cleaning up module\n");
}

module_init(hello_init);
module_exit(hello_cleanup);

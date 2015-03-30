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

asmlinkage void  sys_walk_pagetable(unsigned long addr, pid_t pid)
{ 
    struct page * page = NULL;
    pgd_t *pgd;
    pte_t *ptep, pte;
    pud_t *pud;
    pmd_t *pmd;
    current_process = pid_task(find_vpid(pid), PIDTYPE_PID); // Retrieve task structure
    struct mm_struct * mm = current_process->mm;


   if(!mm){
        printk("No mm structure for process %ld", (long int)current_process->pid);
	return;
   }

   pgd = pgd_offset(mm, addr);
   if (pgd_none(*pgd) || pgd_bad(*pgd)){
        printk("No pgd");
 	return;
   }

    pud = pud_offset(pgd, addr);
    if (pud_none(*pud) || pud_bad(*pud)){
        printk("No pud");
        return;
    }

    pmd = pmd_offset(pud, addr);
    if (pmd_none(*pmd) || pmd_bad(*pmd)){
        printk("No pmd");
	return;
    }

    ptep = pte_offset_map(pmd, addr);
    if (!ptep){
        printk("No PTE");        
	return;
    }
    pte = *ptep;

    page = pte_page(pte);
    if (page)
        printk("page frame struct is @ %p\n", page);
    else
        printk("Virtual page not mapped\n");
    
}



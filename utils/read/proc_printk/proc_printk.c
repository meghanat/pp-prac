#include <linux/module.h>
#include <linux/proc_fs.h>
MODULE_DESCRIPTION("printk example module");
MODULE_AUTHOR("Dietmar.Schindler@manroland-web.com");
MODULE_LICENSE("GPL");

static
ssize_t write(struct file *file, const char *buf, size_t count, loff_t *pos)
{
    static int num=0;
    printk("%.*s", count, buf);
    num++;
    printk(KERN_INFO "num :%d\n",num);
    return count;
}

static struct file_operations file_ops;

int init_module(void)
{
    printk("init printk example module\n");
    struct proc_dir_entry *entry = proc_create("printk", 0, NULL, &file_ops);
    if (!entry) return -ENOENT;

    file_ops.owner = THIS_MODULE,
    file_ops.write = write;
    return 0;
}

void cleanup_module(void)
{
    remove_proc_entry("printk", NULL);
    printk("exit printk example module\n");
}
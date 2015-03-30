#include <stdio.h>
#include <linux/kernel.h>
#include <unistd.h>
#include <sys/types.h>
#include <errno.h>

int a = 100;
int walk_pagetable(int * address, pid_t pid)
{
	return syscall(359, address, pid);
}

int main()
{
		
	printf("%d\n",  getpid());
	walk_pagetable(&a, getpid());

		
	return 0;
}


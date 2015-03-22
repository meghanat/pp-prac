#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

int main(int argc, char ** argv) {
    int i = 0; 
//64 child processes
	fork();
	fork();
	fork();
	fork();
	fork();
	fork();
    int fd = open(argv[1], O_RDWR);
    struct stat stats;
    int rounded_down;
    int page_size;

    fstat(fd, &stats);
    posix_fadvise(fd, 0, stats.st_size, POSIX_FADV_DONTNEED);

    page_size = getpagesize();
    rounded_down = stats.st_size/page_size * page_size;

    char * map = (char *) mmap(NULL,  rounded_down, PROT_READ|PROT_WRITE, MAP_SHARED|MAP_NORESERVE, fd, 0);
    if (map == MAP_FAILED) {
        perror("Failed to mmap");
        return 1;
    }

    // Access every 100th page to generate major page faults  
    for (i = 0;i<5000; i++) {
	int index=rand()%rounded_down;
	//printf("%d\n",index);
        map[index] = 12;
    }

    munmap(map, rounded_down);

    return 0;
}

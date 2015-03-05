#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

int main(int argc, char ** argv) {
  int i = 0; 
  int fd = open(argv[1], O_RDWR);
  struct stat stats;
  fstat(fd, &stats);
  posix_fadvise(fd, 0, stats.st_size, POSIX_FADV_DONTNEED);

  char * map = (char *) mmap(NULL, stats.st_size/4096 * 4096 , PROT_READ|PROT_WRITE, MAP_SHARED|MAP_NORESERVE, fd, 0);
  if (map == MAP_FAILED) {
    perror("Failed to mmap");
    return 1;
  }
  
  // Access every 100th page to generate major page faults  
  for (i = 0; i < stats.st_size; i+= 4096 * 100) {
    map[i] = 12;
  }

  munmap(map, stats.st_size);

  return 0;
}

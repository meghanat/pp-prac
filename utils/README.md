Run using:

gcc majorfault.c -o majorfault

/usr/bin/time -v ./majorfault large-file-input

To limit the physical memory(RAM) a process can use:

1. Create a group : cgcreate -g memory:/myGroup
2. echo $(( 500 * 1024 * 1024 )) > /sys/fs/cgroup/memory/myGroup/memory.limit_in_bytes (limit memory to 5MB)
3. echo $(( 5000 * 1024 * 1024 )) > /sys/fs/cgroup/memory/myGroup/memory.memsw.limit_in_bytes (limit swap to 5MB)
4. Run the program pgm as: cgexec -g memory:myGroup pgm
5. To generate lackey logs for the process, with the memory limit imposed:
sudo cgexec -g memory:myGroup valgrind -q --trace-children=yes --tool=lackey --trace-mem=yes --log-file=log.txt pgm args

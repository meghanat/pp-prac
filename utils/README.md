###Run using:

```sh
gcc majorfault.c -o majorfault
/usr/bin/time -v ./majorfault large-file-input
```

###To limit the physical memory(RAM) a process can use:

1. Create a group :
```sh
cgcreate -g memory:/myGroup
```
2. Limit memory to 5MB 
```sh
echo $(( 5 * 1024 * 1024 )) > /sys/fs/cgroup/memory/myGroup/memory.limit_in_bytes 
```
3. Limit swap to 5000MB 
```sh
echo $(( 5000 * 1024 * 1024 )) > /sys/fs/cgroup/memory/myGroup/memory.memsw.limit_in_bytes 
```
4. Run the program pgm as: 
```sh
cgexec -g memory:myGroup pgm
```
5. To generate lackey logs for the process, with the memory limit imposed:
```sh
sudo cgexec -g memory:myGroup valgrind -q --trace-children=yes --tool=lackey --trace-mem=yes --log-file=log.txt pgm args
```

Note that on a modern Ubuntu distribution this example requires installing the cgroup-bin package and editing /etc/default/grub to change GRUB_CMDLINE_LINUX_DEFAULT to:

GRUB_CMDLINE_LINUX_DEFAULT="cgroup_enable=memory swapaccount=1"
and then rebooting to boot with the new kernel boot parameters.

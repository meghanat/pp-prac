obj-m := Read_File.o
EXTRA_CFLAGS:= -I/home/deborah/pp-prac-clone/utils/read-module/include # use EXTRA_CFLAGS instead of ccflags-y
Read_File-y := src/Read_File.o #relative
Read_File-y += src/lru.o
Read_File-y += src/common.o
Read_File-y += src/fifo.o
Read_File-y += src/lfu.o
Read_File-y += src/clock.o
Read_File-y += src/switcher.o
Read_File-y += src/read.o

TREE=/lib/modules/3.5.0-23-generic/build
MY_CFLAGS += -g -DDEBUG
ccflags-y += ${MY_CFLAGS}
CC += ${MY_CFLAGS}

#before it tries to build the modules target it will change to the directory named in the M variable
all:
	make -C $(TREE) M=$(PWD) modules

clean:
	make -C $(TREE)  M=$(PWD) clean
debug:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules 
	EXTRA_CFLAGS="$(MY_CFLAGS)"

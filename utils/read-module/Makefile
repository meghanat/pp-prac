obj-m := Read_File.o
EXTRA_CFLAGS:= -I/home/deborah/Github/pp-prac/utils/read-module/include # use EXTRA_CFLAGS instead of ccflags-y
Read_File-y := src/Read_File.o #relative
Read_File-y += src/lru.o
TREE=/lib/modules/3.5.0-23-generic/build

#before it tries to build the modules target it will change to the directory named in the M variable
all:
	make -C $(TREE) M=$(PWD) modules

clean:
	make -C $(TREE)  M=$(PWD) clean

obj-m := Read_File.o
EXTRA_CFLAGS:= -I/home/deborah/Documents/Projects/Final-Year-Project/modules/read_final/include # use EXTRA_CFLAGS instead of ccflags-y
Read_File-y := src/Read_File.o #relative


#before it tries to build the modules target it will change to the directory named in the M variable
all:
	make -C $(TREE) M=$(PWD) modules

clean:
	make -C $(TREE)  M=$(PWD) clean

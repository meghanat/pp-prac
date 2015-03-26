obj-m := test_uthash.o
EXTRA_CFLAGS:= -I/home/deborah/Github/pp-prac/utils/uthash/include # use EXTRA_CFLAGS instead of ccflags-y
test_uthash-y := src/test_uthash.o #relative
TREE=/lib/modules/3.5.0-23-generic/build/

#before it tries to build the modules target it will change to the directory named in the M variable
all:
	make -C $(TREE) M=$(PWD) modules

clean:
	make -C $(TREE)  M=$(PWD) clean

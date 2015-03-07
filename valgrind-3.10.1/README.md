##To print PID with --trace-mem

to print Virtual Address, PID, use following command
```sh
valgrind --trace-children=yes --tool=lackey --trace-mem=yes <program-name>
```

###Build and Install

Make sure you don't have valgrind already installed, before proceeding with the installation :

  1. Clone valgrind, cd into the source directory.

  2. Run ./autogen.sh to setup the environment (you need the standard
     autoconf tools to do so).

  3. Run ./configure

  4. Run "sudo make".

  5. Run "sudo make install"

  6. See if it works.  Try "valgrind ls -l".  Either this works, or it
     bombs out with some complaint.  In that case, please let us know
     (see www.valgrind.org).

###Redirect lackey's output to a file
```sh
valgrind a.out > log.txt 2>&1
```

###Segregate lackey's output from program's output
```sh
valgrind -q --trace-children=yes --tool=lackey --trace-mem=yes --log-file=log.txt ./a.out
```

 


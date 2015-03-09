###Build and Install

Make sure you don't have valgrind already installed, before proceeding with the installation :

  1. Download valgrind <a href="http://valgrind.org/downloads/valgrind-3.10.1.tar.bz2">source</a>.
  
  2.  cd into the source directory.
  
  3. Clone pp-prac. Replace valgrind/lackey in the valgrind source code with pp-prac/valgrind-3.10.1/lackey.

  4. Run ./autogen.sh to setup the environment (you need the standard
     autoconf tools to do so).

  5. Run ./configure

  6. Run "sudo make".

  7. Run "sudo make install"

  8. See if it works.  Try "valgrind ls -l".  Either this works, or it
     bombs out with some complaint.  In that case, please let us know
     (see www.valgrind.org).

##To print PID with --trace-mem

to print Virtual Address, PID, use following command
```sh
valgrind --trace-children=yes --tool=lackey --trace-mem=yes <program-name>
```

###Redirect lackey's output to a file
```sh
valgrind a.out > log.txt 2>&1
```

###Segregate lackey's output from program's output
```sh
valgrind -q --trace-children=yes --tool=lackey --trace-mem=yes --log-file=log.txt ./a.out
```

### OSX Specific instructions

Follow the instructions <a href="http://superuser.com/questions/630674/valgrind-installation-errors-on-osx-10-8">here</a>


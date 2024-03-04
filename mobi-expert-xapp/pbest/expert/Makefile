# Makefile for SecSM-eXpert

OS_ARCH	      = $(shell ../get_os_syms.csh OS_ARCH)
OS_SYSN       = $(shell ../get_os_syms.csh OS_SYSN)
#OS_NAME       = $(shell ../get_os_syms.csh OS_NAME_FULL)
#OS_DIR        = $(OS_NAME)
OS_DIR        = $(OS_SYSN)-$(OS_ARCH)

# Directory structure macros -- should only need to change # the value of the ROOT macro
IDES            = ../libpb/
IDESLIB         = ../libpb/$(OS_DIR)
# Where the PBEST translator is
PBCC            = ../pbcc/$(OS_DIR)/pbcc
# Enable "justifications".  Show version number.
PBCCFLAGS       = -j -v
# The garbage collector and runtime libraries
PBCCLIBS        = -L$(IDESLIB) -lpb # -lgc
# The window libraries
XLIBS           = -L$(IDESLIB) -liui -lXaw -lXmu -lXt -lX11
# C compiler stuff -- need the system v compatibility
# version
CC              = gcc
# Include symbols, search the ides and
# global include directories
CFLAGS          = -g -I$(IDES) -O0
############################################################
# Everything above here can be used as a skeleton Makefile.
# The only thing that should need to change is ROOT, which
# should be set when the system is installed.
#
# Things below should be used more as an example.  The main
# thing is to make sure each language processor knows how to
# find the libraries it is looking for.
############################################################

SRC             = rules.pbest
OBJ             = rules.o
CF				= rules.c
#XOBJ            = tstx.o
#
# NOTE:  You must use TABS (^I) between the target and the
#        dependencies, and to start off the command lines
#        below each target-dependency specification.
#        Failure to do this will cause the make program to
#        refuse to do what you want and to produce a series
#        of uninformative error messages.
# this space made by tabs
# ||||||
# VVVVVV
all:	rules.c main.o main

rules:	$(OBJ)
		$(CC) -o $@ $(OBJ) $(PBCCLIBS)

#tstx:	$(XOBJ)
#		$(CC) -o $@ $(XOBJ) $(PBCCLIBS) $(XLIBS)

rules.o:	$(CF)
			$(CC) $(CFLAGS) -c $(CF)

rules.c:	$(SRC)
			$(PBCC) $(PBCCFLAGS) -e -o $@ $(SRC)

main.o:		main.c
			$(CC) $(CFLAGS) -c main.c

main:		main.o
			$(CC) -o $@ main.o $(PBCCLIBS)

#tstx.o:	tstx.c
#		$(CC) $(CFLAGS) -c tstx.c
#
#tstx.c:	tst.pbcc
#		$(PBCC) $(PBCCFLAGS) -x -o $@ tst.pbcc

clean:
		rm -f *.o $(CF) main

end:

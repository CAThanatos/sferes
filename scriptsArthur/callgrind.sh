#!/bin/bash

Usage()
{
	echo "usage: $0 -e executable [-v][-h]

Run callgrind for the specified executable.

OPTIONS:
	-e	The executable to run callgind on
	-v	Verbose mode for valgrind
	-h	Show this help"
}

executable=
verbose=

while getopts "vhe:" OPTION
do
	case $OPTION in
		v)
			verbose=1
			;;
		e)
			executable=$OPTARG
			;;
		h)
			Usage
			exit
			;;
		?)
			Usage
			exit
			;;
	esac
done

if [[ ! -z $executable ]]
then
	if [[ -z $verbose ]]
	then
		valgrind --tool=callgrind --dump-every-bb=10000000 $executable
	else
		valgrind --tool=callgrind -v --dump-every-bb=10000000 $executable
	fi
else
	Usage
	exit
fi

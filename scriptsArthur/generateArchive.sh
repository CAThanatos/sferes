#!/bin/bash

Usage()
{
	echo "usage: $0 -e exp [-n name] [-o outputDirectory]

Generates an archive of the all the files necessary to run a determined experiment.

OPTIONS:
	-h	Shows this message
	-e	The experiment to archive
	-n	The name of the archive
	-o	The ouput directory where to move the archive file"
}

exp=
name=
output=
while getopts "he:n:o:" OPTION
do
	case $OPTION in
		h)
			Usage
			exit 1
			;;
		e)
			exp=$OPTARG
			;;
		n)
			name=$OPTARG
			;;
		o)
			output=$OPTARG
			;;
		?)
			Usage
			exit
			;;
	esac
done

if [[ -z $exp ]]
then
	Usage
	exit 1
fi

if [[ -z $name ]]
then
	name=$exp`eval date +_%Y-%m-%d`
fi
name=$name".tar"

tar -cvf $name /home/abernard/sferes2-0.99/sferes /home/abernard/sferes2-0.99/modules /home/abernard/sferes2-0.99/modules.conf /home/abernard/sferes2-0.99/exp/$exp 

if [[ -d "/home/abernard/sferes2-0.99/build/prod/exp/$exp" ]]
then
	tar -rvf $name /home/abernard/sferes2-0.99/build/prod/exp/$exp
fi

gzip -f $name 

if [[ ! -z $output ]]
then
	name=$name".gz"
	mv $name $output
fi

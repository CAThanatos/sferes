#!/bin/bash

Usage()
{
	echo "usage: $0 -e exp [-n name] [-o outputDirectory] [-s] [-h]

Generates an archive of the all the files necessary to run a determined experiment.

OPTIONS:
	-h	Shows this message
	-e	The experiment to archive
	-n	The name of the archive
	-o	The ouput directory where to move the archive file
	-s	Adds the scripts contained in scriptsArthur to the archive"
}

exp=
name=
output=
addScripts=
while getopts "hse:n:o:" OPTION
do
	case $OPTION in
		h)
			Usage
			exit 1
			;;
		s)
			addScripts=1
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

if [[ ! -z $addScripts ]]
then
	tar -rvf $name /home/abernard/sferes2-0.99/scriptsArthur
fi

gzip -f $name 

if [[ ! -z $output ]]
then
	name=$name".gz"
	mv $name $output
fi

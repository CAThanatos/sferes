#!/bin/bash

Usage()
{
	echo "usage: $0 -e exp

Copies all code necessary for the experiment on the ISIR cluster.

OPTIONS:
	-h	Shows this message
	-e	The experiment to copy"
}

exp=
while getopts "he:" OPTION
do
	case $OPTION in
		h)
			Usage
			exit 1
			;;
		e)
			exp=$OPTARG
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

scp -r /home/abernard/sferes2-0.99/sferes abernard@cluster.isir.upmc.fr:./sferes2-0.99/
scp -r /home/abernard/sferes2-0.99/modules abernard@cluster.isir.upmc.fr:./sferes2-0.99/
scp -r /home/abernard/sferes2-0.99/exp/$exp abernard@cluster.isir.upmc.fr:./sferes2-0.99/exp
scp -r /home/abernard/sferes2-0.99/modules.conf abernard@cluster.isir.upmc.fr:./sferes2-0.99/

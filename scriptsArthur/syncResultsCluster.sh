#!/bin/bash

Usage()
{
	echo "usage: $0 -d directory

Copies the specified directory from the ISIR cluster.

OPTIONS:
	-h	Shows this message
	-d	The directory to copy"
}

dossier=ResultatsCluster
while getopts "hd:" OPTION
do
	case $OPTION in
		h)
			Usage
			exit 1
			;;
		d)
			dossier=$OPTARG
			;;
		?)
			Usage
			exit
			;;
	esac
done

if [[ -z $dossier ]]
then
	Usage
	exit 1
fi

rsync -avz abernard@cluster.isir.upmc.fr:./sferes2-0.99/$dossier /home/abernard/sferes2-0.99

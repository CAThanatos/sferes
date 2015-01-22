#!/bin/bash

Usage()
{
	echo "usage: $0 -d directory [-s site]

Copies the specified directory from a determined site or all the sites.

OPTIONS:
	-h	Shows this message
	-d	The directory to copy
	-s 	The site from which to copy"
}

dossier=./ResultatsG5K
site=
while getopts "hd:s:" OPTION
do
	case $OPTION in
		h)
			Usage
			exit 1
			;;
		d)
			dossier=$OPTARG
			;;
		s)
			site=$OPTARG
			;;
		?)
			Usage
			exit
			;;
	esac
done

if [[ -z $site ]]
then
	for i in rennes grenoble lille luxembourg lyon nancy reims sophia toulouse; do
	#for i in rennes grenoble lille luxembourg lyon nancy reims sophia; do
		echo "rsync on $i:~/$dossier"
	
		rsync -avz $i.g5k:~/$dossier /home/abernard/sferes2-0.99
	done
else
	echo "rsync on $site:~/$dossier";
	
	rsync -avz $site.g5k:~/$dossier /home/abernard/sferes2-0.99
fi

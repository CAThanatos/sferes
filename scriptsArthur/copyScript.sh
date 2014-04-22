#!/bin/bash

Usage()
{
	echo "usage: $0 -f script [-s site] [-r]

Copies a determined file on all grid5000 sites or a determined site.

OPTIONS:
	-h	Shows this message
	-s 	The site where to copy
	-f	The file to copy
	-r	If the file is a directory"
}

script=
site=
directory=
while getopts "hrf:s:" OPTION
do
	case $OPTION in
		h)
			Usage
			exit 1
			;;
		f)
			script=$OPTARG
			;;
		s)
			site=$OPTARG
			;;
		r)
			directory=1
			;;
		?)
			Usage
			exit
			;;
	esac
done

if [[ -z $script ]]
then
	Usage
	exit 1
fi

if [[ -z $site ]]
then
	for i in rennes grenoble lille luxembourg lyon nancy reims sophia toulouse; do
	#for i in rennes grenoble lille luxembourg lyon nancy reims sophia; do
		echo "copying $script on $i..."
	
		if [[ -z $directory ]]
		then
			scp $script $i.g5k:~/
		else
			scp -r $script $i.g5k:~/
		fi
	done
else
	echo "copying $script on $site..."
	
	if [[ -z $directory ]]
	then
		scp $script $site.g5k:~/
	else
		scp -r $script $site.g5k:~/
	fi
fi

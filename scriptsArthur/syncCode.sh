#!/bin/bash

Usage()
{
	echo "usage: $0 -e exp [-s site]

Copies all code necessary for the experiment on all grid5000 sites or a determined site.

OPTIONS:
	-h	Shows this message
	-e	The experiment to copy
	-s 	The site where to copy"
}

exp=StagHuntExp3-Duo
site=
while getopts "he:s:" OPTION
do
	case $OPTION in
		h)
			Usage
			exit 1
			;;
		e)
			exp=$OPTARG
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
	for i in rennes grenoble lille luxembourg lyon nancy reims sophia toulouse nantes; do
	#for i in rennes grenoble lille luxembourg lyon nancy reims sophia; do
		echo "rsync on $i..."
	
		rsync -avz /home/abernard/sferes2-0.99/sferes $i.g5k:~/sferes2-0.99
		rsync -avz /home/abernard/sferes2-0.99/modules $i.g5k:~/sferes2-0.99
		rsync -avz /home/abernard/sferes2-0.99/exp/$exp $i.g5k:~/sferes2-0.99/exp
		rsync -avz /home/abernard/sferes2-0.99/modules.conf $i.g5k:~/sferes2-0.99
	done
else
	echo "rsnyc on $site..."

	rsync -avz /home/abernard/sferes2-0.99/sferes $site.g5k:~/sferes2-0.99
	rsync -avz /home/abernard/sferes2-0.99/modules $site.g5k:~/sferes2-0.99
	rsync -avz /home/abernard/sferes2-0.99/exp/$exp $site.g5k:~/sferes2-0.99/exp
	rsync -avz /home/abernard/sferes2-0.99/modules.conf $site.g5k:~/sferes2-0.99
fi

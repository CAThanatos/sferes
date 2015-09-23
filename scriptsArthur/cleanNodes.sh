#!/bin/bash

Usage()
{
	echo "usage: $0 [-s site]

	Clean all build directories on all sites or a determined site.

	OPTIONS:
		-h	Shows this message
		-s 	The site where to clean"
}

exp=StagHuntExp3-Duo
site=
while getopts "hs:" OPTION
do
	case $OPTION in
		h)
			Usage
			exit 1
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
		echo "clean on $i..."

		ssh $i.g5k "rm -r ~/sferes2-0.99/build/debug/exp/*"
		ssh $i.g5k "rm -r ~/sferes2-0.99/build/default/exp/*"
	done
else
	echo "clean on $site..."

	ssh $site.g5k "rm -r ~/sferes2-0.99/build/debug/exp/*"
	ssh $site.g5k "rm -r ~/sferes2-0.99/build/default/exp/*"
fi

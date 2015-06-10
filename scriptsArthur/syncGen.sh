#!/bin/bash

Usage()
{
	echo "usage: $0 [-s site]

	Copies the experiment file and all files necessary for the pursuit of an experiment on all grid5000 sites or on a determined site.

	OPTIONS:
		-h	Shows this message
		-s 	The site where to copy"
}


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
	for i in lille rennes grenoble luxembourg lyon nancy reims sophia toulouse nantes; do
		ssh $i.g5k "rm -r lastGenPop"
		scp -r lastGenPop/ $i.g5k:./
		scp TemplateExp.exp $i.g5k:./
	done
else
	ssh $site.g5k "rm -r lastGenPop"
	scp -r lastGenPop/ $site.g5k:./
	scp TemplateExp.exp $site.g5k:./
fi

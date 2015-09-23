#!/bin/bash

Usage()
{
	echo "usage: $0

	Copies the experiment file and all files necessary for the pursuit of an experiment on the ISIR cluster.

	OPTIONS:
		-h	Shows this message"
}


while getopts "h" OPTION
do
	case $OPTION in
		h)
			Usage
			exit 1
			;;
		?)
			Usage
			exit
			;;
	esac
done


ssh cluster "rm -r ./sferes2-0.99/lastGenPop"
scp -r lastGenPop/ cluster:./sferes2-0.99/
scp TemplateExp.exp cluster:./sferes2-0.99/
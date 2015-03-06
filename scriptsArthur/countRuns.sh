#!/bin/bash

Usage()
{
	echo "usage: $0 [-s site]

Check for the correct launch of experiments on each site or a particular site.

OPTIONS:
	-h	Shows this message
	-s 	The site where to check"
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
	for i in rennes grenoble lille luxembourg lyon nancy reims sophia toulouse nantes; do
		checkSite=

		while true; do
			read -p "Check on $i ? (Y/N)" yn
			case $yn in
				[Yy]* ) checkSite=true; break;;
				[Nn]* ) checkSite=false; break;;
				* ) echo "No considered."; checkSite=false; break;;
			esac
		done

		if [ $checkSite = true ]
		then
			echo "Number of runs : "
			ssh $i.g5k ./count.sh

			echo "Nodes : "
			ssh $i.g5k ls -ald *.grid5000.fr_*
		fi
	done
else
	echo "Checking on $site..."

	echo "Number of runs : "
	ssh $site.g5k ./count.sh

	echo "Nodes : "
	ssh $site.g5k ls -ald *.grid5000.fr_*
fi

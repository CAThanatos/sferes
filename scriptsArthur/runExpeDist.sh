#!/bin/sh

Usage()
{
	echo "usage: $0 [-s site]

	Submit a job for each site of Grid5000 or a particular site.

	OPTIONS:
		-h	Shows this message
		-s 	The site where to submit a job"
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
			read -p "Submit on $i ? (Y/N)" yn
			case $yn in
				[Yy]* ) checkSite=true; break;;
				[Nn]* ) checkSite=false; break;;
				* ) echo "'No' considered."; checkSite=false; break;;
			esac
		done

		if [ $checkSite = true ]
		then
			read -p "Number of nodes : " nodes

			read -p
			echo "Number of nodes : "
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

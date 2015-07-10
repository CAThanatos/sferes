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


for i in rennes grenoble lille luxembourg lyon nancy reims sophia toulouse nantes; do
	submitSite=

	while true; do
		read -p "Submit on $i ? (Y/N)" yn
		case $yn in
			[Yy]* ) submitSite=true; break;;
			[Nn]* ) submitSite=false; break;;
			* ) echo "'No' considered."; submitSite=false; break;;
		esac
	done

	if [ $submitSite = true ]
	then
		nodes=
		read -p "Number of nodes : " nodes

		day=
		read -p "Day of submit : " day

		dayInt=
		case $day in
			tomorrow | t ) dayInt=-2; break;;
			today | R ) dayInt=-1; break;;
			lundi | monday | l ) dayInt=0; break;;
			mardi | tuesday | m ) dayInt=1; break;;
			mercredi | wednesday | M ) dayInt=2; break;;
			jeudi | thursday | j ) dayInt=3; break;;
			vendredi | friday | v | w ) dayInt=4; break;;
			* ) dayInt=-1; break;;
		esac

		case $dayInt in
			-2 ) ssh $i.g5k ./runExpe.sh -n $nodes -t; break;;
			-1 ) ssh $i.g5k ./runExpe.sh -n $nodes -R; break;;
			0 ) ssh $i.g5k ./runExpe.sh -n $nodes -M; break;;
			1 ) ssh $i.g5k ./runExpe.sh -n $nodes -T; break;;
			2 ) ssh $i.g5k ./runExpe.sh -n $nodes -E; break;;
			3 ) ssh $i.g5k ./runExpe.sh -n $nodes -H; break;;
			4 ) ssh $i.g5k ./runExpe.sh -n $nodes -W; break;;
			* ) ssh $i.g5k ./runExpe.sh -n $nodes -R; break;;
		esac
	fi
done

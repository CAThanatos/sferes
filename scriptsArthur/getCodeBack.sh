#!/bin/bash

Usage()
{
	echo "usage: $0 -e exp -s site

Copies back all code necessary for the experiment from a determined site.

OPTIONS:
	-h	Shows this message
	-e 	The experiment to copy
	-s 	The site where to copy"
}

exp=
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

if [[ -z $exp ]] || [[ -z $site ]]
then
	Usage
	exit 1
fi

echo "rsync on $site..."

rsync -avz $site.g5k:~/sferes2-0.99/sferes /home/abernard/sferes2-0.99
rsync -avz $site.g5k:~/sferes2-0.99/modules /home/abernard/sferes2-0.99
rsync -avz $site.g5k:~/sferes2-0.99/exp/$exp /home/abernard/sferes2-0.99/exp
rsync -avz $site.g5k:~/sferes2-0.99/modules.conf /home/abernard/sferes2-0.99


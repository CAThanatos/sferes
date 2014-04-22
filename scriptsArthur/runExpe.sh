#!/bin/bash

# Usage : ./runExpe.sh <ExperimentFile> <NumberOfNodes> <Walltime> ["<ReservationDate>"]


expe=$1
nbNodes=$2
walltime=$3

echo "Running experiment $expe"
if [ $# -lt 4 ]
then
	oarsub -t deploy -l nodes=$nbNodes,walltime=$walltime "./katapult --deploy-env sferes-env --copy-ssh-key './runExpe.perl -f $expe -w $walltime'"
else
	oarsub -t deploy -r "$4" -l nodes=$nbNodes,walltime=$walltime "./katapult --deploy-env sferes-env --copy-ssh-key './runExpe.perl -f $expe -w $walltime'"
fi

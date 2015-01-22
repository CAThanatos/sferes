#!/usr/bin/env python

import os
import numpy as np
import re
import argparse


def make_dataBest(dossier, precision, output) :
	listBestFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^bestfit(\d*)\.dat$", f))]

	refactString = "Evaluation,Run,Fitness,NbHaresDuo,NbHaresSolo,NbHares,NbSStagsDuo,NbSStagsSolo,NbSStags,NbBStagsDuo,NbBStagsSolo,NbBStags\n"
	for bestfit in listBestFit :
		m = re.search(r"^bestfit(\d*)\.dat$", bestfit)

		if m :
			run = m.group(1)

			with open(dossier + "/" + bestfit, 'r') as fileBest :
				fileBest = fileBest.readlines()
				lines = [line.rstrip('\n').split(',') for line in fileBest]

				cpt = 0
				for line in lines :
					evaluation = int(line[0])
					fitness = float(line[1])
					nbHares = float(line[2])
					nbHaresSolo = float(line[3])
					nbSStags = float(line[4])
					nbSStagsSolo = float(line[5])
					nbBStags = float(line[6])
					nbBStagsSolo = float(line[7])

					nbHaresDuo = nbHares - nbHaresSolo
					nbSStagsDuo = nbSStags - nbSStagsSolo
					nbBStagsDuo = nbBStags - nbBStagsSolo

					if cpt % precision == 0 :
						refactString += "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n".format(evaluation,run,fitness,nbHaresDuo,nbHaresSolo,nbHares,nbSStagsDuo,nbSStagsSolo,nbSStags,nbBStagsDuo,nbBStagsSolo,nbBStags)

					cpt += 1

	with open(dossier + "/" + output, 'w') as fileOut :
		fileOut.write(refactString)


def make_dataDirAll(dossier, precision, output) :
	refactString = "Evaluation,Fitness,NbHaresDuo,NbHaresSolo,NbHares,NbSStagsDuo,NbSStagsSolo,NbSStags,NbBStagsDuo,NbBStagsSolo,NbBStags\n"

	with open(dossier + "/allfitevalstat.dat", 'r') as fileAllFit :
		fileAllFit = fileAllFit.readlines()
		lines = [line.rstrip('\n').split(',') for line in fileAllFit]

		cpt = 0
		lastEval = None
		for line in lines :
			evaluation = int(line[0])
			fitness = float(line[1])
			nbHares = float(line[2])
			nbHaresSolo = float(line[3])
			nbSStags = float(line[4])
			nbSStagsSolo = float(line[5])
			nbBStags = float(line[6])
			nbBStagsSolo = float(line[7])

			nbHaresDuo = nbHares - nbHaresSolo
			nbSStagsDuo = nbSStags - nbSStagsSolo
			nbBStagsDuo = nbBStags - nbBStagsSolo

			if lastEval == None :
				lastEval = evaluation
			elif evaluation > lastEval :
				cpt += 1
				lastEval = evaluation

			if cpt % precision == 0 :
				refactString += "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}\n".format(evaluation,fitness,nbHaresDuo,nbHaresSolo,nbHares,nbSStagsDuo,nbSStagsSolo,nbSStags,nbBStagsDuo,nbBStagsSolo,nbBStags)


	with open(dossier + "/" + output, 'w') as fileOut :
		fileOut.write(refactString)



def make_dataAll(dossier, precision, output) :
	listAllFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^allfiteval(\d*)\.dat$", f))]

	refactString = "Evaluation,Run,Fitness,NbHaresDuo,NbHaresSolo,NbHares,NbSStagsDuo,NbSStagsSolo,NbSStags,NbBStagsDuo,NbBStagsSolo,NbBStags\n"
	for allfit in listAllFit :
		m = re.search(r"^allfitevalstat(\d*)\.dat$", allfit)

		if m :
			run = m.group(1)

			with open(dossier + "/" + allfit, 'r') as fileAllFit :
				fileAllFit = fileAllFit.readlines()
				lines = [line.rstrip('\n').split(',') for line in fileAllFit]

				cpt = 0
				for line in lines :
					evaluation = int(line[0])
					fitness = float(line[1])
					nbHares = float(line[2])
					nbHaresSolo = float(line[3])
					nbSStags = float(line[4])
					nbSStagsSolo = float(line[5])
					nbBStags = float(line[6])
					nbBStagsSolo = float(line[7])

					nbHaresDuo = nbHares - nbHaresSolo
					nbSStagsDuo = nbSStags - nbSStagsSolo
					nbBStagsDuo = nbBStags - nbBStagsSolo

					if cpt % precision == 0 :
						refactString += "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n".format(evaluation,run,fitness,nbHaresDuo,nbHaresSolo,nbHares,nbSStagsDuo,nbSStagsSolo,nbSStags,nbBStagsDuo,nbBStagsSolo,nbBStags)

					cpt += 1

	with open(dossier + "/" + output, 'w') as fileOut :
		fileOut.write(refactString)



if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help = "Results file", default='refactData.dat')
	args = parser.parse_args()
	make_dataAll(args.file, 5, "refactCaca.dat")
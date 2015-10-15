#!/usr/bin/env python

import os
import math
import argparse


def distance(gen1, gen2) :
	assert(len(gen1) == len(gen2))

	cpt = 0;
	distance = 0
	while cpt < len(gen1) :
		distance += pow(gen1[cpt] - gen2[cpt], 2)
		cpt += 1

	return math.sqrt(distance)/math.sqrt(len(gen1))

def main(args) :
	if os.path.isdir(args.directory) :
		if os.path.isfile(os.path.join(args.directory, args.file)) :
			with open(os.path.join(args.directory, args.file), "r") as fileRead :
				fileRead = fileRead.readlines()

				lastEval = None
				listGenomes = []
				genoMean = []
				for line in fileRead :
					data = line.rstrip('\n').split(',')

					if len(data) > 0 :
						eval = data[0]

						if lastEval == None :
							lastEval = eval

						if eval == lastEval :
							listGenomes.append([float(gene) for gene in data[1:]])
						else :
							genoMean = [0.0] * len(listGenomes[0])

							for i in range(0, len(listGenomes)) :
								for j in range(0, len(listGenomes[i])) :
									genoMean[j] += listGenomes[i][j]

							for j in range(0, len(listGenomes[0])) :
								genoMean[j] /= len(listGenomes)

							meanDistance = 0.0
							for i in range(0, len(listGenomes)) :
								meanDistance += distance(listGenomes[i], genoMean)

							meanDistance /= len(listGenomes)

							if meanDistance > 0.2 :
								print("--> Eval " + str(lastEval) + " : " + str(meanDistance))
							else :
								print("Eval " + str(lastEval) + " : " + str(meanDistance))

							listGenomes = []
							listGenomes.append([float(gene) for gene in data[1:]])

						lastEval = eval




if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('-f', '--file', help = "Genome file", default = "allgenomes.dat")
	parser.add_argument('-t', '--threshold', help = "Threshold", type = float, default = 0.2)
	# parser.add_argument('-p', '--precision', help = "Evaluation precision", type = int, default = 1000)
	# parser.add_argument('-o', '--output', help = "Output directory", default = "GraphsResults")
	args = parser.parse_args()

	main(args)

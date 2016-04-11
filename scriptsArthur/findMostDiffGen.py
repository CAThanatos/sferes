#!/usr/bin/env python

import os
import sys
import re
import argparse
import math


def distanceGenomes(gen1, gen2) :
	assert(len(gen1) == len(gen2))

	cpt = 0;
	distance = 0
	while cpt < len(gen1) :
		distance += pow(gen1[cpt] - gen2[cpt], 2)
		cpt += 1

	return math.sqrt(distance)/math.sqrt(len(gen1))


def main(args) :
	if os.path.isfile(args.file) :

		genomeList = list()
		with open(args.file, 'r') as fileRead :
			fileRead = fileRead.readlines()
			fileRead = [line.rstrip('\n') for line in fileRead]

			regexpEval = re.compile(r"^(\d+),(.+)$")

			for line in fileRead :
				s = regexpEval.search(line)

				if s :
					eval = int(s.group(1))

					if eval == args.evaluation :
						genome = [float(gene) for gene in s.group(2).split(',')]
						genomeList.append(genome)

		maxDist = 0
		genome1 = None
		genome2 = None
		if(args.num == -1) :
			for i in range(0, len(genomeList)) :
				for j in range(i + 1, len(genomeList)) :
					distance = distanceGenomes(genomeList[i], genomeList[j])

					if distance > maxDist :
						maxDist = distance
						genome1 = genomeList[i]
						genome2 = genomeList[j]
		else :
			assert(args.num < len(genomeList))
			genome1 = genomeList[args.num]

			for i in range(0, len(genomeList)) :
				distance = distanceGenomes(genome1, genomeList[i])

				if distance > maxDist :
					maxDist = distance
					genome2 = genomeList[i]


		if genome1 != None and genome2 != None :
			print("Distance : " + str(maxDist))

			with open(args.output, "w") as fileWrite :
				stringOut = ""
				cpt = 0
				while cpt < len(genome1) :
					stringOut += str(genome1[cpt])

					if cpt < (len(genome1) - 1) :
						stringOut += ","

					cpt += 1

				stringOut += "\n"
				cpt = 0
				while cpt < len(genome2) :
					stringOut += str(genome2[cpt])

					if cpt < (len(genome2) - 1) :
						stringOut += ","

					cpt += 1

				fileWrite.write(stringOut)



if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('file', help = "Genome file")
	parser.add_argument('evaluation', help = "Evaluation", type = int)
	parser.add_argument('-o', '--output', help = "File out", default = "genome.dat")
	parser.add_argument('-n', '--num', help = "Index of first genome to compare", default = -1, type = int)
	args = parser.parse_args()

	main(args)
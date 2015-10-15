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
	if os.path.isfile(args.file) :
		with open(args.file, "r") as fileRead :
			fileRead = fileRead.readlines()

			listGenomes = []
			for line in fileRead :
				data = line.rstrip('\n').split(',')

				if len(data) > 0 :
					listGenomes.append([float(gene) for gene in data])

			if len(listGenomes) == 2 :
				dist = distance(listGenomes[0], listGenomes[1])

				print("Distance : " + str(dist))



if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('file', help = "Genome file")
	args = parser.parse_args()

	main(args)
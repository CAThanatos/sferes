#!/usr/bin/env python

import os
import argparse
import re

THRESHOLD_COOP_SOLO = 5.0


def main(args) :
	fileIn = os.path.join(args.directory, 'allgenomestrace.dat')
	regexpLine = re.compile(r"^(.+),(.+),(.+),(.+)$")
	phyloTree = {}
	behaviourTree = {}
	if os.path.isfile(fileIn) :
		with open(fileIn, 'r') as fileRead :
			fileRead = fileRead.readlines()

			for line in fileRead :
				line = line.rstrip('\n')

				s = regexpLine.search(line)
				if s :
					eval = int(s.group(1))

					if eval not in phyloTree :
						phyloTree[eval] = []
						behaviourTree[eval] = []

					ancestor = int(s.group(2))
					phyloTree[eval].append(ancestor)

					nb_ind1_leader_first = float(s.group(3))
					nb_preys_killed_coop = float(s.group(4))
					behaviour = None

		listEval = sorted(phyloTree.keys(), reverse = True)
		listAncestors = []

		ancestor = phyloTree[listEval[0]][args.genome]
		listAncestors.append(ancestor)
		cpt = 1
		while cpt < len(listEval) :
			ancestor = phyloTree[listEval[cpt]][ancestor]
			listAncestors.append(ancestor)
			cpt += 1

		print(listAncestors)
		print('\t-> Oldest ancestor : ' + str(listAncestors[-1]))






if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('genome', help = "Child genome for which we want to find the ancestor", type = int)
	args = parser.parse_args()

	main(args)

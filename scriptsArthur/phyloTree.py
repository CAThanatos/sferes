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

		evaluationChild = listEval[0]

		if args.evaluation != -1 and args.evaluation in listEval :
			evaluationChild = args.evaluation

		ancestor = args.genome
		listAncestors.append(ancestor)
		cpt = listEval.index(evaluationChild)
		while cpt < len(listEval) :
			ancestor = phyloTree[listEval[cpt]][ancestor]
			listAncestors.append(ancestor)
			cpt += 1

		print(listAncestors)
		print('\t-> Oldest ancestor : ' + str(listAncestors[-1]))

		if args.coalescence != -1 :
			listAncestors = []

			ancestor = args.coalescence
			listAncestors.append(ancestor)
			cpt = listEval.index(evaluationChild)
			while cpt < len(listEval) :
				ancestor = phyloTree[listEval[cpt]][ancestor]
				listAncestors.append(ancestor)
				cpt += 1

			print(listAncestors)
			print('\t-> Oldest ancestor : ' + str(listAncestors[-1]))

			divergenceIndex = listEval.index(evaluationChild)

			ancestor1 = args.genome
			ancestor2 = args.coalescence
			while divergenceIndex < len(listEval):
				evaluation = listEval[divergenceIndex]
				ancestor1 = phyloTree[evaluation][ancestor1]
				ancestor2 = phyloTree[evaluation][ancestor2]

				if ancestor1 != ancestor2 :
					divergenceIndex += 1
				else :
					break

			if divergenceIndex >= len(listEval) :
				print('No common ancestor between these two genomes.')
			else :
				print('Divergence after evaluation ' + str(listEval[divergenceIndex]) + ' from common ancestor ' + str(ancestor1))







if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('genome', help = "Child genome for which we want to find the ancestor", type = int)
	parser.add_argument('-e', '--evaluation', help = "Evaluation of the child for which we look for the ancestor", type = int, default = -1)
	parser.add_argument('-c', '--coalescence', help = "Second child genome for which we want to find the point of divergence with the first genome", type = int, default = -1)
	args = parser.parse_args()

	main(args)

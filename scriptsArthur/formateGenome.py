#!/usr/bin/env python

import os
import re
import argparse

def main(args) :
	regexp = re.compile(r"^(\d+),")
	if os.path.isfile(args.file) :
		with open(args.file, 'r') as fileRead :
			fileRead = fileRead.readlines()

			evalGenome = args.evaluation
			if evalGenome == -1 :
				cptLine = 0
				while cptLine < len(fileRead) :
					line = fileRead[cptLine]
					s = regexp.search(line)

					if s :
						evalGenome = int(s.group(1))

					cptLine += 1

			cptLine = 0
			while cptLine < len(fileRead) :
				line = fileRead[cptLine]
				s = regexp.search(line)

				if s :
					eval = int(s.group(1))

					if eval >= evalGenome :
						lineGenotype = fileRead[cptLine + args.index]
						genotype = lineGenotype.rstrip('\n').split(',')

						with open(args.output, 'w') as fileWrite :
							cpt = 1
							while cpt < len(genotype) :
								if(cpt < len(genotype) - 1) :
									fileWrite.write(genotype[cpt] + ',')
								else :
									fileWrite.write(genotype[cpt])
								cpt += 1

						break

				cptLine += 1



if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('file', help = "Genome file")
	parser.add_argument('-e', '--evaluation', help = "Evaluation of genotype", type = int, default = -1)
	parser.add_argument('-o', '--output', help = "Output file", default = "gen.out")
	parser.add_argument('-n', '--index', help = "Genome index", default = 0, type = int)
	args = parser.parse_args()

	main(args)
#!/usr/bin/env python

import os
import re
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('directory', help = "Results directory")
parser.add_argument('-n', '--nbByGen', help = "Number of evaluations by generation", default = "20")
parser.add_argument('-f', '--firstGenPop', help = "Number of individuals evaluated at first gen", default = "10")
args = parser.parse_args()

subDirs = [os.path.join(args.directory, d) for d in os.listdir(args.directory) if os.path.isdir(os.path.join(args.directory, d))]
for subDir in subDirs :
	tuples = os.walk(subDir)
	minGen = None
	for tuple in tuples :
		if re.search(r"Dir\d+$", tuple[0]) :
			lastGen = 0
			for fileName in tuple[2] :
				m = re.search(r"^gen_(\d*)$", fileName)

				if m :
					gen = int(m.group(1))

					if(gen > lastGen) :
						lastGen = gen

			if (minGen == None) or (lastGen < minGen) :
				minGen = lastGen

	if minGen != None :
		minEval = (minGen + 1) * int(args.nbByGen) + int(args.firstGenPop)
		print(subDir + " : " + str(minGen) + " -> " + str(minEval))

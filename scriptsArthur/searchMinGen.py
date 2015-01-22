#!/usr/bin/env python

import os
import re
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('directory', help = "Results directory")
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

	print(subDir + " : " + str(minGen))
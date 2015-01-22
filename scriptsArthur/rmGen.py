#!/usr/bin/env python

import os
import sys
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('directory', help = "Directory form which to delete")
parser.add_argument('last', help = "Last generation before deletion")
parser.add_argument('-n', '--nbByGen', help = "Number of evaluations by generation", default = "20")
parser.add_argument('-f', '--firstGenPop', help = "Number of individuals evaluated at first gen", default = "10")
args = parser.parse_args()

dossier = args.directory
lastGen = int(args.last)

nbByGen = int(args.nbByGen)
firstGenPop = int(args.firstGenPop)
lastEval = nbByGen * (lastGen + 1) + firstGenPop

print(str(lastGen) + " -> " + str(lastEval))

listDirs = [os.path.join(dossier, d) for d in os.listdir(dossier) if os.path.join(dossier, d)]

for subDir in listDirs :
	if re.search(r"Dir", subDir) :
		listFiles = [os.path.join(subDir, f) for f in os.listdir(subDir) if os.path.join(subDir, f)]

		for curFile in listFiles :
			r = re.search(r"popGen_(\d+)$", curFile)
			if r :
				gen = int(r.group(1))

				if gen > lastGen :
					pass
					os.remove(curFile)
			else :
				r = re.search(r"gen_(\d+)$", curFile)
				if r :
					gen = int(r.group(1))

					if gen > lastGen :
						pass
						os.remove(curFile)
				else :
					r = re.search(r"\.dat$", curFile)

					if r :
						output = ""
						with open(curFile, 'r') as fileRead :
							fileRead = fileRead.readlines()

							for line in fileRead :
								m = re.search(r"^(\d+),", line)

								if m :
									curEval = int(m.group(1))

									if curEval <= lastEval :
										output += line

						with open(curFile, 'w') as fileWrite :
							fileWrite.write(output)

					else :
						r = re.search(r"\.dat2$", curFile)

						if r :
							os.remove(curFile)

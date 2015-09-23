#!/usr/bin/env python

import argparse
import os
import re

import Tools


def main(args) :
	listTopDirectories = Tools.searchTopDirectories(args.directory)

	regGen = re.compile(r"^gen_(\d+)$")
	regPopGen = re.compile(r"^popGen_(\d+)$")
	regDir = re.compile(r"^Dir(\d+)$")
	for topDirectory in listTopDirectories :
		if os.path.isdir(topDirectory) :
			listSubDirs = [os.path.join(topDirectory, subDir) for subDir in os.listdir(topDirectory) if regDir.search(subDir)]

			for subDir in listSubDirs :
				if os.path.isdir(subDir) :
					listFiles = [fileGen for fileGen in os.listdir(subDir) if (regGen.search(fileGen) or regPopGen.search(fileGen))]

					for curFile in listFiles :
						s = regGen.search(curFile)

						gen = -1
						if s :
							gen = int(s.group(1))
						else :
							s = regPopGen.search(curFile)

							if s :
								gen = int(s.group(1))

						if gen != -1 :
							if gen%100 != 0 :
								os.remove(os.path.join(subDir, curFile))


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	args = parser.parse_args()

	main(args)
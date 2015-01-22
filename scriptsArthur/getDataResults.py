#!/usr/bin/python

import os
import re
import argparse
import shutil

import Tools


def main(args) :
	listTopDirectories = Tools.searchTopDirectoriesPrefix(args.directory, args.prefix)

	if args.clean and os.path.isdir(args.output) :
		shutil.rmtree(args.output)


	regexp = re.compile(r"^Dir\d+$")
	regexpFile = re.compile(r"\.dat$")
	for topDirectory in listTopDirectories :
		if os.path.isdir(topDirectory) :
			curOutput = os.path.join(args.output, os.path.basename(topDirectory))

			if os.path.isdir(curOutput) :
				shutil.rmtree(curOutput)

			os.makedirs(curOutput)

			listSubDirs = [d for d in os.listdir(topDirectory) if os.path.isdir(os.path.join(topDirectory, d)) and regexp.search(d)]
			oldOutput = curOutput
			for subDir in listSubDirs :
				curOutput = os.path.join(oldOutput, subDir)
				os.makedirs(curOutput)

				subDirFull = os.path.join(topDirectory, subDir)
				listFiles = [os.path.join(subDirFull, f) for f in os.listdir(subDirFull) if os.path.isfile(os.path.join(subDirFull, f))]

				for curFile in listFiles :
					if regexpFile.search(curFile) and os.path.basename(curFile) not in args.exclusion :
						shutil.copyfile(curFile, os.path.join(curOutput, os.path.basename(curFile)))



if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('-o', '--output', help = "Output directory", default='ResultatsArticle')
	parser.add_argument('-f', '--prefix', help = "Run prefix", default='Dir')
	parser.add_argument('-c', '--clean', help = "Clean output directory", default=False, action="store_true")
	parser.add_argument('-e', '--exclusion', help = "Excluded files", default=["bestgenome.dat", "allgenomes.dat"], type=str, nargs='+')
	args = parser.parse_args()

	main(args)
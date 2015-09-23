#!/usr/bin/env python

import os
import argparse
import re
import shutil

import Tools

def main(args) :
	regexp = re.compile(r"^Dir(\d+)$")
	if os.path.isdir(args.directory) :
		listSubDir = [os.path.join(args.directory, subDir) for subDir in os.listdir(args.directory) if regexp.search(subDir)]

		for subDir in listSubDir :
			shutil.copyfile(args.file, os.path.join(subDir, args.output))


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('file', help = "Genome file")
	parser.add_argument('-o','--output', help = "Name of output file", default = "genome.dat")
	args = parser.parse_args()

	main(args)
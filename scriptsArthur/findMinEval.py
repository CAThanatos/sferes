#!/usr/bin/env python

import os
import path
import sys
import re
import argparse

import Tools


def main(args) :
	listTopDirectories = Tools.searchTopDirectories(args.directory)

	regexp = re.compile(r"^Dir\d+$")
	for directory in listTopDirectories :
		listSubSubDir = [os.path.join(directory, subSubDir) for subSubDir in os.listdir(directory)]

		if len(listSubSubDir) == 1 :
			bestfitFile = os.path.join(listSubSubDir[0], 'bestfit.dat')
			if os.path.isfile(bestfitFile) :
				with open(bestfitFile, 'r') as fileRead :
					fileRead = fileRead.readlines()
					s = re.search(r"^(\d+),", fileRead[0].rstrip('\n'))

					if s :
						minEval = int(s.group(1))
						print(directory + " : " + str(minEval))





if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('-r', '--refactor', help = "Refactor", default=None, type = str)
	# parser.add_argument('-f', '--prefix', help = "Run prefix", default='Dir')
	# parser.add_argument('-R', '--evalRm', help = "Evaluations from which to start", type=int, default=-1)
	# parser.add_argument('-r', '--refactor', help = "Refactor", default=False, action="store_true")

	# parser.add_argument('-m', '--max', help = "Max evaluation", default='20000')
	# parser.add_argument('-p', '--precision', help = "Precision", default='100')

	# parser.add_argument('-b', '--best', help = "Best only", default=False, action="store_true")
	# parser.add_argument('-a', '--all', help = "All only", default=False, action="store_true")
	# parser.add_argument('-d', '--diversity', help = "Drawing of diversity", default=False, action="store_true")
	# parser.add_argument('-l', '--leadership', help = "Drawing of leadership behavior", default=False, action="store_true")
	# parser.add_argument('-n', '--nn', help = "Drawing of nn stat", default=False, action="store_true")
	# parser.add_argument('-F', '--noDrawFit', help = "No drawing of fitness", default=False, action="store_true")
	# parser.add_argument('-u', '--drawRun', help = "Drawing of each run pareto frontier", default=False, action="store_true")

	# parser.add_argument('-g', '--firstGen', help = "Size of population of first generation", default=10, type=int)
	# parser.add_argument('-E', '--EvalByGen', help = "Number of evaluations by generation", default=20, type=int)
	# parser.add_argument('-G', '--drawGen', help = "Drawing generations", default=False, action="store_true")

	# parser.add_argument('-s', '--selection', help = "Selected runs", default=None, type=int, nargs='+')
	# parser.add_argument('-e', '--exclusion', help = "Excluded runs", default=None, type=int, nargs='+')
	args = parser.parse_args()

	main(args)

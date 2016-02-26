#!/usr/bin/env python

import os
import path
import sys
import re
import argparse

import Tools

FILE_MIN_EVAL = 'listMinEval.txt'

def main(args) :
	if os.path.isfile(FILE_MIN_EVAL) :
		hashMinEval = {}
		hashDiffEval = {}

		regexpFileMin = re.compile(r"^(.+) : (\d+),(\d+)$")
		with open(FILE_MIN_EVAL, 'r') as fileRead :
			fileRead = fileRead.readlines()
			fileRead = [line.rstrip('\n') for line in fileRead]

			for line in fileRead :
				s = regexpFileMin.search(line)

				if s:
					hashMinEval[s.group(1)] = int(s.group(2))
					hashDiffEval[s.group(1)] = int(s.group(3))



		listTopDirectories = Tools.searchTopDirectories(args.directory)

		regexp = re.compile(r"^Dir\d+$")
		regexpLine = re.compile(r"^(\d+),(.+)$")
		for directory in listTopDirectories :
			listSubDir = [subDir for subDir in os.listdir(directory) if regexp.search(subDir)]

			for subDir in listSubDir :
				dirName = os.path.basename(directory)

				if dirName != '' :
					totalName = dirName + "/" + subDir

					if totalName in hashMinEval.keys() :
						minEval = hashMinEval[totalName]
						diffEval = hashDiffEval[totalName]

						curDir = os.path.join(directory, subDir)
						listFiles = [os.path.join(curDir, curFile) for curFile in os.listdir(curDir) if re.search(r"\.dat$", curFile)]

						for curFile in listFiles :
							stringOut = ''
							with open(curFile, 'r') as fileRead :
								fileRead = fileRead.readlines()

								for line in fileRead :
									s = regexpLine.search(line)

									if s :
										eval = int(s.group(1))

										if eval >= minEval :
											newEval = eval - minEval + diffEval
											stringOut += str(newEval) + "," + s.group(2) + "\n"

							# print('Open/Write ' + curFile + " : " + str(minEval))
							os.remove(curFile)
							with open(curFile, 'w') as fileWrite :
								fileWrite.write(stringOut)





if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	args = parser.parse_args()

	main(args)

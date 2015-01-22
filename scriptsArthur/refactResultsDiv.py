#!/usr/bin/python

import os
import argparse
import re
import shutil
import sys

import Tools
from drawGraphsDiv import draw

nbPopFirstGen = 10

def copyFile(fileSource, fileDestination, evalToRemove) :
	if evalToRemove != -1 :
		lines = None
		with open(fileSource, "r") as fileRead :
			fileRead = fileRead.readlines()
			lines = [line.rstrip("\n") for line in fileRead]

		with open(fileDestination, "w") as fileOut :
			firstEval = None
			for line in lines :
				m = re.search(r"^(\d+),", line)
				if m :
					evaluation = int(m.group(1))

					if evaluation >= evalToRemove :
						if firstEval == None :
							firstEval = evaluation - nbPopFirstGen

						newEvaluation = evaluation - firstEval
						newLine = re.sub(r"^(\d+),", str(newEvaluation) + ",", line)

						fileOut.write(newLine + "\n")
	else :
		shutil.copyfile(fileSource, fileDestination)


def parse_dirName(dirName) :
	ret = {
					"fitness" : True,
					"diversity" : False,
					"similarity" : False,
					"name" : "MONOFIT"
				}

	regexp = re.compile(r"DIVERSITY")
	if regexp.search(dirName) :
		ret["diversity"] = True
		ret["name"] = "DIVERSITY"

	regexp = re.compile("SIMILARITY")
	if regexp.search(dirName) :
		ret["similarity"] = True
		ret["name"] += "_SIMILARITY"

		regexp2 = re.compile("SIMILARITY_ACTIVITY")
		if regexp2.search(dirName) :
			ret["name"] += "_ACTIVITY"
		else :
			ret["name"] += "_SENSORS"

	return ret



def main(args) :
	listRefactDir = ['BestFit', 'AllFit']
	regexp = r"^" + re.escape(args.prefix)
	dicoDir = {name : os.path.join(args.directory, name) for name in listRefactDir}

	for refactDir in dicoDir.values() :
		if os.path.isdir(refactDir) :
			shutil.rmtree(refactDir)

		os.makedirs(refactDir)

	listTopDirectories = Tools.searchTopDirectories(args.directory)

	for topDirectory in listTopDirectories :
		if os.path.isdir(topDirectory) :
			ret = parse_dirName(topDirectory)
			nameExp = ret["name"]

			paretoDir = os.path.join(topDirectory, "Pareto")
			if os.path.isdir(paretoDir) :
				shutil.rmtree(paretoDir)

			os.makedirs(paretoDir)

			listSubDirs = [d for d in os.listdir(topDirectory) if os.path.isdir(os.path.join(topDirectory, d))]

			for subDir in listSubDirs :
				if(re.match(regexp, subDir)) :
					m = re.match(r"^Dir(\d+)$", subDir)

					if m :
						numRun = int(m.group(1))

					curDir = os.path.join(topDirectory, subDir)
					listFiles = [f for f in os.listdir(curDir) if not os.path.isdir(os.path.join(curDir,f))]

					for curFile in listFiles :
						if(re.match(r'^bestfit.dat$', curFile)) :
							copyFile(os.path.join(curDir, curFile), os.path.join(dicoDir['BestFit'], 'bestfit{1}{0}.dat'.format(numRun, nameExp)), int(args.evalRm))
						elif(re.match(r'^allfitevalstat.dat$', curFile)) :
							copyFile(os.path.join(curDir, curFile), os.path.join(dicoDir['AllFit'], 'allfitevalstat{1}{0}.dat'.format(numRun, nameExp)), int(args.evalRm))
							copyFile(os.path.join(curDir, curFile), os.path.join(paretoDir, 'allfitevalstat{0}.dat'.format(numRun)), int(args.evalRm))
						elif(re.match(r'^alldivevalstat.dat$', curFile)) :
							copyFile(os.path.join(curDir, curFile), os.path.join(paretoDir, 'alldivevalstat{0}.dat'.format(numRun)), int(args.evalRm))
						elif(re.match(r'^allsimevalstat.dat$', curFile)) :
							copyFile(os.path.join(curDir, curFile), os.path.join(paretoDir, 'allsimevalstat{0}.dat'.format(numRun)), int(args.evalRm))

					numRun += 1


			if ret["diversity"] or ret["similarity"] :
				parametres =  { 
									"argMax" : int(args.max),
									"argMaxGen" : int(args.maxGen),
									"argPrecision" : int(args.precision),
									"argFirstGen" : args.firstGen,
									"argEvalByGen" : args.EvalByGen,
									"argDirectory" : topDirectory,
									"argType" : "Pareto",
									"argDrawRun" : args.drawRun
								}
				draw(**parametres)


	parametres =  { 
						"argMax" : int(args.max),
						"argMaxGen" : int(args.maxGen),
						"argPrecision" : int(args.precision),
						"argFirstGen" : args.firstGen,
						"argEvalByGen" : args.EvalByGen,
						"argDirectory" : args.directory,
						"argType" : "BestFit",
						"argDrawRun" : args.drawRun
					}
	draw(**parametres)




if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('-f', '--prefix', help = "Run prefix", default='Dir')
	parser.add_argument('-R', '--evalRm', help = "Evaluations from which to start", type=int, default=-1)
	parser.add_argument('-r', '--refactor', help = "Refactor", default=False, action="store_true")

	parser.add_argument('-m', '--max', help = "Max evaluation", default='20000')
	parser.add_argument('-M', '--maxGen', help = "Max generation", default='1000')
	parser.add_argument('-p', '--precision', help = "Precision", default='100')

	parser.add_argument('-u', '--drawRun', help = "Drawing of each run pareto frontier", default=False, action="store_true")

	parser.add_argument('-g', '--firstGen', help = "Size of population of first generation", default=10, type=int)
	parser.add_argument('-E', '--EvalByGen', help = "Number of evaluations by generation", default=20, type=int)
	args = parser.parse_args()

	main(args)

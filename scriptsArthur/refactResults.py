#!/usr/bin/python

import os
import argparse
import re
import shutil
import sys

import Tools
from drawGraphs import draw

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



def main(args) :
	listTopDirectories = Tools.searchTopDirectories(args.directory)

	listRefactDirFit = ['BestFit', 'AllFit', 'BestEverFit']
	listRefactDirDiv = ['BestDiv', 'AllDiv', 'BestEverDiv', 'ParetoFront']
	regexp = r"^" + re.escape(args.prefix)
	for topDirectory in listTopDirectories :
		if os.path.isdir(topDirectory) :
			dicoDirFit = {name : os.path.join(topDirectory, name) for name in listRefactDirFit}
			dicoDirDiv = {name : os.path.join(topDirectory, name) for name in listRefactDirDiv}

			listSubDirs = [d for d in os.listdir(topDirectory) if os.path.isdir(os.path.join(topDirectory, d))]

			if args.refactor :
				numRun = 1

				for subDir in listSubDirs :
					if subDir not in listRefactDirFit and subDir not in listRefactDirDiv :
						if not re.search(regexp, subDir) :
							newDir = os.path.join(topDirectory, 'Dir{0}'.format(numRun))

							if os.path.isdir(newDir) :
								print("Probleme lors du refactoring : " + newDir + " deja existant !")
								break
							else :
								shutil.move(os.path.join(topDirectory, subDir), os.path.join(topDirectory, 'Dir{0}'.format(numRun)))
								numRun += 1

			listSubDirs = [d for d in os.listdir(topDirectory) if os.path.isdir(os.path.join(topDirectory, d))]

			for refactDir in dicoDirFit.values() :
				if os.path.isdir(refactDir) :
					shutil.rmtree(refactDir)

				os.makedirs(refactDir)

			if args.diversity :
				for refactDir in dicoDirDiv.values() :
					if os.path.isdir(refactDir) :
						shutil.rmtree(refactDir)

					os.makedirs(refactDir)


			numRun = 1
			for subDir in listSubDirs :
				if(re.match(regexp, subDir)) :
					m = re.match(r"^Dir(\d+)$", subDir)

					if m :
						numRun = int(m.group(1))

					curDir = os.path.join(topDirectory, subDir)
					listFiles = [f for f in os.listdir(curDir) if not os.path.isdir(os.path.join(curDir,f))]

					for curFile in listFiles :
						if(re.match(r'^bestfit.dat$', curFile)) :
							copyFile(os.path.join(curDir, curFile), os.path.join(dicoDirFit['BestFit'], 'bestfit{0}.dat'.format(numRun)), int(args.evalRm))
						elif(re.match(r'^allfitevalstat.dat$', curFile)) :
							copyFile(os.path.join(curDir, curFile), os.path.join(dicoDirFit['AllFit'], 'allfitevalstat{0}.dat'.format(numRun)), int(args.evalRm))

							if not args.noDrawFit and args.diversity :
								copyFile(os.path.join(curDir, curFile), os.path.join(dicoDirDiv['ParetoFront'], 'allfitevalstat{0}.dat'.format(numRun)), int(args.evalRm))
						elif(re.match(r'^besteverfit.dat$', curFile)) :
							copyFile(os.path.join(curDir, curFile), os.path.join(dicoDirFit['BestEverFit'], 'besteverfit{0}.dat'.format(numRun)), int(args.evalRm))
						elif(re.match(r'^bestdiv.dat$', curFile) and args.diversity == True) :
							copyFile(os.path.join(curDir, curFile), os.path.join(dicoDirDiv['BestDiv'], 'bestdiv{0}.dat'.format(numRun)), int(args.evalRm))
						elif(re.match(r'^alldivevalstat.dat$', curFile) and args.diversity == True) :
							copyFile(os.path.join(curDir, curFile), os.path.join(dicoDirDiv['AllDiv'], 'alldivevalstat{0}.dat'.format(numRun)), int(args.evalRm))

							if not args.noDrawFit :
								copyFile(os.path.join(curDir, curFile), os.path.join(dicoDirDiv['ParetoFront'], 'alldivevalstat{0}.dat'.format(numRun)), int(args.evalRm))
						elif(re.match(r'^besteverdiv.dat$', curFile) and args.diversity == True) :
							copyFile(os.path.join(curDir, curFile), os.path.join(dicoDirDiv['BestEverDiv'], 'besteverdiv{0}.dat'.format(numRun)), int(args.evalRm))

					numRun += 1


			parametres =  { 
								"argMax" : int(args.max),
								"argPrecision" : int(args.precision),
								"argSelection" : args.selection,
								"argExclusion" : args.exclusion,
								"argFirstGen" : args.firstGen,
								"argEvalByGen" : args.EvalByGen,
								"argDirectory" : topDirectory,
								"argBest" : args.best,
								"argAll" : args.all,
								"argDiversity" : args.diversity,
								"argNoDrawFit" : args.noDrawFit,
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
	parser.add_argument('-p', '--precision', help = "Precision", default='100')

	parser.add_argument('-b', '--best', help = "Best only", default=False, action="store_true")
	parser.add_argument('-a', '--all', help = "All only", default=False, action="store_true")
	parser.add_argument('-d', '--diversity', help = "Drawing of diversity", default=False, action="store_true")
	parser.add_argument('-F', '--noDrawFit', help = "No drawing of fitness", default=False, action="store_true")
	parser.add_argument('-u', '--drawRun', help = "Drawing of each run pareto frontier", default=False, action="store_true")

	parser.add_argument('-g', '--firstGen', help = "Size of population of first generation", default=10, type=int)
	parser.add_argument('-E', '--EvalByGen', help = "Number of evaluations by generation", default=20, type=int)

	parser.add_argument('-s', '--selection', help = "Selected runs", default=None, type=int, nargs='+')
	parser.add_argument('-e', '--exclusion', help = "Excluded runs", default=None, type=int, nargs='+')
	args = parser.parse_args()

	main(args)

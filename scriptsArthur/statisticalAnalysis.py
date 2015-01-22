#!/usr/bin/env python

from scipy import stats

import os
import argparse
import re
import numpy as np



def main(args) :
	maxEval = args.max
	selection = args.selection
	exclusion = args.exclusion

	serie1 = []
	if os.path.isdir(args.directory1) :
		listAllFit = [f for f in os.listdir(args.directory1) if (os.path.isfile(args.directory1 + "/" + f) and re.match(r"^allfitevalstat(\d*)\.dat$", f))]

		hashRatioCoop = {}
		hashRatio = {}
		hashRatioHares = {}

		for fileAll in listAllFit :
			m = re.search(r'^allfitevalstat(\d*)\.dat$', fileAll)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				hashRatioCoop[run] = {}
				hashRatio[run] = {}
				hashRatioHares[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(args.directory1 + "/" + fileAll, delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

				lastEval = None
				firstEval = True
				evalOffset = 0

				tabRatioCoop = []
				tabRatio = []
				tabRatioHares = []
				for line in data :
					evaluation = line['evaluation']

					if firstEval :
						if evaluation == 10 :
							evalOffset = 10
						firstEval = False

					evaluation += evalOffset

					if evaluation % 5000 == 0 :
						if lastEval == None :
							lastEval = evaluation

						if lastEval != evaluation :
							hashRatioCoop[run][lastEval] = np.mean(tabRatioCoop)
							hashRatio[run][lastEval] = np.mean(tabRatio)
							hashRatioHares[run][lastEval] = np.mean(tabRatioHares)
							lastEval = evaluation
							tabRatioCoop = []
							tabRatio = []
							tabRatioHares = []

						if evaluation < maxEval :
							tabRatioCoop.append((line['nbBStags'] - line['nbBStagsSolo'])*100/line['nbBStags'] if line['nbBStags'] > 0.0 else 0)

							tabRatio.append(line['nbBStags']*100/(line['nbHares'] + line['nbBStags']))
							tabRatioHares.append(line['nbHares']*100/(line['nbHares'] + line['nbBStags']))


				if len(tabRatioCoop) > 0 and lastEval <= maxEval :
							hashRatioCoop[run][lastEval] = np.mean(tabRatioCoop)
							hashRatio[run][lastEval] = np.mean(tabRatio)
							hashRatioHares[run][lastEval] = np.mean(tabRatioHares)

		minEval = None
		for run in hashRatioCoop.keys() :
			lastEval = 0
			for evaluation in hashRatioCoop[run].keys() :
				if evaluation > lastEval :
					lastEval = evaluation

			if minEval == None or lastEval < minEval :
				minEval = lastEval

		print(minEval)
		if args.coop :
			serie1 = [hashRatioCoop[run][minEval] for run in hashRatioCoop.keys()] 
		else :
			serie1 = [hashRatioHares[run][minEval] for run in hashRatioHares.keys()] 
		print(serie1)


	serie2 = []
	if os.path.isdir(args.directory2) :
		listAllFit = [f for f in os.listdir(args.directory2) if (os.path.isfile(args.directory2 + "/" + f) and re.match(r"^allfitevalstat(\d*)\.dat$", f))]

		hashRatioCoop = {}
		hashRatio = {}
		hashRatioHares = {}

		for fileAll in listAllFit :
			m = re.search(r'^allfitevalstat(\d*)\.dat$', fileAll)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				hashRatioCoop[run] = {}
				hashRatio[run] = {}
				hashRatioHares[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(args.directory2 + "/" + fileAll, delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

				lastEval = None
				firstEval = True
				evalOffset = 0

				tabRatioCoop = []
				tabRatio = []
				tabRatioHares = []
				for line in data :
					evaluation = line['evaluation']

					if firstEval :
						if evaluation == 10 :
							evalOffset = 10
						firstEval = False

					evaluation += evalOffset

					if evaluation % 5000 == 0 :
						if lastEval == None :
							lastEval = evaluation

						if lastEval != evaluation :
							hashRatioCoop[run][lastEval] = np.mean(tabRatioCoop)
							hashRatio[run][lastEval] = np.mean(tabRatio)
							hashRatioHares[run][lastEval] = np.mean(tabRatioHares)
							lastEval = evaluation
							tabRatioCoop = []
							tabRatio = []
							tabRatioHares = []

						if evaluation < maxEval :
							tabRatioCoop.append((line['nbBStags'] - line['nbBStagsSolo'])*100/line['nbBStags'] if line['nbBStags'] > 0.0 else 0)

							tabRatio.append(line['nbBStags']*100/(line['nbHares'] + line['nbBStags']))
							tabRatioHares.append(line['nbHares']*100/(line['nbHares'] + line['nbBStags']))


				if len(tabRatioCoop) > 0 and lastEval <= maxEval :
							hashRatioCoop[run][lastEval] = np.mean(tabRatioCoop)
							hashRatio[run][lastEval] = np.mean(tabRatio)
							hashRatioHares[run][lastEval] = np.mean(tabRatioHares)


		minEval = None
		for run in hashRatioCoop.keys() :
			lastEval = 0
			for evaluation in hashRatioCoop[run].keys() :
				if evaluation > lastEval :
					lastEval = evaluation

			if minEval == None or lastEval < minEval :
				minEval = lastEval

		print(minEval)
		if args.coop :
			serie2 = [hashRatioCoop[run][minEval] for run in hashRatioCoop.keys()] 
		else :
			serie2 = [hashRatioHares[run][minEval] for run in hashRatioHares.keys()] 
		print(serie2)

	u, p = stats.mannwhitneyu(serie1, serie2)
	print("U = " + str(u) + "/P = " + str(p))


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory1', help = "Directory of the first population")
	parser.add_argument('directory2', help = "Directory of the second population")

	parser.add_argument('-c', '--coop', help = "Compute the statistical test on proportion of cooperation", default = False, action = "store_true")

	parser.add_argument('-m', '--max', help = "Max evaluation", default='20000')

	parser.add_argument('-s', '--selection', help = "Selected runs", default=None, type=int, nargs='+')
	parser.add_argument('-e', '--exclusion', help = "Excluded runs", default=None, type=int, nargs='+')

	args = parser.parse_args()

	main(args)
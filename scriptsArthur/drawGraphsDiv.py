#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import lines
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from operator import itemgetter
import matplotlib.cm as cm
import seaborn as sns
import numpy as np
import argparse
import re
import os
import math

import makeData
import Tools

colorHaresSolo = 'lime'
colorHaresDuo = 'green'
colorErrorHares = 'black'
alphaHares = 1
colorBStagsSolo = 'magenta'
colorBStagsDuo = 'purple'
colorErrorBStags = 'black'
alphaBStags = 1
colorSStagsSolo = 'cyan'
colorSStagsDuo = 'steelblue'
colorErrorSStags = 'black'
alphaSStags = 1
colorTotal = 'grey'
colorErrorTotal = 'black'
alphaTotal = 1


maxEval = None
maxGen = None
nbEvalByGen = 20
nbPopFirstGen = 20
precision = 100

drawDiversity = False
drawSimilarity = False


def drawBestFit(dossier) :
	if os.path.isdir(dossier) :
		listBestFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^bestfit(\D+)(\d+)\.dat$", f))]

		hashFitness = {}
		hashNbHaresDuo = {}
		hashNbHaresSolo = {}
		hashNbHares = {}
		hashNbBStagsDuo = {}
		hashNbBStagsSolo = {}
		hashNbBStags = {}

		tabEvaluation = []
		for fileBest in listBestFit :
			m = re.search(r"^bestfit(\D+)(\d+)\.dat$", fileBest)
			if m :
				exp = m.group(1)
				run = int(m.group(2))

				hashFitness[exp] = {}
				hashNbHaresDuo[exp] = {}
				hashNbHaresSolo[exp] = {}
				hashNbHares[exp] = {}
				hashNbBStagsDuo[exp] = {}
				hashNbBStagsSolo[exp] = {}
				hashNbBStags[exp] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbHares', 'nbHaresSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3, 6, 7), dtype = dtypes)

				cpt = 0
				firstEval = True
				lastEval = 0
				for line in data :
					evaluation = line['evaluation']

					cpt += evaluation - lastEval
					lastEval = evaluation

					if cpt%precision == 0 or firstEval :
						if evaluation < maxEval :
							if evaluation not in hashFitness[exp].keys() :
								hashFitness[exp][evaluation] = []
								hashNbHaresDuo[exp][evaluation] = []
								hashNbHaresSolo[exp][evaluation] = []
								hashNbHares[exp][evaluation] = []
								hashNbBStagsDuo[exp][evaluation] = []
								hashNbBStagsSolo[exp][evaluation] = []
								hashNbBStags[exp][evaluation] = []

							hashFitness[exp][evaluation].append(line['fitness'])

							hashNbHares[exp][evaluation].append(line['nbHares'])
							hashNbHaresSolo[exp][evaluation].append(line['nbHaresSolo'])
							hashNbHaresDuo[exp][evaluation].append(line['nbHares'] - line['nbHaresSolo'])

							hashNbBStags[exp][evaluation].append(line['nbBStags'])
							hashNbBStagsSolo[exp][evaluation].append(line['nbBStagsSolo'])
							hashNbBStagsDuo[exp][evaluation].append(line['nbBStags'] - line['nbBStagsSolo'])

							if evaluation not in tabEvaluation :
								tabEvaluation.append(evaluation)

					if firstEval :
						firstEval = False

		tabEvaluation = sorted(tabEvaluation)
		lastEval = tabEvaluation[-1]
		diffEvals = lastEval - tabEvaluation[-2]

		while lastEval <= maxEval :
			lastEval += diffEvals
			tabEvaluation.append(lastEval)


		tabGeneration = [int(math.floor((evaluation-nbPopFirstGen)/nbEvalByGen)) for evaluation in tabEvaluation]

		# SEABORN
		sns.set()
		sns.set_style('white')
		sns.set_context('paper')
		palette = sns.color_palette("husl", len(hashNbBStags.keys()))

		matplotlib.rcParams['axes.labelsize'] = 12
		matplotlib.rcParams['xtick.labelsize'] = 12
		matplotlib.rcParams['ytick.labelsize'] = 12
		matplotlib.rcParams['legend.fontsize'] = 12

		dpi = 96
		size = (1280/dpi, 1024/dpi)

		tabPlotEvaluation = tabEvaluation


		# BAR GRAPHS RATIO
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		width = 0.5

		tabPlotExp = [exp for exp in hashFitness.keys()]

		tabNbHares = [np.mean(hashNbHares[exp][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbHares[exp].keys() else sorted(hashNbHares[exp].keys())[-1]]) for exp in tabPlotExp]
		tabNbHaresStd = [np.std(hashNbHares[exp][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbHares[exp].keys() else sorted(hashNbHares[exp].keys())[-1]]) for exp in tabPlotExp]
		tabNbBStags = [np.mean(hashNbBStags[exp][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStags[exp].keys() else sorted(hashNbBStags[exp].keys())[-1]]) for exp in tabPlotExp]
		tabNbBStagsStd = [np.std(hashNbBStags[exp][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStags[exp].keys() else sorted(hashNbBStags[exp].keys())[-1]]) for exp in tabPlotExp]

		barNbHares = axe1.bar(range(len(tabNbHares)), tabNbHares, width = width, color = 'lime', alpha = 0.5, yerr = tabNbHaresStd, ecolor = 'black')
		barNbBStags = axe1.bar(range(len(tabNbBStags)), tabNbBStags, bottom = tabNbHares, width = width, color = 'magenta', alpha = 0.5, yerr = tabNbBStagsStd, ecolor = 'black')

		axe1.set_xticks(np.add(np.arange(len(tabPlotExp)), width/2))
		axe1.set_xticklabels(tabPlotExp)

		axe1.set_xlim(0, len(tabNbBStags))

		axe1.set_xlabel('Experiment')

		axe1.set_ylabel('Number of preys hunted')
		axe1.set_ylim(0)

		plt.legend([barNbHares, barNbBStags], ['Hares', 'Stags'], frameon = True)

		plt.savefig(dossier + "/figureBarsNbPreys.png", bbox_inches = 'tight')



# Courtesy of http://oco-carbon.com/metrics/find-pareto-frontiers-in-python/
def pareto_frontier(Xs, Ys, maxX = True, maxY = True) :
	# Sort the list in either ascending or descending order of X
	myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse = maxX)

	# Start the Pareto frontier with the first value in the sorted list
	p_front = [myList[0]]    

	# Loop through the sorted list
	for pair in myList[1:]:
		if maxY :
			if pair[1] >= p_front[-1][1] :
				p_front.append(pair)
		else :
			if pair[1] <= p_front[-1][1] :
				p_front.append(pair)

	# Turn resulting pairs back into a list of Xs and Ys
	p_frontX = [pair[0] for pair in p_front]
	p_frontY = [pair[1] for pair in p_front]

	return p_frontX, p_frontY



# Courtesy of http://oco-carbon.com/metrics/find-pareto-frontiers-in-python/
def pareto_frontier_indiv(listIndiv, maxX = True, maxY = True) :
	# Sort the list in either ascending or descending order of X
	myList = sorted([[listIndiv[i][0], listIndiv[i][1], i] for i in range(len(listIndiv))], reverse = maxX)

	# Start the Pareto frontier with the first value in the sorted list
	p_front = [myList[0]]    

	# Loop through the sorted list
	for triple in myList[1:]:
		if maxY :
			if triple[1] >= p_front[-1][1] :
				p_front.append(triple)
		else :
			if triple[1] <= p_front[-1][1] :
				p_front.append(triple)

	# Turn resulting triples back into a list of individuals
	p_frontIndiv = [listIndiv[triple[2]] for triple in p_front]

	return p_frontIndiv


def drawPareto(dossier) :
	if os.path.isdir(dossier) :
		listAllDiv = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^alldivevalstat(\d+)\.dat$", f))]
		listAllFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^allfitevalstat(\d+)\.dat$", f))]
		listAllSim = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^allsimevalstat(\d+)\.dat$", f))]

		hashDiversity = {}
		hashFitness = {}
		hashSimilarity = {}

		hashNbHaresDuo = {}
		hashNbHaresSolo = {}
		hashNbHares = {}

		hashNbBStagsDuo = {}
		hashNbBStagsSolo = {}
		hashNbBStags = {}

		hashRatio = {}
		hashRatioHares = {}
		hashRatioCoop = {}

		tabEvaluation = []
		maxFitness = 0
		maxDiversity = 0
		maxSimilarity = 0

		drawDiversity = False
		drawSimilarity = False
		for fileAll in listAllFit :
			m = re.search(r'^allfitevalstat(\d+)\.dat$', fileAll)

			run = int(m.group(1))

			if run not in hashFitness.keys() :
				hashDiversity[run] = {}
				hashFitness[run] = {}
				hashSimilarity[run] = {}

				hashNbHaresDuo[run] = {}
				hashNbHaresSolo[run] = {}
				hashNbHares[run] = {}

				hashNbBStagsDuo[run] = {}
				hashNbBStagsSolo[run] = {}
				hashNbBStags[run] = {}

				hashRatio[run] = {}
				hashRatioHares[run] = {}
				hashRatioCoop[run] = {}


			dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
			data = np.loadtxt(dossier + "/" + fileAll, delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

			evalDone = []
			cpt = 0
			lastEval = None
			for line in data :
				evaluation = line['evaluation']

				if lastEval == None :
					lastEval = evaluation

				if evaluation != lastEval :
					cpt += evaluation - lastEval
					lastEval = evaluation

				if cpt%precision == 0 :
					if evaluation < maxEval :
						if evaluation not in evalDone :
							hashDiversity[run][evaluation] = []
							hashFitness[run][evaluation] = []
							hashSimilarity[run][evaluation] = []

							hashNbHaresDuo[run][evaluation] = []
							hashNbHaresSolo[run][evaluation] = []
							hashNbHares[run][evaluation] = []

							hashNbBStagsDuo[run][evaluation] = []
							hashNbBStagsSolo[run][evaluation] = []
							hashNbBStags[run][evaluation] = []

							hashRatio[run][evaluation] = []
							hashRatioHares[run][evaluation] = []
							hashRatioCoop[run][evaluation] = []

							evalDone.append(evaluation)

						hashFitness[run][evaluation].append(line['fitness'])

						hashNbHares[run][evaluation].append(line['nbHares'])
						hashNbHaresSolo[run][evaluation].append(line['nbHaresSolo'])
						hashNbHaresDuo[run][evaluation].append(line['nbHares'] - line['nbHaresSolo'])

						hashNbBStags[run][evaluation].append(line['nbBStags'])
						hashNbBStagsSolo[run][evaluation].append(line['nbBStagsSolo'])
						hashNbBStagsDuo[run][evaluation].append(line['nbBStags'] - line['nbBStagsSolo'])

						hashRatio[run][evaluation].append(line['nbBStags']*100/(line['nbHares'] + line['nbBStags']))
						hashRatioHares[run][evaluation].append(line['nbHares']*100/(line['nbHares'] + line['nbBStags']))
						hashRatioCoop[run][evaluation].append((line['nbHares'] - line['nbHaresSolo'] + (line['nbBStags'] - line['nbBStagsSolo']))*100/((line['nbHares'] + line['nbBStags'])))

						if evaluation not in tabEvaluation :
							tabEvaluation.append(evaluation)

						if line['fitness'] > maxFitness :
							maxFitness = line['fitness']


		for fileAll in listAllDiv :
			m = re.search(r'^alldivevalstat(\d+)\.dat$', fileAll)

			run = int(m.group(1))

			drawDiversity = True

			dtypes = np.dtype({ 'names' : ('evaluation', 'diversity', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
			data = np.loadtxt(dossier + "/" + fileAll, delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

			cpt = 0
			lastEval = None
			for line in data :
				evaluation = line['evaluation']

				if lastEval == None :
					lastEval = evaluation

				if evaluation != lastEval :
					cpt += evaluation - lastEval
					lastEval = evaluation

				if cpt%precision == 0 and evaluation in hashDiversity[run].keys() :
					if evaluation < maxEval :
						hashDiversity[run][evaluation].append(line['diversity'])

						if evaluation not in tabEvaluation :
							tabEvaluation.append(evaluation)

						if line['diversity'] > maxDiversity :
							maxDiversity = line['diversity']


		for fileAll in listAllSim :
			m = re.search(r'^allsimevalstat(\d+)\.dat$', fileAll)

			drawSimilarity = True

			run = int(m.group(1))


			dtypes = np.dtype({ 'names' : ('evaluation', 'similarity', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
			data = np.loadtxt(dossier + "/" + fileAll, delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

			cpt = 0
			lastEval = None
			for line in data :
				evaluation = line['evaluation']

				if lastEval == None :
					lastEval = evaluation

				if evaluation != lastEval :
					cpt += evaluation - lastEval
					lastEval = evaluation

				if cpt%precision == 0 and evaluation in hashDiversity[run].keys() :
					if evaluation < maxEval :
						hashSimilarity[run][evaluation].append(line['similarity'])

						if evaluation not in tabEvaluation :
							tabEvaluation.append(evaluation)

						if line['similarity'] > maxFitness :
							maxSimilarity = line['similarity']


		tabEvaluation = sorted(tabEvaluation)
		lastEval = tabEvaluation[-1]
		diffEvals = lastEval - tabEvaluation[-2]

		while lastEval <= maxEval :
			lastEval += diffEvals
			tabEvaluation.append(lastEval)


		tabGeneration = [int(math.floor((evaluation-nbPopFirstGen)/nbEvalByGen)) for evaluation in tabEvaluation]


		# SEABORN
		sns.set()
		sns.set_style('white')
		sns.set_context('paper')

		dpi = 96

		tabPlotEvaluation = tabEvaluation


		# Pareto Frontier
		paretoEvals = tabEvaluation[0:-1:10]

		for eval in paretoEvals :
				if drawDiversity :
					listIndivFrontier = []
					doEval = True
					for run in hashFitness.keys() :
						if eval not in hashFitness[run].keys() :
							doEval = False
							break

						assert(len(hashFitness[run][eval]) == len(hashDiversity[run][eval]))

						listIndiv = [(hashFitness[run][eval][cpt], hashDiversity[run][eval][cpt], hashRatio[run][eval][cpt], hashRatioCoop[run][eval][cpt]) for cpt in range(0, len(hashFitness[run][eval]))]
						p_front = pareto_frontier_indiv(listIndiv, maxX= True, maxY = True)

						listIndivFrontier += p_front

					if not doEval :
						continue

					listFitness = []
					listDiversity = []
					listRatio = []
					listRatioCoop = []
					for indiv in listIndivFrontier :
						listFitness.append(indiv[0])
						listDiversity.append(indiv[1])
						listRatio.append(indiv[2])
						listRatioCoop.append(indiv[3])

					listColors = [0 if math.isnan(ratio) else int(ratio) for ratio in listRatio]
					listSizes = [50 if math.isnan(ratio) else 50 + int(ratio*2) for ratio in listRatioCoop]

					p_front = pareto_frontier(listFitness, listDiversity, maxX = True, maxY = True)

					fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
					axe1.scatter(listFitness, listDiversity, c = listColors, cmap = cm.rainbow, s = listSizes)
					axe1.plot(p_front[0], p_front[1])

					axe1.set_xlabel("Fitness")
					axe1.set_xlim(0, maxFitness + 0.1*maxFitness)

					if not drawSimilarity :
						axe1.set_ylabel("Similarity")
					else :
						axe1.set_ylabel("Diversity")

					axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

					axe1.set_title('Pareto frontier evaluation ' + str(eval))

					if not drawSimilarity :
						plt.savefig("./paretoEval" + str(eval) + "FitSim.png", bbox_inches = 'tight')
					else :
						plt.savefig("./paretoEval" + str(eval) + "FitDiv.png", bbox_inches = 'tight')

					plt.close()


				if drawSimilarity :
						listIndivFrontier = []
						doEval = True
						for run in hashFitness.keys() :
							if eval not in hashFitness[run].keys() :
								doEval = False
								break

							assert(len(hashFitness[run][eval]) == len(hashSimilarity[run][eval]))

							listIndiv = [(hashFitness[run][eval][cpt], hashSimilarity[run][eval][cpt], hashRatio[run][eval][cpt], hashRatioCoop[run][eval][cpt]) for cpt in range(0, len(hashFitness[run][eval]))]
							p_front = pareto_frontier_indiv(listIndiv, maxX= True, maxY = True)

							listIndivFrontier += p_front

						if not doEval :
							continue

						listFitness = []
						listSimilarity = []
						listRatio = []
						listRatioCoop = []
						for indiv in listIndivFrontier :
							listFitness.append(indiv[0])
							listSimilarity.append(indiv[1])
							listRatio.append(indiv[2])
							listRatioCoop.append(indiv[3])

						listColors = [0 if math.isnan(ratio) else int(ratio) for ratio in listRatio]
						listSizes = [50 if math.isnan(ratio) else 50 + int(ratio*2) for ratio in listRatioCoop]

						p_front = pareto_frontier(listFitness, listSimilarity, maxX = True, maxY = True)

						fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
						axe1.scatter(listFitness, listSimilarity, c = listColors, cmap = cm.rainbow, s = listSizes)
						axe1.plot(p_front[0], p_front[1])

						axe1.set_xlabel("Fitness")
						axe1.set_xlim(0, maxFitness + 0.1*maxFitness)

						axe1.set_ylabel("Similarity")
						axe1.set_ylim(0, maxSimilarity + 0.1*maxSimilarity)

						axe1.set_title('Pareto frontier evaluation ' + str(eval))

						plt.savefig("./paretoEval" + str(eval) + "FitSim.png", bbox_inches = 'tight')

						plt.close()


						if drawDiversity :
							listIndivFrontier = []
							doEval = True
							for run in hashDiversity.keys() :
								if eval not in hashDiversity[run].keys() :
									doEval = False
									break

								assert(len(hashSimilarity[run][eval]) == len(hashDiversity[run][eval]))

								listIndiv = [(hashSimilarity[run][eval][cpt], hashDiversity[run][eval][cpt], hashRatio[run][eval][cpt], hashRatioCoop[run][eval][cpt]) for cpt in range(0, len(hashSimilarity[run][eval]))]
								p_front = pareto_frontier_indiv(listIndiv, maxX= True, maxY = True)

								listIndivFrontier += p_front

							if not doEval :
								continue

							listSimilarity = []
							listDiversity = []
							listRatio = []
							listRatioCoop = []
							for indiv in listIndivFrontier :
								listSimilarity.append(indiv[0])
								listDiversity.append(indiv[1])
								listRatio.append(indiv[2])
								listRatioCoop.append(indiv[3])

							listColors = [0 if math.isnan(ratio) else int(ratio) for ratio in listRatio]
							listSizes = [50 if math.isnan(ratio) else 50 + int(ratio*2) for ratio in listRatioCoop]

							p_front = pareto_frontier(listSimilarity, listDiversity, maxX = True, maxY = True)

							fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
							axe1.scatter(listSimilarity, listDiversity, c = listColors, cmap = cm.rainbow, s = listSizes)
							axe1.plot(p_front[0], p_front[1])

							axe1.set_xlabel("Similarity")
							axe1.set_xlim(0, maxFitness + 0.1*maxFitness)

							axe1.set_ylabel("Diversity")
							axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

							axe1.set_title('Pareto frontier evaluation ' + str(eval))

							plt.savefig("./paretoEval" + str(eval) + "DivSim.png", bbox_inches = 'tight')

							plt.close()




def draw(**parametres) : 
	global maxEval
	maxEval = parametres["argMax"]

	global maxGen
	maxGen = parametres["argMaxGen"]

	global precision 
	precision = parametres["argPrecision"]

	global nbPopFirstGen
	nbPopFirstGen = parametres["argFirstGen"]

	global nbEvalByGen
	nbEvalByGen = parametres["argEvalByGen"]

	dossier = parametres["argDirectory"]


	if os.path.isdir(dossier) :
		listSubDirs = [d for d in os.listdir(dossier) if os.path.isdir(dossier + '/' + d)]

		print('Directory : ' + dossier)
		for curDir in listSubDirs :
			if re.match(r'^BestFit$', curDir) and parametres["argType"] == "BestFit" :
				print('\t -> Drawing bestfit directory : ' + curDir)
				drawBestFit(dossier + '/' + curDir)
			elif re.match(r'^AllFit$', curDir) and parametres["argType"] == "AllFit" :
				print('\t -> Drawing allfit directory : ' + curDir)
				# drawAllFit(dossier + '/' + curDir)
			elif re.match(r'^ParetoFront$', curDir) and parametres["argType"] == "Pareto" :
				print('\t -> Drawing pareto front : ' + curDir)
				drawPareto(dossier + '/' + curDir)


def main(args) :
	parametres =  { 
									"argMax" : int(arg.max),
									"argMaxGen" : int(arg.maxGen),
									"argPrecision" : int(args.precision),
									"argFirstGen" : args.firstGen,
									"argEvalByGen" : args.EvalByGen,
									"argDirectory" : args.directory,
									"argType" : args.type
								}
	draw(**parametres)



if __name__ == '__main__' :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('-m', '--max', help = "Max evaluation", default='20000')
	parser.add_argument('-M', '--maxGen', help = "Max generation", default='1000')
	parser.add_argument('-p', '--precision', help = "Precision", default='100')

	parser.add_argument('-t', '--type', help = "Type of data", type=str, default="BestFit")

	parser.add_argument('-g', '--firstGen', help = "Size of population of first generation", default=10, type=int)
	parser.add_argument('-E', '--EvalByGen', help = "Number of evaluations by generation", default=20, type=int)
	args = parser.parse_args()

	main(args)
#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import lines
import matplotlib.cm as cm
from matplotlib import animation
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
nbEvalByGen = 20
nbPopFirstGen = 20
selection = None
exclusion = None
precision = 10

argsAnimation = {}

def drawBestFit(dossier) :
	if os.path.isdir(dossier) :
		listBestFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^bestfit(\d*)\.dat$", f))]

		hashFitness = {}

		tabEvaluation = []
		maxFitness = 0
		for fileBest in listBestFit :
			m = re.search(r'^bestfit(\d*)\.dat$', fileBest)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				hashFitness[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness'), 'formats' : [np.int, np.float] })
				data = np.loadtxt(dossier + "/" + fileBest, delimiter=',', usecols = (0, 1), dtype = dtypes)

				cpt = 0
				firstEval = True
				lastEval = 0
				for line in data :
					evaluation = line['evaluation']

					cpt += evaluation - lastEval
					lastEval = evaluation

					if cpt > precision or firstEval :
						if evaluation < maxEval :
							hashFitness[run][evaluation] = line['fitness']

							if evaluation not in tabEvaluation :
								tabEvaluation.append(evaluation)

							if line['fitness'] > maxFitness :
								maxFitness = line['fitness']

							cpt = 0

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
		palette = sns.color_palette("husl", len(hashFitness.keys()))

		matplotlib.rcParams['font.size'] = 15
		matplotlib.rcParams['font.weight'] = 'bold'
		matplotlib.rcParams['axes.labelsize'] = 15
		matplotlib.rcParams['axes.labelweight'] = 'bold'
		matplotlib.rcParams['xtick.labelsize'] = 15
		matplotlib.rcParams['ytick.labelsize'] = 15
		matplotlib.rcParams['legend.fontsize'] = 15

		dpi = 96
		size = (800/dpi, 600/dpi)
		tabPlotEvaluation = tabEvaluation

		# --- BOXPLOT FITNESS ---
		dataBoxPlot = []
		for evaluation in tabPlotEvaluation :
			listFitness = [hashFitness[run][evaluation] for run in hashFitness.keys() if evaluation in hashFitness[run].keys()]

			if len(listFitness) > 0 :
				dataBoxPlot.append(listFitness)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
		axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
		axe1.set_xlabel("Evaluation")

		axe1.set_ylabel("Fitness")
		axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

		axe1.set_title('Boxplot of best fitness')

		plt.savefig(dossier + "/boxplot.png", bbox_inches = 'tight')
		plt.close()



		# --- RUNS FITNESS ---
		palette = sns.color_palette("husl", len(hashFitness.keys()))
		for run in hashFitness.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))

			tabFitness = [hashFitness[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashFitness[run].keys()]

			axe1.plot(range(len(tabFitness)), tabFitness)

			# Divide the x axis by 10
			tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]

			axe1.set_xticks(tabEvaluationTicks)
			axe1.set_xticklabels([tabPlotEvaluation[indice] for indice in tabEvaluationTicks])
			axe1.set_xlabel('Evaluation')

			axe1.set_ylabel('Fitness')
			axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

			axe1.set_title('Best fitness', fontsize = 10)

			plt.savefig(dossier + "/fitnessRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


def drawAllFit(dossier) :
	if os.path.isdir(dossier) :
		listAllFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^allfitevalstat(\d*)\.dat$", f))]

		hashFitness = {}

		tabEvaluation = []
		hashFitnessGlob = {}
		maxFitness = 0
		for fileAll in listAllFit :
			m = re.search(r'^allfitevalstat(\d*)\.dat$', fileAll)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				hashFitness[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness'), 'formats' : [np.int, np.float] })
				data = np.loadtxt(dossier + "/" + fileAll, delimiter=',', skiprows = 1, usecols = (0, 1), dtype = dtypes)

				evalDone = []
				cpt = 0
				lastEval = None
				for line in data :
					evaluation = line['evaluation']

					if lastEval == None :
						lastEval = evaluation

					if evaluation != lastEval :
						if cpt > precision :
							cpt = 0

						cpt += evaluation - lastEval
						lastEval = evaluation

					if cpt > precision :
						if evaluation < maxEval :
							if evaluation not in evalDone :
								hashFitness[run][evaluation] = []

								hashFitnessGlob[evaluation] = []

								evalDone.append(evaluation)

							hashFitness[run][evaluation].append(line['fitness'])

							hashFitnessGlob[evaluation].append(line['fitness'])

							if evaluation not in tabEvaluation :
								tabEvaluation.append(evaluation)

							if line['fitness'] > maxFitness :
								maxFitness = line['fitness']


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
		palette = sns.color_palette("husl", len(hashFitness.keys()))

		matplotlib.rcParams['font.size'] = 15
		matplotlib.rcParams['font.weight'] = 'bold'
		matplotlib.rcParams['axes.labelsize'] = 15
		matplotlib.rcParams['axes.labelweight'] = 'bold'
		matplotlib.rcParams['xtick.labelsize'] = 15
		matplotlib.rcParams['ytick.labelsize'] = 15
		matplotlib.rcParams['legend.fontsize'] = 15

		dpi = 96
		size = (800/dpi, 600/dpi)
		tabPlotEvaluation = tabEvaluation


		# --- BOXPLOT RUN FITNESS ---
		dataBoxPlot = []
		for run in hashFitness.keys() :
			dataBoxPlot = [hashFitness[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashFitness[run].keys()]

			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
			axe1.boxplot(dataBoxPlot)

			axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
			axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
			axe1.set_xlabel("Evaluation")

			axe1.set_ylabel("Fitness")
			axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

			axe1.set_title('Boxplot of population fitness')

			plt.savefig(dossier + "/fitnessRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BOXPLOT ALL RUN FITNESS ---
		dataBoxPlot = [hashFitnessGlob[evaluation] for evaluation in tabPlotEvaluation if evaluation in hashFitnessGlob.keys()]

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
		axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
		axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
		axe1.set_xlabel("Evaluation")

		axe1.set_ylabel("Fitness")
		axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

		axe1.set_title('Boxplot of all fitness')

		plt.savefig(dossier + "/globalFitness", bbox_inches = 'tight')
		plt.close()



def drawBestLeadership(dossier) :
	if os.path.isdir(dossier) :
		listBestLeadership = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^bestleadership(\d*)\.dat$", f))]

		hashProportion = {}
		hashNbLeaderFirst = {}
		hashNbTotalCoop = {}

		tabEvaluation = []
		for fileBest in listBestLeadership :
			m = re.search(r'^bestleadership(\d*)\.dat$', fileBest)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				hashProportion[run] = {}
				hashNbLeaderFirst[run] = {}
				hashNbTotalCoop[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'proportion', 'nb_leader_first', 'nb_total_coop'), 'formats' : [np.int, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3, 4), dtype = dtypes)

				cpt = 0
				firstEval = True
				lastEval = 0
				for line in data :
					evaluation = line['evaluation']

					cpt += evaluation - lastEval
					lastEval = evaluation

					if cpt > precision or firstEval :
						if evaluation < maxEval :
							hashProportion[run][evaluation] = line['proportion'] - 0.5
							hashNbLeaderFirst[run][evaluation] = line['nb_leader_first']
							hashNbTotalCoop[run][evaluation] = line['nb_total_coop']

							if evaluation not in tabEvaluation :
								tabEvaluation.append(evaluation)

							cpt = 0

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
		palette = sns.color_palette("husl", len(hashProportion.keys()))

		matplotlib.rcParams['font.size'] = 15
		matplotlib.rcParams['font.weight'] = 'bold'
		matplotlib.rcParams['axes.labelsize'] = 15
		matplotlib.rcParams['axes.labelweight'] = 'bold'
		matplotlib.rcParams['xtick.labelsize'] = 15
		matplotlib.rcParams['ytick.labelsize'] = 15
		matplotlib.rcParams['legend.fontsize'] = 15

		dpi = 96
		size = (800/dpi, 600/dpi)

		tabPlotEvaluation = tabEvaluation

		# --- BOXPLOT FITNESS ---
		dataBoxPlot = []
		for evaluation in tabPlotEvaluation :
			listProportion = [hashProportion[run][evaluation] for run in hashProportion.keys() if evaluation in hashProportion[run].keys()]

			if len(listProportion) > 0 :
				dataBoxPlot.append(listProportion)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
		axe1.boxplot(dataBoxPlot)

		axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
		axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))

		axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
		axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
		axe1.set_xlabel("Evaluation")

		axe1.set_ylabel("Proportion of leadership")
		axe1.set_ylim(-0.6, 0.6)

		axe1.set_title('Boxplot of best proportion')

		plt.savefig(dossier + "/boxplot.png", bbox_inches = 'tight')
		plt.close()



		# --- RUNS FITNESS ---
		for run in hashProportion.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))

			tabProportion = [hashProportion[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashProportion[run].keys()]

			axe1.plot(range(len(tabProportion)), tabProportion)

			axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
			axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))

			# Divide the x axis by 10
			tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]

			axe1.set_xticks(tabEvaluationTicks)
			axe1.set_xticklabels([tabPlotEvaluation[indice] for indice in tabEvaluationTicks])
			axe1.set_xlabel('Evaluation')

			axe1.set_ylabel("Proportion of leadership")
			axe1.set_ylim(-0.6, 0.6)

			axe1.set_title('Boxplot of best proportion')

			plt.savefig(dossier + "/proportionRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


def drawAllLeadership(dossier) :
	if os.path.isdir(dossier) :
		listAllLeadership = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^allleadershipevalstat(\d*)\.dat$", f))]


		tabEvaluation = []

		hashProportion = {}
		hashProportionGlob = {}
		hashNbLeaderFirst = {}
		hashNbTotalCoop = {}

		maxFitness = 0
		for fileAll in listAllFit :
			m = re.search(r'^allleadershipevalstat(\d*)\.dat$', fileAll)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				hashProportion[run] = {}
				hashNbLeaderFirst[run] = {}
				hashNbTotalCoop[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'proportion', 'nb_leader_first', 'nb_total_coop'), 'formats' : [np.int, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileAll, delimiter=',', usecols = (0, 1, 2, 3, 4), dtype = dtypes)

				evalDone = []
				cpt = 0
				lastEval = None
				for line in data :
					evaluation = line['evaluation']

					if lastEval == None :
						lastEval = evaluation

					if evaluation != lastEval :
						if cpt > precision :
							cpt = 0

						cpt += evaluation - lastEval
						lastEval = evaluation

					if cpt > precision or firstEval :
						if evaluation < maxEval :
							if evaluation not in evalDone :
								hashProportion[run][evaluation] = []
								hashNbLeaderFirst[run][evaluation] = []
								hashNbTotalCoop[run][evaluation] = []

								hashFitnessGlob[evaluation] = []

								evalDone.append(evaluation)

							hashProportion[run][evaluation].append(line['proportion'] - 0.5)
							hashFitnessGlob[evaluation].append(line['proportion'] - 0.5)
							hashNbLeaderFirst[run][evaluation].append(line['nb_leader_first'])
							hashNbTotalCoop[run][evaluation].append(line['nb_total_coop'])

							if evaluation not in tabEvaluation :
								tabEvaluation.append(evaluation)

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
		palette = sns.color_palette("husl", len(hashProportion.keys()))

		matplotlib.rcParams['font.size'] = 15
		matplotlib.rcParams['font.weight'] = 'bold'
		matplotlib.rcParams['axes.labelsize'] = 15
		matplotlib.rcParams['axes.labelweight'] = 'bold'
		matplotlib.rcParams['xtick.labelsize'] = 15
		matplotlib.rcParams['ytick.labelsize'] = 15
		matplotlib.rcParams['legend.fontsize'] = 15

		dpi = 96
		size = (800/dpi, 600/dpi)

		tabPlotEvaluation = tabEvaluation


		# --- BOXPLOT RUN PROPORTION ---
		dataBoxPlot = []
		for run in hashProportion.keys() :
			dataBoxPlot = [hashProportion[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashProportion[run].keys()]

			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
			axe1.boxplot(dataBoxPlot)
	
			axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
			axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))

			axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
			axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
			axe1.set_xlabel("Evaluation")

			axe1.set_ylabel("Proportion of leadership")
			axe1.set_ylim(-0.6, 0.6)

			axe1.set_title('Boxplot of population proportion')

			plt.savefig(dossier + "/proportionRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BOXPLOT ALL RUN PROPORTION ---
		dataBoxPlot = [hashProportionGlob[evaluation] for evaluation in tabPlotEvaluation if evaluation in hashProportionGlob.keys()]

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)
	
		axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
		axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))

		axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
		axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
		axe1.set_xlabel("Evaluation")

		axe1.set_ylabel("Proportion of leadership")
		axe1.set_ylim(-0.6, 0.6)

		axe1.set_title('Boxplot of all proportions')

		plt.savefig(dossier + "/globalProportion", bbox_inches = 'tight')
		plt.close()



def draw(**parametres) : 
	global maxEval
	maxEval = parametres["argMax"]

	global precision 
	precision = parametres["argPrecision"]

	global selection
	selection = parametres["argSelection"]

	global exclusion
	exclusion = parametres["argExclusion"]

	global nbPopFirstGen
	nbPopFirstGen = parametres["argFirstGen"]

	global nbEvalByGen
	nbEvalByGen = parametres["argEvalByGen"]

	dossier = parametres["argDirectory"]


	if os.path.isdir(dossier) :
		listSubDirs = [d for d in os.listdir(dossier) if os.path.isdir(dossier + '/' + d)]

		print('Directory : ' + dossier)
		for curDir in listSubDirs :
			if parametres["argNoDrawFit"] != True :
				if re.match(r'^BestFit$', curDir) and parametres["argAll"] != True :
					print('\t -> Drawing bestfit directory : ' + curDir)
					drawBestFit(dossier + '/' + curDir)
				elif re.match(r'^AllFit$', curDir) and parametres["argBest"] != True :
					print('\t -> Drawing allfit directory : ' + curDir)
					drawAllFit(dossier + '/' + curDir)

			if parametres["argLeadership"] == True :
				if re.match(r'^BestLeadership$', curDir) and parametres["argAll"] != True :
					print('\t -> Drawing bestleadership directory : ' + curDir)
					drawBestLeadership(dossier + '/' + curDir)
				elif re.match(r'^AllLeadership$', curDir) and parametres["argBest"] != True :
					print('\t -> Drawing allleadership directory : ' + curDir)
					drawAllLeadership(dossier + '/' + curDir)

def main(args) :
	parametres =  { 
									"argMax" : int(arg.max),
									"argPrecision" : int(args.precision),
									"argSelection" : args.selection,
									"argExclusion" : argExclusion,
									"argFirstGen" : args.firstGen,
									"argEvalByGen" : args.EvalByGen,
									"argDirectory" : args.directory,
									"argBest" : args.best,
									"argAll" : args.all,
									"argNoDrawFit" : args.noDrawFit,
									"argDiversity" : args.diversity,
									"argLeadership" : args.leadership,
									"argDrawRun" : args.drawRun
								}
	draw(**parametres)



if __name__ == '__main__' :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('-m', '--max', help = "Max evaluation", default='20000')
	parser.add_argument('-p', '--precision', help = "Precision", default='10')

	parser.add_argument('-b', '--best', help = "Best only", default=False, action="store_true")
	parser.add_argument('-a', '--all', help = "All only", default=False, action="store_true")
	parser.add_argument('-d', '--diversity', help = "Drawing of diversity", default=False, action="store_true")
	parser.add_argument('-l', '--leadership', help = "Drawing of leadership", default=False, action="store_true")
	parser.add_argument('-f', '--noDrawFit', help = "No drawing of the fitness", default=False, action="store_true")
	parser.add_argument('-u', '--drawRun', help = "Drawing of each run pareto frontier", default=False, action="store_true")

	parser.add_argument('-g', '--firstGen', help = "Size of population of first generation", default=10, type=int)
	parser.add_argument('-E', '--EvalByGen', help = "Number of evaluations by generation", default=20, type=int)

	parser.add_argument('-s', '--selection', help = "Selected runs", default=None, type=int, nargs='+')
	parser.add_argument('-e', '--exclusion', help = "Excluded runs", default=None, type=int, nargs='+')
	args = parser.parse_args()

	main(args)
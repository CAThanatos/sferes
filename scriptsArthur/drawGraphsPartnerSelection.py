#!/usr/bin/env python

import matplotlib

# For ssh compatibility
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib import lines
import matplotlib.cm as cm
from matplotlib import animation
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from operator import itemgetter
import seaborn as sns
import numpy as np
import argparse
import re
import os
import math

import makeData
import Tools
#import Drawing

colorCooperate = 'green'
colorErrorCooperate = 'black'
alphaCooperate = 1

colorDefect = 'purple'
colorErrorDefect = 'black'
alphaDefect = 1

maxEval = None
nbEvalByGen = 20
nbPopFirstGen = 20
selection = None
exclusion = None
precision = 10

def drawBestFit(dossier) :
	if os.path.isdir(dossier) :
		listBestFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^bestfit(\d*)\.dat$", f))]

		hashFitness = {}
		hashNbCooperate = {}
		hashNbDefect = {}

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
				hashNbCooperate[run] = {}
				hashNbDefect[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbCooperate', 'nbDefect'), 'formats' : [np.int, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3), dtype = dtypes)

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

							hashNbCooperate[run][evaluation] = line['nbCooperate']
							hashNbDefect[run][evaluation] = line['nbDefect']

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
		palette = sns.color_palette("husl", len(hashNbCooperate.keys()))

		matplotlib.rcParams['font.size'] = 15
		matplotlib.rcParams['font.weight'] = 'bold'
		matplotlib.rcParams['axes.labelsize'] = 15
		matplotlib.rcParams['axes.labelweight'] = 'bold'
		matplotlib.rcParams['xtick.labelsize'] = 15
		matplotlib.rcParams['ytick.labelsize'] = 15
		matplotlib.rcParams['legend.fontsize'] = 15

		dpi = 96
		size = (1280/dpi, 1024/dpi)

		tabPlotEvaluation = tabEvaluation

		# with open(os.path.join(dossier, "lastGenBest.dat"), "w") as fileWrite :
		# 	for run in hashRatioSuccess.keys() :
		# 		evalEnd = sorted(hashRatioSuccess[run].keys())[-1]
		# 		lastValue = hashRatioSuccess[run][evalEnd]

		# 		fileWrite.write(str(evalEnd) + "," + str(lastValue) + "\n")


		# --- BOXPLOT FITNESS ---
		dataBoxPlot = []
		for evaluation in tabPlotEvaluation :
			listFitness = [hashFitness[run][evaluation] for run in hashFitness.keys() if evaluation in hashFitness[run].keys()]

			if len(listFitness) > 0 :
				dataBoxPlot.append(listFitness)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		bp = axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
		axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
		axe1.set_xlabel("Evaluation")

		axe1.set_ylabel("Fitness")
		axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

		axe1.set_title('Boxplot of best fitness')

		for i in range(0, len(bp['boxes'])):
		   bp['boxes'][i].set_color(palette[0])
		   # we have two whiskers!
		   bp['whiskers'][i*2].set_color(palette[0])
		   bp['whiskers'][i*2 + 1].set_color(palette[0])
		   bp['whiskers'][i*2].set_linewidth(2)
		   bp['whiskers'][i*2 + 1].set_linewidth(2)

		   # top and bottom fliers
		   # (set allows us to set many parameters at once)
		   # bp['fliers'][i * 2].set(markerfacecolor=palette[0],
		   #                 marker='o', alpha=0.75, markersize=6,
		   #                 markeredgecolor='none')
		   # bp['fliers'][i * 2 + 1].set(markerfacecolor=palette[0],
		   #                 marker='o', alpha=0.75, markersize=6,
		   #                 markeredgecolor='none')

		   bp['medians'][i].set_color('black')
		   bp['medians'][i].set_linewidth(3)

		   # and 4 caps to remove
		   for c in bp['caps']:
		       c.set_linewidth(0)

		plt.savefig(dossier + "/boxplot.png", bbox_inches = 'tight')
		plt.close()


		# --- RUNS FITNESS ---
		palette = sns.color_palette("husl", len(hashFitness.keys()))
		for run in hashFitness.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			tabFitness = [hashFitness[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashFitness[run].keys()]

			axe1.plot(range(len(tabFitness)), tabFitness)

			# Divide the x axis by 10
			# tabEvaluationTicks = [indice for indice in range(len(tabFitness)) if indice % (int(len(tabFitness)/10)) == 0]
			tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]

			axe1.set_xticks(tabEvaluationTicks)
			axe1.set_xticklabels([tabPlotEvaluation[indice] for indice in tabEvaluationTicks])
			axe1.set_xlabel('Evaluation')

			axe1.set_ylabel('Fitness')
			axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

			axe1.set_title('Best fitness', fontsize = 10)

			plt.savefig(dossier + "/fitnessRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BARS ---
		for run in hashNbCooperate.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			width = 0.8

			tabNbCooperate = [hashNbCooperate[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbCooperate[run].keys()]
			tabNbDefect = [hashNbDefect[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbDefect[run].keys()]

			barNbCooperate = axe1.bar(range(len(tabNbCooperate)), tabNbCooperate, width = width, color = colorCooperate, alpha = alphaCooperate)
			barNbDefect = axe1.bar(range(len(tabNbDefect)), tabNbDefect, bottom = tabNbCooperate, width = width, color = colorDefect, alpha = alphaDefect)

			tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]

			axe1.set_xticks(tabEvaluationTicks)
			axe1.set_xticklabels([tabPlotEvaluation[indice] for indice in tabEvaluationTicks])
			axe1.set_xlabel('Evaluation')

			# axe1.set_ylim(0, maxNbPreys + 0.1*maxNbPreys)
			axe1.set_ylabel('Number of interactions')
			
			axe1.set_title('Repartition of sharing interactions', fontsize = 10)

			plt.legend([barNbCooperate, barNbDefect], ['Cooperation', 'Defection'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=1, mode="expand", borderaxespad=0.)

			plt.savefig(dossier + "/preysRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


def drawAllFit(dossier) :
	if os.path.isdir(dossier) :
		listAllFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^allfitevalstat(\d*)\.dat$", f))]

		hashFitness = {}
		hashNbCooperate = {}
		hashNbDefect = {}

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
				hashNbCooperate[run] = {}
				hashNbDefect[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbCooperate', 'nbDefect'), 'formats' : [np.int, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileAll, delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3), dtype = dtypes)

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
								hashNbCooperate[run][evaluation] = []
								hashNbDefect[run][evaluation] = []

								hashFitnessGlob[evaluation] = []

								evalDone.append(evaluation)

							hashFitness[run][evaluation].append(line['fitness'])

							hashNbCooperate[run][evaluation].append(line['nbCooperate'])
							hashNbDefect[run][evaluation].append(line['nbDefect'])

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


		# SEABORN
		sns.set()
		sns.set_style('white')
		sns.set_context('paper')
		palette = sns.color_palette("husl", len(hashNbCooperate.keys()))

		matplotlib.rcParams['font.size'] = 15
		matplotlib.rcParams['font.weight'] = 'bold'
		matplotlib.rcParams['axes.labelsize'] = 15
		matplotlib.rcParams['axes.labelweight'] = 'bold'
		matplotlib.rcParams['xtick.labelsize'] = 15
		matplotlib.rcParams['ytick.labelsize'] = 15
		matplotlib.rcParams['legend.fontsize'] = 15

		dpi = 96
		size = (1280/dpi, 1024/dpi)

		tabPlotEvaluation = tabEvaluation

		# --- BOXPLOT RUN FITNESS ---
		dataBoxPlot = []
		for run in hashFitness.keys() :
			dataBoxPlot = [hashFitness[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashFitness[run].keys()]

			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
			bp = axe1.boxplot(dataBoxPlot)

			axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
			axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
			axe1.set_xlabel("Evaluation")

			axe1.set_ylabel("Fitness")
			axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

			axe1.set_title('Boxplot of population fitness')

			for i in range(0, len(bp['boxes'])):
			   bp['boxes'][i].set_color(palette[0])
			   # we have two whiskers!
			   bp['whiskers'][i*2].set_color(palette[0])
			   bp['whiskers'][i*2 + 1].set_color(palette[0])
			   bp['whiskers'][i*2].set_linewidth(2)
			   bp['whiskers'][i*2 + 1].set_linewidth(2)

			   # top and bottom fliers
			   # (set allows us to set many parameters at once)
			   # bp['fliers'][i * 2].set(markerfacecolor=palette[0],
			   #                 marker='o', alpha=0.75, markersize=6,
			   #                 markeredgecolor='none')
			   # bp['fliers'][i * 2 + 1].set(markerfacecolor=palette[0],
			   #                 marker='o', alpha=0.75, markersize=6,
			   #                 markeredgecolor='none')

			   bp['medians'][i].set_color('black')
			   bp['medians'][i].set_linewidth(3)

			   # and 4 caps to remove
			   for c in bp['caps']:
			       c.set_linewidth(0)

			plt.savefig(dossier + "/fitnessRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BOXPLOT ALL RUN FITNESS ---
		dataBoxPlot = [hashFitnessGlob[evaluation] for evaluation in tabPlotEvaluation if evaluation in hashFitnessGlob.keys()]

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		bp = axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
		axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
		axe1.set_xlabel("Evaluation")

		axe1.set_ylabel("Fitness")
		axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

		axe1.set_title('Boxplot of all fitness')

		for i in range(0, len(bp['boxes'])):
		   bp['boxes'][i].set_color(palette[0])
		   # we have two whiskers!
		   bp['whiskers'][i*2].set_color(palette[0])
		   bp['whiskers'][i*2 + 1].set_color(palette[0])
		   bp['whiskers'][i*2].set_linewidth(2)
		   bp['whiskers'][i*2 + 1].set_linewidth(2)

		   # top and bottom fliers
		   # (set allows us to set many parameters at once)
		   # bp['fliers'][i * 2].set(markerfacecolor=palette[0],
		   #                 marker='o', alpha=0.75, markersize=6,
		   #                 markeredgecolor='none')
		   # bp['fliers'][i * 2 + 1].set(markerfacecolor=palette[0],
		   #                 marker='o', alpha=0.75, markersize=6,
		   #                 markeredgecolor='none')

		   bp['medians'][i].set_color('black')
		   bp['medians'][i].set_linewidth(3)

		   # and 4 caps to remove
		   for c in bp['caps']:
		       c.set_linewidth(0)

		plt.savefig(dossier + "/globalFitness", bbox_inches = 'tight')
		plt.close()


		# --- BARS ---
		for run in hashNbCooperate.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			width = 0.8

			tabNbCooperate = [np.mean(hashNbCooperate[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbCooperate[run].keys()]
			tabNbDefect = [np.mean(hashNbDefect[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbDefect[run].keys()]

			barNbCooperate = axe1.bar(range(len(tabNbCooperate)), tabNbCooperate, width = width, color = colorCooperate, alpha = alphaCooperate)
			barNbDefect = axe1.bar(range(len(tabNbDefect)), tabNbDefect, bottom = tabNbCooperate, width = width, color = colorDefect, alpha = alphaDefect)

			tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]

			axe1.set_xticks(tabEvaluationTicks)
			axe1.set_xticklabels([tabPlotEvaluation[indice] for indice in tabEvaluationTicks])
			axe1.set_xlabel('Evaluation')
			# axe1.set_xlim(0, len(tabGenerationTicks))

			axe1.set_ylabel('Number of interactions')
			axe1.set_title('Repartition of sharing interactions', fontsize = 10)

			plt.legend([barNbCooperate, barNbDefect], ['Cooperation', 'Defection'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=1, mode="expand", borderaxespad=0.)

			plt.savefig(dossier + "/preysRun" + str(run) + ".png", bbox_inches = 'tight')
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
			if re.match(r'^BestFit$', curDir) and parametres["argAll"] != True :
				print('\t -> Drawing bestfit directory : ' + curDir)
				drawBestFit(dossier + '/' + curDir)
			elif re.match(r'^AllFit$', curDir) and parametres["argBest"] != True :
				print('\t -> Drawing allfit directory : ' + curDir)
				drawAllFit(dossier + '/' + curDir)


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
	parser.add_argument('-u', '--drawRun', help = "Drawing of each run pareto frontier", default=False, action="store_true")

	parser.add_argument('-g', '--firstGen', help = "Size of population of first generation", default=10, type=int)
	parser.add_argument('-E', '--EvalByGen', help = "Number of evaluations by generation", default=20, type=int)

	parser.add_argument('-s', '--selection', help = "Selected runs", default=None, type=int, nargs='+')
	parser.add_argument('-e', '--exclusion', help = "Excluded runs", default=None, type=int, nargs='+')
	args = parser.parse_args()

	main(args)

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
number = 3

argsAnimation = {}

def drawBestFitTuple(dossier) :
	if os.path.isdir(dossier) :
		listBestFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^bestfittuple(\d*)\.dat$", f))]

		hashFitness = {}
		hashNbHares = {}
		hashNbSStags = {}
		hashNbBStags = {}

		tabGeneration = []
		maxFitness = 0

		for fileBest in listBestFit :
			m = re.search(r'^bestfittuple(\d*)\.dat$', fileBest)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				hashFitness[run] = {}
				hashNbHares[run] = {}
				hashNbSStags[run] = {}
				hashNbBStags[run] = {}

				with open(os.path.join(dossier, fileBest), 'r') as fileRead :
					fileRead = fileRead.readlines()

					firstEval = True
					generation = 0

					for line in fileRead :
						line = line.rstrip('\n').split(',')

						assert(len(line) == (number*3 + 2))

						if generation%precision == 0 or firstEval :
							if generation < maxEval :
								hashFitness[run][generation] = float(line[1])

								hashNbHares[run][generation] = list()
								hashNbSStags[run][generation] = list()
								hashNbBStags[run][generation] = list()

								for i in range(0, number) :
									hashNbHares[run][generation].append(float(line[2 + i*3]))
									hashNbSStags[run][generation].append(float(line[2 + i*3 + 1]))
									hashNbBStags[run][generation].append(float(line[2 + i*3 + 2]))

								if generation not in tabGeneration :
									tabGeneration.append(generation)

								if line[1] > maxFitness :
									maxFitness = float(line[1])

								if firstEval :
									firstEval = False

						generation += 1


		tabGeneration = sorted(tabGeneration)
		lastEval = tabGeneration[-1]
		diffEvals = lastEval - tabGeneration[-2]

		while lastEval <= maxEval :
			lastEval += diffEvals
			tabGeneration.append(lastEval)


		# SEABORN
		sns.set()
		sns.set_style('white')
		sns.set_context('paper')
		palette = sns.color_palette("deep", len(hashNbBStags.keys()))

		matplotlib.rcParams['font.size'] = 15
		matplotlib.rcParams['font.weight'] = 'bold'
		matplotlib.rcParams['axes.labelsize'] = 15
		matplotlib.rcParams['axes.labelweight'] = 'bold'
		matplotlib.rcParams['xtick.labelsize'] = 15
		matplotlib.rcParams['ytick.labelsize'] = 15
		matplotlib.rcParams['legend.fontsize'] = 15

		dpi = 96
		size = (1280/dpi, 1024/dpi)

		tabPlotGeneration = tabGeneration

		# with open(os.path.join(dossier, "lastGenBest.dat"), "w") as fileWrite :
		# 	for run in hashRatioSuccess.keys() :
		# 		evalEnd = sorted(hashRatioSuccess[run].keys())[-1]
		# 		lastValue = hashRatioSuccess[run][evalEnd]

		# 		fileWrite.write(str(evalEnd) + "," + str(lastValue) + "\n")


		# --- BOXPLOT FITNESS ---
		dataBoxPlot = []
		for generation in tabPlotGeneration :
			listFitness = [hashFitness[run][generation] for run in hashFitness.keys() if generation in hashFitness[run].keys()]

			if len(listFitness) > 0 :
				dataBoxPlot.append(listFitness)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		bp = axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
		axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
		axe1.set_xlabel("Generation")

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
		# palette = sns.color_palette("husl", len(hashFitness.keys()))
		for run in hashFitness.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			tabFitness = [hashFitness[run][generation] for generation in tabPlotGeneration if generation in hashFitness[run].keys()]

			axe1.plot(range(len(tabFitness)), tabFitness)

			# Divide the x axis by 10
			# tabEvaluationTicks = [indice for indice in range(len(tabFitness)) if indice % (int(len(tabFitness)/10)) == 0]
			tabEvaluationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabEvaluationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabEvaluationTicks])
			axe1.set_xlabel('Generation')

			axe1.set_ylabel('Fitness')
			axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

			axe1.set_title('Best fitness', fontsize = 10)

			plt.savefig(dossier + "/fitnessRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BARS HARES ---
		for run in hashNbHares.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			width = 0.8

			cumulTab = None
			listBars = list()
			for i in range(0, len(hashNbHares[run][tabGeneration[0]])) :
				tab = [hashNbHares[run][generation][i] for generation in tabPlotGeneration if generation in hashNbHares[run].keys()]

				if cumulTab == None :
					listBars.append(axe1.bar(range(len(tab)), tab, width = width, color = palette[i], alpha = alphaHares))
					cumulTab = tab
				else :
					listBars.append(axe1.bar(range(len(tab)), tab, width = width, bottom = cumulTab, color = palette[i], alpha = alphaHares))
					cumulTab = np.add(tab, cumulTab)

			tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')
			# axe1.set_xlim(0, len(tabGenerationTicks))

			axe1.set_ylabel('Number of preys hunted')
			
			axe1.set_title('Repartition of hares hunted', fontsize = 10)

			plt.legend(listBars, [nbHunters + 1 for nbHunters in range(0, number)], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
			# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbSStagsSolo, barNbSStagsDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Small stags solo', 'Small stags coop.', 'Big stags solo', 'Big stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

			plt.savefig(dossier + "/preysHaresRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()



		# --- BARS SSTAGS ---
		for run in hashNbSStags.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			width = 0.8

			cumulTab = None
			listBars = list()
			for i in range(0, len(hashNbSStags[run][tabGeneration[0]])) :
				tab = [hashNbSStags[run][generation][i] for generation in tabPlotGeneration if generation in hashNbSStags[run].keys()]

				if cumulTab == None :
					listBars.append(axe1.bar(range(len(tab)), tab, width = width, color = palette[i], alpha = alphaHares))
					cumulTab = tab
				else :
					listBars.append(axe1.bar(range(len(tab)), tab, width = width, bottom = cumulTab, color = palette[i], alpha = alphaHares))
					cumulTab = np.add(tab, cumulTab)

			tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')
			# axe1.set_xlim(0, len(tabGenerationTicks))

			axe1.set_ylabel('Number of preys hunted')
			
			axe1.set_title('Repartition of small stags hunted', fontsize = 10)

			plt.legend(listBars, [nbHunters + 1 for nbHunters in range(0, number)], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
			# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Stags solo', 'Stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
			# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbSStagsSolo, barNbSStagsDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Small stags solo', 'Small stags coop.', 'Big stags solo', 'Big stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

			plt.savefig(dossier + "/preysSStagsRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()



		# --- BARS BStags ---
		for run in hashNbBStags.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			width = 0.8

			cumulTab = None
			listBars = list()
			for i in range(0, len(hashNbBStags[run][tabGeneration[0]])) :
				tab = [hashNbBStags[run][generation][i] for generation in tabPlotGeneration if generation in hashNbBStags[run].keys()]

				if cumulTab == None :
					listBars.append(axe1.bar(range(len(tab)), tab, width = width, color = palette[i], alpha = alphaHares))
					cumulTab = tab
				else :
					listBars.append(axe1.bar(range(len(tab)), tab, width = width, bottom = cumulTab, color = palette[i], alpha = alphaHares))
					cumulTab = np.add(tab, cumulTab)

			tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')
			# axe1.set_xlim(0, len(tabGenerationTicks))

			axe1.set_ylabel('Number of preys hunted')
			
			axe1.set_title('Repartition of big stags hunted', fontsize = 10)

			plt.legend(listBars, [nbHunters + 1 for nbHunters in range(0, number)], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
			# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Stags solo', 'Stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
			# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbSStagsSolo, barNbSStagsDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Small stags solo', 'Small stags coop.', 'Big stags solo', 'Big stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

			plt.savefig(dossier + "/preysBStagsRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()



		# --- BARS LAST GEN ---
		for run in hashNbHares.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			width = 0.8

			lastGen = sorted(hashNbHares[run].keys())[-1]
			tabNbHares = [hashNbHares[run][lastGen][nbHunters] for nbHunters in range(0, number)]
			tabNbSStags = [hashNbSStags[run][lastGen][nbHunters] for nbHunters in range(0, number)]
			tabNbBstags = [hashNbBStags[run][lastGen][nbHunters] for nbHunters in range(0, number)]

			barNbHares = axe1.bar(range(len(tabNbHares)), tabNbHares, width = width, color = palette[0])
			barNbSStags = axe1.bar(range(len(tabNbSStags)), tabNbSStags, width = width, bottom = tabNbHares, color = palette[0])
			barNbBstags = axe1.bar(range(len(tabNbBstags)), tabNbBstags, width = width, bottom = np.add(tabNbHares, tabNbSStags), color = palette[0])

			axe1.set_xlabel('Number of hunters')
			# axe1.set_xlim(0, len(tabGenerationTicks))

			axe1.set_ylabel('Number of preys hunted')
			
			axe1.set_title('Repartition of big stags hunted', fontsize = 10)

			plt.legend([barNbHares, barNbSStags, barNbBstags], ['Hares', 'Small Stags', 'Big Stags'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
			# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbSStagsSolo, barNbSStagsDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Small stags solo', 'Small stags coop.', 'Big stags solo', 'Big stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

			plt.savefig(dossier + "/preysLastGenRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()



def drawAllFitTuple(dossier) :
	if os.path.isdir(dossier) :
		listAllFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^allfitevalstat(\d*)\.dat$", f))]

		hashFitness = {}
		hashNbHaresDuo = {}
		hashNbHaresSolo = {}
		hashNbHares = {}
		hashNbSStagsDuo = {}
		hashNbSStagsSolo = {}
		hashNbSStags = {}
		hashNbBStagsDuo = {}
		hashNbBStagsSolo = {}
		hashNbBStags = {}
		hashRatio = {}
		hashRatioHares = {}

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
				hashNbHaresDuo[run] = {}
				hashNbHaresSolo[run] = {}
				hashNbHares[run] = {}
				hashNbSStagsDuo[run] = {}
				hashNbSStagsSolo[run] = {}
				hashNbSStags[run] = {}
				hashNbBStagsDuo[run] = {}
				hashNbBStagsSolo[run] = {}
				hashNbBStags[run] = {}
				hashRatio[run] = {}
				hashRatioHares[run] = {}

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
						if cpt > precision :
							cpt = 0

						cpt += evaluation - lastEval
						lastEval = evaluation

					if cpt > precision :
						if evaluation < maxEval :
							if evaluation not in evalDone :
								hashFitness[run][evaluation] = []
								hashNbHaresDuo[run][evaluation] = []
								hashNbHaresSolo[run][evaluation] = []
								hashNbHares[run][evaluation] = []
								hashNbSStagsDuo[run][evaluation] = []
								hashNbSStagsSolo[run][evaluation] = []
								hashNbSStags[run][evaluation] = []
								hashNbBStagsDuo[run][evaluation] = []
								hashNbBStagsSolo[run][evaluation] = []
								hashNbBStags[run][evaluation] = []
								hashRatio[run][evaluation] = []
								hashRatioHares[run][evaluation] = []

								hashFitnessGlob[evaluation] = []

								evalDone.append(evaluation)

							hashFitness[run][evaluation].append(line['fitness'])

							hashNbHares[run][evaluation].append(line['nbHares'])
							hashNbHaresSolo[run][evaluation].append(line['nbHaresSolo'])
							hashNbHaresDuo[run][evaluation].append(line['nbHares'] - line['nbHaresSolo'])

							hashNbSStags[run][evaluation].append(line['nbSStags'])
							hashNbSStagsSolo[run][evaluation].append(line['nbSStagsSolo'])
							hashNbSStagsDuo[run][evaluation].append(line['nbSStags'] - line['nbSStagsSolo'])

							hashNbBStags[run][evaluation].append(line['nbBStags'])
							hashNbBStagsSolo[run][evaluation].append(line['nbBStagsSolo'])
							hashNbBStagsDuo[run][evaluation].append(line['nbBStags'] - line['nbBStagsSolo'])

							hashRatio[run][evaluation].append(line['nbBStags']*100/(line['nbHares'] + line['nbBStags']))
							hashRatioHares[run][evaluation].append(line['nbHares']*100/(line['nbHares'] + line['nbBStags']))

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
		palette = sns.color_palette("husl", len(hashNbBStags.keys()))

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

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
		axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
		axe1.set_xlabel("Evaluation")

		axe1.set_ylabel("Fitness")
		axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

		axe1.set_title('Boxplot of all fitness')

		plt.savefig(dossier + "/globalFitness", bbox_inches = 'tight')
		plt.close()


		# --- BARS ---
		for run in hashNbHaresSolo.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			width = 0.8

			tabNbHaresSolo = [np.mean(hashNbHaresSolo[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbHaresSolo[run].keys()]
			tabNbHaresDuo = [np.mean(hashNbHaresDuo[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbHaresDuo[run].keys()]
			tabNbBStagsSolo = [np.mean(hashNbBStagsSolo[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbBStagsSolo[run].keys()]
			tabNbBStagsDuo = [np.mean(hashNbBStagsDuo[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbBStagsDuo[run].keys()]

			barNbHaresSolo = axe1.bar(range(len(tabNbHaresSolo)), tabNbHaresSolo, width = width, color = colorHaresSolo, alpha = alphaHares)
			barNbHaresDuo = axe1.bar(range(len(tabNbHaresDuo)), tabNbHaresDuo, bottom = tabNbHaresSolo, width = width, color = colorHaresDuo, alpha = alphaHares)
			barNbBStagsSolo = axe1.bar(range(len(tabNbBStagsSolo)), tabNbBStagsSolo, bottom = np.add(tabNbHaresDuo, tabNbHaresSolo), width = width, color = colorBStagsSolo, alpha = alphaBStags)
			barNbBStagsDuo = axe1.bar(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, bottom = np.add(tabNbBStagsSolo, np.add(tabNbHaresDuo, tabNbHaresSolo)), width = width, color = colorBStagsDuo, alpha = alphaBStags)

			tabEvaluationTicks = [indice for indice in range(len(tabNbHaresSolo)) if indice % (int(len(tabNbHaresSolo)/10)) == 0]

			axe1.set_xticks(tabEvaluationTicks)
			axe1.set_xticklabels([tabPlotEvaluation[indice] for indice in tabEvaluationTicks])
			axe1.set_xlabel('Evaluation')
			# axe1.set_xlim(0, len(tabGenerationTicks))

			axe1.set_ylabel('Number of preys hunted')
			axe1.set_title('Repartition of preys hunted', fontsize = 10)

			plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Stags solo', 'Stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

			plt.savefig(dossier + "/preysRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()



def drawAllNN(dossier) :
	print('Not implemented !')


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
			if re.match(r'^BestFitTuple$', curDir) and parametres["argAll"] != True :
				print('\t -> Drawing bestfittuple directory : ' + curDir)
				drawBestFitTuple(dossier + '/' + curDir)
			elif re.match(r'^AllFitTuple$', curDir) and parametres["argBest"] != True :
				print('\t -> Drawing allfittuple directory : ' + curDir)
				drawAllFitTuple(dossier + '/' + curDir)


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
									"argDrawRun" : args.drawRun,
									"argNumber" : args.number
								}
	draw(**parametres)



if __name__ == '__main__' :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('-m', '--max', help = "Max evaluation", default= 20000)
	parser.add_argument('-p', '--precision', help = "Precision", default= 10)

	parser.add_argument('-n', '--number', help = "Number of robots", default = 3)

	parser.add_argument('-b', '--best', help = "Best only", default=False, action="store_true")
	parser.add_argument('-a', '--all', help = "All only", default=False, action="store_true")
	parser.add_argument('-u', '--drawRun', help = "Drawing of each run pareto frontier", default=False, action="store_true")

	parser.add_argument('-g', '--firstGen', help = "Size of population of first generation", default=10, type=int)
	parser.add_argument('-E', '--EvalByGen', help = "Number of evaluations by generation", default=20, type=int)

	parser.add_argument('-s', '--selection', help = "Selected runs", default=None, type=int, nargs='+')
	parser.add_argument('-e', '--exclusion', help = "Excluded runs", default=None, type=int, nargs='+')
	args = parser.parse_args()

	main(args)

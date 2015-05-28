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


maxGen = None
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
		hashRatioSuccess = {}
		hashRatioHares = {}

		maxFitness = 0
		maxNbPreys = 0
		tabGeneration = []
		lastGen = 0
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
				hashRatioSuccess[run] = {}
				hashRatioHares[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

				cpt = 0
				firstEval = True
				generation = 0
				for line in data :
					evaluation = line['evaluation']

					if generation % precision == 0 or firstEval :
						if generation < maxGen :
							hashFitness[run][generation] = line['fitness']

							hashNbHares[run][generation] = line['nbHares']
							hashNbHaresSolo[run][generation] = line['nbHaresSolo']
							hashNbHaresDuo[run][generation] = line['nbHares'] - line['nbHaresSolo']

							hashNbSStags[run][generation] = line['nbSStags']
							hashNbSStagsSolo[run][generation] = line['nbSStagsSolo']
							hashNbSStagsDuo[run][generation] = line['nbSStags'] - line['nbSStagsSolo']

							hashNbBStags[run][generation] = line['nbBStags']
							hashNbBStagsSolo[run][generation] = line['nbBStagsSolo']
							hashNbBStagsDuo[run][generation] = line['nbBStags'] - line['nbBStagsSolo']

							hashRatio[run][generation] = line['nbBStags']*100/(line['nbHares'] + line['nbBStags'])
							hashRatioSuccess[run][generation] = (line['nbBStags'] - line['nbBStagsSolo'])*100/(line['nbHares'] + (line['nbBStags'] - line['nbBStagsSolo'])) 
							hashRatioHares[run][generation] = line['nbHares']*100/(line['nbHares'] + line['nbBStags'])

							if generation not in tabGeneration :
								tabGeneration.append(generation)

							if line['fitness'] > maxFitness :
								maxFitness = line['fitness']

							if (line['nbHares'] + line['nbBStags'] + line['nbSStags']) > maxNbPreys :
								maxNbPreys = (line['nbHares'] + line['nbBStags'] + line['nbSStags'])

							if lastGen < generation :
								lastGen = generation

					if firstEval :
						firstEval = False

					generation += 1

		tabGeneration = sorted(tabGeneration)
		while lastGen <= maxGen :
			lastGen += precision
			tabGeneration.append(lastGen)

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

		# --- BOXPLOT HARES FITNESS ---
		runHares = []
		for run in hashNbHares.keys() :
			lastGenRun = sorted(hashNbHares[run].keys())[-1]
			if hashNbHares[run][lastGenRun] > hashNbBStags[run][lastGenRun] :
				runHares.append(run)

		dataBoxPlot = []
		for generation in tabPlotGeneration :
			listFitness = [hashFitness[run][generation] for run in runHares if generation in hashFitness[run].keys()]

			if len(listFitness) > 0 :
				dataBoxPlot.append(listFitness)

		if len(dataBoxPlot) > 0 :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
			axe1.boxplot(dataBoxPlot)

			axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
			axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
			axe1.set_xlabel("Generation")

			axe1.set_ylabel("Fitness")
			axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

			axe1.set_title('Boxplot of best fitness')

			plt.savefig(dossier + "/boxplotRunHares.png", bbox_inches = 'tight')
			plt.close()


		# --- BOXPLOT STAGS FITNESS ---
		runStags = []
		for run in hashNbBStags.keys() :
			lastGenRun = sorted(hashNbHares[run].keys())[-1]
			if hashNbBStagsDuo[run][lastGenRun] > hashNbHares[run][lastGenRun] :
				runStags.append(run)

		dataBoxPlot = []
		for generation in tabPlotGeneration :
			listFitness = [hashFitness[run][generation] for run in runStags if generation in hashFitness[run].keys()]

			if len(listFitness) > 0 :
				dataBoxPlot.append(listFitness)

		if len(dataBoxPlot) > 0 :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
			axe1.boxplot(dataBoxPlot)

			axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
			axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
			axe1.set_xlabel("Generation")

			axe1.set_ylabel("Fitness")
			axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

			axe1.set_title('Boxplot of best fitness')

			plt.savefig(dossier + "/boxplotRunStags.png", bbox_inches = 'tight')
			plt.close()



		# --- RUNS FITNESS ---
		palette = sns.color_palette("husl", len(hashFitness.keys()))
		for run in hashFitness.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			tabFitness = [hashFitness[run][generation] for generation in tabPlotGeneration if generation in hashFitness[run].keys()]

			axe1.plot(range(len(tabFitness)), tabFitness)

			# Divide the x axis by 10
			# tabGenerationTicks = [indice for indice in range(len(tabFitness)) if indice % (int(len(tabFitness)/10)) == 0]
			tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')

			axe1.set_ylabel('Fitness')
			axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

			axe1.set_title('Best fitness', fontsize = 10)

			plt.savefig(dossier + "/fitnessRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()



		# --- RUNS RATIO ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		cpt = 0
		lastVals = []
		captions = []
		for run in hashRatioSuccess.keys() :
			tabRatio = [np.mean(hashRatioSuccess[run][generation]) for generation in tabPlotGeneration if generation in hashRatioSuccess[run].keys()]
			axe1.plot(range(len(tabRatio)), tabRatio, color = palette[cpt])
			lastVals.append(tabRatio[-1])
			captions.append("Run " + str(run))

			cpt += 1

		axe1.set_ylim(0, 100)

		sortedVals = zip(*(sorted(zip(lastVals, range(len(lastVals))), key = itemgetter(0))))
		sortedLastVals = sortedVals[0]
		sortedIndexes = sortedVals[1]

		# Create new axes on the right containing captions
		divider = make_axes_locatable(axe1)
		rax = divider.append_axes("right", size="25%", pad=0.00)

		# Add captions text on axis, and lines
		yCaptionsCoords = np.linspace(0., 1., len(sortedIndexes))
		connectionLinesCoords = []
		for y, i in zip(yCaptionsCoords, sortedIndexes):
			cap = captions[i]
			lastVal = lastVals[i]
			color = palette[i]
			rax.text(1.10, y, cap,
					horizontalalignment='left',
					verticalalignment='center',
					transform = rax.transAxes)

			# Add lines
			normalizedY = float(y) * float(axe1.get_ylim()[1])
			rax.plot([lastVal, normalizedY], color=color)


		rax.set_axis_off()
		rax.set_ylim(0, 100)

		# Divide the x axis by 10
		tabGeneration = [(generation+30)/40 for generation in tabPlotGeneration]
		tabGeneration[-1] = 300

		tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]
		axe1.set_xticks(tabGenerationTicks)
		axe1.set_xticklabels([tabGeneration[indice] for indice in tabGenerationTicks])
		axe1.set_xlabel('Generation')

		axe1.set_ylabel('Pourcentage of stags hunted')
		# axe1.set_ylim(0, 100)

		plt.savefig(dossier + "/figureRatioBStagsSuccess.png", bbox_inches = 'tight')


		# --- BARS ---
		for run in hashNbHaresSolo.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			width = 0.8

			tabNbHaresSolo = [hashNbHaresSolo[run][generation] for generation in tabPlotGeneration if generation in hashNbHaresSolo[run].keys()]
			tabNbHaresDuo = [hashNbHaresDuo[run][generation] for generation in tabPlotGeneration if generation in hashNbHaresDuo[run].keys()]
			tabNbSStagsSolo = [hashNbSStagsSolo[run][generation] for generation in tabPlotGeneration if generation in hashNbSStagsSolo[run].keys()]
			tabNbSStagsDuo = [hashNbSStagsDuo[run][generation] for generation in tabPlotGeneration if generation in hashNbSStagsDuo[run].keys()]
			tabNbBStagsSolo = [hashNbBStagsSolo[run][generation] for generation in tabPlotGeneration if generation in hashNbBStagsSolo[run].keys()]
			tabNbBStagsDuo = [hashNbBStagsDuo[run][generation] for generation in tabPlotGeneration if generation in hashNbBStagsDuo[run].keys()]

			barNbHaresSolo = axe1.bar(range(len(tabNbHaresSolo)), tabNbHaresSolo, width = width, color = colorHaresSolo, alpha = alphaHares)
			barNbHaresDuo = axe1.bar(range(len(tabNbHaresDuo)), tabNbHaresDuo, bottom = tabNbHaresSolo, width = width, color = colorHaresDuo, alpha = alphaHares)
			barNbSStagsSolo = axe1.bar(range(len(tabNbSStagsSolo)), tabNbSStagsSolo, bottom = np.add(tabNbHaresDuo, tabNbHaresSolo), width = width, color = colorSStagsSolo, alpha = alphaSStags)
			barNbSStagsDuo = axe1.bar(range(len(tabNbSStagsDuo)), tabNbSStagsDuo, bottom = np.add(tabNbSStagsSolo, np.add(tabNbHaresDuo, tabNbHaresSolo)), width = width, color = colorSStagsDuo, alpha = alphaSStags)
			barNbBStagsSolo = axe1.bar(range(len(tabNbBStagsSolo)), tabNbBStagsSolo, bottom = np.add(tabNbSStagsDuo, np.add(tabNbSStagsSolo, np.add(tabNbHaresDuo, tabNbHaresSolo))), width = width, color = colorBStagsSolo, alpha = alphaBStags)
			barNbBStagsDuo = axe1.bar(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, bottom = np.add(tabNbBStagsSolo, np.add(tabNbSStagsDuo, np.add(tabNbSStagsSolo, np.add(tabNbHaresDuo, tabNbHaresSolo)))), width = width, color = colorBStagsDuo, alpha = alphaBStags)

			tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')
			# axe1.set_xlim(0, len(tabGenerationTicks))

			axe1.set_ylim(0, maxNbPreys + 0.1*maxNbPreys)
			axe1.set_ylabel('Number of preys hunted')
			
			axe1.set_title('Repartition of preys hunted', fontsize = 10)

			# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Stags solo', 'Stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
			# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbSStagsSolo, barNbSStagsDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Small stags solo', 'Small stags coop.', 'Big stags solo', 'Big stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

			plt.savefig(dossier + "/preysRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


def drawAllFit(dossier) :
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

		hashFitnessGlob = {}
		maxFitness = 0
		tabGeneration = []
		lastGen = 0
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

				genDone = []
				cpt = 0
				lastEval = None
				generation = 0
				for line in data :
					evaluation = line['evaluation']

					if lastEval == None :
						lastEval = evaluation

					if evaluation != lastEval :
						generation += 1
						lastEval = evaluation

					if generation % precision == 0 :
						if generation < maxGen :
							if generation not in genDone :
								hashFitness[run][generation] = []
								hashNbHaresDuo[run][generation] = []
								hashNbHaresSolo[run][generation] = []
								hashNbHares[run][generation] = []
								hashNbSStagsDuo[run][generation] = []
								hashNbSStagsSolo[run][generation] = []
								hashNbSStags[run][generation] = []
								hashNbBStagsDuo[run][generation] = []
								hashNbBStagsSolo[run][generation] = []
								hashNbBStags[run][generation] = []
								hashRatio[run][generation] = []
								hashRatioHares[run][generation] = []

								hashFitnessGlob[generation] = []

								genDone.append(generation)

							hashFitness[run][generation].append(line['fitness'])

							hashNbHares[run][generation].append(line['nbHares'])
							hashNbHaresSolo[run][generation].append(line['nbHaresSolo'])
							hashNbHaresDuo[run][generation].append(line['nbHares'] - line['nbHaresSolo'])

							hashNbSStags[run][generation].append(line['nbSStags'])
							hashNbSStagsSolo[run][generation].append(line['nbSStagsSolo'])
							hashNbSStagsDuo[run][generation].append(line['nbSStags'] - line['nbSStagsSolo'])

							hashNbBStags[run][generation].append(line['nbBStags'])
							hashNbBStagsSolo[run][generation].append(line['nbBStagsSolo'])
							hashNbBStagsDuo[run][generation].append(line['nbBStags'] - line['nbBStagsSolo'])

							hashRatio[run][generation].append(line['nbBStags']*100/(line['nbHares'] + line['nbBStags']))
							hashRatioHares[run][generation].append(line['nbHares']*100/(line['nbHares'] + line['nbBStags']))

							hashFitnessGlob[generation].append(line['fitness'])

							if generation not in tabGeneration :
								tabGeneration.append(generation)

							if line['fitness'] > maxFitness :
								maxFitness = line['fitness']

							if lastGen < generation :
								lastGen = generation


		tabGeneration = sorted(tabGeneration)

		while lastGen <= maxGen :
			lastGen += precision
			tabGeneration.append(lastGen)


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

		tabPlotGeneration = tabGeneration


		# --- BOXPLOT RUN FITNESS ---
		dataBoxPlot = []
		for run in hashFitness.keys() :
			dataBoxPlot = [hashFitness[run][generation] for generation in tabPlotGeneration if generation in hashFitness[run].keys()]

			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
			axe1.boxplot(dataBoxPlot)

			axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
			axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
			axe1.set_xlabel("Generation")

			axe1.set_ylabel("Fitness")
			axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

			axe1.set_title('Boxplot of population fitness')

			plt.savefig(dossier + "/fitnessRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BOXPLOT ALL RUN FITNESS ---
		dataBoxPlot = [hashFitnessGlob[generation] for generation in tabPlotGeneration if generation in hashFitnessGlob.keys()]

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
		axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
		axe1.set_xlabel("Generation")

		axe1.set_ylabel("Fitness")
		axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

		axe1.set_title('Boxplot of all fitness')

		plt.savefig(dossier + "/globalFitness", bbox_inches = 'tight')
		plt.close()


		# --- BARS ---
		for run in hashNbHaresSolo.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			width = 0.8

			tabNbHaresSolo = [np.mean(hashNbHaresSolo[run][generation]) for generation in tabPlotGeneration if generation in hashNbHaresSolo[run].keys()]
			tabNbHaresDuo = [np.mean(hashNbHaresDuo[run][generation]) for generation in tabPlotGeneration if generation in hashNbHaresDuo[run].keys()]
			tabNbBStagsSolo = [np.mean(hashNbBStagsSolo[run][generation]) for generation in tabPlotGeneration if generation in hashNbBStagsSolo[run].keys()]
			tabNbBStagsDuo = [np.mean(hashNbBStagsDuo[run][generation]) for generation in tabPlotGeneration if generation in hashNbBStagsDuo[run].keys()]

			barNbHaresSolo = axe1.bar(range(len(tabNbHaresSolo)), tabNbHaresSolo, width = width, color = colorHaresSolo, alpha = alphaHares)
			barNbHaresDuo = axe1.bar(range(len(tabNbHaresDuo)), tabNbHaresDuo, bottom = tabNbHaresSolo, width = width, color = colorHaresDuo, alpha = alphaHares)
			barNbBStagsSolo = axe1.bar(range(len(tabNbBStagsSolo)), tabNbBStagsSolo, bottom = np.add(tabNbHaresDuo, tabNbHaresSolo), width = width, color = colorBStagsSolo, alpha = alphaBStags)
			barNbBStagsDuo = axe1.bar(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, bottom = np.add(tabNbBStagsSolo, np.add(tabNbHaresDuo, tabNbHaresSolo)), width = width, color = colorBStagsDuo, alpha = alphaBStags)

			tabGenerationTicks = [indice for indice in range(len(tabNbHaresSolo)) if indice % (int(len(tabNbHaresSolo)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')
			# axe1.set_xlim(0, len(tabGenerationTicks))

			axe1.set_ylabel('Number of preys hunted')
			axe1.set_title('Repartition of preys hunted', fontsize = 10)

			plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Stags solo', 'Stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

			plt.savefig(dossier + "/preysRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


def drawBestDiv(dossier) :
	if os.path.isdir(dossier) :
		listBestDiv = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^bestdiv(\d*)\.dat$", f))]

		hashDiversity = {}
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

		maxDiversity = 0
		tabGeneration = []
		lastGen = 0
		for fileBest in listBestDiv :
			m = re.search(r'^bestdiv(\d*)\.dat$', fileBest)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				hashDiversity[run] = {}
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

				dtypes = np.dtype({ 'names' : ('evaluation', 'diversity', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

				firstEval = True
				generation = 0
				for line in data :
					evaluation = line['evaluation']

					if generation % precision == 0 or firstEval :
						if generation < maxGen :
							hashDiversity[run][generation] = line['diversity']

							hashNbHares[run][generation] = line['nbHares']
							hashNbHaresSolo[run][generation] = line['nbHaresSolo']
							hashNbHaresDuo[run][generation] = line['nbHares'] - line['nbHaresSolo']

							hashNbSStags[run][generation] = line['nbSStags']
							hashNbSStagsSolo[run][generation] = line['nbSStagsSolo']
							hashNbSStagsDuo[run][generation] = line['nbSStags'] - line['nbSStagsSolo']

							hashNbBStags[run][generation] = line['nbBStags']
							hashNbBStagsSolo[run][generation] = line['nbBStagsSolo']
							hashNbBStagsDuo[run][generation] = line['nbBStags'] - line['nbBStagsSolo']

							hashRatio[run][generation] = line['nbBStags']*100/(line['nbHares'] + line['nbBStags'])
							hashRatioHares[run][generation] = line['nbHares']*100/(line['nbHares'] + line['nbBStags'])

							if generation not in tabGeneration :
								tabGeneration.append(generation)

							if line['diversity'] > maxDiversity :
								maxDiversity = line['diversity']

							cpt = 0

							if lastGen < generation :
								lastGen = generation

					if firstEval :
						firstEval = False

					generation += 1

		tabGeneration = sorted(tabGeneration)

		while lastGen <= maxGen :
			lastGen += precision
			tabGeneration.append(lastGen)


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

		tabPlotGeneration = tabGeneration


		# --- BOXPLOT FITNESS ---
		dataBoxPlot = []
		for generation in tabPlotGeneration :
			listDiversity = [hashDiversity[run][generation] for run in hashDiversity.keys() if generation in hashDiversity[run].keys()]

			if len(listDiversity) > 0 :
				dataBoxPlot.append(listDiversity)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
		axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
		axe1.set_xlabel("Generation")

		axe1.set_ylabel("Diversity")
		axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

		axe1.set_title('Boxplot of best diversity')

		plt.savefig(dossier + "/boxplot.png", bbox_inches = 'tight')
		plt.close()



		# --- RUNS FITNESS ---
		palette = sns.color_palette("husl", len(hashDiversity.keys()))
		for run in hashDiversity.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			tabDiversity = [hashDiversity[run][generation] for generation in tabPlotGeneration if generation in hashDiversity[run].keys()]

			axe1.plot(range(len(tabDiversity)), tabDiversity)

			# Divide the x axis by 10
			# tabGenerationTicks = [indice for indice in range(len(tabDiversity)) if indice % (int(len(tabDiversity)/10)) == 0]
			tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')

			axe1.set_ylabel('Diversity')
			axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

			axe1.set_title('Best diversity', fontsize = 10)

			plt.savefig(dossier + "/diversityRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()



		# --- BARS ---
		for run in hashNbHaresSolo.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			width = 0.8

			tabNbHaresSolo = [hashNbHaresSolo[run][generation] for generation in tabPlotGeneration if generation in hashNbHaresSolo[run].keys()]
			tabNbHaresDuo = [hashNbHaresDuo[run][generation] for generation in tabPlotGeneration if generation in hashNbHaresDuo[run].keys()]
			tabNbBStagsSolo = [hashNbBStagsSolo[run][generation] for generation in tabPlotGeneration if generation in hashNbBStagsSolo[run].keys()]
			tabNbBStagsDuo = [hashNbBStagsDuo[run][generation] for generation in tabPlotGeneration if generation in hashNbBStagsDuo[run].keys()]

			barNbHaresSolo = axe1.bar(range(len(tabNbHaresSolo)), tabNbHaresSolo, width = width, color = colorHaresSolo, alpha = alphaHares)
			barNbHaresDuo = axe1.bar(range(len(tabNbHaresDuo)), tabNbHaresDuo, bottom = tabNbHaresSolo, width = width, color = colorHaresDuo, alpha = alphaHares)
			barNbBStagsSolo = axe1.bar(range(len(tabNbBStagsSolo)), tabNbBStagsSolo, bottom = np.add(tabNbHaresDuo, tabNbHaresSolo), width = width, color = colorBStagsSolo, alpha = alphaBStags)
			barNbBStagsDuo = axe1.bar(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, bottom = np.add(tabNbBStagsSolo, np.add(tabNbHaresDuo, tabNbHaresSolo)), width = width, color = colorBStagsDuo, alpha = alphaBStags)

			if len(tabNbHaresSolo) >= 10 :
				tabGenerationTicks = [indice for indice in range(len(tabNbHaresSolo)) if indice % (int(len(tabNbHaresSolo)/10)) == 0]
			else :
				tabGenerationTicks = [0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')
			# axe1.set_xlim(0, len(tabGenerationTicks))

			axe1.set_ylabel('Number of preys hunted')
			axe1.set_title('Repartition of preys hunted', fontsize = 10)

			plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Stags solo', 'Stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

			plt.savefig(dossier + "/preysRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


def drawAllDiv(dossier) :
	if os.path.isdir(dossier) :
		listAllDiv = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^alldivevalstat(\d*)\.dat$", f))]

		hashDiversity = {}
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

		hashDiversityGlob = {}
		maxDiversity = 0
		tabGeneration = []
		lastGen = 0
		for fileAll in listAllDiv :
			m = re.search(r'^alldivevalstat(\d*)\.dat$', fileAll)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				hashDiversity[run] = {}
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

				dtypes = np.dtype({ 'names' : ('evaluation', 'diversity', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileAll, delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

				genDone = []
				lastEval = None
				generation = 0
				for line in data :
					evaluation = line['evaluation']

					if lastEval == None :
						lastEval = evaluation

					if evaluation != lastEval :
						generation += 1
						lastGen = evaluation

					if generation % precision == 0 :
						if generation < maxGen :
							if generation not in genDone :
								hashDiversity[run][generation] = []
								hashNbHaresDuo[run][generation] = []
								hashNbHaresSolo[run][generation] = []
								hashNbHares[run][generation] = []
								hashNbSStagsDuo[run][generation] = []
								hashNbSStagsSolo[run][generation] = []
								hashNbSStags[run][generation] = []
								hashNbBStagsDuo[run][generation] = []
								hashNbBStagsSolo[run][generation] = []
								hashNbBStags[run][generation] = []
								hashRatio[run][generation] = []
								hashRatioHares[run][generation] = []

								hashDiversityGlob[generation] = []

								genDone.append(generation)

							hashDiversity[run][generation].append(line['diversity'])

							hashNbHares[run][generation].append(line['nbHares'])
							hashNbHaresSolo[run][generation].append(line['nbHaresSolo'])
							hashNbHaresDuo[run][generation].append(line['nbHares'] - line['nbHaresSolo'])

							hashNbSStags[run][generation].append(line['nbSStags'])
							hashNbSStagsSolo[run][generation].append(line['nbSStagsSolo'])
							hashNbSStagsDuo[run][generation].append(line['nbSStags'] - line['nbSStagsSolo'])

							hashNbBStags[run][generation].append(line['nbBStags'])
							hashNbBStagsSolo[run][generation].append(line['nbBStagsSolo'])
							hashNbBStagsDuo[run][generation].append(line['nbBStags'] - line['nbBStagsSolo'])

							hashRatio[run][generation].append(line['nbBStags']*100/(line['nbHares'] + line['nbBStags']))
							hashRatioHares[run][generation].append(line['nbHares']*100/(line['nbHares'] + line['nbBStags']))

							hashDiversityGlob[generation].append(line['diversity'])

							if generation not in tabGeneration :
								tabGeneration.append(generation)

							if line['diversity'] > maxDiversity :
								maxDiversity = line['diversity']

							if lastGen < generation :
								lastGen = generation


		tabGeneration = sorted(tabGeneration)

		while lastGen <= maxGen :
			lastGen += precision
			tabGeneration.append(lastGen)


		# SEABORN
		sns.set()
		sns.set_style('white')
		sns.set_context('paper')
		palette = sns.color_palette("husl", len(hashDiversity.keys()))

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


		# --- BOXPLOT RUN FITNESS ---
		dataBoxPlot = []
		for run in hashDiversity.keys() :
			dataBoxPlot = [hashDiversity[run][generation] for generation in tabPlotGeneration if generation in hashDiversity[run].keys()]

			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
			axe1.boxplot(dataBoxPlot)

			axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
			axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
			axe1.set_xlabel("Generation")

			axe1.set_ylabel("Diversity")
			axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

			axe1.set_title('Boxplot of population diversity')

			plt.savefig(dossier + "/diversityRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BOXPLOT ALL RUN FITNESS ---
		dataBoxPlot = [hashDiversityGlob[generation] for generation in tabPlotGeneration if generation in hashDiversityGlob.keys()]

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
		axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
		axe1.set_xlabel("Generation")

		axe1.set_ylabel("Diversity")
		axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

		axe1.set_title('Boxplot of all diversity')

		plt.savefig(dossier + "/globalDiversity", bbox_inches = 'tight')
		plt.close()


		# --- BARS ---
		for run in hashNbHaresSolo.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			width = 0.8

			tabNbHaresSolo = [np.mean(hashNbHaresSolo[run][generation]) for generation in tabPlotGeneration if generation in hashNbHaresSolo[run].keys()]
			tabNbHaresDuo = [np.mean(hashNbHaresDuo[run][generation]) for generation in tabPlotGeneration if generation in hashNbHaresDuo[run].keys()]
			tabNbBStagsSolo = [np.mean(hashNbBStagsSolo[run][generation]) for generation in tabPlotGeneration if generation in hashNbBStagsSolo[run].keys()]
			tabNbBStagsDuo = [np.mean(hashNbBStagsDuo[run][generation]) for generation in tabPlotGeneration if generation in hashNbBStagsDuo[run].keys()]

			barNbHaresSolo = axe1.bar(range(len(tabNbHaresSolo)), tabNbHaresSolo, width = width, color = colorHaresSolo, alpha = alphaHares)
			barNbHaresDuo = axe1.bar(range(len(tabNbHaresDuo)), tabNbHaresDuo, bottom = tabNbHaresSolo, width = width, color = colorHaresDuo, alpha = alphaHares)
			barNbBStagsSolo = axe1.bar(range(len(tabNbBStagsSolo)), tabNbBStagsSolo, bottom = np.add(tabNbHaresDuo, tabNbHaresSolo), width = width, color = colorBStagsSolo, alpha = alphaBStags)
			barNbBStagsDuo = axe1.bar(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, bottom = np.add(tabNbBStagsSolo, np.add(tabNbHaresDuo, tabNbHaresSolo)), width = width, color = colorBStagsDuo, alpha = alphaBStags)

			tabGenerationTicks = [indice for indice in range(len(tabNbHaresSolo)) if indice % (int(len(tabNbHaresSolo)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')
			# axe1.set_xlim(0, len(tabGenerationTicks))

			axe1.set_ylabel('Number of preys hunted')
			axe1.set_title('Repartition of preys hunted', fontsize = 10)

			plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Stags solo', 'Stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

			plt.savefig(dossier + "/preysRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


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


def drawPareto(dossier) :
	if os.path.isdir(dossier) :
		listAllDiv = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^alldivevalstat(\d*)\.dat$", f))]
		listAllFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^allfitevalstat(\d*)\.dat$", f))]

		hashDiversity = {}
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
		hashRatioCoop = {}

		maxDiversity = 0
		maxFitness = 0
		tabGeneration = []
		lastGen = 0
		for fileAll in listAllDiv :
			m = re.search(r'^alldivevalstat(\d*)\.dat$', fileAll)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				hashDiversity[run] = {}
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
				hashRatioCoop[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'diversity', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileAll, delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

				genDone = []
				cpt = 0
				lastEval = None
				generation = 0
				for line in data :
					evaluation = line['evaluation']

					if lastEval == None :
						lastEval = evaluation

					if evaluation != lastEval :
						generation += 1
						lastEval = evaluation

					if generation % precision == 0 :
						if generation < maxGen :
							if generation not in genDone :
								hashDiversity[run][generation] = []
								hashFitness[run][generation] = []

								hashNbHaresDuo[run][generation] = []
								hashNbHaresSolo[run][generation] = []
								hashNbHares[run][generation] = []

								hashNbSStagsDuo[run][generation] = []
								hashNbSStagsSolo[run][generation] = []
								hashNbSStags[run][generation] = []

								hashNbBStagsDuo[run][generation] = []
								hashNbBStagsSolo[run][generation] = []
								hashNbBStags[run][generation] = []

								hashRatio[run][generation] = []
								hashRatioHares[run][generation] = []
								hashRatioCoop[run][generation] = []

								genDone.append(generation)

							hashDiversity[run][generation].append(line['diversity'])

							hashNbHares[run][generation].append(line['nbHares'])
							hashNbHaresSolo[run][generation].append(line['nbHaresSolo'])
							hashNbHaresDuo[run][generation].append(line['nbHares'] - line['nbHaresSolo'])

							hashNbSStags[run][generation].append(line['nbSStags'])
							hashNbSStagsSolo[run][generation].append(line['nbSStagsSolo'])
							hashNbSStagsDuo[run][generation].append(line['nbSStags'] - line['nbSStagsSolo'])

							hashNbBStags[run][generation].append(line['nbBStags'])
							hashNbBStagsSolo[run][generation].append(line['nbBStagsSolo'])
							hashNbBStagsDuo[run][generation].append(line['nbBStags'] - line['nbBStagsSolo'])

							hashRatio[run][generation].append(line['nbBStags']*100/(line['nbHares'] + line['nbBStags']))
							hashRatioHares[run][generation].append(line['nbHares']*100/(line['nbHares'] + line['nbBStags']))
							hashRatioCoop[run][generation].append((line['nbHares'] - line['nbHaresSolo'] + (line['nbBStags'] - line['nbBStagsSolo']))*100/((line['nbHares'] + line['nbBStags'])))

							if generation not in tabGeneration :
								tabGeneration.append(generation)

							if line['diversity'] > maxDiversity :
								maxDiversity = line['diversity']

							if lastGen < generation :
								lastGen = generation


		for fileAll in listAllFit :
			m = re.search(r'^allfitevalstat(\d*)\.dat$', fileAll)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileAll, delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

				genDone = []
				lastEval = None
				generation = 0
				for line in data :
					evaluation = line['evaluation']

					if lastEval == None :
						lastEval = evaluation

					if evaluation != lastEval :
						generation += 1
						lastEval = evaluation

					if generation % precision == 0 and generation in hashDiversity[run].keys() :
						if generation < maxGen :
							hashFitness[run][generation].append(line['fitness'])

							if generation not in tabGeneration :
								tabGeneration.append(generation)

							if line['fitness'] > maxFitness :
								maxFitness = line['fitness']

							if lastGen < generation :
								lastGen = generation


		tabGeneration = sorted(tabGeneration)

		while lastGen <= maxGen :
			lastGen += precision
			tabGeneration.append(lastGen)


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
		size = (1280/dpi, 1024/dpi)

		dpi = 96

		tabPlotGeneration = tabGeneration


		# Pareto Frontier
		for run in hashFitness.keys() :
			assert(len(hashFitness[run].keys()) == len(hashDiversity[run].keys()))
			lastGenRun = sorted(hashFitness[run].keys())[-1]
			assert(lastGenRun == sorted(hashDiversity[run].keys())[-1])

			listFitness = hashFitness[run][lastGenRun]
			listDiversity = hashDiversity[run][lastGenRun]

			listRatio = hashRatio[run][lastGenRun]
			listColors = [0 if math.isnan(ratio) else int(ratio) for ratio in listRatio]

			listRatioCoop = hashRatioCoop[run][lastGenRun]
			listSizes = [50 if math.isnan(ratio) else 50 + int(ratio*2) for ratio in listRatioCoop]

			p_front = pareto_frontier(listFitness, listDiversity, maxX = True, maxY = True)

			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
			axe1.scatter(listFitness, listDiversity, c = listColors, cmap = cm.rainbow, s = listSizes)
			axe1.plot(p_front[0], p_front[1])

			axe1.set_xlabel("Fitness")
			axe1.set_xlim(0, maxFitness + 0.1*maxFitness)

			axe1.set_ylabel("Diversity")
			axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

			axe1.set_title('Pareto frontier at last evaluation')

			plt.savefig(dossier + "/paretoRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


def drawParetoRun(dossier, run) :
	if os.path.isdir(dossier) :
		listAllDiv = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^alldivevalstat(\d*)\.dat$", f))]
		listAllFit = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^allfitevalstat(\d*)\.dat$", f))]

		hashDiversity = {}
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
		hashRatioCoop = {}

		tabGeneration = []
		maxDiversity = 0
		maxFitness = 0

		lastGen = 0

		testRun = None
		if selection != None :
			testRun = lambda run : run in selection
		elif exclusion != None :
			testRun = lambda run : run not in exclusion

		if (testRun == None) or (testRun(run)) :
			dtypes = np.dtype({ 'names' : ('evaluation', 'diversity', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
			data = np.loadtxt(os.path.join(dossier, 'alldivevalstat.dat'), delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

			genDone = []
			cpt = 0
			lastEval = None
			generation = 0
			for line in data :
				evaluation = line['evaluation']

				if lastEval == None :
					lastEval = evaluation

				if evaluation != lastEval :
					generation += 1
					lastEval = evaluation

				if generation % precision == 0 :
					if generaiton < maxGen :
						if generation not in genDone :
							hashDiversity[generation] = []
							hashFitness[generation] = []

							hashNbHaresDuo[generation] = []
							hashNbHaresSolo[generation] = []
							hashNbHares[generation] = []

							hashNbSStagsDuo[generation] = []
							hashNbSStagsSolo[generation] = []
							hashNbSStags[generation] = []

							hashNbBStagsDuo[generation] = []
							hashNbBStagsSolo[generation] = []
							hashNbBStags[generation] = []

							hashRatio[generation] = []
							hashRatioHares[generation] = []
							hashRatioCoop[generation] = []

							genDone.append(generation)

						hashDiversity[generation].append(line['diversity'])

						hashNbHares[generation].append(line['nbHares'])
						hashNbHaresSolo[generation].append(line['nbHaresSolo'])
						hashNbHaresDuo[generation].append(line['nbHares'] - line['nbHaresSolo'])

						hashNbSStags[generation].append(line['nbSStags'])
						hashNbSStagsSolo[generation].append(line['nbSStagsSolo'])
						hashNbSStagsDuo[generation].append(line['nbSStags'] - line['nbSStagsSolo'])

						hashNbBStags[generation].append(line['nbBStags'])
						hashNbBStagsSolo[generation].append(line['nbBStagsSolo'])
						hashNbBStagsDuo[generation].append(line['nbBStags'] - line['nbBStagsSolo'])

						hashRatio[generation].append(line['nbBStags']*100/(line['nbHares'] + line['nbBStags']))
						hashRatioHares[generation].append(line['nbHares']*100/(line['nbHares'] + line['nbBStags']))
						hashRatioCoop[generation].append((line['nbHares'] - line['nbHaresSolo'] + (line['nbBStags'] - line['nbBStagsSolo']))*100/((line['nbHares'] + line['nbBStags'])))

						if generation not in tabGeneration :
							tabGeneration.append(generation)

						if line['diversity'] > maxDiversity :
							maxDiversity = line['diversity']


						if lastGen < generation :
							lastGen = generation


			dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
			data = np.loadtxt(os.path.join(dossier, 'allfitevalstat.dat'), delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

			genDone = []
			cpt = 0
			lastEval = None
			lastGen = None
			generation = 0
			for line in data :
				evaluation = line['evaluation']

				if lastEval == None :
					lastEval = evaluation

				if evaluation != lastEval :
					generation += 1
					lastEval = evaluation

				if generation % precision == 0 :
					if generation < maxGen :
						hashFitness[generation].append(line['fitness'])

						if generation not in tabGeneration :
							tabGeneration.append(generation)

						if line['fitness'] > maxFitness :
							maxFitness = line['fitness']


			tabGeneration = sorted(tabGeneration)

			while lastGen <= maxGen :
				lastGen += precision
				tabGeneration.append(lastGen)


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

			tabPlotGeneration = tabGeneration


			# Pareto Frontier
			assert(len(hashFitness.keys()) == len(hashDiversity.keys()))
			lastGenRun = sorted(hashFitness.keys())[-1]
			assert(lastGenRun == sorted(hashDiversity.keys())[-1])

			paretoEvals = sorted(hashFitness.keys())[0:-1:int(math.floor(len(hashFitness.keys())/20.0))]

			if lastGenRun not in paretoEvals :
				paretoEvals.append(lastGenRun)

			for eval in paretoEvals :
				listFitness = hashFitness[eval]
				listDiversity = hashDiversity[eval]

				listRatio = hashRatio[eval]
				listColors = [0 if math.isnan(ratio) else int(ratio) for ratio in listRatio]

				listRatioCoop = hashRatioCoop[eval]
				listSizes = [50 if math.isnan(ratio) else 50 + int(ratio*2) for ratio in listRatioCoop]

				p_front = pareto_frontier(listFitness, listDiversity, maxX = True, maxY = True)

				fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
				axe1.scatter(listFitness, listDiversity, c = listColors, cmap = cm.rainbow, s = listSizes)
				axe1.plot(p_front[0], p_front[1])

				axe1.set_xlabel("Fitness")
				axe1.set_xlim(0, maxFitness + 0.1*maxFitness)

				axe1.set_ylabel("Diversity")
				axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

				axe1.set_title('Pareto frontier at evaluation ' + str(eval))

				plt.savefig(dossier + "/paretoEval" + str(eval) + ".png", bbox_inches = 'tight')
				plt.close()

			# Tools.makeVideo(dossier)



def drawBestLeadership(dossier) :
	if os.path.isdir(dossier) :
		listBestLeadership = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^bestleadership(\d*)\.dat$", f))]

		hashProportion = {}
		hashProportionAsym = {}
		hashNbLeaderFirst = {}
		hashNbTotalCoop = {}

		lastGen = 0

		tabGeneration = []
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
				hashProportionAsym[run] = {}
				hashNbLeaderFirst[run] = {}
				hashNbTotalCoop[run] = {}

				# dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'proportion', 'proportionAsym', 'nb_leader_first', 'nb_total_coop'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float] })
				# data = np.loadtxt(dossier + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3, 4, 5), dtype = dtypes)
				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'proportion', 'proportionAsym'), 'formats' : [np.int, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3), dtype = dtypes)

				firstEval = True
				generation = 0
				for line in data :
					evaluation = line['evaluation']

					if generation % precision == 0 or firstEval :
						if generation < maxGen :
							hashProportion[run][generation] = line['proportion']
							hashProportionAsym[run][generation] = line['proportionAsym'] - 0.5
							# hashNbLeaderFirst[run][generation] = line['nb_leader_first']
							# hashNbTotalCoop[run][generation] = line['nb_total_coop']

							if generation not in tabGeneration :
								tabGeneration.append(generation)

							if lastGen < generation :
								lastGen = generation


					if firstEval :
						firstEval = False

					generation += 1

		tabGeneration = sorted(tabGeneration)

		while lastGen <= maxGen :
			lastGen += precision
			tabGeneration.append(lastGen)


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
		size = (1280/dpi, 1024/dpi)

		tabPlotGeneration = tabGeneration

		# --- BOXPLOT LEADERSHIP ---
		dataBoxPlot = []
		for generation in tabPlotGeneration :
			listProportion = [hashProportion[run][generation] for run in hashProportion.keys() if generation in hashProportion[run].keys()]

			if len(listProportion) > 0 :
				dataBoxPlot.append(listProportion)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)

		# axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
		# axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))

		axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
		axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
		axe1.set_xlabel("Generation")

		axe1.set_ylabel("Proportion of leadership")
		axe1.set_ylim(-0.1, 1.1)

		axe1.set_title('Boxplot of best proportion')

		plt.savefig(dossier + "/boxplot.png", bbox_inches = 'tight')
		plt.close()



		# --- RUNS LEADERSHIP ---
		for run in hashProportion.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			tabProportion = [hashProportion[run][generation] for generation in tabPlotGeneration if generation in hashProportion[run].keys()]

			axe1.plot(range(len(tabProportion)), tabProportion)

			# axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
			# axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))

			# Divide the x axis by 10
			tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')

			axe1.set_ylabel("Proportion of leadership")
			axe1.set_ylim(-0.1, 1.1)

			axe1.set_title('Best proportion')

			plt.savefig(dossier + "/proportionRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BOXPLOT LEADERSHIP ASYM ---
		dataBoxPlot = []
		for generation in tabPlotGeneration :
			listProportionAsym = [hashProportionAsym[run][generation] for run in hashProportionAsym.keys() if generation in hashProportionAsym[run].keys()]

			if len(listProportionAsym) > 0 :
				dataBoxPlot.append(listProportionAsym)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)

		axe1.add_line(lines.Line2D([0, lastGen], [0.5, 0.5], color="red"))
		axe1.add_line(lines.Line2D([0, lastGen], [-0.5, -0.5], color="red"))

		axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
		axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
		axe1.set_xlabel("Generation")

		axe1.set_ylabel("Proportion of leadership")
		axe1.set_ylim(-0.6, 0.6)

		axe1.set_title('Boxplot of best proportion')

		plt.savefig(dossier + "/boxplotAsym.png", bbox_inches = 'tight')
		plt.close()



		# --- RUNS LEADERSHIP ASYM ---
		for run in hashProportionAsym.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			tabProportionAsym = [hashProportionAsym[run][generation] for generation in tabPlotGeneration if generation in hashProportionAsym[run].keys()]

			axe1.plot(range(len(tabProportionAsym)), tabProportionAsym)

			axe1.add_line(lines.Line2D([0, lastGen], [0.5, 0.5], color="red"))
			axe1.add_line(lines.Line2D([0, lastGen], [-0.5, -0.5], color="red"))

			# Divide the x axis by 10
			tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')

			axe1.set_ylabel("Proportion of leadership")
			axe1.set_ylim(-0.6, 0.6)

			axe1.set_title('Boxplot of best proportion')

			plt.savefig(dossier + "/proportionAsymRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


def drawAllLeadership(dossier) :
	if os.path.isdir(dossier) :
		listAllLeadership = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^allleadershipevalstat(\d*)\.dat$", f))]

		hashProportion = {}
		hashProportionAsym = {}
		hashProportionGlob = {}
		hashNbLeaderFirst = {}
		hashNbTotalCoop = {}

		lastGen = 0

		maxFitness = 0
		tabGeneration = []
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
				hashProportionAsym[run] = {}
				hashNbLeaderFirst[run] = {}
				hashNbTotalCoop[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'proportion', 'proportionAsym'), 'formats' : [np.int, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileAll, delimiter=',', usecols = (0, 1, 2, 3), dtype = dtypes)
				# dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'proportion', 'proportionAsym', 'nb_leader_first', 'nb_total_coop'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float] })
				# data = np.loadtxt(dossier + "/" + fileAll, delimiter=',', usecols = (0, 1, 2, 3, 4, 5), dtype = dtypes)

				genDone = []
				lastEval = None
				generation = 0
				for line in data :
					evaluation = line['evaluation']

					if lastEval == None :
						lastEval = evaluation

					if evaluation != lastEval :
						generation += 1
						lastEval = evaluation

					if generation % precision == 0 or firstEval :
						if generation < maxGen :
							if generation not in genDone :
								hashProportion[run][generation] = []
								hashProportionAsym[run][generation] = []
								hashNbLeaderFirst[run][generation] = []
								hashNbTotalCoop[run][generation] = []

								hashFitnessGlob[generation] = []

								genDone.append(generation)

							hashProportion[run][generation].append(line['proportion'])
							hashProportionAsym[run][generation].append(line['proportionAsym'] - 0.5)
							hashFitnessGlob[generation].append(line['proportionAsym'] - 0.5)
							# hashNbLeaderFirst[run][generation].append(line['nb_leader_first'])
							# hashNbTotalCoop[run][generation].append(line['nb_total_coop'])

							if generation not in tabGeneration :
								tabGeneration.append(generation)

		tabGeneration = sorted(tabGeneration)

		while lastGen <= maxGen :
			lastGen += precision
			tabGeneration.append(lastGen)


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
		size = (1280/dpi, 1024/dpi)

		tabPlotGeneration = tabGeneration


		# --- BOXPLOT RUN PROPORTION ---
		dataBoxPlot = []
		for run in hashProportion.keys() :
			dataBoxPlot = [hashProportion[run][generation] for generation in tabPlotGeneration if generation in hashProportion[run].keys()]

			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
			axe1.boxplot(dataBoxPlot)
	
			# axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
			# axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))

			axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
			axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
			axe1.set_xlabel("Generation")

			axe1.set_ylabel("Proportion of leadership")
			axe1.set_ylim(-0.1, 1.1)

			axe1.set_title('Boxplot of population proportion')

			plt.savefig(dossier + "/proportionRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BOXPLOT ALL RUN PROPORTION ---
		dataBoxPlot = [hashProportionGlob[generation] for generation in tabPlotGeneration if generation in hashProportionGlob.keys()]

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)
	
		# axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
		# axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))

		axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
		axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
		axe1.set_xlabel("Generation")

		axe1.set_ylabel("Proportion of leadership")
		axe1.set_ylim(-0.1, 1.1)

		axe1.set_title('Boxplot of all proportions')

		plt.savefig(dossier + "/globalProportionAsym", bbox_inches = 'tight')
		plt.close()


		# --- BOXPLOT RUN PROPORTION ASYM ---
		dataBoxPlot = []
		for run in hashProportionAsym.keys() :
			dataBoxPlot = [hashProportionAsym[run][generation] for generation in tabPlotGeneration if generation in hashProportionAsym[run].keys()]

			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
			axe1.boxplot(dataBoxPlot)
	
			axe1.add_line(lines.Line2D([0, lastGen], [0.5, 0.5], color="red"))
			axe1.add_line(lines.Line2D([0, lastGen], [-0.5, -0.5], color="red"))

			axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
			axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
			axe1.set_xlabel("Generation")

			axe1.set_ylabel("Proportion of leadership")
			axe1.set_ylim(-0.6, 0.6)

			axe1.set_title('Boxplot of population proportion')

			plt.savefig(dossier + "/proportionAsymRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BOXPLOT ALL RUN PROPORTION ASYM ---
		dataBoxPlot = [hashProportionGlob[generation] for generation in tabPlotGeneration if generation in hashProportionGlob.keys()]

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)
	
		axe1.add_line(lines.Line2D([0, lastGen], [0.5, 0.5], color="red"))
		axe1.add_line(lines.Line2D([0, lastGen], [-0.5, -0.5], color="red"))

		axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
		axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
		axe1.set_xlabel("Generation")

		axe1.set_ylabel("Proportion of leadership")
		axe1.set_ylim(-0.6, 0.6)

		axe1.set_title('Boxplot of all proportions')

		plt.savefig(dossier + "/globalProportion", bbox_inches = 'tight')
		plt.close()



def drawBestNN(dossier) :
	if os.path.isdir(dossier) :
		listBestNN = [f for f in os.listdir(dossier) if (os.path.isfile(dossier + "/" + f) and re.match(r"^bestnn(\d*)\.dat$", f))]

		hashNbNN1Chosen = {}
		hashNbBiggerNN1Chosen = {}
		hashNbRoleDivisions = {}
		hashProportionNN1 = {}
		hashGenomeSize = {}

		lastGen = 0

		tabGeneration = []
		for fileBest in listBestNN :
			m = re.search(r'^bestnn(\d*)\.dat$', fileBest)
			run = int(m.group(1))

			testRun = None
			if selection != None :
				testRun = lambda run : run in selection
			elif exclusion != None :
				testRun = lambda run : run not in exclusion

			if (testRun == None) or (testRun(run)) :
				hashNbNN1Chosen[run] = {}
				hashNbBiggerNN1Chosen[run] = {}
				hashNbRoleDivisions[run] = {}
				hashProportionNN1[run] = {}
				hashGenomeSize[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nb_nn1_chosen', 'nb_bigger_nn1_chosen', 'nb_role_divisions', 'genome_size'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3, 4, 5), dtype = dtypes)

				firstEval = True
				lastGen = 0
				generation = 0
				for line in data :
					evaluation = line['evaluation']

					if generation % precision == 0 or firstEval :
						if generation < maxGen :
							hashNbNN1Chosen[run][generation] = line['nb_nn1_chosen']
							hashNbBiggerNN1Chosen[run][generation] = line['nb_bigger_nn1_chosen']

							if line['nb_nn1_chosen'] == 0 :
								hashProportionNN1[run][generation] = 0
							else :
								hashProportionNN1[run][generation] = ((line['nb_bigger_nn1_chosen']/line['nb_nn1_chosen'])*2) - 1

							hashNbRoleDivisions[run][generation] = line['nb_role_divisions']
							hashGenomeSize[run][generation] = line['genome_size']

							if generation not in tabGeneration :
								tabGeneration.append(generation)

							cpt = 0
		
							if lastGen < generation :
								lastGen = generation

					if firstEval :
						firstEval = False

					generation += 1

		tabGeneration = sorted(tabGeneration)

		while lastGen <= maxGen :
			lastGen += precision
			tabGeneration.append(lastGen)


		# SEABORN
		sns.set()
		sns.set_style('white')
		sns.set_context('paper')
		palette = sns.color_palette("husl", len(hashProportionNN1.keys()))

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


		# --- RUNS PROPORTION ASYM ---
		for run in hashProportionNN1.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			tabProportionNN1 = [hashProportionNN1[run][generation] for generation in tabPlotGeneration if generation in hashProportionNN1[run].keys()]

			axe1.plot(range(len(tabProportionNN1)), tabProportionNN1)

			axe1.add_line(lines.Line2D([0, lastGen], [1, 1], color="red"))
			axe1.add_line(lines.Line2D([0, lastGen], [-1, -1], color="red"))

			# Divide the x axis by 10
			tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')

			axe1.set_ylabel("Proportion")
			axe1.set_ylim(-1.1, 1.1)

			axe1.set_title('Choice of first nn')

			plt.savefig(dossier + "/proportionRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BOXPLOT ROLE DIVISION
		dataBoxPlot = []
		for generation in tabPlotGeneration :
			listRoleDivision = [hashNbRoleDivisions[run][generation] for run in hashNbRoleDivisions.keys() if generation in hashNbRoleDivisions[run].keys()]

			if len(listRoleDivision) > 0 :
				dataBoxPlot.append(listRoleDivision)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		bp = axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
		axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
		axe1.set_xlabel("Generation")

		axe1.set_ylabel("Proportion of role division")
		axe1.set_ylim(0, 1.1)

		axe1.set_title('Boxplot of role division')

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



		# --- RUNS ROLE DIVISION ---
		for run in hashNbRoleDivisions.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			tabRoleDivision = [hashNbRoleDivisions[run][generation] for generation in tabPlotGeneration if generation in hashNbRoleDivisions[run].keys()]

			axe1.plot(range(len(tabRoleDivision)), tabRoleDivision)

			# Divide the x axis by 10
			# tabGenerationTicks = [indice for indice in range(len(tabFitness)) if indice % (int(len(tabFitness)/10)) == 0]
			tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')

			axe1.set_ylabel("Proportion of role division")
			axe1.set_ylim(0, 1.1)

			# axe1.set_title('Best role', fontsize = 10)

			plt.savefig(dossier + "/roleDivisionRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()



		# --- GENOME SIZE ---
		palette = sns.color_palette("husl", 3)
		for run in hashGenomeSize.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			tabGenomeSize = [hashGenomeSize[run][generation] for generation in tabPlotGeneration if generation in hashGenomeSize[run].keys()]
			tabNNChoice = [hashNbNN1Chosen[run][generation] for generation in tabPlotGeneration if generation in hashNbNN1Chosen[run].keys()]

			axe1.plot(range(len(tabGenomeSize)), tabGenomeSize, color = palette[0])

			axe1.set_ylabel("Genome size", color = palette[0])
			axe1.set_ylim(0, 2000)
			for tl in axe1.get_yticklabels():
			    tl.set_color(palette[0])

			axe2 = axe1.twinx()

			axe2.plot(range(len(tabNNChoice)), tabNNChoice, color = palette[1])

			axe2.set_ylabel("Neural network choice", color = palette[1])
			axe2.set_ylim(-0.1, 1.1)
			for tl in axe2.get_yticklabels():
			    tl.set_color(palette[1])

			# Divide the x axis by 10
			# tabGenerationTicks = [indice for indice in range(len(tabFitness)) if indice % (int(len(tabFitness)/10)) == 0]
			tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]

			axe1.set_xticks(tabGenerationTicks)
			axe1.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe1.set_xlabel('Generation')

			axe2.set_xticks(tabGenerationTicks)
			axe2.set_xticklabels([tabPlotGeneration[indice] for indice in tabGenerationTicks])
			axe2.set_xlabel('Generation')

			# axe1.set_title('Best role', fontsize = 10)

			plt.savefig(dossier + "/genomeSizeRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()



def drawAllNN(dossier) :
	print('Not implemented !')


def draw(**parametres) : 
	global maxGen
	maxGen = parametres["argMax"]

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

			if parametres["argDiversity"] == True :
				if re.match(r'^BestDiv$', curDir) and parametres["argAll"] != True :
					print('\t -> Drawing bestdiv directory : ' + curDir)
					drawBestDiv(dossier + '/' + curDir)
				elif re.match(r'^AllDiv$', curDir) and parametres["argBest"] != True :
					print('\t -> Drawing alldiv directory : ' + curDir)
					drawAllDiv(dossier + '/' + curDir)
				elif re.match(r'^ParetoFront$', curDir) and not parametres["argNoDrawFit"] :
					print('\t -> Drawing pareto front : ' + curDir)
					# drawPareto(dossier + '/' + curDir)
				elif parametres["argDrawRun"] :
					m = re.match(r'^Dir(\d+)$', curDir)
					if m and not parametres["argNoDrawFit"] :
						run = int(m.group(1))
						print('\t -> Drawing Dir : ' + curDir)
						drawParetoRun(os.path.join(dossier, curDir), run)

			if parametres["argLeadership"] == True :
				if re.match(r'^BestLeadership$', curDir) and parametres["argAll"] != True :
					print('\t -> Drawing bestleadership directory : ' + curDir)
					drawBestLeadership(dossier + '/' + curDir)
				elif re.match(r'^AllLeadership$', curDir) and parametres["argBest"] != True :
					print('\t -> Drawing allleadership directory : ' + curDir)
					drawAllLeadership(dossier + '/' + curDir)

			if parametres["argNN"] == True :
				if re.match(r'^BestNN$', curDir) and parametres["argAll"] != True :
					print('\t -> Drawing bestNN directory : ' + curDir)
					drawBestNN(dossier + '/' + curDir)
				elif re.match(r'^AllNN$', curDir) and parametres["argBest"] != True :
					print('\t -> Drawing allNN directory : ' + curDir)
					drawAllNN(dossier + '/' + curDir)


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
									"argNN" : args.nn,
									"argDrawRun" : args.drawRun
								}
	draw(**parametres)



if __name__ == '__main__' :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('-m', '--max', help = "Max generation", default='20000')
	parser.add_argument('-p', '--precision', help = "Precision", default='10')

	parser.add_argument('-b', '--best', help = "Best only", default=False, action="store_true")
	parser.add_argument('-a', '--all', help = "All only", default=False, action="store_true")
	parser.add_argument('-d', '--diversity', help = "Drawing of diversity", default=False, action="store_true")
	parser.add_argument('-l', '--leadership', help = "Drawing of leadership", default=False, action="store_true")
	parser.add_argument('-n', '--nn', help = "Drawing of nn stat", default=False, action="store_true")
	parser.add_argument('-f', '--noDrawFit', help = "No drawing of the fitness", default=False, action="store_true")
	parser.add_argument('-u', '--drawRun', help = "Drawing of each run pareto frontier", default=False, action="store_true")

	parser.add_argument('-g', '--firstGen', help = "Size of population of first generation", default=10, type=int)
	parser.add_argument('-E', '--EvalByGen', help = "Number of evaluations by generation", default=20, type=int)

	parser.add_argument('-s', '--selection', help = "Selected runs", default=None, type=int, nargs='+')
	parser.add_argument('-e', '--exclusion', help = "Excluded runs", default=None, type=int, nargs='+')
	args = parser.parse_args()

	main(args)

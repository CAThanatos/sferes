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
selection = None
exclusion = None
precision = 100

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
		hashRatioSuccess = {}
		hashRatioHares = {}
		hashRatioHaresSuccess = {}

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
				hashRatioSuccess[run] = {}
				hashRatioHares[run] = {}
				hashRatioHaresSuccess[run] = {}

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
						cpt += lastEval - evaluation
						lastEval = evaluation

					if cpt%precision == 0 :
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
								hashRatioSuccess[run][evaluation] = []
								hashRatioHares[run][evaluation] = []
								hashRatioHaresSuccess[run][evaluation] = []

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
							hashRatioSuccess[run][evaluation].append((line['nbBStags'] - line['nbBStagsSolo'])*100/(line['nbHares'] + (line['nbBStags'] - line['nbBStagsSolo'])))
							hashRatioHares[run][evaluation].append(line['nbHares']*100/(line['nbHares'] + line['nbBStags']))
							hashRatioHaresSuccess[run][evaluation].append(line['nbHares']*100/(line['nbHares'] + (line['nbBStags'] - line['nbBStagsSolo'])))

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

		tabPlotGeneration = tabGeneration
		tabPlotEvaluation = tabEvaluation


		# --- MEAN RATIO BSTAGS ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		cpt = 0
		lastVals = []
		captions = []
		for run in hashFitness.keys() :
			tabRatio = [np.mean(hashRatio[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashRatio[run].keys()]
			axe1.plot(range(len(tabRatio)), tabRatio, color = palette[cpt])
			lastVals.append(tabRatio[-1])
			captions.append("Run " + str(run))

			cpt += 1

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
			normalizedLastVal = float(lastVal) / float(axe1.get_ylim()[1])
			normalizedY = float(y) * float(axe1.get_ylim()[1])
			rax.plot([lastVal, normalizedY], color=color)


		rax.set_axis_off()
		rax.set_ylim(0, 100)

		# Divide the x axis by 10
		tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]
		axe1.set_xticks(tabEvaluationTicks)
		axe1.set_xticklabels([tabGeneration[indice] for indice in tabEvaluationTicks])
		axe1.set_xlabel('Generation')

		axe1.set_ylabel('Pourcentage of stags hunted')
		axe1.set_ylim(0, 100)

		plt.savefig(dossier + "/figureRatioBStags.png", bbox_inches = 'tight')


		# --- MEAN RATIO BSTAGS SUCCESS ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		cpt = 0
		lastVals = []
		captions = []
		for run in hashFitness.keys() :
			tabRatio = [np.mean(hashRatioSuccess[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashRatioSuccess[run].keys()]
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
		tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]
		axe1.set_xticks(tabEvaluationTicks)
		axe1.set_xticklabels([tabGeneration[indice] for indice in tabEvaluationTicks])
		axe1.set_xlabel('Generation')

		axe1.set_ylabel('Pourcentage of stags hunted')
		# axe1.set_ylim(0, 100)

		plt.savefig(dossier + "/figureRatioBStagsSuccess.png", bbox_inches = 'tight')


		# --- MEAN RATIO HARES ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		palette = sns.color_palette("husl", len(hashNbBStags.keys()))
		cpt = 0
		lastVals = []
		captions = []
		for run in hashFitness.keys() :
			tabRatio = [np.mean(hashRatioHares[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashRatioHares[run].keys()]
			axe1.plot(range(len(tabRatio)), tabRatio, color = palette[cpt])

			lastVals.append(tabRatio[-1])
			captions.append("Run " + str(run))
			cpt += 1

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
			normalizedLastVal = float(lastVal) / float(axe1.get_ylim()[1])
			normalizedY = float(y) * float(axe1.get_ylim()[1])
			rax.plot([lastVal, normalizedY], color=color)


		rax.set_axis_off()
		rax.set_ylim(0, 100)


		# Divide the x axis by 10
		tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]
		axe1.set_xticks(tabEvaluationTicks)
		axe1.set_xticklabels([tabGeneration[indice] for indice in tabEvaluationTicks])
		axe1.set_xlabel('Generation')

		axe1.set_ylabel('Pourcentage of hares hunted')
		axe1.set_ylim(0, 100)

		plt.savefig(dossier + "/figureRatioHares.png", bbox_inches = 'tight')


		# --- MEAN RATIO HARES SUCCESS ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		palette = sns.color_palette("husl", len(hashNbBStags.keys()))
		cpt = 0
		lastVals = []
		captions = []
		for run in hashFitness.keys() :
			tabRatio = [np.mean(hashRatioHaresSuccess[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashRatioHaresSuccess[run].keys()]
			axe1.plot(range(len(tabRatio)), tabRatio, color = palette[cpt])

			lastVals.append(tabRatio[-1])
			captions.append("Run " + str(run))
			cpt += 1

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
			normalizedLastVal = float(lastVal) / float(axe1.get_ylim()[1])
			normalizedY = float(y) * float(axe1.get_ylim()[1])
			rax.plot([lastVal, normalizedY], color=color)


		rax.set_axis_off()
		rax.set_ylim(0, 100)


		# Divide the x axis by 10
		tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]
		axe1.set_xticks(tabEvaluationTicks)
		axe1.set_xticklabels([tabGeneration[indice] for indice in tabEvaluationTicks])
		axe1.set_xlabel('Generation')

		axe1.set_ylabel('Pourcentage of hares hunted')
		axe1.set_ylim(0, 100)

		plt.savefig(dossier + "/figureRatioHaresSuccess.png", bbox_inches = 'tight')


		# --- NUMBER OF PREYS HUNTED ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		palette = sns.color_palette("husl", len(hashNbBStags.keys()))
		firstGraphStags = None
		firstGraphHares = None
		cpt = 0
		for run in hashNbBStags.keys() :
			tabNbBStags = [np.mean(hashNbBStags[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbBStags[run].keys()]
			tabNbHares = [np.mean(hashNbHares[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbHares[run].keys()]

			tmp1, = axe1.plot(range(len(tabNbBStags)), tabNbBStags, color = palette[cpt])
			tmp2, = axe1.plot(range(len(tabNbHares)), tabNbHares, color = palette[cpt], linestyle = "--")

			if firstGraphStags == None :
				firstGraphStags = tmp1

			if firstGraphHares == None :
				firstGraphHares = tmp2

			cpt += 1

		# Divide the x axis by 10
		tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]
		axe1.set_xticks(tabEvaluationTicks)
		axe1.set_xticklabels([tabGeneration[indice] for indice in tabEvaluationTicks])
		axe1.set_xlabel('Generation')

		axe1.set_ylabel('Number of preys hunted')

		plt.legend([firstGraphStags, firstGraphHares], ['Stags', 'Hares'], bbox_to_anchor=(0., 0., 1., .102), frameon = True)

		plt.savefig(dossier + "/figureNbPreys.png", bbox_inches = 'tight')


		# --- BARS NUMBER OF PREYS ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		width = 0.5
		tabPlotRun = [run for run in sorted(hashNbBStags.keys())]
		tabNbHares = [np.mean(hashNbHares[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbHares[run].keys() else sorted(hashNbHares[run].keys())[-1]]) for run in tabPlotRun]
		tabNbHaresStd = [np.std(hashNbHares[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbHares[run].keys() else sorted(hashNbHares[run].keys())[-1]]) for run in tabPlotRun]
		tabNbBStags = [np.mean(hashNbBStags[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStags[run].keys() else sorted(hashNbBStags[run].keys())[-1]]) for run in tabPlotRun]
		tabNbBStagsStd = [np.std(hashNbBStags[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStags[run].keys() else sorted(hashNbBStags[run].keys())[-1]]) for run in tabPlotRun]

		barNbHares = axe1.bar(range(len(tabNbHares)), tabNbHares, width = width, color = 'lime', alpha = 0.5, yerr = tabNbHaresStd, ecolor = 'black')
		barNbBStags = axe1.bar(range(len(tabNbBStags)), tabNbBStags, bottom = tabNbHares, width = width, color = 'magenta', alpha = 0.5, yerr = tabNbBStagsStd, ecolor = 'black')

		axe1.set_xticks(np.add(np.arange(len(tabPlotRun)), width/2))
		axe1.set_xticklabels(tabPlotRun)
		# axe1.set_xticklabels(np.add(np.arange(len(tabPlotRun)), 1))
		axe1.set_xlim(0, len(tabNbBStags))
#		axe1.set_xticklabels(tabPlotRun)
		axe1.set_xlabel('Run')

		axe1.set_ylabel('Number of preys hunted')
		axe1.set_ylim(0)

		plt.legend([barNbHares, barNbBStags], ['Hares', 'Stags'], frameon = True)

		plt.savefig(dossier + "/figureBarsNbPreys.png", bbox_inches = 'tight')


		# --- NUMBER OF PREYS HUNTED SUCCESS ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		palette = sns.color_palette("husl", len(hashNbBStagsDuo.keys()))
		firstGraphStags = None
		firstGraphHares = None
		cpt = 0
		for run in hashNbBStagsDuo.keys() :
			tabNbBStags = [np.mean(hashNbBStagsDuo[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbBStagsDuo[run].keys()]
			tabNbHares = [np.mean(hashNbHares[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbHares[run].keys()]

			tmp1, = axe1.plot(range(len(tabNbBStags)), tabNbBStags, color = palette[cpt])
			tmp2, = axe1.plot(range(len(tabNbHares)), tabNbHares, color = palette[cpt], linestyle = "--")

			if firstGraphStags == None :
				firstGraphStags = tmp1

			if firstGraphHares == None :
				firstGraphHares = tmp2

			cpt += 1

		# Divide the x axis by 10
		tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]
		axe1.set_xticks(tabEvaluationTicks)
		axe1.set_xticklabels([tabGeneration[indice] for indice in tabEvaluationTicks])
		axe1.set_xlabel('Generation')

		axe1.set_ylabel('Number of preys hunted')

		plt.legend([firstGraphStags, firstGraphHares], ['Stags', 'Hares'], bbox_to_anchor=(0., 0., 1., .102), frameon = True)

		plt.savefig(dossier + "/figureNbPreysSuccess.png", bbox_inches = 'tight')


		# --- BARS NUMBER OF PREYS COOP ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		width = 0.5
		tabPlotRun = [run for run in sorted(hashNbBStags.keys())]
		tabNbHares = [np.mean(hashNbHares[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbHares[run].keys() else sorted(hashNbHares[run].keys())[-1]]) for run in tabPlotRun]
		tabNbHaresStd = [np.std(hashNbHares[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbHares[run].keys() else sorted(hashNbHares[run].keys())[-1]]) for run in tabPlotRun]
		tabNbBStagsDuo = [np.mean(hashNbBStagsDuo[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStagsDuo[run].keys() else sorted(hashNbBStagsDuo[run].keys())[-1]]) for run in tabPlotRun]
		tabNbBStagsDuoStd = [np.std(hashNbBStagsDuo[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStagsDuo[run].keys() else sorted(hashNbBStagsDuo[run].keys())[-1]]) for run in tabPlotRun]
		tabNbBStagsSolo = [np.mean(hashNbBStagsSolo[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStagsSolo[run].keys() else sorted(hashNbBStagsSolo[run].keys())[-1]]) for run in tabPlotRun]
		tabNbBStagsSoloStd = [np.std(hashNbBStagsSolo[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStagsSolo[run].keys() else sorted(hashNbBStagsSolo[run].keys())[-1]]) for run in tabPlotRun]

		barNbHares = axe1.bar(range(len(tabNbHares)), tabNbHares, width = width, color = 'lime', alpha = 0.5, yerr = tabNbHaresStd, ecolor = 'black')
		barNbBStagsDuo = axe1.bar(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, bottom = tabNbHares, width = width, color = 'magenta', alpha = 0.5, yerr = tabNbBStagsDuoStd, ecolor = 'black')
		barNbBStagsSolo = axe1.bar(range(len(tabNbBStagsSolo)), tabNbBStagsSolo, bottom = np.add(tabNbHares, tabNbBStagsDuo), width = width, color = 'grey', alpha = 0.5, yerr = tabNbBStagsSoloStd, ecolor = 'black')

		axe1.set_xticks(np.add(np.arange(len(tabPlotRun)), width/2))
		axe1.set_xticklabels(tabPlotRun)
		# axe1.set_xticklabels(np.add(np.arange(len(tabPlotRun)), 1))
		axe1.set_xlim(0, len(tabNbBStagsDuo))
#		axe1.set_xticklabels(tabPlotRun)
		axe1.set_xlabel('Run')

		axe1.set_ylabel('Number of preys hunted')
		axe1.set_ylim(0)

		plt.legend([barNbHares, barNbBStagsDuo, barNbBStagsSolo], ['Hares', 'Stags coop.', 'Stags solo'], frameon = True)

		plt.savefig(dossier + "/figureBarsNbPreysSuccess.png", bbox_inches = 'tight')


		# --- COOPERATION ON BSTAGS ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		palette = sns.color_palette("husl", len(hashNbBStags.keys()))
		firstGraphTotal = None
		firstGraphCoop = None
		cpt = 0
		for run in hashNbBStags.keys() :
			tabNbBStags = [np.mean(hashNbBStags[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbBStags[run].keys()]
			tabNbBStagsDuo = [np.mean(hashNbBStagsDuo[run][evaluation]) for evaluation in tabPlotEvaluation if evaluation in hashNbBStagsDuo[run].keys()]

			tmp1, = axe1.plot(range(len(tabNbBStags)), tabNbBStags, color = palette[cpt])
			tmp2, = axe1.plot(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, color = palette[cpt], linestyle = "--")

			if firstGraphTotal == None :
				firstGraphTotal = tmp1

			if firstGraphCoop == None :
				firstGraphCoop = tmp2

			cpt += 1

		# Divide the x axis by 10
		tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]
		axe1.set_xticks(tabEvaluationTicks)
		axe1.set_xticklabels([tabGeneration[indice] for indice in tabEvaluationTicks])
		axe1.set_xlabel('Generation')

		axe1.set_ylabel('Number of preys hunted')

		plt.legend([firstGraphTotal, firstGraphCoop], ['Solo', 'Coop.'], bbox_to_anchor=(0., 0., 1., .102), frameon = True)

		plt.savefig(dossier + "/figureBStagsCoop.png", bbox_inches = 'tight')


		# --- BARS COOP BSTAGS ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		width = 0.5
		tabPlotRun = [run for run in sorted(hashNbBStagsSolo.keys())]
		tabNbBStagsSolo = [np.mean(hashNbBStagsSolo[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStagsSolo[run].keys() else sorted(hashNbBStagsSolo[run].keys())[-1]]) for run in tabPlotRun]
		tabNbBStagsSoloStd = [np.std(hashNbBStagsSolo[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStagsSolo[run].keys() else sorted(hashNbBStagsSolo[run].keys())[-1]]) for run in tabPlotRun]
		tabNbBStagsDuo = [np.mean(hashNbBStagsDuo[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStagsDuo[run].keys() else sorted(hashNbBStagsDuo[run].keys())[-1]]) for run in tabPlotRun]
		tabNbBStagsDuoStd = [np.std(hashNbBStagsDuo[run][tabPlotEvaluation[-1] if tabPlotEvaluation[-1] in hashNbBStagsDuo[run].keys() else sorted(hashNbBStagsDuo[run].keys())[-1]]) for run in tabPlotRun]

		barNbBStagsSolo = axe1.bar(range(len(tabNbBStagsSolo)), tabNbBStagsSolo, width = width, color = 'magenta', alpha = 0.5, yerr = tabNbBStagsSoloStd, ecolor = 'black')
		barNbBStagsDuo = axe1.bar(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, bottom = tabNbBStagsSolo, width = width, color = 'purple', alpha = 0.5, yerr = tabNbBStagsDuoStd, ecolor = 'black')

		axe1.set_xticks(np.add(np.arange(len(tabPlotRun)), width/2))
		axe1.set_xticklabels(tabPlotRun)
		# axe1.set_xticklabels(np.add(np.arange(len(tabPlotRun)), 1))
		axe1.set_xlim(0, len(tabNbBStagsSolo))
#		axe1.set_xticklabels(tabPlotRun)
		axe1.set_xlabel('Run')

		axe1.set_ylabel('Number of preys hunted')
		axe1.set_ylim(0)

		plt.legend([barNbBStagsSolo, barNbBStagsDuo], ['Solo', 'Coop.'], frameon = True)

		plt.savefig(dossier + "/figureBarsBStagsCoop.png", bbox_inches = 'tight')





def draw(**parametres) : 
	global maxEval
	maxEval = parametres["argMax"]

	global maxGen
	maxGen = parametres["argMaxGen"]

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
					drawPareto(dossier + '/' + curDir)
				elif parametres["argDrawRun"] :
					m = re.match(r'^Dir(\d+)$', curDir)
					if m and not parametres["argNoDrawFit"] :
						run = int(m.group(1))
						print('\t -> Drawing Dir : ' + curDir)
						drawParetoRun(os.path.join(dossier, curDir), run)


def main(args) :
	parametres =  { 
									"argMax" : int(arg.max),
									"argMaxGen" : int(arg.maxGen),
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
									"argDrawRun" : args.drawRun
								}
	draw(**parametres)



if __name__ == '__main__' :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('-m', '--max', help = "Max evaluation", default='20000')
	parser.add_argument('-M', '--maxGen', help = "Max generation", default='1000')
	parser.add_argument('-p', '--precision', help = "Precision", default='100')

	parser.add_argument('-b', '--best', help = "Best only", default=False, action="store_true")
	parser.add_argument('-a', '--all', help = "All only", default=False, action="store_true")
	parser.add_argument('-d', '--diversity', help = "Drawing of diversity", default=False, action="store_true")
	parser.add_argument('-f', '--noDrawFit', help = "No drawing of the fitness", default=False, action="store_true")
	parser.add_argument('-u', '--drawRun', help = "Drawing of each run pareto frontier", default=False, action="store_true")

	parser.add_argument('-g', '--firstGen', help = "Size of population of first generation", default=10, type=int)
	parser.add_argument('-E', '--EvalByGen', help = "Number of evaluations by generation", default=20, type=int)

	parser.add_argument('-s', '--selection', help = "Selected runs", default=None, type=int, nargs='+')
	parser.add_argument('-e', '--exclusion', help = "Excluded runs", default=None, type=int, nargs='+')
	args = parser.parse_args()

	main(args)
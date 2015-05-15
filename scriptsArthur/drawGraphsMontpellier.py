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

from pylab import Polygon
from scipy import stats

import os
import argparse
import re
import math
import shutil


maxGen = 40000
precision = 100
startGen = 0
selection = None
exclusion = None
directories = None
outputDir = "GraphsResults"
drawStatAnalysis = False
removeOutput = False

colorHaresSolo = 'lime'
colorHaresDuo = 'green'
colorErrorHares = 'black'
alphaHares = 1
colorBStagsSolo = 'magenta'
colorBStagsDuo = 'purple'
colorErrorBStags = 'black'
alphaBStags = 1
# colorSStagsSolo = 'cyan'
# colorSStagsDuo = 'steelblue'
colorSStagsSolo = 'lime'
colorSStagsDuo = 'green'
colorErrorSStags = 'black'
alphaSStags = 1
colorTotal = 'grey'
colorErrorTotal = 'black'
alphaTotal = 1



# SEABORN
sns.set()
sns.set_style('white')
sns.set_context('paper')
palette = sns.color_palette("husl", 4)

# MATPLOTLIB PARAMS
matplotlib.rcParams['font.size'] = 15
matplotlib.rcParams['font.weight'] = 'bold'
matplotlib.rcParams['axes.labelsize'] = 15
matplotlib.rcParams['axes.labelweight'] = 'bold'
matplotlib.rcParams['xtick.labelsize'] = 15
matplotlib.rcParams['ytick.labelsize'] = 15
matplotlib.rcParams['legend.fontsize'] = 15

# GRAPHS GLOBAL VARIABLES
linewidth = 2
# linestyles = ['-', '--', '-.']
linestyles = ['-', '-', '-', '-']
markers = [None, None, None, None] #['o', '+', '*']

dpi = 96
size = (1280/dpi, 1024/dpi)



def drawHuntingTask() :
	if os.path.isdir(outputDir) :
		if removeOutput :
			shutil.rmtree(outputDir)
			os.makedirs(outputDir)
	else :
		os.makedirs(outputDir)


	tabGeneration = []
	dataHash = []
	for directory in directories :
		if os.path.isdir(directory) :
			listBestFit = [f for f in os.listdir(directory) if (os.path.isfile(directory + "/" + f) and re.match(r"^bestfit(\d*)\.dat$", f))]

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

			# tabEvaluation = []
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
					data = np.loadtxt(directory + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

					cpt = 0
					firstEval = True
					lastEval = 0
					maxGenDone = False
					generation = 0 - startGen
					for line in data :
						evaluation = line['evaluation']

						if generation % precision == 0 or firstEval :
							if generation >= 0 and generation <= maxGen :
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

								# hashRatio[run][generation] = line['nbBStags']*100/(line['nbHares'] + line['nbBStags'])
								hashRatioSuccess[run][generation] = (line['nbBStags'] - line['nbBStagsSolo'])*100/(line['nbSStags'] + (line['nbBStags'] - line['nbBStagsSolo'])) 
								# hashRatioHares[run][generation] = line['nbHares']*100/(line['nbHares'] + line['nbBStags'])
								hashRatio[run][generation] = 0
								# hashRatioSuccess[run][generation] = 0
								hashRatioHares[run][generation] = 0

								if generation not in tabGeneration :
									tabGeneration.append(generation)

								cpt = 0

								# if generation > maxGen :
								# 	maxGenDone = True

								if firstEval :
									firstEval = False


						generation += 1

			hashData = {}
			hashData["hashFitness"] = hashFitness

			hashData["hashNbHares"] = hashNbHares
			hashData["hashNbHaresSolo"] = hashNbHaresSolo
			hashData["hashNbHaresDuo"] = hashNbHaresDuo
			
			hashData["hashNbSStags"] = hashNbSStags
			hashData["hashNbSStagsSolo"] = hashNbSStagsSolo
			hashData["hashNbSStagsDuo"] = hashNbSStagsDuo
			
			hashData["hashNbBStags"] = hashNbBStags
			hashData["hashNbBStagsSolo"] = hashNbBStagsSolo
			hashData["hashNbBStagsDuo"] = hashNbBStagsDuo

			hashData["hashRatio"] = hashRatio
			hashData["hashRatioSuccess"] = hashRatioSuccess
			hashData["hashRatioHares"] = hashRatioHares

			dataHash.append(hashData)



	tabGeneration = sorted(tabGeneration)

	hashRunStags = []
	for data in dataHash :
		hashNbBStags = data['hashNbBStags']
		hashNbBStagsDuo = data['hashNbBStagsDuo']
		hashNbHares = data['hashNbHares']
		runStags = []

		for run in hashNbBStags.keys() :
			lastGenRun = sorted(hashNbHares[run].keys())[-1]

			# if hashNbBStags[run][lastGenRun] > hashNbHares[run][lastGenRun] and hashNbBStags[run][lastGenRun] > 1 :
			# 	runStags.append(run)
			if hashNbBStagsDuo[run][lastGenRun] > hashNbHares[run][lastGenRun] and hashNbBStagsDuo[run][lastGenRun] > 1 :
				runStags.append(run)

		hashRunStags.append(runStags)


	tabPlotGeneration = tabGeneration


	# Fitness Boxplots Stags
	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# plt.axes(frameon=0)
	plt.grid()

	cptData = 0
	for data in dataHash :
		dataPlot = []
		hashFitness = data['hashFitness']
		hashNbBStags = data['hashNbBStags']
		hashNbBStagsDuo = data['hashNbBStagsDuo']
		hashNbHares = data['hashNbHares']

		for generation in tabPlotGeneration :
			proportionGen = float(len([run for run in hashFitness.keys() if hashNbBStagsDuo[run][generation] > hashNbSStags[run][generation] and hashNbBStagsDuo[run][generation] > 1]))/float(len(hashFitness.keys()))

			dataPlot.append(proportionGen)

		# cpt = 0
		# while cpt < len(dataPlot) :
		# 	if math.isnan(dataPlot[cpt]) :
		# 		if cpt > 0 and cpt < len(dataPlot) - 1 :
		# 			dataPlot[cpt] = (dataPlot[cpt + 1] + dataPlot[cpt - 1])/2
		# 			dataPerc25[cpt] = (dataPerc25[cpt + 1] + dataPerc25[cpt - 1])/2
		# 			dataPerc75[cpt] = (dataPerc75[cpt + 1] + dataPerc75[cpt - 1])/2
		# 		elif cpt > 0 :
		# 			dataPlot[cpt] = dataPlot[cpt - 1]
		# 			dataPerc25[cpt] = dataPerc25[cpt - 1]
		# 			dataPerc75[cpt] = dataPerc75[cpt - 1]
		# 		else :
		# 			dataPlot[cpt] = dataPlot[cpt + 1]
		# 			dataPerc25[cpt] = dataPerc25[cpt + 1]
		# 			dataPerc75[cpt] = dataPerc75[cpt + 1]

		# 	cpt += 1

		axe1.plot(range(len(dataPlot)), dataPlot, color=palette[cptData], linestyle=linestyles[cptData], linewidth=linewidth, marker=markers[cptData])

		# plt.fill_between(range(len(dataPlot)), dataPerc25, dataPerc75, alpha=0.25, linewidth=0, color=palette[cptData])

		cptData += 1


	tabPlotTicks = []
	for generation in tabPlotGeneration :
		if generation > maxGen :
			tabPlotTicks.append(maxGen)
		else :
			tabPlotTicks.append(generation)

	ticks = range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/5))
	if len(tabPlotGeneration) - 1 not in ticks :
		ticks.append(len(tabPlotGeneration) - 1)

	axe1.set_xticks(ticks)
	axe1.set_xticklabels([tabPlotTicks[x] for x in ticks])
	axe1.set_xlabel("Generation")
	axe1.set_xlim(0, len(tabPlotGeneration) - 1)

	axe1.set_ylabel("Proportion of Cooperative Runs")
	axe1.set_ylim(-0.1, 1.1)

	# legend = plt.legend(['Control Without Leadership', 'Control With Leaderhip', 'Without Leadership', 'With Leadership'], loc = 4, frameon=True)
	# frame = legend.get_frame()
	# frame.set_facecolor('0.9')
	# frame.set_edgecolor('0.9')

	# axe1.set_title('Boxplot of best fitness')

	plt.savefig(outputDir + "/proportionStags.png", bbox_inches = 'tight')
	plt.savefig(outputDir + "/proportionStags.svg", bbox_inches = 'tight')
	plt.close()

	# --- BARS ---
	cptData = 0
	tabDirs = ['ControlWoLeadership','ControlWLeadership', 'WoLeadership', 'WLeadership']
	for data in dataHash :
		outputData = os.path.join(outputDir, tabDirs[cptData])

		if os.path.isdir(outputData) :
			if removeOutput :
				shutil.rmtree(outputData)
				os.makedirs(outputData)
		else :
			os.makedirs(outputData)

		hashNbHaresSolo = data['hashNbHaresSolo']
		hashNbHaresDuo = data['hashNbHaresDuo']
		hashNbSStagsSolo = data['hashNbSStagsSolo']
		hashNbSStagsDuo = data['hashNbSStagsDuo']
		hashNbBStagsSolo = data['hashNbBStagsSolo']
		hashNbBStagsDuo = data['hashNbBStagsDuo']

		for run in hashNbHaresSolo.keys() :
			if run in [2, 8, 22] :
				fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
				plt.grid()

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


				tabPlotTicks = []
				for generation in tabPlotGeneration :
					if generation > maxGen :
						tabPlotTicks.append(maxGen)
					else :
						tabPlotTicks.append(generation)

				ticks = range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/5))
				if len(tabPlotGeneration) - 1 not in ticks :
					ticks.append(len(tabPlotGeneration) - 1)

				axe1.set_xticks(ticks)
				axe1.set_xticklabels([tabPlotTicks[x] for x in ticks])
				axe1.set_xlabel("Generation")
				axe1.set_xlim(0, len(tabPlotGeneration) - 1)

				axe1.set_ylim(0, 20)
				axe1.set_ylabel('Number of preys hunted')
				
				# axe1.set_title('Repartition of preys hunted', fontsize = 10)

				# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Stags solo', 'Stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
				# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbSStagsSolo, barNbSStagsDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Small stags solo', 'Small stags coop.', 'Big stags solo', 'Big stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

				plt.savefig(outputData + "/preysRun" + str(run) + ".png", bbox_inches = 'tight')
				plt.savefig(outputData + "/preysRun" + str(run) + ".svg", bbox_inches = 'tight')
				plt.close()

		cptData += 1


	# --- MEAN RATIO BSTAGS SUCCESS ---
	cptData = 0
	for data in dataHash :
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		plt.grid()

		hashRatioSuccess = data['hashRatioSuccess']

		cpt = 0
		lastVals = []
		captions = []
		for run in hashFitness.keys() :
			tabRatio = [np.mean(hashRatioSuccess[run][generation]) for generation in tabPlotGeneration if generation in hashRatioSuccess[run].keys()]
			axe1.plot(range(len(tabRatio)), tabRatio, color = palette[cpt])
			lastVals.append(tabRatio[-1])
			captions.append("Run " + str(run))

			cpt += 1

		axe1.set_ylim(-5, 105)

		sortedVals = zip(*(sorted(zip(lastVals, range(len(lastVals))), key = itemgetter(0))))
		sortedLastVals = sortedVals[0]
		sortedIndexes = sortedVals[1]

		# Create new axes on the right containing captions
		# divider = make_axes_locatable(axe1)
		# rax = divider.append_axes("right", size="25%", pad=0.00)

		# # Add captions text on axis, and lines
		# yCaptionsCoords = np.linspace(0., 1., len(sortedIndexes))
		# connectionLinesCoords = []
		# for y, i in zip(yCaptionsCoords, sortedIndexes):
		# 	cap = captions[i]
		# 	lastVal = lastVals[i]
		# 	color = palette[i]
		# 	rax.text(1.10, y, cap,
		# 			horizontalalignment='left',
		# 			verticalalignment='center',
		# 			transform = rax.transAxes)

		# 	# Add lines
		# 	normalizedY = float(y) * float(axe1.get_ylim()[1])
		# 	rax.plot([lastVal, normalizedY], color=color)


		# rax.set_axis_off()
		# rax.set_ylim(0, 100)

		tabPlotTicks = []
		for generation in tabPlotGeneration :
			if generation > maxGen :
				tabPlotTicks.append(maxGen)
			else :
				tabPlotTicks.append(generation)

		ticks = range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/5))
		if len(tabPlotGeneration) - 1 not in ticks :
			ticks.append(len(tabPlotGeneration) - 1)

		axe1.set_xticks(ticks)
		axe1.set_xticklabels([tabPlotTicks[x] for x in ticks])
		axe1.set_xlabel("Generation")
		axe1.set_xlim(0, len(tabPlotGeneration) - 1)

		# Divide the x axis by 10
		# tabGenerationTicks = [indice for indice in range(len(tabPlotGeneration)) if indice % (int(len(tabPlotGeneration)/10)) == 0]
		# axe1.set_xticks(tabGenerationTicks)
		# axe1.set_xticklabels([tabGeneration[indice] for indice in tabGenerationTicks])
		# axe1.set_xlabel('Generation')

		axe1.set_ylabel('Pourcentage of stags hunted')
		# axe1.set_ylim(0, 100)

		plt.savefig(outputDir + "/figureRatioBStagsSuccess" + tabDirs[cptData] + ".png", bbox_inches = 'tight')
		plt.savefig(outputDir + "/figureRatioBStagsSuccess" + tabDirs[cptData] + ".svg", bbox_inches = 'tight')

		cptData += 1



def drawLeadership() :
	if os.path.isdir(outputDir) :
		if removeOutput :
			shutil.rmtree(outputDir)
			os.makedirs(outputDir)
	else :
		os.makedirs(outputDir)

	tabGeneration = []
	dataHash = []

	for directory in directories :
		if os.path.isdir(directory) :
			listBestLeadership = [f for f in os.listdir(directory) if (os.path.isfile(directory + "/" + f) and re.match(r"^bestleadership(\d*)\.dat$", f))]

			hashProportion = {}
			hashProportionAsym = {}
			hashNbLeaderFirst = {}
			hashNbTotalCoop = {}

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
					# data = np.loadtxt(directory + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3, 4, 5), dtype = dtypes)
					dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'proportion', 'proportionAsym'), 'formats' : [np.int, np.float, np.float, np.float] })
					data = np.loadtxt(directory + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3), dtype = dtypes)

					cpt = 0
					firstEval = True
					lastEval = 0
					maxEvalDone = False
					generation = 0 - startGen
					for line in data :
						evaluation = line['evaluation']

						if generation % precision == 0 or firstEval :
							if generation >= 0 and generation <= maxGen :
								hashProportion[run][generation] = line['proportion']
								hashProportionAsym[run][generation] = line['proportionAsym'] - 0.5
								# hashNbLeaderFirst[run][evaluation] = line['nb_leader_first']
								# hashNbTotalCoop[run][evaluation] = line['nb_total_coop']

								if generation not in tabGeneration :
									tabGeneration.append(generation)

								cpt = 0


								if firstEval :
									firstEval = False

						generation += 1


			hashData = {}
			hashData["hashProportion"] = hashProportion
			hashData["hashProportionAsym"] = hashProportionAsym

			dataHash.append(hashData)


	tabGeneration = sorted(tabGeneration)
	# lastEval = tabEvaluation[-1]
	# diffEvals = lastEval - tabEvaluation[-2]

	# while lastEval <= maxEval :
	# 	lastEval += diffEvals
	# 	tabEvaluation.append(lastEval)

	hashRunSuccess = []
	for data in dataHash :
		hashProportion = data['hashProportion']
		runSuccess = []

		for run in hashProportion.keys() :
			lastGenerationRun = sorted(hashProportion[run].keys())[-1]

			if hashProportion[run][lastGenerationRun] > 0.75 :
				runSuccess.append(run)

		hashRunSuccess.append(runSuccess)


	tabPlotGeneration = tabGeneration


	# Fitness Boxplots
	cptData = 0
	tabDirs = ['ControlWoLeadership', 'ControlWLeadership', 'WoLeaderhip', 'WLeadership']
	for data in dataHash :
		outputData = os.path.join(outputDir, tabDirs[cptData])

		if os.path.isdir(outputData) :
			if removeOutput :
				shutil.rmtree(outputData)
				os.makedirs(outputData)
		else :
			os.makedirs(outputData)

		hashProportion = data['hashProportion']

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		plt.grid()

		dataBoxPlot = []

		tabGens = []
		for generation in tabPlotGeneration :
			listProportion = [hashProportion[run][generation] for run in hashProportion.keys() if generation in hashProportion[run].keys()]

			if len(listProportion) > 0 :
				dataBoxPlot.append(listProportion)
				tabGens.append(generation)

		bp = axe1.boxplot(dataBoxPlot)

		for i in range(0, len(bp['boxes'])):
			# We fill the boxes
			box = bp['boxes'][i]
			box.set_linewidth(0)
			boxX = []
			boxY = []

			for j in range(5) :
				boxX.append(box.get_xdata()[j])
				boxY.append(box.get_ydata()[j])

			boxCoords = zip(boxX, boxY)
			boxPolygon = Polygon(boxCoords, facecolor = palette[2], linewidth = 0)
			axe1.add_patch(boxPolygon)

			bp['boxes'][i].set_color(palette[2])

			# we have two whiskers!
			bp['whiskers'][i*2].set_color(palette[2])
			bp['whiskers'][i*2 + 1].set_color(palette[2])
			bp['whiskers'][i*2].set_linewidth(2)
			bp['whiskers'][i*2 + 1].set_linewidth(2)

			# top and bottom fliers
			# (set allows us to set many parameters at once)
			# if (i * 2 + 1) < len(bp['fliers']) :
			# 	bp['fliers'][i * 2].set(markerfacecolor=palette[2],
			# 	                marker='o', alpha=0.75, markersize=6,
			# 	                markeredgecolor='none')
			# 	bp['fliers'][i * 2 + 1].set(markerfacecolor=palette[2],
			# 	                marker='o', alpha=0.75, markersize=6,
			# 	                markeredgecolor='none')


			bp['medians'][i].set_color('black')
			bp['medians'][i].set_linewidth(3)

			# and 4 caps to remove
			for c in bp['caps']:
			   c.set_linewidth(0)

		axe1.add_line(lines.Line2D([0, maxGen], [1, 1], color="red"))

		tabPlotTicks = []
		for generation in tabPlotGeneration :
			if generation > maxGen :
				tabPlotTicks.append(maxGen)
			else :
				tabPlotTicks.append(generation)

		ticks = range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/5))
		if len(tabPlotGeneration) - 1 not in ticks :
			ticks.append(len(tabPlotGeneration) - 1)

		axe1.set_xticks(ticks)
		axe1.set_xticklabels([tabPlotTicks[x] for x in ticks])
		axe1.set_xlabel("Generation")
		axe1.set_xlim(0, len(tabPlotGeneration) - 1)

		axe1.set_ylabel("Proportion")
		axe1.set_ylim(0, 1.1)

		# axe1.set_title('Boxplot of best fitness')

		plt.savefig(outputData + "/boxplotLeadership.png", bbox_inches = 'tight')
		plt.savefig(outputData + "/boxplotLeadership.svg", bbox_inches = 'tight')
		plt.close()

		cptData += 1




	# # Fitness Boxplots
	# fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# # plt.axes(frameon=0)
	# plt.grid()

	# cptData = 0
	# for data in dataHash :
	# 	dataPlot = []
	# 	dataPerc25 = []
	# 	dataPerc75 = []
	# 	hashProportion = data['hashProportion']

	# 	for evaluation in tabPlotGeneration :
	# 		proportionEval = [hashProportion[run][evaluation] for run in hashProportion.keys() if run in hashRunSuccess[cptData] and evaluation in hashProportion[run].keys()]
	# 		proportionMed = np.median(proportionEval)

	# 		perc25 = proportionMed
	# 		perc75 = proportionMed
	# 		if len(proportionEval) > 1 :
	# 			perc25 = np.percentile(proportionEval, 25)
	# 			perc75 = np.percentile(proportionEval, 75)

	# 		dataPlot.append(proportionMed)
	# 		dataPerc25.append(perc25)
	# 		dataPerc75.append(perc75)

	# 	cpt = 0
	# 	while cpt < len(dataPlot) :
	# 		if math.isnan(dataPlot[cpt]) :
	# 			if cpt > 0 and cpt < len(dataPlot) - 1 :
	# 				dataPlot[cpt] = (dataPlot[cpt + 1] + dataPlot[cpt - 1])/2
	# 				dataPerc25[cpt] = (dataPerc25[cpt + 1] + dataPerc25[cpt - 1])/2
	# 				dataPerc75[cpt] = (dataPerc75[cpt + 1] + dataPerc75[cpt - 1])/2
	# 			elif cpt > 0 :
	# 				dataPlot[cpt] = dataPlot[cpt - 1]
	# 				dataPerc25[cpt] = dataPerc25[cpt - 1]
	# 				dataPerc75[cpt] = dataPerc75[cpt - 1]
	# 			else :
	# 				dataPlot[cpt] = dataPlot[cpt + 1]
	# 				dataPerc25[cpt] = dataPerc25[cpt + 1]
	# 				dataPerc75[cpt] = dataPerc75[cpt + 1]

	# 		cpt += 1

	# 	axe1.plot(range(len(dataPlot)), dataPlot, color=palette[cptData], linestyle=linestyles[cptData], linewidth=linewidth, marker=markers[cptData])

	# 	plt.fill_between(range(len(dataPlot)), dataPerc25, dataPerc75, alpha=0.25, linewidth=0, color=palette[cptData])

	# 	cptData += 1


	# axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
	# axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
	# axe1.set_xlabel("Evaluation")

	# axe1.set_ylabel("Proportion")
	# # axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

	# legend = plt.legend(['Control', 'Clonal', 'Coevolution'], loc = 4, frameon=True)
	# frame = legend.get_frame()
	# frame.set_facecolor('0.9')
	# frame.set_edgecolor('0.9')

	# # axe1.set_title('Boxplot of best proportion')

	# plt.savefig(outputDir + "/boxplotProportionSuccess.png", bbox_inches = 'tight')
	# plt.savefig(outputDir + "/boxplotProportionSuccess.svg", bbox_inches = 'tight')
	# plt.close()


	# # Fitness Boxplots Success
	# fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# # plt.axes(frameon=0)
	# plt.grid()

	# cptData = 0
	# for data in dataHash :
	# 	dataPlot = []
	# 	dataPerc25 = []
	# 	dataPerc75 = []
	# 	hashProportion = data['hashProportion']

	# 	for evaluation in tabPlotEvaluation :
	# 		proportionEval = [hashProportion[run][evaluation] for run in hashProportion.keys() if evaluation in hashProportion[run].keys()]
	# 		proportionMed = np.median(proportionEval)

	# 		perc25 = proportionMed
	# 		perc75 = proportionMed
	# 		if len(proportionEval) > 1 :
	# 			perc25 = np.percentile(proportionEval, 25)
	# 			perc75 = np.percentile(proportionEval, 75)

	# 		dataPlot.append(proportionMed)
	# 		dataPerc25.append(perc25)
	# 		dataPerc75.append(perc75)

	# 	cpt = 0
	# 	while cpt < len(dataPlot) :
	# 		if math.isnan(dataPlot[cpt]) :
	# 			if cpt > 0 and cpt < len(dataPlot) - 1 :
	# 				dataPlot[cpt] = (dataPlot[cpt + 1] + dataPlot[cpt - 1])/2
	# 				dataPerc25[cpt] = (dataPerc25[cpt + 1] + dataPerc25[cpt - 1])/2
	# 				dataPerc75[cpt] = (dataPerc75[cpt + 1] + dataPerc75[cpt - 1])/2
	# 			elif cpt > 0 :
	# 				dataPlot[cpt] = dataPlot[cpt - 1]
	# 				dataPerc25[cpt] = dataPerc25[cpt - 1]
	# 				dataPerc75[cpt] = dataPerc75[cpt - 1]
	# 			else :
	# 				dataPlot[cpt] = dataPlot[cpt + 1]
	# 				dataPerc25[cpt] = dataPerc25[cpt + 1]
	# 				dataPerc75[cpt] = dataPerc75[cpt + 1]

	# 		cpt += 1

	# 	axe1.plot(range(len(dataPlot)), dataPlot, color=palette[cptData], linestyle=linestyles[cptData], linewidth=linewidth, marker=markers[cptData])

	# 	plt.fill_between(range(len(dataPlot)), dataPerc25, dataPerc75, alpha=0.25, linewidth=0, color=palette[cptData])

	# 	cptData += 1


	# axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
	# axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
	# axe1.set_xlabel("Generation")

	# axe1.set_ylabel("Proportion of Cooperative Runs")
	# axe1.set_ylim(-0.1, 1.1)

	# legend = plt.legend(['Control', 'Clonal', 'Coevolution'], loc = 4, frameon=True)
	# frame = legend.get_frame()
	# frame.set_facecolor('0.9')
	# frame.set_edgecolor('0.9')

	# # axe1.set_title('Boxplot of best proportion')

	# plt.savefig(outputDir + "/boxplotProportion.png", bbox_inches = 'tight')
	# plt.savefig(outputDir + "/boxplotProportion.svg", bbox_inches = 'tight')
	# plt.close()



def main(args) :
	global maxGen
	maxGen = int(args.max)

	global precision
	precision = int(args.precision)

	global outputDir
	outputDir = args.output

	global removeOutput
	removeOutput = bool(args.removeOutput)

	global directories
	directories = args.directories

	global startGen
	startGen = args.startGen

	if not args.drawLeadership :
		print("\t-> Drawing Hunting Task")
		drawHuntingTask()
	else :
		print("\t-> Drawing Leadership")
		drawLeadership()



if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directories', help = "Directories to plot", type=str, nargs='+')

	# parser.add_argument('-c', '--coop', help = "Compute the statistical test on proportion of cooperation", default = False, action = "store_true")

	parser.add_argument('-m', '--max', help = "Max evaluation", default='20000', type=int)
	parser.add_argument('-p', '--precision', help = "Precision", default='100', type=int)
	parser.add_argument('-S', '--startGen', help = "Starting Generation", default='0', type=int)

	parser.add_argument('-l', '--drawLeadership', help = "Drawing Leadership", default=False, action='store_true')

	parser.add_argument('-o', '--output', help = "Output directory", default='GraphsResults')
	parser.add_argument('-r', '--removeOutput', help = "Remove output directory if exists", default=False, action='store_true')

	parser.add_argument('-s', '--selection', help = "Selected runs", default=None, type=int, nargs='+')
	parser.add_argument('-e', '--exclusion', help = "Excluded runs", default=None, type=int, nargs='+')

	args = parser.parse_args()

	main(args)
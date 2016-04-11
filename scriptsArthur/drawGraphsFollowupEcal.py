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


precision = 10
selection = None
exclusion = None
directories = None
outputDir = "GraphsResultsFollowup"
drawStatAnalysis = False
removeOutput = False
drawGen = False
maxGen = 1500


colorHaresSolo = 'lime'
colorHaresDuo = 'green'
colorErrorHares = 'black'
alphaHares = 1
colorBStagsSolo = 'magenta'
colorBStagsDuo = 'purple'
colorErrorBStags = 'black'
alphaBStags = 1
colorTotal = 'grey'
colorErrorTotal = 'black'
alphaTotal = 1


payoffsOpt = [
							5250,
							5000,
							5250,
							5250,
							5250,
							4900,
							5050,
							5100,
							5100,
							5500,
							5000,
							5250,
							5250,
							5250,
							5100,
							5250,
							5000,
							5000,
							5050,
							4650
						 ]

beginningGen = {
								1 : 4300,
								2 : 1900,
								3 : 4300,
								4 : 1900,
								5 : 1900,
								6 : 1900,
								7 : 4100,
								8 : 4200,
								9 : 4200,
								10 : 1900
							 }


# SEABORN
sns.set()
sns.set_style('white')
sns.set_context('paper')
palette = sns.color_palette("husl", 3)

# MATPLOTLIB PARAMS
matplotlib.rcParams['font.size'] = 15
matplotlib.rcParams['font.weight'] = 'bold'
matplotlib.rcParams['axes.labelsize'] = 25
matplotlib.rcParams['axes.labelweight'] = 'bold'
matplotlib.rcParams['xtick.labelsize'] = 25
matplotlib.rcParams['ytick.labelsize'] = 25
matplotlib.rcParams['legend.fontsize'] = 25

# GRAPHS GLOBAL VARIABLES
linewidth = 2
linestyles = ['-', '--', '-.']
linestylesOff = ['-', '-', '-']
markers = [None, None, None] #['o', '+', '*']

dpi = 96
size = (1280/dpi, 1024/dpi)



def draw(args) :
	if os.path.isdir(outputDir) :
		if removeOutput :
			shutil.rmtree(outputDir)
			os.makedirs(outputDir)
	else :
		os.makedirs(outputDir)


	tabGeneration = []
	tabEvaluation = []
	dataHash = []
	for directory in directories :
		if os.path.isdir(directory) :
			listBestFit = [f for f in os.listdir(directory) if (os.path.isfile(directory + "/" + f) and re.match(r"^bestfit(\d*)\.dat$", f))]

			hashFitness = {}
			hashNbSStagsDuo = {}
			hashNbSStagsSolo = {}
			hashNbSStags = {}
			hashRatio = {}
			hashRatioSuccess = {}
			hashRatioHares = {}

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
					hashNbSStagsDuo[run] = {}
					hashNbSStagsSolo[run] = {}
					hashNbSStags[run] = {}
					hashRatio[run] = {}
					hashRatioSuccess[run] = {}
					hashRatioHares[run] = {}

					dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
					data = np.loadtxt(directory + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

					cpt = 0
					maxGenDone = False
					generation = 0
					for line in data :
						evaluation = line['evaluation']

						# # MERGE COEVO						
						# if directoryCoevo :
						# 	evaluation += 10

						if not args.beginningGen or (run in beginningGen.keys() and generation >= beginningGen[run]) :
							# print(str(run) + " : " + str(generation))
							cpt += 1

							curGen = generation
							if args.beginningGen :
								curGen = generation - beginningGen[run]

							if cpt > precision or curGen == 0 :
								if not maxGenDone :
									hashFitness[run][curGen] = line['fitness']

									hashNbSStags[run][curGen] = line['nbSStags']
									hashNbSStagsSolo[run][curGen] = line['nbSStagsSolo']
									hashNbSStagsDuo[run][curGen] = line['nbSStags'] - line['nbSStagsSolo']

									# hashRatio[run][curGen] = line['nbBStags']*100/(line['nbHares'] + line['nbBStags'])
									# hashRatioSuccess[run][curGen] = (line['nbBStags'] - line['nbBStagsSolo'])*100/(line['nbHares'] + (line['nbBStags'] - line['nbBStagsSolo'])) 
									# hashRatioHares[run][curGen] = line['nbHares']*100/(line['nbHares'] + line['nbBStags'])
									hashRatio[run][curGen] = 0
									hashRatioSuccess[run][curGen] = 0
									hashRatioHares[run][curGen] = 0

									if curGen not in tabGeneration :
										tabGeneration.append(curGen)

									if evaluation not in tabEvaluation :
										tabEvaluation.append(evaluation)

									cpt = 0

									if curGen > maxGen :
										maxGenDone = True

						generation += 1

			hashData = {}
			hashData["hashFitness"] = hashFitness
			
			hashData["hashNbSStags"] = hashNbSStags
			hashData["hashNbSStagsSolo"] = hashNbSStagsSolo
			hashData["hashNbSStagsDuo"] = hashNbSStagsDuo

			hashData["hashRatio"] = hashRatio
			hashData["hashRatioSuccess"] = hashRatioSuccess
			hashData["hashRatioHares"] = hashRatioHares

			dataHash.append(hashData)


	tabEvaluation = sorted(tabEvaluation)
	tabGeneration = sorted(tabGeneration)
	# lastEval = tabEvaluation[-1]
	# diffEvals = lastEval - tabEvaluation[-2]

	# while lastEval <= maxEval :
	# 	lastEval += diffEvals
	# 	tabEvaluation.append(lastEval)


	hashRunCoop = []
	for data in dataHash :
		hashNbSStags = data['hashNbSStags']
		hashNbSStagsDuo = data['hashNbSStagsDuo']
		runsCoop = []

		for run in hashNbSStags.keys() :
			lastGenRun = sorted(hashNbSStags[run].keys())[-1]

			if hashNbSStagsDuo[run][lastGenRun] > hashNbSStags[run][lastGenRun]/float(2.0) and hashNbSStagsDuo[run][lastGenRun] > 1 :
				runsCoop.append(run)

		hashRunCoop.append(runsCoop)


	# # Statistical Analysis
	# if args.statAnalysis :
	# 	cpt = 0
	# 	while cpt < len(dataHash) :
	# 		minEvalSerie1 = None
	# 		hashFitness = dataHash[cpt]["hashFitness"]

	# 		for run in hashRunStags[cpt] :
	# 			lastEval = sorted(hashFitness[run].keys())[-1]

	# 			if minEvalSerie1 == None or lastEval < minEvalSerie1 :
	# 				minEvalSerie1 = lastEval

	# 		serie1 = [hashFitness[run][minEvalSerie1] for run in hashRunStags[cpt]]
	# 		# print([sorted(hashFitness[run].keys())[-1] for run in hashFitness.keys()])
	# 		# print(serie1)
			
	# 		cpt2 = cpt + 1
	# 		while cpt2 < len(dataHash) :
	# 			minEvalSerie2 = None
	# 			hashFitness = dataHash[cpt2]["hashFitness"]

	# 			for run in hashRunStags[cpt2] :
	# 				lastEval = sorted(hashFitness[run].keys())[-1]

	# 				if minEvalSerie2 == None or lastEval < minEvalSerie2 :
	# 					minEvalSerie2 = lastEval

	# 			serie2 = [hashFitness[run][minEvalSerie2] for run in hashRunStags[cpt2]]
	# 			# print(serie2)

	# 			U, P = stats.mannwhitneyu(serie1, serie2)
	# 			print("Min1 = " + str(minEvalSerie1) + ", Min2 = " + str(minEvalSerie2))
	# 			print("Mann-Whitney (" + directories[cpt] + ", " + directories[cpt2] + ")\n\t -> U = " + str(U) + "/P = " + str(P))

	# 			with open(os.path.join(outputDir, "statAnalysis.txt"), 'w') as fileWrite :
	# 				fileWrite.write("Min1 = " + str(minEvalSerie1) + ", Min2 = " + str(minEvalSerie2))
	# 				fileWrite.write("Mann-Whitney (" + directories[cpt] + ", " + directories[cpt2] + ")\n\t -> U = " + str(U) + "/P = " + str(P))

	# 			cpt2 += 1
	# 		cpt += 1

	tabPlotEvaluation = tabEvaluation
	tabPlotGeneration = tabGeneration


	# Fitness Boxplots Stags
	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# plt.axes(frameon=0)
	plt.grid()

	# Fitness
	cptData = 0
	for data in dataHash :
		dataPlot = []
		dataPerc25 = []
		dataPerc75 = []
		hashFitness = data['hashFitness']

		for generation in tabPlotGeneration :
			fitnessEval = [hashFitness[run][generation] for run in hashFitness.keys() if run in hashRunCoop[cptData] and generation in hashFitness[run].keys()]
			print(fitnessEval)
			fitnessMed = np.median(fitnessEval)

			perc25 = fitnessMed
			perc75 = fitnessMed
			if len(fitnessEval) > 1 :
				perc25 = np.percentile(fitnessEval, 25)
				perc75 = np.percentile(fitnessEval, 75)

			dataPlot.append(fitnessMed)
			dataPerc25.append(perc25)
			dataPerc75.append(perc75)

		cpt = 0
		while cpt < len(dataPlot) :
			if math.isnan(dataPlot[cpt]) :
				if cpt > 0 and cpt < len(dataPlot) - 1 :
					dataPlot[cpt] = (dataPlot[cpt + 1] + dataPlot[cpt - 1])/2
					dataPerc25[cpt] = (dataPerc25[cpt + 1] + dataPerc25[cpt - 1])/2
					dataPerc75[cpt] = (dataPerc75[cpt + 1] + dataPerc75[cpt - 1])/2
				elif cpt > 0 :
					dataPlot[cpt] = dataPlot[cpt - 1]
					dataPerc25[cpt] = dataPerc25[cpt - 1]
					dataPerc75[cpt] = dataPerc75[cpt - 1]
				else :
					dataPlot[cpt] = dataPlot[cpt + 1]
					dataPerc25[cpt] = dataPerc25[cpt + 1]
					dataPerc75[cpt] = dataPerc75[cpt + 1]

			cpt += 1

		axe1.plot(range(len(dataPlot)), dataPlot, color=palette[cptData], linestyle=linestyles[cptData], linewidth=linewidth, marker=markers[cptData])

		plt.fill_between(range(len(dataPlot)), dataPerc25, dataPerc75, alpha=0.25, linewidth=0, color=palette[cptData])

		cptData += 1


	tabPlotTicks = []
	for generation in tabPlotGeneration :
		if generation > maxGen :
			tabPlotTicks.append(maxGen)
		else :
			tabPlotTicks.append(generation)

	ticks = range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/2))
	if len(tabPlotGeneration) - 1 not in ticks :
		ticks.append(len(tabPlotGeneration) - 1)

	# tabPlotTicks[ticks[0]] = 0
	# tabPlotTicks[ticks[1]] = 20000
	# tabPlotTicks[ticks[2]] = 40000

	axe1.set_xticks(ticks)
	axe1.set_xticklabels([tabPlotTicks[x] for x in ticks])
	axe1.set_xlabel("Generation")
	axe1.set_xlim(0, len(tabPlotGeneration) - 1)

	axe1.set_ylabel("Fitness")
	# axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

	legend = plt.legend(['Single Pop.', 'Two Pop.'], loc = 4, frameon=True)
	frame = legend.get_frame()
	frame.set_facecolor('0.9')
	frame.set_edgecolor('0.9')

	# axe1.set_title('Boxplot of best fitness')

	plt.savefig(outputDir + "/boxplotFitness.png", bbox_inches = 'tight')
	plt.savefig(outputDir + "/boxplotFitness.svg", bbox_inches = 'tight')
	plt.close()


	if args.optimum :
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		# plt.axes(frameon=0)
		plt.grid()

		# Fitness
		cptData = 0
		for data in dataHash :
			dataPlot = []
			dataPerc25 = []
			dataPerc75 = []
			hashFitness = data['hashFitness']

			for generation in tabPlotGeneration :
				fitnessEval = [hashFitness[run][generation] for run in hashFitness.keys() if run in hashRunCoop[cptData] and generation in hashFitness[run].keys()]
				fitnessMed = np.median(fitnessEval)

				perc25 = fitnessMed
				perc75 = fitnessMed
				if len(fitnessEval) > 1 :
					perc25 = np.percentile(fitnessEval, 25)
					perc75 = np.percentile(fitnessEval, 75)

				dataPlot.append(fitnessMed)
				dataPerc25.append(perc25)
				dataPerc75.append(perc75)

			cpt = 0
			while cpt < len(dataPlot) :
				if math.isnan(dataPlot[cpt]) :
					if cpt > 0 and cpt < len(dataPlot) - 1 :
						dataPlot[cpt] = (dataPlot[cpt + 1] + dataPlot[cpt - 1])/2
						dataPerc25[cpt] = (dataPerc25[cpt + 1] + dataPerc25[cpt - 1])/2
						dataPerc75[cpt] = (dataPerc75[cpt + 1] + dataPerc75[cpt - 1])/2
					elif cpt > 0 :
						dataPlot[cpt] = dataPlot[cpt - 1]
						dataPerc25[cpt] = dataPerc25[cpt - 1]
						dataPerc75[cpt] = dataPerc75[cpt - 1]
					else :
						dataPlot[cpt] = dataPlot[cpt + 1]
						dataPerc25[cpt] = dataPerc25[cpt + 1]
						dataPerc75[cpt] = dataPerc75[cpt + 1]

				cpt += 1

			axe1.plot(range(len(dataPlot)), dataPlot, color=palette[cptData], linestyle=linestyles[cptData], linewidth=linewidth, marker=markers[cptData])

			plt.fill_between(range(len(dataPlot)), dataPerc25, dataPerc75, alpha=0.25, linewidth=0, color=palette[cptData])

			cptData += 1

		dataPlot = []
		dataPerc25 = []
		dataPerc75 = []
		for generation in tabPlotGeneration :
			fitnessMed = np.median(payoffsOpt)

			perc25 = fitnessMed
			perc75 = fitnessMed
			if len(payoffsOpt) > 1 :
				perc25 = np.percentile(payoffsOpt, 25)
				perc75 = np.percentile(payoffsOpt, 75)

			dataPlot.append(fitnessMed)
			dataPerc25.append(perc25)
			dataPerc75.append(perc75)

		cpt = 0
		while cpt < len(dataPlot) :
			if math.isnan(dataPlot[cpt]) :
				if cpt > 0 and cpt < len(dataPlot) - 1 :
					dataPlot[cpt] = (dataPlot[cpt + 1] + dataPlot[cpt - 1])/2
					dataPerc25[cpt] = (dataPerc25[cpt + 1] + dataPerc25[cpt - 1])/2
					dataPerc75[cpt] = (dataPerc75[cpt + 1] + dataPerc75[cpt - 1])/2
				elif cpt > 0 :
					dataPlot[cpt] = dataPlot[cpt - 1]
					dataPerc25[cpt] = dataPerc25[cpt - 1]
					dataPerc75[cpt] = dataPerc75[cpt - 1]
				else :
					dataPlot[cpt] = dataPlot[cpt + 1]
					dataPerc25[cpt] = dataPerc25[cpt + 1]
					dataPerc75[cpt] = dataPerc75[cpt + 1]

			cpt += 1

		axe1.plot(range(len(dataPlot)), dataPlot, color=palette[cptData], linestyle=linestyles[cptData], linewidth=linewidth, marker=markers[cptData])

		plt.fill_between(range(len(dataPlot)), dataPerc25, dataPerc75, alpha=0.25, linewidth=0, color=palette[cptData])


		tabPlotTicks = []
		for generation in tabPlotGeneration :
			if generation > maxGen :
				tabPlotTicks.append(maxGen)
			else :
				tabPlotTicks.append(generation)

		ticks = range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/2))
		if len(tabPlotGeneration) - 1 not in ticks :
			ticks.append(len(tabPlotGeneration) - 1)

		# tabPlotTicks[ticks[0]] = 0
		# tabPlotTicks[ticks[1]] = 20000
		# tabPlotTicks[ticks[2]] = 40000

		axe1.set_xticks(ticks)
		axe1.set_xticklabels([tabPlotTicks[x] for x in ticks])
		axe1.set_xlabel("Generation")
		axe1.set_xlim(0, len(tabPlotGeneration) - 1)

		axe1.set_ylabel("Fitness")
		axe1.set_ylim(0, 6000)

		legend = plt.legend(['Random population', 'Optimum'], loc = 4, frameon=True)
		frame = legend.get_frame()
		frame.set_facecolor('0.9')
		frame.set_edgecolor('0.9')

		# axe1.set_title('Boxplot of best fitness')

		plt.savefig(outputDir + "/boxplotFitnessOpt.png", bbox_inches = 'tight')
		plt.savefig(outputDir + "/boxplotFitnessOpt.svg", bbox_inches = 'tight')
		plt.close()


	# # Proportion of cooperation
	# fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# # plt.axes(frameon=0)
	# plt.grid()

	# cptData = 0
	# for data in dataHash :
	# 	dataPlot = []
	# 	hashFitness = data['hashFitness']
	# 	hashNbBStags = data['hashNbBStags']
	# 	hashNbBStagsDuo = data['hashNbBStagsDuo']
	# 	hashNbHares = data['hashNbHares']

	# 	for evaluation in tabPlotEvaluation :
	# 		proportionEval = float(len([run for run in hashFitness.keys() if evaluation in hashFitness[run] and hashNbBStagsDuo[run][evaluation] > hashNbHares[run][evaluation] and hashNbBStagsDuo[run][evaluation] > 1]))/float(len(hashFitness.keys()))

	# 		dataPlot.append(proportionEval)

	# 	cpt = 0
	# 	while cpt < len(dataPlot) :
	# 		if dataPlot[cpt] == 0 :
	# 			if cpt > 0 and cpt < len(dataPlot) - 1 :
	# 				dataPlot[cpt] = (dataPlot[cpt + 1] + dataPlot[cpt - 1])/2
	# 			elif cpt > 0 :
	# 				dataPlot[cpt] = dataPlot[cpt - 1]
	# 			else :
	# 				dataPlot[cpt] = dataPlot[cpt + 1]

	# 		cpt += 1

	# 	axe1.plot(range(len(dataPlot)), dataPlot, color=palette[cptData], linestyle=linestylesOff[cptData], linewidth=linewidth, marker=markers[cptData])

	# 	cptData += 1


	# # tabPlotTicks = []
	# # for generation in tabPlotGeneration :
	# # 	if generation > maxGen :
	# # 		tabPlotTicks.append(maxGen)
	# # 	else :
	# # 		tabPlotTicks.append(generation)

	# # ticks = range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/5))
	# # if len(tabPlotGeneration) - 1 not in ticks :
	# # 	ticks.append(len(tabPlotGeneration) - 1)

	# # axe1.set_xticks(ticks)
	# # axe1.set_xticklabels([tabPlotTicks[x] for x in ticks])
	# # axe1.set_xlabel("Generation")
	# # axe1.set_xlim(0, len(tabPlotGeneration) - 1)

	# # axe1.set_ylabel("Proportion of Cooperative Runs")
	# # axe1.set_ylim(-0.1, 1.1)

	# tabPlotTicks = []
	# for eval in tabPlotEvaluation :
	# 	if eval > maxEval :
	# 		tabPlotTicks.append(maxEval)
	# 	else :
	# 		tabPlotTicks.append(eval)

	# ticks = range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/2))
	# if len(tabPlotEvaluation) - 1 not in ticks :
	# 	ticks.append(len(tabPlotEvaluation) - 1)

	# tabPlotTicks[ticks[0]] = 0
	# tabPlotTicks[ticks[1]] = 20000
	# tabPlotTicks[ticks[2]] = 40000

	# axe1.set_xticks(ticks)
	# axe1.set_xticklabels([tabPlotTicks[x] for x in ticks])
	# axe1.set_xlabel("Evaluation")
	# axe1.set_xlim(0, len(tabPlotEvaluation) - 1)

	# axe1.set_ylabel("Proportion of Cooperative Runs (/60)")
	# axe1.set_ylim(0.0, 1.0)

	# # legend = plt.legend(['Control', 'Clonal', 'Coevolution'], loc = 4, frameon=True)
	# # frame = legend.get_frame()
	# # frame.set_facecolor('0.9')
	# # frame.set_edgecolor('0.9')

	# plt.savefig(outputDir + "/proportionCooperation.png", bbox_inches = 'tight')
	# plt.savefig(outputDir + "/proportionCooperation.svg", bbox_inches = 'tight')
	# plt.close()


	# # --- BARS ---
	# cptData = 0
	# tabDirs = ['Control','Clonal', 'Coevolution']
	# for data in dataHash :
	# 	outputData = os.path.join(outputDir, tabDirs[cptData])

	# 	if os.path.isdir(outputData) :
	# 		if removeOutput :
	# 			shutil.rmtree(outputData)
	# 			os.makedirs(outputData)
	# 	else :
	# 		os.makedirs(outputData)

	# 	hashNbHaresSolo = data['hashNbHaresSolo']
	# 	hashNbHaresDuo = data['hashNbHaresDuo']
	# 	hashNbBStagsSolo = data['hashNbBStagsSolo']
	# 	hashNbBStagsDuo = data['hashNbBStagsDuo']

	# 	for run in hashNbHaresSolo.keys() :
	# 		if run in [24, 8, 47, 41, 57] :
	# 			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# 			plt.grid()

	# 			width = 1.0 # 0.8

	# 			tabNbHaresSolo = [hashNbHaresSolo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbHaresSolo[run].keys()]
	# 			tabNbHaresDuo = [hashNbHaresDuo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbHaresDuo[run].keys()]
	# 			tabNbBStagsSolo = [hashNbBStagsSolo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbBStagsSolo[run].keys()]
	# 			tabNbBStagsDuo = [hashNbBStagsDuo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbBStagsDuo[run].keys()]

	# 			barNbHaresSolo = axe1.bar(range(len(tabNbHaresSolo)), tabNbHaresSolo, width = width, color = colorHaresSolo, alpha = alphaHares)
	# 			barNbHaresDuo = axe1.bar(range(len(tabNbHaresDuo)), tabNbHaresDuo, bottom = tabNbHaresSolo, width = width, color = colorHaresDuo, alpha = alphaHares)
	# 			barNbBStagsSolo = axe1.bar(range(len(tabNbBStagsSolo)), tabNbBStagsSolo, bottom = np.add(tabNbHaresDuo, tabNbHaresSolo), width = width, color = colorBStagsSolo, alpha = alphaBStags)
	# 			barNbBStagsDuo = axe1.bar(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, bottom = np.add(tabNbBStagsSolo, np.add(tabNbHaresDuo, tabNbHaresSolo)), width = width, color = colorBStagsDuo, alpha = alphaBStags)

	# 			tabPlotTicks = []

	# 			ticks = range(0, len(tabNbHaresSolo), int(len(tabNbHaresSolo)/2))
	# 			if len(tabNbHaresSolo) - 1 not in ticks :
	# 				ticks.append(len(tabNbHaresSolo) - 1)

	# 			for eval in tabPlotEvaluation :
	# 				if eval > maxEval :
	# 					tabPlotTicks.append(maxEval)
	# 				else :
	# 					tabPlotTicks.append(eval)

	# 			# ticks = range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/2))
	# 			# if len(tabPlotEvaluation) - 1 not in ticks :
	# 			# 	ticks.append(len(tabPlotEvaluation) - 1)

	# 			tabPlotTicks[ticks[0]] = 0
	# 			tabPlotTicks[ticks[1]] = 20000
	# 			tabPlotTicks[ticks[2]] = 40000

	# 			axe1.set_xticks(ticks)
	# 			axe1.set_xticklabels([tabPlotTicks[x] for x in ticks])
	# 			axe1.set_xlabel("Evaluation")
	# 			axe1.set_xlim(0, len(tabNbHaresSolo) - 1)

	# 			axe1.set_ylabel("Number of targets collected")
	# 			axe1.set_ylim(0, 20)

	# 			# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Green solo', 'Green coop.', 'Purple solo', 'Purple coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
	# 			# plt.legend([barNbHaresSolo, barNbHaresDuo, barNbSStagsSolo, barNbSStagsDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Small stags solo', 'Small stags coop.', 'Big stags solo', 'Big stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

	# 			plt.savefig(outputData + "/preysRun" + str(run) + ".png", bbox_inches = 'tight')
	# 			plt.savefig(outputData + "/preysRun" + str(run) + ".svg", bbox_inches = 'tight')
	# 			plt.close()

	# 	cptData += 1



def drawLeadership(args) :
	if os.path.isdir(outputDir) :
		if removeOutput :
			shutil.rmtree(outputDir)
			os.makedirs(outputDir)
	else :
		os.makedirs(outputDir)

	tabEvaluation = []
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

					dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'proportion', 'proportionAsym'), 'formats' : [np.int, np.float, np.float, np.float] })
					data = np.loadtxt(directory + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3), dtype = dtypes)

					cpt = 0
					maxEvalDone = False
					generation = 0
					firstEval = True
					for line in data :
						evaluation = line['evaluation']
						cpt += evaluation

						if cpt > precision or firstEval :
							if not maxEvalDone :
								hashProportion[run][evaluation] = line['proportion']

								if evaluation not in tabEvaluation :
									tabEvaluation.append(evaluation)

								cpt = 0

								if evaluation > maxGen :
									maxEvalDone = True

								if firstEval :
									firstEval = False

			dirBestFit = os.path.join(directory, "../BestFit")
			listBestFitness = [f for f in os.listdir(dirBestFit) if (os.path.isfile(dirBestFit + "/" + f) and re.match(r"^bestfit(\d*)\.dat$", f))]

			hashNbSStags = {}
			hashNbSStagsSolo = {}
			hashNbSStagsDuo = {}

			for fileBest in listBestFitness :
				m = re.search(r'^bestfit(\d*)\.dat$', fileBest)
				run = int(m.group(1))

				testRun = None
				if selection != None :
					testRun = lambda run : run in selection
				elif exclusion != None :
					testRun = lambda run : run not in exclusion

				if (testRun == None) or (testRun(run)) :
					hashNbSStags[run] = {}
					hashNbSStagsSolo[run] = {}
					hashNbSStagsDuo[run] = {}

					dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
					data = np.loadtxt(dirBestFit + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

					cpt = 0
					maxEvalDone = False
					generation = 0
					firstEval = True
					for line in data :
						evaluation = line['evaluation']
						cpt += evaluation

						if cpt > precision or firstEval :
							if not maxEvalDone :
								hashNbSStags[run][evaluation] = line['nbSStags']
								hashNbSStagsSolo[run][evaluation] = line['nbSStagsSolo']
								hashNbSStagsDuo[run][evaluation] = line['nbSStags'] - line['nbSStagsSolo']

								if evaluation not in tabEvaluation :
									tabEvaluation.append(evaluation)

								cpt = 0

								if evaluation > maxGen :
									maxEvalDone = True

								if firstEval :
									firstEval = False									


			hashData = {}
			hashData["hashProportion"] = hashProportion
			hashData["hashProportionAsym"] = hashProportionAsym
			hashData["hashNbSStags"] = hashNbSStags
			hashData["hashNbSStagsSolo"] = hashNbSStagsSolo
			hashData["hashNbSStagsDuo"] = hashNbSStagsDuo

			dataHash.append(hashData)


	tabEvaluation = sorted(tabEvaluation)
	tabGeneration = sorted(tabGeneration)
	# lastEval = tabEvaluation[-1]
	# diffEvals = lastEval - tabEvaluation[-2]

	# while lastEval <= maxEval :
	# 	lastEval += diffEvals
	# 	tabEvaluation.append(lastEval)

	# hashRunCoop = []
	# for data in dataHash :
	# 	hashNbSStagsDuo = data['hashNbSStagsDuo']
	# 	hashNbSStags = data['hashNbSStags']
	# 	runCoop = []

	# 	for run in hashNbSStagsDuo.keys() :
	# 		lastGenRun = sorted(hashNbSStagsDuo[run].keys())[-1]

	# 		if hashNbSStagsDuo[run][lastGenRun] > (0.5 * hashNbSStags) hashProportion[run][lastGenRun] > 0.75 :
	# 			runCoop.append(run)

	# 	hashRunCoop.append(runCoop)


	# # Statistical Analysis
	# if args.statAnalysis :
	# 	cpt = 0
	# 	while cpt < len(dataHash) :
	# 		minEvalSerie1 = None
	# 		hashProportion = dataHash[cpt]["hashProportion"]

	# 		for run in hashRunSuccess[cpt] :
	# 			lastEval = sorted(hashProportion[run].keys())[-1]

	# 			if minEvalSerie1 == None or lastEval < minEvalSerie1 :
	# 				minEvalSerie1 = lastEval

	# 		serie1 = [hashProportion[run][minEvalSerie1] for run in hashRunSuccess[cpt]]
			
	# 		cpt2 = cpt + 1
	# 		while cpt2 < len(dataHash) :
	# 			minEvalSerie2 = None
	# 			hashProportion = dataHash[cpt2]["hashProportion"]

	# 			for run in hashRunSuccess[cpt2] :
	# 				lastEval = sorted(hashProportion[run].keys())[-1]

	# 				if minEvalSerie2 == None or lastEval < minEvalSerie2 :
	# 					minEvalSerie2 = lastEval

	# 			serie2 = [hashProportion[run][minEvalSerie2] for run in hashRunSuccess[cpt2]]

	# 			U, P = stats.mannwhitneyu(serie1, serie2)
	# 			print("Min1 = " + str(minEvalSerie1) + ", Min2 = " + str(minEvalSerie2))
	# 			print("Mann-Whitney (" + directories[cpt] + ", " + directories[cpt2] + ")\n\t -> U = " + str(U) + "/P = " + str(P))

	# 			with open(os.path.join(outputDir, "statAnalysis.txt"), 'w') as fileWrite :
	# 				fileWrite.write("Min1 = " + str(minEvalSerie1) + ", Min2 = " + str(minEvalSerie2))
	# 				fileWrite.write("Mann-Whitney (" + directories[cpt] + ", " + directories[cpt2] + ")\n\t -> U = " + str(U) + "/P = " + str(P))

	# 			cpt2 += 1
	# 		cpt += 1

	tabPlotEvaluation = tabEvaluation
	tabPlotGeneration = tabGeneration


	# # Fitness Boxplots
	# cptData = 0
	# dataNames = ["Single Pop.", "Two Pop."]
	# for data in dataHash :
	# 	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# 	plt.grid()

	# 	dataBoxPlot = []
	# 	hashProportion = data['hashProportion']

	# 	tabEvals = []
	# 	for evaluation in tabPlotEvaluation :
	# 		listProportion = [hashProportion[run][evaluation] for run in hashProportion.keys() if run in hashRunSuccess[cptData] and evaluation in hashProportion[run].keys()]

	# 		if len(listProportion) > 0 :
	# 			dataBoxPlot.append(listProportion)
	# 			tabEvals.append(evaluation)

	# 	bp = axe1.boxplot(dataBoxPlot)

	# 	for i in range(0, len(bp['boxes'])):
	# 		# We fill the boxes
	# 		box = bp['boxes'][i]
	# 		box.set_linewidth(0)
	# 		boxX = []
	# 		boxY = []

	# 		for j in range(5) :
	# 			boxX.append(box.get_xdata()[j])
	# 			boxY.append(box.get_ydata()[j])

	# 		boxCoords = zip(boxX, boxY)
	# 		boxPolygon = Polygon(boxCoords, facecolor = palette[2], linewidth = 0)
	# 		axe1.add_patch(boxPolygon)

	# 		bp['boxes'][i].set_color(palette[2])

	# 		# we have two whiskers!
	# 		bp['whiskers'][i*2].set_color(palette[2])
	# 		bp['whiskers'][i*2 + 1].set_color(palette[2])
	# 		bp['whiskers'][i*2].set_linewidth(2)
	# 		bp['whiskers'][i*2 + 1].set_linewidth(2)

	# 		# top and bottom fliers
	# 		# (set allows us to set many parameters at once)
	# 		# if (i * 2 + 1) < len(bp['fliers']) :
	# 		# 	bp['fliers'][i * 2].set(markerfacecolor=palette[2],
	# 		# 	                marker='o', alpha=0.75, markersize=6,
	# 		# 	                markeredgecolor='none')
	# 		# 	bp['fliers'][i * 2 + 1].set(markerfacecolor=palette[2],
	# 		# 	                marker='o', alpha=0.75, markersize=6,
	# 		# 	                markeredgecolor='none')


	# 		bp['medians'][i].set_color('black')
	# 		bp['medians'][i].set_linewidth(3)

	# 		# and 4 caps to remove
	# 		for c in bp['caps']:
	# 		   c.set_linewidth(0)

	# 	axe1.add_line(lines.Line2D([0, maxEval], [1, 1], color="red"))


	# 	tabPlotTicks = []
	# 	for eval in tabEvals :
	# 		if eval > maxEval :
	# 			tabPlotTicks.append(maxEval)
	# 		else :
	# 			tabPlotTicks.append(eval)

	# 	ticks = range(0, len(tabEvals), int(len(tabEvals)/2))
	# 	if len(tabEvals) - 1 not in ticks :
	# 		ticks.append(len(tabEvals) - 1)

	# 	tabPlotTicks[ticks[0]] = 0
	# 	tabPlotTicks[ticks[1]] = 20000
	# 	tabPlotTicks[ticks[2]] = 40000

	# 	axe1.set_xticks(ticks)
	# 	axe1.set_xticklabels([tabPlotTicks[x] for x in ticks])
	# 	axe1.set_xlabel("Evaluation")
	# 	axe1.set_xlim(0, len(tabPlotTicks) - 1)

	# 	axe1.set_ylabel("Proportion")
	# 	axe1.set_ylim(0, 1.1)

	# 	# axe1.set_title('Boxplot of best fitness')

	# 	plt.savefig(outputDir + "/boxplotLeadership" + dataNames[cptData] + ".png", bbox_inches = 'tight')
	# 	plt.savefig(outputDir + "/boxplotLeadership" + dataNames[cptData] + ".svg", bbox_inches = 'tight')
	# 	plt.close()

	# 	cptData += 1




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

	# 	for evaluation in tabPlotEvaluation :
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


	# # Proportion Leadership
	# fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# # plt.axes(frameon=0)
	# plt.grid()

	# cptData = 0
	# for data in dataHash :
	# 	dataPlot = []
	# 	dataPerc25 = []
	# 	dataPerc75 = []
	# 	hashProportion = data['hashProportion']

	# 	for generation in tabPlotGeneration :
	# 		proportionEval = [hashProportion[run][generation] for run in hashProportion.keys() if generation in hashProportion[run].keys()]
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

	# tabPlotTicks = []
	# for generation in tabPlotGeneration :
	# 	if generation > maxGen :
	# 		tabPlotTicks.append(maxGen)
	# 	else :
	# 		tabPlotTicks.append(generation)

	# ticks = range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/2))
	# if len(tabPlotGeneration) - 1 not in ticks :
	# 	ticks.append(len(tabPlotGeneration) - 1)

	# # tabPlotTicks[ticks[0]] = 0
	# # tabPlotTicks[ticks[1]] = 20000
	# # tabPlotTicks[ticks[2]] = 40000

	# axe1.set_xticks(ticks)
	# axe1.set_xticklabels([tabPlotTicks[x] for x in ticks])
	# # axe1.set_xticks(range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10)))
	# # axe1.set_xticklabels([tabPlotGeneration[x] for x in range(0, len(tabPlotGeneration), int(len(tabPlotGeneration)/10))])
	# axe1.set_xlabel("Generation")
	# axe1.set_xlim(0, len(tabPlotGeneration) - 1)
	# axe1.set_ylabel("Proportion")
	# # axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

	# legend = plt.legend(['Single Pop.', 'Two Pop.'], loc = 4, frameon=True)
	# frame = legend.get_frame()
	# frame.set_facecolor('0.9')
	# frame.set_edgecolor('0.9')

	# # axe1.set_title('Boxplot of best proportion')

	# plt.savefig(outputDir + "/boxplotProportion.png", bbox_inches = 'tight')
	# plt.savefig(outputDir + "/boxplotProportion.svg", bbox_inches = 'tight')
	# plt.close()


	# Proportion Time Leadership

	# Statistical analyses Fitness
	# U, P = stats.mannwhitneyu(dataHash['SF'][:, 0], dataHash['TT'][:, 0])
	# print("Mann-Whitney -> U = " + str(U) + "/P = " + str(P))

	# stars = "-"
	# if P < 0.0001:
	#    stars = "****"
	# elif (P < 0.001):
	#    stars = "***"
	# elif (P < 0.01):
	#    stars = "**"
	# elif (P < 0.05):
	#    stars = "*"



	# Boxplots fitness
	cptData = 0
	dataTime = list()
	for data in dataHash :
		hashProportion = data['hashProportion']
		hashNbSStagsDuo = data['hashNbSStagsDuo']
		hashNbSStags = data['hashNbSStags']

		timeRun = list()
		for run in hashProportion :
			curTime = 0
			longestTime = 0
			longestTimeMax = 0

			totalEval = 0
			sortEval = sorted(hashProportion[run].keys())
			for eval in sortEval :
				if hashNbSStagsDuo[run][eval] >= (0.5 * hashNbSStags[run][eval]) :
					if hashProportion[run][eval] > args.threshold :
						curTime += 1
						longestTime += 1
					else :
						if longestTime > longestTimeMax :
							longestTimeMax = longestTime

						longestTime = 0

					totalEval += 1

			if longestTime > longestTimeMax :
				longestTimeMax = longestTime

			# longestTimeMax /= float(totalEval)
			# timeRun.append(longestTimeMax)

			if totalEval > 0 :
				curTime /= float(totalEval)
			timeRun.append(curTime)

		dataTime.append(timeRun)
		cptData += 1

	dataStats = list()
	for data in dataTime :
		curDataStats = list()
		for dataCmp in dataTime :
			U, P = stats.mannwhitneyu(data, dataCmp)
			stars = "-"
			if P < 0.0001:
			   stars = "****"
			elif (P < 0.001):
			   stars = "***"
			elif (P < 0.01):
			   stars = "**"
			elif (P < 0.05):
			   stars = "*"

			curDataStats.append(stars)
		dataStats.append(curDataStats)

	for i in range(0, len(dataStats)) :
		print("Data " + str(i) + " : ")
		for j in range(0, len(dataStats[i])) :
			print("Data " + str(j) + " : P = " + str(dataStats[i][j]))


	fig, ax = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# plt.grid()

	bp = ax.boxplot([data for data in dataTime])
	
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	ax.spines['left'].set_visible(False)
	ax.get_xaxis().tick_bottom()
	ax.get_yaxis().tick_left()
	ax.tick_params(axis='x', direction='out')
	ax.tick_params(axis='y', length=0)

	ax.set_xlabel("Population size")
	ax.set_ylabel("Proportion of time")
	ax.set_ylim(0, 1)

	ax.grid(axis='y', color="0.9", linestyle='-', linewidth=1)
	ax.set_axisbelow(True)

	for i in range(0, len(bp['boxes'])):
		bp['boxes'][i].set_color(palette[i])
		# we have two whiskers!
		bp['whiskers'][i*2].set_color(palette[i])
		bp['whiskers'][i*2 + 1].set_color(palette[i])
		bp['whiskers'][i*2].set_linewidth(2)
		bp['whiskers'][i*2 + 1].set_linewidth(2)
		# top and bottom fliers
		# (set allows us to set many parameters at once)
		# bp['fliers'][i].set(markerfacecolor=palette[1],
		#                 marker='o', alpha=0.75, markersize=6,
		#                 markeredgecolor='none')
		# bp['fliers'][1].set(markerfacecolor=palette[1],
		#                 marker='o', alpha=0.75, markersize=6,
		#                 markeredgecolor='none')
		if (i * 2) < len(bp['fliers']) :
		   bp['fliers'][i * 2].set(markerfacecolor='black',
		                   marker='o', alpha=0.75, markersize=6,
		                   markeredgecolor='none')
		if (i * 2 + 1) < len(bp['fliers']) :
		   bp['fliers'][i * 2 + 1].set(markerfacecolor='black',
		                   marker='o', alpha=0.75, markersize=6,
		                   markeredgecolor='none')
		bp['medians'][i].set_color('black')
		bp['medians'][i].set_linewidth(3)
		# and 4 caps to remove
		for c in bp['caps']:
		   c.set_linewidth(0)

	for i in range(len(bp['boxes'])):
	   box = bp['boxes'][i]
	   box.set_linewidth(0)
	   boxX = []
	   boxY = []
	   for j in range(5):
	       boxX.append(box.get_xdata()[j])
	       boxY.append(box.get_ydata()[j])
	       boxCoords = zip(boxX,boxY)
	       boxPolygon = Polygon(boxCoords, facecolor = palette[i], linewidth=0)
	       ax.add_patch(boxPolygon)
	
	fig.subplots_adjust(left=0.2)

	ax.set_xticklabels(['20', '40', '100'])

	# y_max = np.max(np.concatenate((dataHash['SF'][:, 0], dataHash['TT'][:, 0])))
	# y_min = np.min(np.concatenate((dataHash['SF'][:, 0], dataHash['TT'][:, 0])))
	y_min = 0

	# print y_max

	cptData = 0
	while cptData < len(dataStats) :
		cptComp = cptData + 1
		while cptComp < len(dataStats[cptData]) :
			if dataStats[cptData][cptComp] != "-" :
				ax.annotate("", xy=(cptData + 1, 0.75), xycoords='data',
				           xytext=(cptComp + 1, 0.75), textcoords='data',
				           arrowprops=dict(arrowstyle="-", ec='#000000',
				                           connectionstyle="bar,fraction=0.05"))
				ax.text(2, 0.80, dataStats[cptData][cptComp],
				       horizontalalignment='center',
				       verticalalignment='center')

			cptComp += 1
		cptData += 1

	plt.savefig(outputDir + "/boxplotLeadershipTime.png", bbox_inches = 'tight')
	plt.savefig(outputDir + "/boxplotLeadershipTime.svg", bbox_inches = 'tight')
	plt.close()



def main(args) :
	global precision
	precision = int(args.precision)

	global outputDir
	outputDir = args.output

	global removeOutput
	removeOutput = bool(args.removeOutput)

	global drawStatAnalysis
	drawStatAnalysis = bool(args.statAnalysis)

	global selection
	selection = args.selection

	global exclusion
	exclusion = args.exclusion

	global directories
	directories = args.directories

	global maxGen
	maxGen = int(args.max)

	if args.drawLeadership :
		print("\t-> Drawing Leadership")
		drawLeadership(args)
	else :
		print("\t-> Drawing Hunting Task")
		draw(args)



if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directories', help = "Directories to plot", type=str, nargs='+')

	parser.add_argument('-m', '--max', help = "Max evaluation", default='1500', type=int)
	parser.add_argument('-p', '--precision', help = "Precision", default='10', type=int)

	parser.add_argument('-o', '--output', help = "Output directory", default='GraphsResultsFollowup')
	parser.add_argument('-r', '--removeOutput', help = "Remove output directory if exists", default=False, action='store_true')
	parser.add_argument('-b', '--beginningGen', help = "First generation from which we draw", default = False, action = 'store_true')

	parser.add_argument('-a', '--statAnalysis', help = "Compute Mann-Whitney", default=False, action='store_true')
	parser.add_argument('-l', '--drawLeadership', help = "Draw leadership", default=False, action='store_true')
	parser.add_argument('-u', '--unique', help = "Draw a unique run", default = -1, type = int)

	parser.add_argument('-s', '--selection', help = "Selected runs", default=None, type=int, nargs='+')
	parser.add_argument('-e', '--exclusion', help = "Excluded runs", default=None, type=int, nargs='+')

	parser.add_argument('-O', '--optimum', help = "Draw optimum", default = False, action = 'store_true')

	parser.add_argument('-t', '--threshold', help = "Leadership threshold", default = 0.6, type = float)

	args = parser.parse_args()

	main(args)
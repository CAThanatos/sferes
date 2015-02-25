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

from scipy import stats

import os
import argparse
import re
import math
import shutil


maxEval = 40000
precision = 100
selection = None
exclusion = None
directories = None
outputDir = "GraphsResults"
drawStatAnalysis = False
removeOutput = False


def drawHuntingTask() :
	if os.path.isdir(outputDir) :
		if removeOutput :
			shutil.rmtree(outputDir)
			os.makedirs(outputDir)
	else :
		os.makedirs(outputDir)


	tabEvaluation = []
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
					for line in data :
						evaluation = line['evaluation']

						cpt += evaluation - lastEval
						lastEval = evaluation

						if cpt > precision or firstEval :
							if evaluation < maxEval :
								hashFitness[run][evaluation] = line['fitness']

								hashNbHares[run][evaluation] = line['nbHares']
								hashNbHaresSolo[run][evaluation] = line['nbHaresSolo']
								hashNbHaresDuo[run][evaluation] = line['nbHares'] - line['nbHaresSolo']

								hashNbSStags[run][evaluation] = line['nbSStags']
								hashNbSStagsSolo[run][evaluation] = line['nbSStagsSolo']
								hashNbSStagsDuo[run][evaluation] = line['nbSStags'] - line['nbSStagsSolo']

								hashNbBStags[run][evaluation] = line['nbBStags']
								hashNbBStagsSolo[run][evaluation] = line['nbBStagsSolo']
								hashNbBStagsDuo[run][evaluation] = line['nbBStags'] - line['nbBStagsSolo']

								# hashRatio[run][evaluation] = line['nbBStags']*100/(line['nbHares'] + line['nbBStags'])
								# hashRatioSuccess[run][evaluation] = (line['nbBStags'] - line['nbBStagsSolo'])*100/(line['nbHares'] + (line['nbBStags'] - line['nbBStagsSolo'])) 
								# hashRatioHares[run][evaluation] = line['nbHares']*100/(line['nbHares'] + line['nbBStags'])
								hashRatio[run][evaluation] = 0
								hashRatioSuccess[run][evaluation] = 0
								hashRatioHares[run][evaluation] = 0

								if evaluation not in tabEvaluation :
									tabEvaluation.append(evaluation)

								cpt = 0

						if firstEval :
							firstEval = False

			hashData = {}
			hashData["hashFitness"] = hashFitness

			hashData["hashNbHares"] = hashNbHares
			hashData["hashNbHaresSolo"] = hashNbHaresSolo
			hashData["hashNbHaresDuo"] = hashNbHaresDuo
			
			hashData["hashNbBStags"] = hashNbBStags
			hashData["hashNbBStagsSolo"] = hashNbBStagsSolo
			hashData["hashNbBStagsDuo"] = hashNbBStagsDuo

			hashData["hashRatio"] = hashRatio
			hashData["hashRatioSuccess"] = hashRatioSuccess
			hashData["hashRatioHares"] = hashRatioHares

			dataHash.append(hashData)



	tabEvaluation = sorted(tabEvaluation)
	# lastEval = tabEvaluation[-1]
	# diffEvals = lastEval - tabEvaluation[-2]

	# while lastEval <= maxEval :
	# 	lastEval += diffEvals
	# 	tabEvaluation.append(lastEval)


	# Statistical Analysis
	if args.statAnalysis :
		cpt = 0
		while cpt < len(dataHash) :
			minEvalSerie1 = None
			hashFitness = dataHash[cpt]["hashFitness"]

			for run in hashFitness.keys() :
				lastEval = sorted(hashFitness[run].keys())[-1]

				if minEvalSerie1 == None or lastEval < minEvalSerie1 :
					minEvalSerie1 = lastEval

			serie1 = [hashFitness[run][minEvalSerie1] for run in hashFitness.keys()]
			# print([sorted(hashFitness[run].keys())[-1] for run in hashFitness.keys()])
			
			cpt2 = cpt + 1
			while cpt2 < len(dataHash) :
				minEvalSerie2 = None
				hashFitness = dataHash[cpt2]["hashFitness"]

				for run in hashFitness.keys() :
					lastEval = sorted(hashFitness[run].keys())[-1]

					if minEvalSerie2 == None or lastEval < minEvalSerie2 :
						minEvalSerie2 = lastEval

				serie2 = [hashFitness[run][minEvalSerie2] for run in hashFitness.keys()]

				U, P = stats.mannwhitneyu(serie1, serie2)
				print("Min1 = " + str(minEvalSerie1) + ", Min2 = " + str(minEvalSerie2))
				print("Mann-Whitney (" + directories[cpt] + ", " + directories[cpt2] + ")\n\t -> U = " + str(U) + "/P = " + str(P))

				with open(os.path.join(outputDir, "statAnalysis.txt"), 'w') as fileWrite :
					fileWrite.write("Min1 = " + str(minEvalSerie1) + ", Min2 = " + str(minEvalSerie2))
					fileWrite.write("Mann-Whitney (" + directories[cpt] + ", " + directories[cpt2] + ")\n\t -> U = " + str(U) + "/P = " + str(P))

				cpt2 += 1
			cpt += 1


	# SEABORN
	sns.set()
	sns.set_style('white')
	sns.set_context('paper')
	palette = sns.color_palette("husl", len(directories))

	matplotlib.rcParams['font.size'] = 15
	matplotlib.rcParams['font.weight'] = 'bold'
	matplotlib.rcParams['axes.labelsize'] = 15
	matplotlib.rcParams['axes.labelweight'] = 'bold'
	matplotlib.rcParams['xtick.labelsize'] = 15
	matplotlib.rcParams['ytick.labelsize'] = 15
	matplotlib.rcParams['legend.fontsize'] = 15

	linewidth = 2
	linestyles = ['-', '--', '-.']
	markers = [None, None, None] #['o', '+', '*']

	dpi = 96
	size = (1280/dpi, 1024/dpi)

	tabPlotEvaluation = tabEvaluation


	# # Fitness Boxplots Stags
	# fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

	# cptData = 0
	# for data in dataHash :
	# 	dataBoxPlot = []
	# 	hashFitness = data['hashFitness']
	# 	hashNbBStags = data['hashNbBStags']
	# 	hashNbBStagsDuo = data['hashNbBStagsDuo']
	# 	hashNbHares = data['hashNbHares']

	# 	runStags = []
	# 	for run in hashNbBStags.keys() :
	# 		lastEvalRun = sorted(hashNbHares[run].keys())[-1]
	# 		if hashNbBStagsDuo[run][lastEvalRun] > hashNbHares[run][lastEvalRun] :
	# 			runStags.append(run)

	# 	for evaluation in tabPlotEvaluation :
	# 		listFitness = [hashFitness[run][evaluation] for run in hashFitness.keys() if run in runStags and evaluation in hashFitness[run].keys()]

	# 		if len(listFitness) > 0 :
	# 			dataBoxPlot.append(listFitness)

	# 	bp = axe1.boxplot(dataBoxPlot)

	# 	for i in range(0, len(bp['boxes'])):
	# 	   bp['boxes'][i].set_color(palette[cptData])
	# 	   # we have two whiskers!
	# 	   bp['whiskers'][i*2].set_color(palette[cptData])
	# 	   bp['whiskers'][i*2 + 1].set_color(palette[cptData])
	# 	   bp['whiskers'][i*2].set_linewidth(2)
	# 	   bp['whiskers'][i*2 + 1].set_linewidth(2)

	# 	   # top and bottom fliers
	# 	   # (set allows us to set many parameters at once)
	# 	   # bp['fliers'][i * 2].set(markerfacecolor=palette[cptData],
	# 	   #                 marker='o', alpha=0.75, markersize=6,
	# 	   #                 markeredgecolor='none')
	# 	   # bp['fliers'][i * 2 + 1].set(markerfacecolor=palette[cptData],
	# 	   #                 marker='o', alpha=0.75, markersize=6,
	# 	   #                 markeredgecolor='none')

	# 	   bp['medians'][i].set_color('black')
	# 	   bp['medians'][i].set_linewidth(3)

	# 	   # and 4 caps to remove
	# 	   for c in bp['caps']:
	# 	       c.set_linewidth(0)

	# 	cptData += 1


	# axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
	# axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
	# axe1.set_xlabel("Evaluation")

	# axe1.set_ylabel("Fitness")
	# # axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

	# axe1.set_title('Boxplot of best fitness')

	# plt.savefig(outputDir + "/boxplotStags.png", bbox_inches = 'tight')
	# plt.close()


	# Fitness Boxplots Stags
	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# plt.axes(frameon=0)
	plt.grid()

	cptData = 0
	for data in dataHash :
		dataPlot = []
		dataPerc25 = []
		dataPerc75 = []
		hashFitness = data['hashFitness']
		hashNbBStags = data['hashNbBStags']
		hashNbBStagsDuo = data['hashNbBStagsDuo']
		hashNbHares = data['hashNbHares']

		runStags = []
		for run in hashNbBStags.keys() :
			lastEvalRun = sorted(hashNbHares[run].keys())[-1]
			# if hashNbBStags[run][lastEvalRun] > hashNbHares[run][lastEvalRun] and hashNbBStags[run][lastEvalRun] > 1 :
			# 	runStags.append(run)
			if hashNbBStagsDuo[run][lastEvalRun] > hashNbHares[run][lastEvalRun] and hashNbBStagsDuo[run][lastEvalRun] > 1 :
				runStags.append(run)

		for evaluation in tabPlotEvaluation :
			fitnessEval = [hashFitness[run][evaluation] for run in hashFitness.keys() if run in runStags and evaluation in hashFitness[run].keys()]
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


	axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
	axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
	axe1.set_xlabel("Evaluation")

	axe1.set_ylabel("Fitness")
	# axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

	legend = plt.legend(['Aclonal', 'Clonal', 'Co-evolution'], loc = 4, frameon=True)
	frame = legend.get_frame()
	frame.set_facecolor('0.9')
	frame.set_edgecolor('0.9')

	axe1.set_title('Boxplot of best fitness')

	plt.savefig(outputDir + "/boxplotStags.png", bbox_inches = 'tight')
	plt.close()



def drawWaypointsTask() :
	if os.path.isdir(outputDir) :
		if removeOutput :
			shutil.rmtree(outputDir)
			os.makedirs(outputDir)
	else :
		os.makedirs(outputDir)

	tabEvaluation = []
	dataHash = []
	for directory in directories :
		if os.path.isdir(directory) :
			listBestFit = [f for f in os.listdir(directory) if (os.path.isfile(directory + "/" + f) and re.match(r"^bestfit(\d*)\.dat$", f))]

			hashFitness = {}

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
					data = np.loadtxt(directory + "/" + fileBest, delimiter=',', usecols = (0, 1), dtype = dtypes)

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

								cpt = 0

						if firstEval :
							firstEval = False


			hashData = {}
			hashData["hashFitness"] = hashFitness

			dataHash.append(hashData)



	tabEvaluation = sorted(tabEvaluation)
	# lastEval = tabEvaluation[-1]
	# diffEvals = lastEval - tabEvaluation[-2]

	# while lastEval <= maxEval :
	# 	lastEval += diffEvals
	# 	tabEvaluation.append(lastEval)


	# Statistical Analysis
	if args.statAnalysis :
		cpt = 0
		while cpt < len(dataHash) :
			minEvalSerie1 = None
			hashFitness = dataHash[cpt]["hashFitness"]

			for run in hashFitness.keys() :
				lastEval = sorted(hashFitness[run].keys())[-1]

				if minEvalSerie1 == None or lastEval < minEvalSerie1 :
					minEvalSerie1 = lastEval

			serie1 = [hashFitness[run][minEvalSerie1] for run in hashFitness.keys()]
			
			cpt2 = cpt + 1
			while cpt2 < len(dataHash) :
				minEvalSerie2 = None
				hashFitness = dataHash[cpt2]["hashFitness"]

				for run in hashFitness.keys() :
					lastEval = sorted(hashFitness[run].keys())[-1]

					if minEvalSerie2 == None or lastEval < minEvalSerie2 :
						minEvalSerie2 = lastEval

				serie2 = [hashFitness[run][minEvalSerie2] for run in hashFitness.keys()]

				U, P = stats.mannwhitneyu(serie1, serie2)
				print("Min1 = " + str(minEvalSerie1) + ", Min2 = " + str(minEvalSerie2))
				print("Mann-Whitney (" + directories[cpt] + ", " + directories[cpt2] + ")\n\t -> U = " + str(U) + "/P = " + str(P))

				with open(os.path.join(outputDir, "statAnalysis.txt"), 'w') as fileWrite :
					fileWrite.write("Min1 = " + str(minEvalSerie1) + ", Min2 = " + str(minEvalSerie2))
					fileWrite.write("Mann-Whitney (" + directories[cpt] + ", " + directories[cpt2] + ")\n\t -> U = " + str(U) + "/P = " + str(P))

				cpt2 += 1
			cpt += 1


	# SEABORN
	sns.set()
	sns.set_style('white')
	sns.set_context('paper')
	palette = sns.color_palette("husl", len(directories))

	matplotlib.rcParams['font.size'] = 15
	matplotlib.rcParams['font.weight'] = 'bold'
	matplotlib.rcParams['axes.labelsize'] = 15
	matplotlib.rcParams['axes.labelweight'] = 'bold'
	matplotlib.rcParams['xtick.labelsize'] = 15
	matplotlib.rcParams['ytick.labelsize'] = 15
	matplotlib.rcParams['legend.fontsize'] = 15

	linewidth = 2
	# linestyles = ['-', '-', '-']
	linestyles = ['-', '--', '-.', ':']
	markers = [None, None, None, None] #['o', '+', '*']

	dpi = 96
	size = (1280/dpi, 1024/dpi)

	tabPlotEvaluation = tabEvaluation


	# # Fitness Boxplots Stags
	# fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

	# cptData = 0
	# for data in dataHash :
	# 	dataBoxPlot = []
	# 	hashFitness = data['hashFitness']
	# 	hashNbBStags = data['hashNbBStags']
	# 	hashNbBStagsDuo = data['hashNbBStagsDuo']
	# 	hashNbHares = data['hashNbHares']

	# 	runStags = []
	# 	for run in hashNbBStags.keys() :
	# 		lastEvalRun = sorted(hashNbHares[run].keys())[-1]
	# 		if hashNbBStagsDuo[run][lastEvalRun] > hashNbHares[run][lastEvalRun] :
	# 			runStags.append(run)

	# 	for evaluation in tabPlotEvaluation :
	# 		listFitness = [hashFitness[run][evaluation] for run in hashFitness.keys() if run in runStags and evaluation in hashFitness[run].keys()]

	# 		if len(listFitness) > 0 :
	# 			dataBoxPlot.append(listFitness)

	# 	bp = axe1.boxplot(dataBoxPlot)

	# 	for i in range(0, len(bp['boxes'])):
	# 	   bp['boxes'][i].set_color(palette[cptData])
	# 	   # we have two whiskers!
	# 	   bp['whiskers'][i*2].set_color(palette[cptData])
	# 	   bp['whiskers'][i*2 + 1].set_color(palette[cptData])
	# 	   bp['whiskers'][i*2].set_linewidth(2)
	# 	   bp['whiskers'][i*2 + 1].set_linewidth(2)

	# 	   # top and bottom fliers
	# 	   # (set allows us to set many parameters at once)
	# 	   # bp['fliers'][i * 2].set(markerfacecolor=palette[cptData],
	# 	   #                 marker='o', alpha=0.75, markersize=6,
	# 	   #                 markeredgecolor='none')
	# 	   # bp['fliers'][i * 2 + 1].set(markerfacecolor=palette[cptData],
	# 	   #                 marker='o', alpha=0.75, markersize=6,
	# 	   #                 markeredgecolor='none')

	# 	   bp['medians'][i].set_color('black')
	# 	   bp['medians'][i].set_linewidth(3)

	# 	   # and 4 caps to remove
	# 	   for c in bp['caps']:
	# 	       c.set_linewidth(0)

	# 	cptData += 1


	# axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
	# axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
	# axe1.set_xlabel("Evaluation")

	# axe1.set_ylabel("Fitness")
	# # axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

	# axe1.set_title('Boxplot of best fitness')

	# plt.savefig(outputDir + "/boxplotStags.png", bbox_inches = 'tight')
	# plt.close()


	# Fitness Boxplots
	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# plt.axes(frameon=0)
	plt.grid()

	cptData = 0
	for data in dataHash :
		dataPlot = []
		dataPerc25 = []
		dataPerc75 = []
		hashFitness = data['hashFitness']

		for evaluation in tabPlotEvaluation :
			fitnessEval = [hashFitness[run][evaluation] for run in hashFitness.keys() if evaluation in hashFitness[run].keys()]
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


		# print(dataPlot)
		axe1.plot(range(len(dataPlot)), dataPlot, color=palette[cptData], linestyle=linestyles[cptData], linewidth=linewidth, marker=markers[cptData])

		plt.fill_between(range(len(dataPlot)), dataPerc25, dataPerc75, alpha=0.25, linewidth=0, color=palette[cptData])

		cptData += 1
		# break


	axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
	axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
	axe1.set_xlabel("Evaluation")

	axe1.set_ylabel("Fitness")
	# axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

	legend = plt.legend(['Aclonal', 'Clonal', 'Co-evolution'], loc = 4, frameon=True)
	frame = legend.get_frame()
	frame.set_facecolor('0.9')
	frame.set_edgecolor('0.9')

	axe1.set_title('Boxplot of best fitness')

	plt.savefig(outputDir + "/boxplot.png", bbox_inches = 'tight')
	plt.close()



def drawLeadership() :
	if os.path.isdir(outputDir) :
		if removeOutput :
			shutil.rmtree(outputDir)
			os.makedirs(outputDir)
	else :
		os.makedirs(outputDir)

	tabEvaluation = []
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
					for line in data :
						evaluation = line['evaluation']

						cpt += evaluation - lastEval
						lastEval = evaluation

						if cpt > precision or firstEval :
							if evaluation < maxEval :
								hashProportion[run][evaluation] = line['proportion']
								hashProportionAsym[run][evaluation] = line['proportionAsym'] - 0.5
								# hashNbLeaderFirst[run][evaluation] = line['nb_leader_first']
								# hashNbTotalCoop[run][evaluation] = line['nb_total_coop']

								if evaluation not in tabEvaluation :
									tabEvaluation.append(evaluation)

								cpt = 0

						if firstEval :
							firstEval = False


			hashData = {}
			hashData["hashProportion"] = hashProportion
			hashData["hashProportionAsym"] = hashProportionAsym

			dataHash.append(hashData)



	tabEvaluation = sorted(tabEvaluation)
	# lastEval = tabEvaluation[-1]
	# diffEvals = lastEval - tabEvaluation[-2]

	# while lastEval <= maxEval :
	# 	lastEval += diffEvals
	# 	tabEvaluation.append(lastEval)


	# Statistical Analysis
	if args.statAnalysis :
		cpt = 0
		while cpt < len(dataHash) :
			minEvalSerie1 = None
			hashProportion = dataHash[cpt]["hashProportion"]

			for run in hashProportion.keys() :
				lastEval = sorted(hashProportion[run].keys())[-1]

				if minEvalSerie1 == None or lastEval < minEvalSerie1 :
					minEvalSerie1 = lastEval

			serie1 = [hashProportion[run][minEvalSerie1] for run in hashProportion.keys()]
			
			cpt2 = cpt + 1
			while cpt2 < len(dataHash) :
				minEvalSerie2 = None
				hashProportion = dataHash[cpt2]["hashProportion"]

				for run in hashProportion.keys() :
					lastEval = sorted(hashProportion[run].keys())[-1]

					if minEvalSerie2 == None or lastEval < minEvalSerie2 :
						minEvalSerie2 = lastEval

				serie2 = [hashProportion[run][minEvalSerie2] for run in hashProportion.keys()]

				U, P = stats.mannwhitneyu(serie1, serie2)
				print("Min1 = " + str(minEvalSerie1) + ", Min2 = " + str(minEvalSerie2))
				print("Mann-Whitney (" + directories[cpt] + ", " + directories[cpt2] + ")\n\t -> U = " + str(U) + "/P = " + str(P))

				with open(os.path.join(outputDir, "statAnalysis.txt"), 'w') as fileWrite :
					fileWrite.write("Min1 = " + str(minEvalSerie1) + ", Min2 = " + str(minEvalSerie2))
					fileWrite.write("Mann-Whitney (" + directories[cpt] + ", " + directories[cpt2] + ")\n\t -> U = " + str(U) + "/P = " + str(P))

				cpt2 += 1
			cpt += 1


	# SEABORN
	sns.set()
	sns.set_style('white')
	sns.set_context('paper')
	palette = sns.color_palette("husl", len(directories))

	matplotlib.rcParams['font.size'] = 15
	matplotlib.rcParams['font.weight'] = 'bold'
	matplotlib.rcParams['axes.labelsize'] = 15
	matplotlib.rcParams['axes.labelweight'] = 'bold'
	matplotlib.rcParams['xtick.labelsize'] = 15
	matplotlib.rcParams['ytick.labelsize'] = 15
	matplotlib.rcParams['legend.fontsize'] = 15

	linewidth = 2
	linestyles = ['-', '--', '-.', ':']
	markers = [None, None, None, None] #['o', '+', '*']

	dpi = 96
	size = (1280/dpi, 1024/dpi)

	tabPlotEvaluation = tabEvaluation


	# # Fitness Boxplots Stags
	# fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

	# cptData = 0
	# for data in dataHash :
	# 	dataBoxPlot = []
	# 	hashFitness = data['hashFitness']
	# 	hashNbBStags = data['hashNbBStags']
	# 	hashNbBStagsDuo = data['hashNbBStagsDuo']
	# 	hashNbHares = data['hashNbHares']

	# 	runStags = []
	# 	for run in hashNbBStags.keys() :
	# 		lastEvalRun = sorted(hashNbHares[run].keys())[-1]
	# 		if hashNbBStagsDuo[run][lastEvalRun] > hashNbHares[run][lastEvalRun] :
	# 			runStags.append(run)

	# 	for evaluation in tabPlotEvaluation :
	# 		listFitness = [hashFitness[run][evaluation] for run in hashFitness.keys() if run in runStags and evaluation in hashFitness[run].keys()]

	# 		if len(listFitness) > 0 :
	# 			dataBoxPlot.append(listFitness)

	# 	bp = axe1.boxplot(dataBoxPlot)

	# 	for i in range(0, len(bp['boxes'])):
	# 	   bp['boxes'][i].set_color(palette[cptData])
	# 	   # we have two whiskers!
	# 	   bp['whiskers'][i*2].set_color(palette[cptData])
	# 	   bp['whiskers'][i*2 + 1].set_color(palette[cptData])
	# 	   bp['whiskers'][i*2].set_linewidth(2)
	# 	   bp['whiskers'][i*2 + 1].set_linewidth(2)

	# 	   # top and bottom fliers
	# 	   # (set allows us to set many parameters at once)
	# 	   # bp['fliers'][i * 2].set(markerfacecolor=palette[cptData],
	# 	   #                 marker='o', alpha=0.75, markersize=6,
	# 	   #                 markeredgecolor='none')
	# 	   # bp['fliers'][i * 2 + 1].set(markerfacecolor=palette[cptData],
	# 	   #                 marker='o', alpha=0.75, markersize=6,
	# 	   #                 markeredgecolor='none')

	# 	   bp['medians'][i].set_color('black')
	# 	   bp['medians'][i].set_linewidth(3)

	# 	   # and 4 caps to remove
	# 	   for c in bp['caps']:
	# 	       c.set_linewidth(0)

	# 	cptData += 1


	# axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
	# axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
	# axe1.set_xlabel("Evaluation")

	# axe1.set_ylabel("Fitness")
	# # axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

	# axe1.set_title('Boxplot of best fitness')

	# plt.savefig(outputDir + "/boxplotStags.png", bbox_inches = 'tight')
	# plt.close()


	# Fitness Boxplots
	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# plt.axes(frameon=0)
	plt.grid()

	cptData = 0
	for data in dataHash :
		dataPlot = []
		dataPerc25 = []
		dataPerc75 = []
		hashProportion = data['hashProportion']

		runSuccess = []
		for run in hashProportion.keys() :
			lastEvalRun = sorted(hashProportion[run].keys())[-1]
			if hashProportion[run][lastEvalRun] > 0.75 :
				runSuccess.append(run)

		for evaluation in tabPlotEvaluation :
			proportionEval = [hashProportion[run][evaluation] for run in hashProportion.keys() if run in runSuccess and evaluation in hashProportion[run].keys()]
			proportionMed = np.median(proportionEval)

			perc25 = proportionMed
			perc75 = proportionMed
			if len(proportionEval) > 1 :
				perc25 = np.percentile(proportionEval, 25)
				perc75 = np.percentile(proportionEval, 75)

			dataPlot.append(proportionMed)
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


	axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
	axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
	axe1.set_xlabel("Evaluation")

	axe1.set_ylabel("Proportion")
	# axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

	legend = plt.legend(['Aclonal', 'Clonal', 'Co-evolution'], loc = 4, frameon=True)
	frame = legend.get_frame()
	frame.set_facecolor('0.9')
	frame.set_edgecolor('0.9')

	axe1.set_title('Boxplot of best proportion')

	plt.savefig(outputDir + "/boxplotProportionSuccess.png", bbox_inches = 'tight')
	plt.close()


	# Fitness Boxplots Success
	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# plt.axes(frameon=0)
	plt.grid()

	cptData = 0
	for data in dataHash :
		dataPlot = []
		dataPerc25 = []
		dataPerc75 = []
		hashProportion = data['hashProportion']

		for evaluation in tabPlotEvaluation :
			proportionEval = [hashProportion[run][evaluation] for run in hashProportion.keys() if evaluation in hashProportion[run].keys()]
			proportionMed = np.median(proportionEval)

			perc25 = proportionMed
			perc75 = proportionMed
			if len(proportionEval) > 1 :
				perc25 = np.percentile(proportionEval, 25)
				perc75 = np.percentile(proportionEval, 75)

			dataPlot.append(proportionMed)
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


	axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
	axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
	axe1.set_xlabel("Evaluation")

	axe1.set_ylabel("Proportion")
	# axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

	legend = plt.legend(['Aclonal', 'Clonal', 'Co-evolution'], loc = 4, frameon=True)
	frame = legend.get_frame()
	frame.set_facecolor('0.9')
	frame.set_edgecolor('0.9')

	axe1.set_title('Boxplot of best proportion')

	plt.savefig(outputDir + "/boxplotProportion.png", bbox_inches = 'tight')
	plt.close()

def main(args) :
	global maxEval
	maxEval = int(args.max)

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

	if args.drawLeadership :
		print("\t-> Drawing Leadership")
		drawLeadership()
	else :
		if not args.drawWaypoints :
			print("\t-> Drawing Hunting Task")
			drawHuntingTask()
		else :
			print("\t-> Drawing Waypoints Task")
			drawWaypointsTask()



if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directories', help = "Directories to plot", type=str, nargs='+')

	# parser.add_argument('-c', '--coop', help = "Compute the statistical test on proportion of cooperation", default = False, action = "store_true")

	parser.add_argument('-m', '--max', help = "Max evaluation", default='20000', type=int)
	parser.add_argument('-p', '--precision', help = "Precision", default='100', type=int)

	parser.add_argument('-o', '--output', help = "Output directory", default='GraphsResults')
	parser.add_argument('-r', '--removeOutput', help = "Remove output directory if exists", default=False, action='store_true')

	parser.add_argument('-a', '--statAnalysis', help = "Compute Mann-Whitney", default=False, action='store_true')
	parser.add_argument('-w', '--drawWaypoints', help = "Draw waypoints task", default=False, action='store_true')
	parser.add_argument('-l', '--drawLeadership', help = "Draw leadership", default=False, action='store_true')

	parser.add_argument('-s', '--selection', help = "Selected runs", default=None, type=int, nargs='+')
	parser.add_argument('-e', '--exclusion', help = "Excluded runs", default=None, type=int, nargs='+')

	args = parser.parse_args()

	main(args)
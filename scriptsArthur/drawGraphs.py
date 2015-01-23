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
		maxFitness = 0
		maxNbPreys = 0
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
				hashRatioHares[run] = {}

				dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
				data = np.loadtxt(dossier + "/" + fileBest, delimiter=',', usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

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

							hashRatio[run][evaluation] = line['nbBStags']*100/(line['nbHares'] + line['nbBStags'])
							hashRatioHares[run][evaluation] = line['nbHares']*100/(line['nbHares'] + line['nbBStags'])

							if evaluation not in tabEvaluation :
								tabEvaluation.append(evaluation)

							if line['fitness'] > maxFitness :
								maxFitness = line['fitness']

							if (line['nbHares'] + line['nbBStags']) > maxNbPreys :
								maxNbPreys = (line['nbHares'] + line['nbBStags'])

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

		dpi = 96

		tabPlotEvaluation = tabEvaluation

		# --- BOXPLOT FITNESS ---
		dataBoxPlot = []
		for evaluation in tabPlotEvaluation :
			listFitness = [hashFitness[run][evaluation] for run in hashFitness.keys() if evaluation in hashFitness[run].keys()]

			if len(listFitness) > 0 :
				dataBoxPlot.append(listFitness)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
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
		for run in hashNbHaresSolo.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))

			width = 0.8

			tabNbHaresSolo = [hashNbHaresSolo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbHaresSolo[run].keys()]
			tabNbHaresDuo = [hashNbHaresDuo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbHaresDuo[run].keys()]
			tabNbBStagsSolo = [hashNbBStagsSolo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbBStagsSolo[run].keys()]
			tabNbBStagsDuo = [hashNbBStagsDuo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbBStagsDuo[run].keys()]

			barNbHaresSolo = axe1.bar(range(len(tabNbHaresSolo)), tabNbHaresSolo, width = width, color = colorHaresSolo, alpha = alphaHares)
			barNbHaresDuo = axe1.bar(range(len(tabNbHaresDuo)), tabNbHaresDuo, bottom = tabNbHaresSolo, width = width, color = colorHaresDuo, alpha = alphaHares)
			barNbBStagsSolo = axe1.bar(range(len(tabNbBStagsSolo)), tabNbBStagsSolo, bottom = np.add(tabNbHaresDuo, tabNbHaresSolo), width = width, color = colorBStagsSolo, alpha = alphaBStags)
			barNbBStagsDuo = axe1.bar(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, bottom = np.add(tabNbBStagsSolo, np.add(tabNbHaresDuo, tabNbHaresSolo)), width = width, color = colorBStagsDuo, alpha = alphaBStags)

			tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]

			axe1.set_xticks(tabEvaluationTicks)
			axe1.set_xticklabels([tabPlotEvaluation[indice] for indice in tabEvaluationTicks])
			axe1.set_xlabel('Evaluation')
			# axe1.set_xlim(0, len(tabGenerationTicks))

			axe1.set_ylim(0, maxNbPreys + 0.1*maxNbPreys)
			axe1.set_ylabel('Number of preys hunted')
			
			axe1.set_title('Repartition of preys hunted', fontsize = 10)

			plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Stags solo', 'Stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

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

		dpi = 96

		tabPlotEvaluation = tabEvaluation


		# --- BOXPLOT RUN FITNESS ---
		dataBoxPlot = []
		for run in hashFitness.keys() :
			dataBoxPlot = [hashFitness[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashFitness[run].keys()]

			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
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


		# --- BARS ---
		for run in hashNbHaresSolo.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))

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

		tabEvaluation = []
		maxDiversity = 0
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

				cpt = 0
				firstEval = True
				lastEval = 0
				for line in data :
					evaluation = line['evaluation']

					cpt += evaluation - lastEval
					lastEval = evaluation

					if cpt > precision or firstEval :
						if evaluation < maxEval :
							hashDiversity[run][evaluation] = line['diversity']

							hashNbHares[run][evaluation] = line['nbHares']
							hashNbHaresSolo[run][evaluation] = line['nbHaresSolo']
							hashNbHaresDuo[run][evaluation] = line['nbHares'] - line['nbHaresSolo']

							hashNbSStags[run][evaluation] = line['nbSStags']
							hashNbSStagsSolo[run][evaluation] = line['nbSStagsSolo']
							hashNbSStagsDuo[run][evaluation] = line['nbSStags'] - line['nbSStagsSolo']

							hashNbBStags[run][evaluation] = line['nbBStags']
							hashNbBStagsSolo[run][evaluation] = line['nbBStagsSolo']
							hashNbBStagsDuo[run][evaluation] = line['nbBStags'] - line['nbBStagsSolo']

							hashRatio[run][evaluation] = line['nbBStags']*100/(line['nbHares'] + line['nbBStags'])
							hashRatioHares[run][evaluation] = line['nbHares']*100/(line['nbHares'] + line['nbBStags'])

							if evaluation not in tabEvaluation :
								tabEvaluation.append(evaluation)

							if line['diversity'] > maxDiversity :
								maxDiversity = line['diversity']

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

		dpi = 96

		tabPlotEvaluation = tabEvaluation

		# --- BOXPLOT FITNESS ---
		dataBoxPlot = []
		for evaluation in tabPlotEvaluation :
			listDiversity = [hashDiversity[run][evaluation] for run in hashDiversity.keys() if evaluation in hashDiversity[run].keys()]

			if len(listDiversity) > 0 :
				dataBoxPlot.append(listDiversity)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
		axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
		axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
		axe1.set_xlabel("Evaluation")

		axe1.set_ylabel("Diversity")
		axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

		axe1.set_title('Boxplot of best diversity')

		plt.savefig(dossier + "/boxplot.png", bbox_inches = 'tight')
		plt.close()



		# --- RUNS FITNESS ---
		palette = sns.color_palette("husl", len(hashDiversity.keys()))
		for run in hashDiversity.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))

			tabDiversity = [hashDiversity[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashDiversity[run].keys()]

			axe1.plot(range(len(tabDiversity)), tabDiversity)

			# Divide the x axis by 10
			# tabEvaluationTicks = [indice for indice in range(len(tabDiversity)) if indice % (int(len(tabDiversity)/10)) == 0]
			tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]

			axe1.set_xticks(tabEvaluationTicks)
			axe1.set_xticklabels([tabPlotEvaluation[indice] for indice in tabEvaluationTicks])
			axe1.set_xlabel('Evaluation')

			axe1.set_ylabel('Diversity')
			axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

			axe1.set_title('Best diversity', fontsize = 10)

			plt.savefig(dossier + "/diversityRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()



		# --- BARS ---
		for run in hashNbHaresSolo.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))

			width = 0.8

			tabNbHaresSolo = [hashNbHaresSolo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbHaresSolo[run].keys()]
			tabNbHaresDuo = [hashNbHaresDuo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbHaresDuo[run].keys()]
			tabNbBStagsSolo = [hashNbBStagsSolo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbBStagsSolo[run].keys()]
			tabNbBStagsDuo = [hashNbBStagsDuo[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashNbBStagsDuo[run].keys()]

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

		tabEvaluation = []
		hashDiversityGlob = {}
		maxDiversity = 0
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
								hashDiversity[run][evaluation] = []
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

								hashDiversityGlob[evaluation] = []

								evalDone.append(evaluation)

							hashDiversity[run][evaluation].append(line['diversity'])

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

							hashDiversityGlob[evaluation].append(line['diversity'])

							if evaluation not in tabEvaluation :
								tabEvaluation.append(evaluation)

							if line['diversity'] > maxDiversity :
								maxDiversity = line['diversity']


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


		# --- BOXPLOT RUN FITNESS ---
		dataBoxPlot = []
		for run in hashDiversity.keys() :
			dataBoxPlot = [hashDiversity[run][evaluation] for evaluation in tabPlotEvaluation if evaluation in hashDiversity[run].keys()]

			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
			axe1.boxplot(dataBoxPlot)

			axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
			axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
			axe1.set_xlabel("Evaluation")

			axe1.set_ylabel("Diversity")
			axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

			axe1.set_title('Boxplot of population diversity')

			plt.savefig(dossier + "/diversityRun" + str(run) + ".png", bbox_inches = 'tight')
			plt.close()


		# --- BOXPLOT ALL RUN FITNESS ---
		dataBoxPlot = [hashDiversityGlob[evaluation] for evaluation in tabPlotEvaluation if evaluation in hashDiversityGlob.keys()]

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
		axe1.boxplot(dataBoxPlot)

		axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
		axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])
		axe1.set_xlabel("Evaluation")

		axe1.set_ylabel("Diversity")
		axe1.set_ylim(0, maxDiversity + 0.1*maxDiversity)

		axe1.set_title('Boxplot of all diversity')

		plt.savefig(dossier + "/globalDiversity", bbox_inches = 'tight')
		plt.close()


		# --- BARS ---
		for run in hashNbHaresSolo.keys() :
			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))

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

		tabEvaluation = []
		maxDiversity = 0
		maxFitness = 0
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
								hashDiversity[run][evaluation] = []
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
								hashRatioCoop[run][evaluation] = []

								evalDone.append(evaluation)

							hashDiversity[run][evaluation].append(line['diversity'])

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
							hashRatioCoop[run][evaluation].append((line['nbHares'] - line['nbHaresSolo'] + (line['nbBStags'] - line['nbBStagsSolo']))*100/((line['nbHares'] + line['nbBStags'])))

							if evaluation not in tabEvaluation :
								tabEvaluation.append(evaluation)

							if line['diversity'] > maxDiversity :
								maxDiversity = line['diversity']


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

					if cpt > precision and evaluation in hashDiversity[run].keys() :
						if evaluation < maxEval :
							hashFitness[run][evaluation].append(line['fitness'])

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

		dpi = 96

		tabPlotEvaluation = tabEvaluation


		# Pareto Frontier
		for run in hashFitness.keys() :
			assert(len(hashFitness[run].keys()) == len(hashDiversity[run].keys()))
			lastEvalRun = sorted(hashFitness[run].keys())[-1]
			assert(lastEvalRun == sorted(hashDiversity[run].keys())[-1])

			listFitness = hashFitness[run][lastEvalRun]
			listDiversity = hashDiversity[run][lastEvalRun]

			listRatio = hashRatio[run][lastEvalRun]
			listColors = [0 if math.isnan(ratio) else int(ratio) for ratio in listRatio]

			listRatioCoop = hashRatioCoop[run][lastEvalRun]
			listSizes = [50 if math.isnan(ratio) else 50 + int(ratio*2) for ratio in listRatioCoop]

			p_front = pareto_frontier(listFitness, listDiversity, maxX = True, maxY = True)

			fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
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

		tabEvaluation = []
		maxDiversity = 0
		maxFitness = 0

		testRun = None
		if selection != None :
			testRun = lambda run : run in selection
		elif exclusion != None :
			testRun = lambda run : run not in exclusion

		if (testRun == None) or (testRun(run)) :
			dtypes = np.dtype({ 'names' : ('evaluation', 'diversity', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
			data = np.loadtxt(os.path.join(dossier, 'alldivevalstat.dat'), delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

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
							hashDiversity[evaluation] = []
							hashFitness[evaluation] = []

							hashNbHaresDuo[evaluation] = []
							hashNbHaresSolo[evaluation] = []
							hashNbHares[evaluation] = []

							hashNbSStagsDuo[evaluation] = []
							hashNbSStagsSolo[evaluation] = []
							hashNbSStags[evaluation] = []

							hashNbBStagsDuo[evaluation] = []
							hashNbBStagsSolo[evaluation] = []
							hashNbBStags[evaluation] = []

							hashRatio[evaluation] = []
							hashRatioHares[evaluation] = []
							hashRatioCoop[evaluation] = []

							evalDone.append(evaluation)

						hashDiversity[evaluation].append(line['diversity'])

						hashNbHares[evaluation].append(line['nbHares'])
						hashNbHaresSolo[evaluation].append(line['nbHaresSolo'])
						hashNbHaresDuo[evaluation].append(line['nbHares'] - line['nbHaresSolo'])

						hashNbSStags[evaluation].append(line['nbSStags'])
						hashNbSStagsSolo[evaluation].append(line['nbSStagsSolo'])
						hashNbSStagsDuo[evaluation].append(line['nbSStags'] - line['nbSStagsSolo'])

						hashNbBStags[evaluation].append(line['nbBStags'])
						hashNbBStagsSolo[evaluation].append(line['nbBStagsSolo'])
						hashNbBStagsDuo[evaluation].append(line['nbBStags'] - line['nbBStagsSolo'])

						hashRatio[evaluation].append(line['nbBStags']*100/(line['nbHares'] + line['nbBStags']))
						hashRatioHares[evaluation].append(line['nbHares']*100/(line['nbHares'] + line['nbBStags']))
						hashRatioCoop[evaluation].append((line['nbHares'] - line['nbHaresSolo'] + (line['nbBStags'] - line['nbBStagsSolo']))*100/((line['nbHares'] + line['nbBStags'])))

						if evaluation not in tabEvaluation :
							tabEvaluation.append(evaluation)

						if line['diversity'] > maxDiversity :
							maxDiversity = line['diversity']


			dtypes = np.dtype({ 'names' : ('evaluation', 'fitness', 'nbHares', 'nbHaresSolo', 'nbSStags', 'nbSStagsSolo', 'nbBStags', 'nbBStagsSolo'), 'formats' : [np.int, np.float, np.float, np.float, np.float, np.float, np.float, np.float] })
			data = np.loadtxt(os.path.join(dossier, 'allfitevalstat.dat'), delimiter=',', skiprows = 1, usecols = (0, 1, 2, 3, 4, 5, 6, 7), dtype = dtypes)

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
						hashFitness[evaluation].append(line['fitness'])

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

			dpi = 96

			tabPlotEvaluation = tabEvaluation


			# Pareto Frontier
			assert(len(hashFitness.keys()) == len(hashDiversity.keys()))
			lastEvalRun = sorted(hashFitness.keys())[-1]
			assert(lastEvalRun == sorted(hashDiversity.keys())[-1])

			paretoEvals = sorted(hashFitness.keys())[0:-1:int(math.floor(len(hashFitness.keys())/20.0))]

			if lastEvalRun not in paretoEvals :
				paretoEvals.append(lastEvalRun)

			for eval in paretoEvals :
				listFitness = hashFitness[eval]
				listDiversity = hashDiversity[eval]

				listRatio = hashRatio[eval]
				listColors = [0 if math.isnan(ratio) else int(ratio) for ratio in listRatio]

				listRatioCoop = hashRatioCoop[eval]
				listSizes = [50 if math.isnan(ratio) else 50 + int(ratio*2) for ratio in listRatioCoop]

				p_front = pareto_frontier(listFitness, listDiversity, maxX = True, maxY = True)

				fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = (800/dpi, 600/dpi))
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
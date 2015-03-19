#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import lines
import matplotlib.cm as cm
from matplotlib import animation
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from operator import itemgetter
import seaborn as sns
import numpy as np
import re
import os
import math
import sys


# COLORS
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


# SEABORN
sns.set()
sns.set_style('white')
sns.set_context('paper')
# palette = sns.color_palette("husl", len(hashNbBStags.keys()))

matplotlib.rcParams['font.size'] = 15
matplotlib.rcParams['font.weight'] = 'bold'
matplotlib.rcParams['axes.labelsize'] = 15
matplotlib.rcParams['axes.labelweight'] = 'bold'
matplotlib.rcParams['xtick.labelsize'] = 15
matplotlib.rcParams['ytick.labelsize'] = 15
matplotlib.rcParams['legend.fontsize'] = 15

dpi = 96
size = (1280/dpi, 1024/dpi)

plt.grid()


def loadParam(param, **params) :
	if param in params.keys() : 
		return params[param]
	else
		print(param + " not in Parameters")
		sys.exit(0)


def setTicks(tabPlot, axe) :
	if tabPlot != None :
		# Divide the x axis by 10
		tabEvaluationTicks = [indice for indice in range(len(tabPlot)) if indice % (int(len(tabPlot)/10)) == 0]

		axe.set_xticks(tabEvaluationTicks)
		axe.set_xticklabels([tabPlot[indice] for indice in tabEvaluationTicks])



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



###################################################################
# - DRAW RUN FITNESS                                            - #
###################################################################
def drawRunFitness(dossier, **params) :
	hashFitness = loadParam("hashFitness", params)
	maxFitness = loadParam("maxFitness", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))
	ylabel = loadParam("ylabel", params)

	palette = sns.color_palette("husl", len(hashFitness.keys()))
	for run in hashFitness.keys() :
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		tabFitness = [hashFitness[run][evaluation] for evaluation in tabPlot if evaluation in hashFitness[run].keys()]

		axe1.plot(range(len(tabFitness)), tabFitness)

		setTicks(tabPlot, axe1)

		if drawEval :
			axe1.set_xlabel('Evaluation')
		else :
			axe1.set_xlabel('Generation')

		axe1.set_ylabel(ylabel)
		axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

		axe1.set_title('Best ' + ylabel, fontsize = 10)

		plt.savefig(dossier + "/" + ylabel.lower() + "Run" + str(run) + ".png", bbox_inches = 'tight')
		plt.close()



###################################################################
# - DRAW RUN RATIO BSTAGS SUCCESS                               - #
###################################################################
def drawRunRatioBStagSuccess(dossier, **params) :
	hashRatioSuccess = loadParam("hashRatioSuccess", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))
	prolongedRuns = bool(loadParam("drawEval", params))

	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

	cpt = 0
	lastVals = []
	captions = []
	palette = sns.color_palette("husl", len(hashRatioSuccess.keys()))
	for run in hashRatioSuccess.keys() :
		tabRatio = [np.mean(hashRatioSuccess[run][evaluation]) for evaluation in tabPlot if evaluation in hashRatioSuccess[run].keys()]
		axe1.plot(range(len(tabRatio)), tabRatio, color = palette[cpt])
		lastVals.append(tabRatio[-1])
		captions.append("Run " + str(run))

		cpt += 1

	axe1.set_ylim(0, 100)

	sortedVals = zip(*(sorted(zip(lastVals, range(len(lastVals))), key = itemgetter(0))))
	sortedLastVals = sortedVals[0]
	sortedIndexes = sortedVals[1]

	if prolongedRuns :
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

	setTicks(tabPlot, axe1)

	if drawEval :
		axe1.set_xlabel('Evaluation')
	else :
		axe1.set_xlabel('Generation')

	axe1.set_ylabel('Pourcentage of stags hunted')

	plt.savefig(dossier + "/figureRatioBStagsSuccess.png", bbox_inches = 'tight')



###################################################################
# - DRAW BARS                                                   - #
###################################################################
def drawBars(dossier, **params) :
	hashNbHaresSolo = loadParam("hashNbHaresSolo", params)
	hashNbHaresDuo = loadParam("hashNbHaresDuo", params)
	hashNbBStagsSolo = loadParam("hashNbBStagsSolo", params)
	hashNbBStagsDuo = loadParam("hashNbBStagsDuo", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))
	drawLegend = bool(loadParams("drawLegend", params))


	# --- BARS ---
	for run in hashNbHaresSolo.keys() :
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		width = 0.8

		tabNbHaresSolo = [hashNbHaresSolo[run][evaluation] for evaluation in tabPlot if evaluation in hashNbHaresSolo[run].keys()]
		tabNbHaresDuo = [hashNbHaresDuo[run][evaluation] for evaluation in tabPlot if evaluation in hashNbHaresDuo[run].keys()]
		tabNbBStagsSolo = [hashNbBStagsSolo[run][evaluation] for evaluation in tabPlot if evaluation in hashNbBStagsSolo[run].keys()]
		tabNbBStagsDuo = [hashNbBStagsDuo[run][evaluation] for evaluation in tabPlot if evaluation in hashNbBStagsDuo[run].keys()]

		barNbHaresSolo = axe1.bar(range(len(tabNbHaresSolo)), tabNbHaresSolo, width = width, color = colorHaresSolo, alpha = alphaHares)
		barNbHaresDuo = axe1.bar(range(len(tabNbHaresDuo)), tabNbHaresDuo, bottom = tabNbHaresSolo, width = width, color = colorHaresDuo, alpha = alphaHares)
		barNbBStagsSolo = axe1.bar(range(len(tabNbBStagsSolo)), tabNbBStagsSolo, bottom = np.add(tabNbHaresDuo, tabNbHaresSolo), width = width, color = colorBStagsSolo, alpha = alphaBStags)
		barNbBStagsDuo = axe1.bar(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, bottom = np.add(tabNbBStagsSolo, np.add(tabNbHaresDuo, tabNbHaresSolo)), width = width, color = colorBStagsDuo, alpha = alphaBStags)

		setTicks(tabPlot, axe1)

		if drawEval :
			axe1.set_xlabel('Evaluation')
		else :
			axe1.set_xlabel('Generation')

		axe1.set_ylim(0, maxNbPreys + 0.1*maxNbPreys)
		axe1.set_ylabel('Number of preys hunted')
		
		axe1.set_title('Repartition of preys hunted', fontsize = 10)

		if drawLegend :
			plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Stags solo', 'Stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

		plt.savefig(dossier + "/preysRun" + str(run) + ".png", bbox_inches = 'tight')
		plt.close()



###################################################################
# - BOXPLOT RUN FITNESS                                         - #
###################################################################
def drawRunBoxplotFitness(dossier, **params) :
	hashFitness = loadParam("hashFitness", params)
	maxFitness = loadParam("maxFitness", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))
	ylabel = loadParam("ylabel", params)


	dataBoxPlot = []
	for run in hashFitness.keys() :
		dataBoxPlot = [hashFitness[run][evaluation] for evaluation in tabPlot if evaluation in hashFitness[run].keys()]

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)

		setTicks(tabPlot, axe1)

		if drawEval :
			axe1.set_xlabel('Evaluation')
		else :
			axe1.set_xlabel('Generation')

		axe1.set_ylabel(ylabel)
		axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

		axe1.set_title('Boxplot of population ' + ylabel)

		plt.savefig(dossier + "/" + ylabel.lower() + "Run" + str(run) + ".png", bbox_inches = 'tight')
		plt.close()




###################################################################
# - BOXPLOT ALL RUN FITNESS                                     - #
###################################################################
def drawAllRunBoxplotFitness(dossier, **params) :
	hashFitnessGlob = loadParam("hashFitnessGlob", params)
	maxFitness = loadParam("maxFitness", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))
	ylabel = loadParam("ylabel", params)


	# --- BOXPLOT ALL RUN FITNESS ---
	dataBoxPlot = [hashFitnessGlob[evaluation] for evaluation in tabPlot if evaluation in hashFitnessGlob.keys()]

	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	axe1.boxplot(dataBoxPlot)

	setTicks(tabPlot, axe1)


	if drawEval :
		axe1.set_xlabel("Evaluation")
	else :
		axe1.set_xlabel("Generation")

	axe1.set_ylabel(ylabel)
	axe1.set_ylim(0, maxFitness + 0.1*maxFitness)

	axe1.set_title('Boxplot of all ' + ylabel)

	plt.savefig(dossier + "/global" + ylabel, bbox_inches = 'tight')
	plt.close()




###################################################################
# - BARS MEAN RUN                                               - #
###################################################################
def drawBarsMean(dossier, **params) :
	hashNbHaresSolo = loadParam("hashNbHaresSolo", params)
	hashNbHaresDuo = loadParam("hashNbHaresDuo", params)
	hashNbBStagsSolo = loadParam("hashNbBStagsSolo", params)
	hashNbBStagsDuo = loadParam("hashNbBStagsDuo", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))


	# --- BARS ---
	for run in hashNbHaresSolo.keys() :
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		width = 0.8

		tabNbHaresSolo = [np.mean(hashNbHaresSolo[run][evaluation]) for evaluation in tabPlot if evaluation in hashNbHaresSolo[run].keys()]
		tabNbHaresDuo = [np.mean(hashNbHaresDuo[run][evaluation]) for evaluation in tabPlot if evaluation in hashNbHaresDuo[run].keys()]
		tabNbBStagsSolo = [np.mean(hashNbBStagsSolo[run][evaluation]) for evaluation in tabPlot if evaluation in hashNbBStagsSolo[run].keys()]
		tabNbBStagsDuo = [np.mean(hashNbBStagsDuo[run][evaluation]) for evaluation in tabPlot if evaluation in hashNbBStagsDuo[run].keys()]

		barNbHaresSolo = axe1.bar(range(len(tabNbHaresSolo)), tabNbHaresSolo, width = width, color = colorHaresSolo, alpha = alphaHares)
		barNbHaresDuo = axe1.bar(range(len(tabNbHaresDuo)), tabNbHaresDuo, bottom = tabNbHaresSolo, width = width, color = colorHaresDuo, alpha = alphaHares)
		barNbBStagsSolo = axe1.bar(range(len(tabNbBStagsSolo)), tabNbBStagsSolo, bottom = np.add(tabNbHaresDuo, tabNbHaresSolo), width = width, color = colorBStagsSolo, alpha = alphaBStags)
		barNbBStagsDuo = axe1.bar(range(len(tabNbBStagsDuo)), tabNbBStagsDuo, bottom = np.add(tabNbBStagsSolo, np.add(tabNbHaresDuo, tabNbHaresSolo)), width = width, color = colorBStagsDuo, alpha = alphaBStags)

		setTicks(tabPlot, axe1)

		if drawEval :
			axe1.set_xlabel("Evaluation")
		else :
			axe1.set_xlabel("Generation")

		axe1.set_ylabel('Number of preys hunted')
		axe1.set_title('Repartition of preys hunted', fontsize = 10)

		plt.legend([barNbHaresSolo, barNbHaresDuo, barNbBStagsSolo,  barNbBStagsDuo], ['Hares solo', 'Hares coop.', 'Stags solo', 'Stags coop.'], bbox_to_anchor=(0., 1.05, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

		plt.savefig(dossier + "/preysRun" + str(run) + ".png", bbox_inches = 'tight')
		plt.close()





###################################################################
# - BARS RUN                                                    - #
###################################################################
def drawBarsRun(dossier, **params) :
	hashNbHares = loadParam("hashNbHares", params)
	hashNbBStagsSolo = loadParam("hashNbBStagsSolo", params)
	hashNbBStagsDuo = loadParam("hashNbBStagsDuo", params)

	tabPlotRun = loadParam("tabPlotRun", params)

	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

	width = 0.5
	tabPlotRun = [run for run in sorted(hashNbBStagsDuo.keys())]
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

	axe1.set_xlim(0, len(tabNbBStagsDuo))

	axe1.set_xlabel('Run')

	axe1.set_ylabel('Number of preys hunted')
	axe1.set_ylim(0)

	plt.legend([barNbHares, barNbBStagsDuo, barNbBStagsSolo], ['Hares', 'Stags coop.', 'Stags solo'], frameon = True)

	plt.savefig(dossier + "/figureBarsNbPreysSuccess.png", bbox_inches = 'tight')





###################################################################
# - DRAW PARETO                                                 - #
###################################################################
def drawPareto(dossier, **params) :
	hashObj1 = loadParam("hashObj1", params)
	hashObj2 = loadParam("hashObj2", params)
	hashRatio = loadParam("hashRatio", params)
	hashRatioCoop = loadParam("hashRatioCoop", params)
	xlabel = loadParam("xlabel", params)
	ylabel = loadParam("ylabel", params)
	maxObj1 = loadParam("maxObj1", params)
	maxObj2 = loadParam("maxObj2", params)

	for run in hashObj1.keys() :
		assert(len(hashObj1[run].keys()) == len(hashObj2[run].keys()))
		lastEvalRun = sorted(hashObj1[run].keys())[-1]
		assert(lastEvalRun == sorted(hashObj2[run].keys())[-1])

		listObj1 = hashObj1[run][lastEvalRun]
		listObj2 = hashObj2[run][lastEvalRun]

		listRatio = hashRatio[run][lastEvalRun]
		listColors = [0 if math.isnan(ratio) else int(ratio) for ratio in listRatio]

		listRatioCoop = hashRatioCoop[run][lastEvalRun]
		listSizes = [50 if math.isnan(ratio) else 50 + int(ratio*2) for ratio in listRatioCoop]

		p_front = pareto_frontier(listObj1, listObj2, maxX = True, maxY = True)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.scatter(listObj1, listObj2, c = listColors, cmap = cm.rainbow, s = listSizes)
		axe1.plot(p_front[0], p_front[1])

		axe1.set_xlabel(xlabel)
		axe1.set_xlim(0, maxObj1 + 0.1*maxObj1)

		axe1.set_ylabel(ylabel)
		axe1.set_ylim(0, maxObj2 + 0.1*maxObj2)

		axe1.set_title('Pareto frontier at last evaluation')

		plt.savefig(dossier + "/paretoRun" + str(run) + ".png", bbox_inches = 'tight')
		plt.close()





###################################################################
# - DRAW PARETO RUN                                             - #
###################################################################
def drawPareto(dossier, **params) :
	hashObj1 = loadParam("hashObj1", params)
	hashObj2 = loadParam("hashObj2", params)
	hashRatio = loadParam("hashRatio", params)
	hashRatioCoop = loadParam("hashRatioCoop", params)
	xlabel = loadParam("xlabel", params)
	ylabel = loadParam("ylabel", params)
	maxObj1 = loadParam("maxObj1", params)
	maxObj2 = loadParam("maxObj2", params)

	# Pareto Frontier
	assert(len(hashObj1.keys()) == len(hashObj2.keys()))
	lastEvalRun = sorted(hashObj1.keys())[-1]
	assert(lastEvalRun == sorted(hashObj2.keys())[-1])

	paretoEvals = sorted(hashObj1.keys())[0:-1:int(math.floor(len(hashObj1.keys())/20.0))]

	if lastEvalRun not in paretoEvals :
		paretoEvals.append(lastEvalRun)

	for eval in paretoEvals :
		listObj1 = hashObj1[eval]
		listObj2 = hashObj2[eval]

		listRatio = hashRatio[eval]
		listColors = [0 if math.isnan(ratio) else int(ratio) for ratio in listRatio]

		listRatioCoop = hashRatioCoop[eval]
		listSizes = [50 if math.isnan(ratio) else 50 + int(ratio*2) for ratio in listRatioCoop]

		p_front = pareto_frontier(listObj1, listObj2, maxX = True, maxY = True)

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.scatter(listObj1, listObj2, c = listColors, cmap = cm.rainbow, s = listSizes)
		axe1.plot(p_front[0], p_front[1])

		axe1.set_xlabel(xlabel)
		axe1.set_xlim(0, maxObj1 + 0.1*maxObj1)

		axe1.set_ylabel(ylabel)
		axe1.set_ylim(0, maxObj2 + 0.1*maxObj2)

		axe1.set_title('Pareto frontier at evaluation ' + str(eval))

		plt.savefig(dossier + "/paretoEval" + str(eval) + ".png", bbox_inches = 'tight')
		plt.close()





###################################################################
# - DRAW BOXPLOT LEADERSHIP                                     - #
###################################################################
def drawBoxplotLeadership(dossier, **params) :
	hashProportion = loadParam("hashProportion", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))

	dataBoxPlot = []

	for evaluation in tabPlot :
		listProportion = [hashProportion[run][evaluation] for run in hashProportion.keys() if evaluation in hashProportion[run].keys()]

		if len(listProportion) > 0 :
			dataBoxPlot.append(listProportion)

	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	axe1.boxplot(dataBoxPlot)

	axe1.set_xticks(range(0, len(tabPlot), int(len(tabPlot)/10)))
	axe1.set_xticklabels([tabPlot[x] for x in range(0, len(tabPlot), int(len(tabPlot)/10))])

	if drawEval :
		axe1.set_xlabel("Evaluation")
	else :
		axe1.set_xlabel("Generation")

	axe1.set_ylabel("Proportion of leadership")
	axe1.set_ylim(-0.1, 1.1)

	axe1.set_title('Boxplot of best proportion')

	plt.savefig(dossier + "/boxplot.png", bbox_inches = 'tight')
	plt.close()




###################################################################
# - DRAW RUN LEADERSHIP                                         - #
###################################################################
def drawRunLeadership(dossier, **params) :
	hashProportion = loadParam("hashProportion", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))

	for run in hashProportion.keys() :
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		tabProportion = [hashProportion[run][evaluation] for evaluation in tabPlot if evaluation in hashProportion[run].keys()]

		axe1.plot(range(len(tabProportion)), tabProportion)


		setTicks(tabPlot, axe1)

		if drawEval :
			axe1.set_xlabel("Evaluation")
		else :
			axe1.set_xlabel("Generation")

		axe1.set_ylabel("Proportion of leadership")
		axe1.set_ylim(-0.1, 1.1)

		axe1.set_title('Best proportion')

		plt.savefig(dossier + "/proportionRun" + str(run) + ".png", bbox_inches = 'tight')
		plt.close()






###################################################################
# - DRAW BOXPLOT LEADERSHIP ASYM                                - #
###################################################################
def drawBoxplotLeadershipAsym(dossier, **params) :
	hashProportionAsym = loadParam("hashProportionAsym", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))

	dataBoxPlot = []

	for evaluation in tabPlot :
		listProportionAsym = [hashProportionAsym[run][evaluation] for run in hashProportionAsym.keys() if evaluation in hashProportionAsym[run].keys()]

		if len(listProportionAsym) > 0 :
			dataBoxPlot.append(listProportionAsym)

	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	axe1.boxplot(dataBoxPlot)

	axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
	axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))

	setTicks(tabPlot, axe1)

	if drawEval :
		axe1.set_xlabel("Evaluation")
	else :
		axe1.set_xlabel("Generation")

	axe1.set_ylabel("Proportion of leadership")
	axe1.set_ylim(-0.6, 0.6)

	axe1.set_title('Boxplot of best proportion')

	plt.savefig(dossier + "/boxplotAsym.png", bbox_inches = 'tight')
	plt.close()





###################################################################
# - DRAW RUN LEADERSHIP ASYM                                    - #
###################################################################
def drawRunLeadershipAsym(dossier, **params) :
	hashProportionAsym = loadParam("hashProportionAsym", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))

	for run in hashProportionAsym.keys() :
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		tabProportionAsym = [hashProportionAsym[run][evaluation] for evaluation in tabPlot if evaluation in hashProportionAsym[run].keys()]

		axe1.plot(range(len(tabProportionAsym)), tabProportionAsym)

		axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
		axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))

		setTicks(tabPlot, axe1)

		if drawEval :
			axe1.set_xlabel("Evaluation")
		else :
			axe1.set_xlabel("Generation")

		axe1.set_ylabel("Proportion of leadership")
		axe1.set_ylim(-0.6, 0.6)

		axe1.set_title('Boxplot of best proportion')

		plt.savefig(dossier + "/proportionAsymRun" + str(run) + ".png", bbox_inches = 'tight')
		plt.close()





###################################################################
# - DRAW BOXPLOT RUN LEADERSHIP                                 - #
###################################################################
def drawRunBoxplotLeadership(dossier, **params) :
	hashProportion = loadParam("hashProportion", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))		


	dataBoxPlot = []
	for run in hashProportion.keys() :
		dataBoxPlot = [hashProportion[run][evaluation] for evaluation in tabPlot if evaluation in hashProportion[run].keys()]

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)

		# axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
		# axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))

		setTicks(tabPlot, axe1)

		if drawEval :
			axe1.set_xlabel("Evaluation")
		else :
			axe1.set_xlabel("Generation")

		axe1.set_ylabel("Proportion of leadership")
		axe1.set_ylim(-0.1, 1.1)

		axe1.set_title('Boxplot of population proportion')

		plt.savefig(dossier + "/proportionRun" + str(run) + ".png", bbox_inches = 'tight')
		plt.close()


###################################################################
# - DRAW BOXPLOT ALL RUN LEADERSHIP                             - #
###################################################################
def drawRunBoxplotLeadership(dossier, **params) :
	hashProportionGlob = loadParam("hashProportionGlob", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))		


	dataBoxPlot = [hashProportionGlob[evaluation] for evaluation in tabPlot if evaluation in hashProportionGlob.keys()]

	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	axe1.boxplot(dataBoxPlot)

	# axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
	# axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))


	setTicks(tabPlot, axe1)

	if drawEval :
		axe1.set_xlabel("Evaluation")
	else :
		axe1.set_xlabel("Generation")

	axe1.set_ylabel("Proportion of leadership")
	axe1.set_ylim(-0.1, 1.1)

	axe1.set_title('Boxplot of all proportions')

	plt.savefig(dossier + "/globalProportionAsym", bbox_inches = 'tight')
	plt.close()


###################################################################
# - DRAW BOXPLOT RUN LEADERSHIP ASYM                            - #
###################################################################
def drawRunBoxplotLeadership(dossier, **params) :
	hashProportionAsym = loadParam("hashProportionAsym", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))		


	dataBoxPlot = []
	for run in hashProportionAsym.keys() :
		dataBoxPlot = [hashProportionAsym[run][evaluation] for evaluation in tabPlot if evaluation in hashProportionAsym[run].keys()]

		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
		axe1.boxplot(dataBoxPlot)

		axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
		axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))


		setTicks(tabPlot, axe1)

		if drawEval :
			axe1.set_xlabel("Evaluation")
		else :
			axe1.set_xlabel("Generation")

		axe1.set_ylabel("Proportion of leadership")
		axe1.set_ylim(-0.6, 0.6)

		axe1.set_title('Boxplot of population proportion')

		plt.savefig(dossier + "/proportionAsymRun" + str(run) + ".png", bbox_inches = 'tight')
		plt.close()




###################################################################
# - DRAW BOXPLOT ALL RUN LEADERSHIP ASYM                        - #
###################################################################
def drawRunBoxplotLeadership(dossier, **params) :
	hashProportionAsym = loadParam("hashProportionAsym", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))	

	dataBoxPlot = [hashProportionGlob[evaluation] for evaluation in tabPlot if evaluation in hashProportionGlob.keys()]

	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	axe1.boxplot(dataBoxPlot)

	axe1.add_line(lines.Line2D([0, lastEval], [0.5, 0.5], color="red"))
	axe1.add_line(lines.Line2D([0, lastEval], [-0.5, -0.5], color="red"))


	setTicks(tabPlot, axe1)

	if drawEval :
		axe1.set_xlabel("Evaluation")
	else :
		axe1.set_xlabel("Generation")

	axe1.set_ylabel("Proportion of leadership")
	axe1.set_ylim(-0.6, 0.6)

	axe1.set_title('Boxplot of all proportions')

	plt.savefig(dossier + "/globalProportion", bbox_inches = 'tight')
	plt.close()




###################################################################
# - DRAW MEDIAN BEST                                            - #
###################################################################
def drawMedianBest(dossier, **params) :
	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

	dataHash = loadParam("dataHas", params)
	tabPlot = loadParam("tabPlot", params)
	drawEval = bool(loadParam("drawEval", params))	

	cptData = 0
	for data in dataHash :
		dataPlot = []
		dataPerc25 = []
		dataPerc75 = []
		hashFitness = data['hashFitness']
		hashNbBStags = data['hashNbBStags']
		hashNbBStagsDuo = data['hashNbBStagsDuo']
		hashNbHares = data['hashNbHares']

		for evaluation in tabPlot :
			fitnessEval = [hashFitness[run][evaluation] for run in hashFitness.keys() if run in hashRunStags[cptData] and evaluation in hashFitness[run].keys()]
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



	setTicks(tabPlot, axe1)

	if drawEval :
		axe1.set_xlabel("Evaluation")
	else :
		axe1.set_xlabel("Generation")

	axe1.set_ylabel(yLabel)
	axe1.set_ylim(-0.6, 0.6)

	axe1.set_title('Boxplot of all fitness')

	plt.savefig(dossier + "/boxplotMedians.png", bbox_inches = 'tight')
	plt.close()

	legend = plt.legend(['Control', 'Clonal', 'Coevolution'], loc = 4, frameon=True)
	frame = legend.get_frame()
	frame.set_facecolor('0.9')
	frame.set_edgecolor('0.9')

	# axe1.set_title('Boxplot of best fitness')

	plt.savefig(outputDir + "/boxplotStags.png", bbox_inches = 'tight')
	plt.savefig(outputDir + "/boxplotStags.svg", bbox_inches = 'tight')
	plt.close()



def main() :
	pass

if __name__ == "__main__" : 
	main()
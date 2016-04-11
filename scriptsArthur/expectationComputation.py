#!/usr/bin/env python

import argparse
import math
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import lines
import matplotlib.cm as cm
import matplotlib
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pylab import *
import ternary

import os
import re
import sys




FITNESS_ARRAY = {
									'Solo' :	
									{
										'Solo' : 1265,
										'Turner' : 3480,
										'Follower' : 5000
									},
									'Turner' :	
									{
										'Solo' : 3480,
										'Turner' : 2755,
										'Follower' : 2750
									},
									'Follower' :	
									{
										'Solo' : 5000,
										'Turner' : 2750,
										'Follower' : 100
									}
								}


def computeExpectation(genotype, tabProportions) :
	result = 0.0
	for opponent in tabProportions.keys() :
		result += tabProportions[opponent] * FITNESS_ARRAY[genotype][opponent]

	return result


def computeExpectationBestChoice(genotype, tabProportions) :
	result = 0.0
	for opponent in tabProportions.keys() :
		if tabProportions[opponent] > 0.0 :
			if FITNESS_ARRAY[genotype][opponent] > result :
				result = FITNESS_ARRAY[genotype][opponent]

	return result


def main(args) :
	sns.set()
	sns.set_style('white')
	sns.set_context('paper')
	palette = sns.color_palette("husl", 4)

	dpi = 96

	size = (1280/dpi, 1024/dpi)

	tabProportions = {}
	Xproportions = np.arange(0.0, 1.0 + args.precision, args.precision)	
	Yproportions = np.arange(0.0, 1.0 + args.precision, args.precision)	

	hashExpectations = {}
	hashExpectations['Follower'] = []
	hashExpectations['Solo'] = []
	hashExpectations['Turner'] = []
	for Xproportion in Xproportions :
		tabProportions['Follower'] = Xproportion

		tmpArrayFollower = []
		tmpArraySolo = []
		tmpArrayTurner = []
		for Yproportion in Yproportions : 
			if Xproportion + Yproportion <= 1.0 :
				tabProportions['Solo'] = Yproportion
				tabProportions['Turner'] = 1.0 - Xproportion - Yproportion

				tmpArrayFollower.append(computeExpectation('Follower', tabProportions))
				tmpArraySolo.append(computeExpectation('Solo', tabProportions))
				tmpArrayTurner.append(computeExpectation('Turner', tabProportions))
			else :
				tmpArrayFollower.append(0.0)
				tmpArraySolo.append(0.0)
				tmpArrayTurner.append(0.0)

		hashExpectations['Follower'].append(tmpArrayFollower)
		hashExpectations['Solo'].append(tmpArraySolo)
		hashExpectations['Turner'].append(tmpArrayTurner)

	if args.bestchoice :
		hashExpectationsBestChoice = {}
		hashExpectationsBestChoice['Follower'] = []
		hashExpectationsBestChoice['Solo'] = []
		hashExpectationsBestChoice['Turner'] = []
		for Xproportion in Xproportions :
			tabProportions['Follower'] = Xproportion

			tmpArrayFollower = []
			tmpArraySolo = []
			tmpArrayTurner = []
			for Yproportion in Yproportions : 
				if Xproportion + Yproportion <= 1.0 :
					tabProportions['Solo'] = Yproportion
					tabProportions['Turner'] = 1.0 - Xproportion - Yproportion

					tmpArrayFollower.append(computeExpectationBestChoice('Follower', tabProportions))
					tmpArraySolo.append(computeExpectationBestChoice('Solo', tabProportions))
					tmpArrayTurner.append(computeExpectationBestChoice('Turner', tabProportions))
				else :
					tmpArrayFollower.append(0.0)
					tmpArraySolo.append(0.0)
					tmpArrayTurner.append(0.0)

			hashExpectationsBestChoice['Follower'].append(tmpArrayFollower)
			hashExpectationsBestChoice['Solo'].append(tmpArraySolo)
			hashExpectationsBestChoice['Turner'].append(tmpArrayTurner)


	# matplotlib.rcParams['font.size'] = 15
	# matplotlib.rcParams['font.weight'] = 'bold'
	# matplotlib.rcParams['axes.labelsize'] = 25
	# matplotlib.rcParams['axes.titlesize'] = 25
	# matplotlib.rcParams['axes.labelweight'] = 'bold'
	# matplotlib.rcParams['xtick.labelsize'] = 25
	# matplotlib.rcParams['ytick.labelsize'] = 25
	# matplotlib.rcParams['legend.fontsize'] = 25

	# matplotlib.rcParams['font.size'] = 15
	# matplotlib.rcParams['font.weight'] = 'bold'
	# matplotlib.rcParams['axes.labelsize'] = 25
	# matplotlib.rcParams['axes.titlesize'] = 25
	# matplotlib.rcParams['axes.labelweight'] = 'bold'
	# matplotlib.rcParams['xtick.labelsize'] = 25
	# matplotlib.rcParams['ytick.labelsize'] = 25
	# matplotlib.rcParams['legend.fontsize'] = 25

	matplotlib.rcParams['font.size'] = 15
	matplotlib.rcParams['font.weight'] = 'bold'
	matplotlib.rcParams['axes.labelsize'] = 25
	matplotlib.rcParams['axes.titlesize'] = 25
	matplotlib.rcParams['axes.labelweight'] = 'bold'
	matplotlib.rcParams['xtick.labelsize'] = 25
	matplotlib.rcParams['ytick.labelsize'] = 25
	matplotlib.rcParams['legend.fontsize'] = 25

	# GRAPHS GLOBAL VARIABLES
	linewidth = 2
	linestyles = ['-', '--', '-.']
	linestylesOff = ['-', '-', '-']
	markers = [None, None, None] #['o', '+', '*']


	ZexpectationFollower = dict()
	ZexpectationSolo = dict()
	ZexpectationTurner = dict()
	ZexpectationFollowerSolo = dict() 
	ZexpectationFollowerTurner = dict() 
	ZexpectationSoloFollower = dict() 
	ZexpectationSoloTurner = dict() 
	ZexpectationTurnerFollower = dict() 
	ZexpectationTurnerSolo = dict() 
	ZexpectationFollowerPart = dict() 
	ZexpectationSoloPart = dict() 
	ZexpectationTurnerPart = dict()
	ZexpectationFollowerFull = dict() 
	ZexpectationSoloFull = dict() 
	ZexpectationTurnerFull = dict()
	ZexpectationAllFull = dict()

	listPoints = list()
	listPointsDest = list()
	listPointsDestBestChoice = list()
	listPointsEquilibrium = list()
	precisionVector = 2

	cptX = 0
	while cptX < len(Xproportions) :

		cptY = 0
		while cptY < len(Yproportions) :
			if (cptX + cptY) <= 100 :
				curTuple = (cptX, cptY, 100 - (cptX + cptY))

				ZexpectationFollower[curTuple] = hashExpectations['Follower'][cptX][cptY]
				ZexpectationSolo[curTuple] = hashExpectations['Solo'][cptX][cptY]
				ZexpectationTurner[curTuple] = hashExpectations['Turner'][cptX][cptY]

				ZexpectationFollowerSolo[curTuple] = hashExpectations['Follower'][cptX][cptY] if hashExpectations['Follower'][cptX][cptY] - hashExpectations['Solo'][cptX][cptY] > 0 else 0
				ZexpectationFollowerTurner[curTuple] = hashExpectations['Follower'][cptX][cptY] if hashExpectations['Follower'][cptX][cptY] - hashExpectations['Turner'][cptX][cptY] > 0 else 0

				ZexpectationSoloFollower[curTuple] = hashExpectations['Solo'][cptX][cptY] if hashExpectations['Solo'][cptX][cptY] - hashExpectations['Follower'][cptX][cptY] > 0 else 0
				ZexpectationSoloTurner[curTuple] = hashExpectations['Solo'][cptX][cptY] if hashExpectations['Solo'][cptX][cptY] - hashExpectations['Turner'][cptX][cptY] > 0 else 0

				ZexpectationTurnerSolo[curTuple] = hashExpectations['Turner'][cptX][cptY] if hashExpectations['Turner'][cptX][cptY] - hashExpectations['Solo'][cptX][cptY] > 0 else 0
				ZexpectationTurnerFollower[curTuple] = hashExpectations['Turner'][cptX][cptY] if hashExpectations['Turner'][cptX][cptY] - hashExpectations['Follower'][cptX][cptY] > 0 else 0

				if (ZexpectationFollowerSolo[curTuple] > 0 and ZexpectationFollowerTurner[curTuple] > 0) :
					ZexpectationFollowerFull[curTuple] = hashExpectations['Follower'][cptX][cptY]
					ZexpectationFollowerPart[curTuple] = hashExpectations['Follower'][cptX][cptY]
				else :
					ZexpectationFollowerFull[curTuple] = 0

				if (ZexpectationSoloFollower[curTuple] > 0 and ZexpectationSoloTurner[curTuple] > 0) :
					ZexpectationSoloFull[curTuple] = hashExpectations['Solo'][cptX][cptY]
					ZexpectationSoloPart[curTuple] = hashExpectations['Solo'][cptX][cptY]
				else :
					ZexpectationSoloFull[curTuple] = 0

				if (ZexpectationTurnerSolo[curTuple] > 0 and ZexpectationTurnerFollower[curTuple] > 0) :
					ZexpectationTurnerFull[curTuple] = hashExpectations['Turner'][cptX][cptY]
					ZexpectationTurnerPart[curTuple] = hashExpectations['Turner'][cptX][cptY]
				else :
					ZexpectationTurnerFull[curTuple] = 0


				if ZexpectationFollowerFull[curTuple] > 0.0 :
					ZexpectationAllFull[curTuple] = ZexpectationFollowerFull[curTuple]
				elif ZexpectationSoloFull[curTuple] > 0.0 :
					ZexpectationAllFull[curTuple] = ZexpectationSoloFull[curTuple]
				elif ZexpectationTurnerFull[curTuple] > 0.0 :
					ZexpectationAllFull[curTuple] = ZexpectationTurnerFull[curTuple]
				else :
					ZexpectationAllFull[curTuple] = 0.0


				if (cptX%precisionVector == 0) and (cptY%precisionVector == 0) :
					listPoints.append(curTuple)
					propFollower = cptX/float(100)
					propSolo = cptY/float(100)
					propTurner = 1.0 - (propFollower + propSolo)

					# print("(" + str(propFollower) + "," + str(propSolo) + "," + str(propTurner) + ")")

					fitnessFollower = hashExpectations['Follower'][cptX][cptY]
					fitnessSolo = hashExpectations['Solo'][cptX][cptY]
					fitnessTurner = hashExpectations['Turner'][cptX][cptY]

					# print("(" + str(fitnessFollower) + "," + str(fitnessSolo) + "," + str(fitnessTurner) + ")")

					meanFitness = propFollower*fitnessFollower + propSolo*fitnessSolo + propTurner*fitnessTurner

					# print("Mean fitness : " + str(meanFitness))

					nextPropFollower = propFollower * fitnessFollower / meanFitness
					nextPropSolo = propSolo * fitnessSolo / meanFitness
					nextPropTurner = propTurner * fitnessTurner / meanFitness

					assert(abs((nextPropFollower + nextPropSolo + nextPropTurner) - 1.0) <= 1e-10)

					listPointsDest.append((nextPropFollower*100, nextPropSolo*100, nextPropTurner*100))

					if (nextPropSolo == propSolo) and (nextPropTurner == propTurner) and (nextPropFollower == propFollower) :
						listPointsEquilibrium.append(curTuple)

					if args.bestchoice :
						fitnessFollower = hashExpectationsBestChoice['Follower'][cptX][cptY]
						fitnessSolo = hashExpectationsBestChoice['Solo'][cptX][cptY]
						fitnessTurner = hashExpectationsBestChoice['Turner'][cptX][cptY]

						# print("(" + str(fitnessFollower) + "," + str(fitnessSolo) + "," + str(fitnessTurner) + ")")

						meanFitness = propFollower*fitnessFollower + propSolo*fitnessSolo + propTurner*fitnessTurner

						# print("Mean fitness : " + str(meanFitness))

						nextPropFollower = propFollower * fitnessFollower / meanFitness
						nextPropSolo = propSolo * fitnessSolo / meanFitness
						nextPropTurner = propTurner * fitnessTurner / meanFitness

						assert(abs((nextPropFollower + nextPropSolo + nextPropTurner) - 1.0) <= 1e-10)

						listPointsDestBestChoice.append((nextPropFollower*100, nextPropSolo*100, nextPropTurner*100))


			cptY += 1
		cptX += 1


	scale = 100


	# with open("debug.txt", "w") as fileWrite :
		
	# 	cpt = 0
	# 	while cpt < len(listPoints) :
	# 		fileWrite.write(str(listPoints[cpt]) + " -> " + str(listPointsDest[cpt]) + "\n")

	# 		cpt += 1

	# # -- Expectation Followers --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# # print(ZexpectationFollower)
	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationFollower, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000, colorbar = False)
	# # tax.scatter([(10, 20, 30)], color = 'red')
	# # tax.scatter([(0, 20, 10)], color = 'blue')
	# # tax.scatter([(80, 10, 10)], color = 'green')
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsFollowers.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsFollowers.png", bbox_inches = 'tight')


	# # -- Expectation Solos --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationSolo, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000, colorbar = False)
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsSolos.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsSolos.png", bbox_inches = 'tight')


	# # -- Expectation Turners --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationTurner, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsTurners.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsTurners.png", bbox_inches = 'tight')


	# # -- Expectation Followers VS Solo --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationFollowerSolo, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsFollowersSolo.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsFollowersSolo.png", bbox_inches = 'tight')


	# # -- Expectation Followers VS Turners --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationFollowerTurner, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsFollowersTurner.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsFollowersTurner.png", bbox_inches = 'tight')


	# # -- Expectation Followers Full --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationFollowerFull, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsFollowersFull.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsFollowersFull.png", bbox_inches = 'tight')


	# # -- Expectation Solo VS Followers --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationSoloFollower, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsSolosFollower.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsSolosFollower.png", bbox_inches = 'tight')


	# # -- Expectation Solo VS Turners --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationSoloTurner, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsSolosTurner.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsSolosTurner.png", bbox_inches = 'tight')


	# # -- Expectation Solo Full --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationSoloFull, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsSolosFull.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsSolosFull.png", bbox_inches = 'tight')


	# # -- Expectation Turners VS Followers --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationTurnerFollower, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsTurnersFollower.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsTurnersFollower.png", bbox_inches = 'tight')


	# # -- Expectation Turners VS Solo --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationTurnerSolo, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsTurnersSolo.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsTurnersSolo.png", bbox_inches = 'tight')



	# # -- Expectation Turners Full --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationTurnerFull, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsTurnersFull.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsTurnersFull.png", bbox_inches = 'tight')


	# We look for the separation between each domain
	cptX = 0
	precision = args.precision * 100

	frontSolo = list()
	frontFollower = list()
	frontTurner = list()
	while cptX < len(Xproportions) :

		cptY = 0
		while cptY < len(Yproportions) :
			if(cptX + cptY) <= 100 :
				cptZ = 100 - (cptX + cptY)
				curTuple = (cptX, cptY, cptZ)

				if ZexpectationSoloFull[curTuple] > 0.0 :
					if ((cptX + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationSoloFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) \
						or ((cptX + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationSoloFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) \
						or ((cptX - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationSoloFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) \
						or ((cptX - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationSoloFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) \
						or ((cptY + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationSoloFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) \
						or ((cptY + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationSoloFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) \
						or ((cptY - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationSoloFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) \
						or ((cptY - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationSoloFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) \
						or ((cptZ + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationSoloFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) \
						or ((cptZ + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationSoloFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) \
						or ((cptZ - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationSoloFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) \
						or ((cptZ - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationSoloFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) :

						frontSolo.append(curTuple)

				if ZexpectationFollowerFull[curTuple] > 0.0 :
					if ((cptX + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationFollowerFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) \
						or ((cptX + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationFollowerFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) \
						or ((cptX - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationFollowerFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) \
						or ((cptX - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationFollowerFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) \
						or ((cptY + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationFollowerFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) \
						or ((cptY + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationFollowerFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) \
						or ((cptY - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationFollowerFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) \
						or ((cptY - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationFollowerFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) \
						or ((cptZ + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationFollowerFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) \
						or ((cptZ + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationFollowerFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) \
						or ((cptZ - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationFollowerFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) \
						or ((cptZ - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationFollowerFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) :

						frontFollower.append(curTuple)

				if ZexpectationTurnerFull[curTuple] > 0.0 :
					if ((cptX + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationTurnerFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) \
						or ((cptX + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationTurnerFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) \
						or ((cptX - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationTurnerFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) \
						or ((cptX - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationTurnerFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) \
						or ((cptY + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationTurnerFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) \
						or ((cptY + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationTurnerFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) \
						or ((cptY - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationTurnerFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) \
						or ((cptY - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationTurnerFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) \
						or ((cptZ + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationTurnerFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) \
						or ((cptZ + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationTurnerFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) \
						or ((cptZ - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationTurnerFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) \
						or ((cptZ - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationTurnerFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) :

						frontTurner.append(curTuple)

				# if ZexpectationSoloFull[curTuple] > 0.0 :
				# 	if ((cptX + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationSoloFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) :
				# 		frontSolo.append((cptX + precision/float(2.0), cptY - precision/float(2.0), cptZ))
				# 	elif ((cptX + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationSoloFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) :
				# 		frontSolo.append((cptX + precision/float(2.0), cptY, cptZ - precision/float(2.0)))
				# 	elif ((cptX - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationSoloFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) :
				# 		frontSolo.append((cptX - precision/float(2.0), cptY - precision/float(2.0), cptZ))
				# 	elif ((cptX - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationSoloFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) :
				# 		frontSolo.append((cptX - precision/float(2.0), cptY, cptZ - precision/float(2.0)))
				# 	elif ((cptY + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationSoloFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) :
				# 		frontSolo.append((cptX - precision/float(2.0), cptY + precision/float(2.0), cptZ))
				# 	elif ((cptY + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationSoloFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) :
				# 		frontSolo.append((cptX, cptY + precision/float(2.0), cptZ - precision/float(2.0)))
				# 	elif ((cptY - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationSoloFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) :
				# 		frontSolo.append((cptX + precision/float(2.0), cptY - precision/float(2.0), cptZ))
				# 	elif ((cptY - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationSoloFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) :
				# 		frontSolo.append((cptX, cptY - precision/float(2.0), cptZ + precision/float(2.0)))
				# 	elif ((cptZ + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationSoloFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) :
				# 		frontSolo.append((cptX - precision/float(2.0), cptY, cptZ + precision/float(2.0)))
				# 	elif ((cptZ + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationSoloFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) :
				# 		frontSolo.append((cptX, cptY - precision/float(2.0), cptZ + precision/float(2.0)))
				# 	elif ((cptZ - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationSoloFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) :
				# 		frontSolo.append((cptX + precision/float(2.0), cptY, cptZ - precision/float(2.0)))
				# 	elif ((cptZ - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationSoloFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) :
				# 		frontSolo.append((cptX, cptY + precision/float(2.0), cptZ - precision/float(2.0)))

				# if ZexpectationFollowerFull[curTuple] > 0.0 :
				# 	if ((cptX + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationFollowerFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) :
				# 		frontFollower.append((cptX + precision/float(2.0), cptY - precision/float(2.0), cptZ))
				# 	elif ((cptX + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationFollowerFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) :
				# 		frontFollower.append((cptX + precision/float(2.0), cptY, cptZ - precision/float(2.0)))
				# 	elif ((cptX - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationFollowerFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) :
				# 		frontFollower.append((cptX - precision/float(2.0), cptY - precision/float(2.0), cptZ))
				# 	elif ((cptX - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationFollowerFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) :
				# 		frontFollower.append((cptX - precision/float(2.0), cptY, cptZ - precision/float(2.0)))
				# 	elif ((cptY + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationFollowerFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) :
				# 		frontFollower.append((cptX - precision/float(2.0), cptY + precision/float(2.0), cptZ))
				# 	elif ((cptY + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationFollowerFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) :
				# 		frontFollower.append((cptX, cptY + precision/float(2.0), cptZ - precision/float(2.0)))
				# 	elif ((cptY - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationFollowerFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) :
				# 		frontFollower.append((cptX + precision/float(2.0), cptY - precision/float(2.0), cptZ))
				# 	elif ((cptY - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationFollowerFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) :
				# 		frontFollower.append((cptX, cptY - precision/float(2.0), cptZ + precision/float(2.0)))
				# 	elif ((cptZ + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationFollowerFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) :
				# 		frontFollower.append((cptX - precision/float(2.0), cptY, cptZ + precision/float(2.0)))
				# 	elif ((cptZ + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationFollowerFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) :
				# 		frontFollower.append((cptX, cptY - precision/float(2.0), cptZ + precision/float(2.0)))
				# 	elif ((cptZ - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationFollowerFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) :
				# 		frontFollower.append((cptX + precision/float(2.0), cptY, cptZ - precision/float(2.0)))
				# 	elif ((cptZ - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationFollowerFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) :
				# 		frontFollower.append((cptX, cptY + precision/float(2.0), cptZ - precision/float(2.0)))

				# if ZexpectationTurnerFull[curTuple] > 0.0 :
				# 	if ((cptX + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationTurnerFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) :
				# 		frontTurner.append((cptX + precision/float(2.0), cptY - precision/float(2.0), cptZ))
				# 	elif ((cptX + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationTurnerFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) :
				# 		frontTurner.append((cptX + precision/float(2.0), cptY, cptZ - precision/float(2.0)))
				# 	elif ((cptX - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationTurnerFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) :
				# 		frontTurner.append((cptX - precision/float(2.0), cptY - precision/float(2.0), cptZ))
				# 	elif ((cptX - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationTurnerFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) :
				# 		frontTurner.append((cptX - precision/float(2.0), cptY, cptZ - precision/float(2.0)))
				# 	elif ((cptY + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationTurnerFull[(cptX - precision, cptY + precision, cptZ)] <= 0.0)) :
				# 		frontTurner.append((cptX - precision/float(2.0), cptY + precision/float(2.0), cptZ))
				# 	elif ((cptY + precision <= 100.0) and (cptZ - precision >= 0.0) and (ZexpectationTurnerFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) :
				# 		frontTurner.append((cptX, cptY + precision/float(2.0), cptZ - precision/float(2.0)))
				# 	elif ((cptY - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationTurnerFull[(cptX + precision, cptY - precision, cptZ)] <= 0.0)) :
				# 		frontTurner.append((cptX + precision/float(2.0), cptY - precision/float(2.0), cptZ))
				# 	elif ((cptY - precision >= 0.0) and (cptZ + precision <= 100.0) and (ZexpectationTurnerFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) :
				# 		frontTurner.append((cptX, cptY - precision/float(2.0), cptZ + precision/float(2.0)))
				# 	elif ((cptZ + precision <= 100.0) and (cptX - precision >= 0.0) and (ZexpectationTurnerFull[(cptX - precision, cptY, cptZ + precision)] <= 0.0)) :
				# 		frontTurner.append((cptX - precision/float(2.0), cptY, cptZ + precision/float(2.0)))
				# 	elif ((cptZ + precision <= 100.0) and (cptY - precision >= 0.0) and (ZexpectationTurnerFull[(cptX, cptY - precision, cptZ + precision)] <= 0.0)) :
				# 		frontTurner.append((cptX, cptY - precision/float(2.0), cptZ + precision/float(2.0)))
				# 	elif ((cptZ - precision >= 0.0) and (cptX + precision <= 100.0) and (ZexpectationTurnerFull[(cptX + precision, cptY, cptZ - precision)] <= 0.0)) :
				# 		frontTurner.append((cptX + precision/float(2.0), cptY, cptZ - precision/float(2.0)))
				# 	elif ((cptZ - precision >= 0.0) and (cptY + precision <= 100.0) and (ZexpectationTurnerFull[(cptX, cptY + precision, cptZ - precision)] <= 0.0)) :
				# 		frontTurner.append((cptX, cptY + precision/float(2.0), cptZ - precision/float(2.0)))

			cptY += 1

		cptX += 1

	# print(np.vstack(frontSolo))
	# print(np.vstack(frontFollower))
	pA = (0, 16, 84)
	pB = (20, 34, 46)
	pC = (36, 64, 0)
	pD = (50, 50, 0)

	# # -- Expectation All Full --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# tax.get_axes().set_aspect(1.)
	# tax.heatmap(ZexpectationAllFull, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# # tax.heatmap(ZexpectationFollowerPart, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# # tax.heatmap(ZexpectationSoloPart, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# # tax.heatmap(ZexpectationTurnerPart, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.plot([pA, pB, pC], color = 'black', linewidth = 2, linestyle = "--")
	# tax.plot([pA, pB, pD], color = 'black', linewidth = 2, linestyle = "--")
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/ExpectationsAllFull.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsAllFull.png", bbox_inches = 'tight')


	if args.vector :
		# -- Expectation All Full --
		fig, ax = plt.subplots(ncols = 1, figsize = size)
		ax.axis("off")
		figure, tax = ternary.figure(ax = ax, scale = scale)

		X, Y = ternary.helpers.project_sequence(listPoints)
		X2, Y2 = ternary.helpers.project_sequence(listPointsDest)

		U = [X2[i] - X[i] for i in range(0, len(X))]
		V = [Y2[i] - Y[i] for i in range(0, len(Y))]

		tax.get_axes().set_aspect(1.)
		Q = tax.get_axes().quiver(X[::1], Y[::1], U[::1], V[::1], width = 0.001, color = 'r')

		tax.plot([pA, pB, pC], color = 'black', linewidth = 2, linestyle = "--")
		tax.plot([pA, pB, pD], color = 'black', linewidth = 2, linestyle = "--")
		tax.boundary(linewidth=2.0)
		tax.gridlines(color="black", multiple=10)

		tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

		# Remove default Matplotlib Axes
		tax.clear_matplotlib_ticks()

		fontsize = 25
		fontweight = 'bold'
		tax.left_axis_label("Solo", (0.0 - 0.09, 1.0 + 0.17, 0.5), 0.0, fontsize = fontsize, fontweight = fontweight)
		tax.right_axis_label("Follower", (1.0 - 0.06, 0.1, 0.0), -120, fontsize = fontsize, fontweight = fontweight)
		tax.bottom_axis_label("Turner", (-0.04, 0.1, 1.0), 120, fontsize = fontsize, fontweight = fontweight)

		# plt.colorbar(Q, cax = tax.get_axes())

		plt.tight_layout()
		plt.savefig("./GraphsResults/ExpectationsVectors.svg", bbox_inches = 'tight')
		plt.savefig("./GraphsResults/ExpectationsVectors.png", bbox_inches = 'tight')
		# plt.show()


		# -- Expectation All Full --
		fig, ax = plt.subplots(ncols = 1, figsize = size)
		ax.axis("off")
		figure, tax = ternary.figure(ax = ax, scale = scale)

		speed = [np.sqrt(U[i]**2 + V[i]**2) for i in range(0, len(U))]
		UN = [U[i]/speed[i] if speed[i] > 0 else U[i] for i in range(0, len(U))]
		VN = [V[i]/speed[i] if speed[i] > 0 else V[i] for i in range(0, len(V))]

		# print(speed)
		tax.get_axes().set_aspect(1.)
		Q = tax.get_axes().quiver(X[::1], Y[::1], UN[::1], VN[::1], speed, width = 0.002, cmap = cm.jet)

		tax.plot([pA, pB, pC], color = 'black', linewidth = 2, linestyle = "--")
		tax.plot([pA, pB, pD], color = 'black', linewidth = 2, linestyle = "--")
		tax.boundary(linewidth=2.0)
		tax.gridlines(color="black", multiple=10)

		tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

		# Remove default Matplotlib Axes
		tax.clear_matplotlib_ticks()

		fontsize = 25
		fontweight = 'bold'
		tax.left_axis_label("Solo", (0.0 - 0.09, 1.0 + 0.17, 0.5), 0.0, fontsize = fontsize, fontweight = fontweight)
		tax.right_axis_label("Follower", (1.0 - 0.06, 0.1, 0.0), -120, fontsize = fontsize, fontweight = fontweight)
		tax.bottom_axis_label("Turner", (-0.04, 0.1, 1.0), 120, fontsize = fontsize, fontweight = fontweight)

		# divider = make_axes_locatable(ax5)
		# cax = divider.append_axes("right", size="5%", pad=0.05)

		plt.tight_layout()
		plt.savefig("./GraphsResults/ExpectationsVectorsNormalized.svg", bbox_inches = 'tight')
		plt.savefig("./GraphsResults/ExpectationsVectorsNormalized.png", bbox_inches = 'tight')


		if args.bestchoice :
			# -- Expectation All Full --
			fig, ax = plt.subplots(ncols = 1, figsize = size)
			ax.axis("off")
			figure, tax = ternary.figure(ax = ax, scale = scale)

			X, Y = ternary.helpers.project_sequence(listPoints)
			X2, Y2 = ternary.helpers.project_sequence(listPointsDestBestChoice)

			U = [X2[i] - X[i] for i in range(0, len(X))]
			V = [Y2[i] - Y[i] for i in range(0, len(Y))]

			tax.get_axes().set_aspect(1.)
			Q = tax.get_axes().quiver(X[::1], Y[::1], U[::1], V[::1], width = 0.001, color = 'r')

			tax.plot([pA, pB, pC], color = 'black', linewidth = 2, linestyle = "--")
			tax.plot([pA, pB, pD], color = 'black', linewidth = 2, linestyle = "--")
			# tax.boundary(linewidth=2.0)
			tax.gridlines(color="black", multiple=10)

			tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

			# Remove default Matplotlib Axes
			tax.clear_matplotlib_ticks()

			fontsize = 25
			fontweight = 'bold'
			tax.left_axis_label("Solo", (0.0 - 0.09, 1.0 + 0.17, 0.5), 0.0, fontsize = fontsize, fontweight = fontweight)
			tax.right_axis_label("Follower", (1.0 - 0.06, 0.1, 0.0), -120, fontsize = fontsize, fontweight = fontweight)
			tax.bottom_axis_label("Turner", (-0.04, 0.1, 1.0), 120, fontsize = fontsize, fontweight = fontweight)

			# plt.colorbar(Q, cax = tax.get_axes())

			plt.tight_layout()
			plt.savefig("./GraphsResults/ExpectationsVectorsBestChoice.svg", bbox_inches = 'tight')
			plt.savefig("./GraphsResults/ExpectationsVectorsBestChoice.png", bbox_inches = 'tight')
			# plt.show()


			# -- Expectation All Full --
			fig, ax = plt.subplots(ncols = 1, figsize = size)
			ax.axis("off")
			figure, tax = ternary.figure(ax = ax, scale = scale)

			speed = [np.sqrt(U[i]**2 + V[i]**2) for i in range(0, len(U))]
			UN = [U[i]/speed[i] if speed[i] > 0 else U[i] for i in range(0, len(U))]
			VN = [V[i]/speed[i] if speed[i] > 0 else V[i] for i in range(0, len(V))]

			# print(speed)
			tax.get_axes().set_aspect(1.)
			Q = tax.get_axes().quiver(X[::1], Y[::1], UN[::1], VN[::1], speed, width = 0.002, cmap = cm.jet)

			tax.plot([pA, pB, pC], color = 'black', linewidth = 2, linestyle = "--")
			tax.plot([pA, pB, pD], color = 'black', linewidth = 2, linestyle = "--")
			# tax.boundary(linewidth=2.0)
			tax.gridlines(color="black", multiple=10)

			tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

			# Remove default Matplotlib Axes
			tax.clear_matplotlib_ticks()

			fontsize = 25
			fontweight = 'bold'
			tax.left_axis_label("Solo", (0.0 - 0.09, 1.0 + 0.17, 0.5), 0.0, fontsize = fontsize, fontweight = fontweight)
			tax.right_axis_label("Follower", (1.0 - 0.06, 0.1, 0.0), -120, fontsize = fontsize, fontweight = fontweight)
			tax.bottom_axis_label("Turner", (-0.04, 0.1, 1.0), 120, fontsize = fontsize, fontweight = fontweight)

			# divider = make_axes_locatable(ax5)
			# cax = divider.append_axes("right", size="5%", pad=0.05)

			plt.tight_layout()
			plt.savefig("./GraphsResults/ExpectationsVectorsBestChoiceNormalized.svg", bbox_inches = 'tight')
			plt.savefig("./GraphsResults/ExpectationsVectorsBestChoiceNormalized.png", bbox_inches = 'tight')


	listColors = ['r', 'g', 'b', 'y']
	listStyles = ['-', '--', '-.', ':']
	listMarkers = ['o', 's', 'D', '*']
	listLabels = ['N=20', 'N=100', 'N=1000']
	# listLabels = ['$N = 20$', '$N = 100$', '$N = 1000$']

	if args.trajectory != None :
		listTrajectories = list()
		for fileTrajectory in args.trajectory :
			if os.path.isfile(fileTrajectory) :
				trajectory = list()
				regexpLine = re.compile(r"^\((.+),(.+),(.+)\)$")
				with open(fileTrajectory, 'r') as fileRead :
					fileRead = fileRead.readlines()
					for line in fileRead :
						s = regexpLine.search(line.rstrip('\n'))

						if s :
							trajectory.append((int(float(s.group(1)) * 100), int(float(s.group(2)) * 100), int(float(s.group(3)) * 100)))

				listTrajectories.append(trajectory)

		if len(listTrajectories) > 0 :
			# -- Expectation All Full with trajectory --
			fig, ax = plt.subplots(ncols = 1, figsize = size)
			ax.axis("off")
			figure, tax = ternary.figure(ax = ax, scale = scale)

			# tax.heatmap(ZexpectationAllFull, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000, colorbar = False)
			tax.get_axes().set_aspect(1.)
			tax.plot([pA, pB, pC], color = 'black', linewidth = 2, linestyle = "--")
			tax.plot([pA, pB, pD], color = 'black', linewidth = 2, linestyle = "--")

			cpt = 0
			for trajectory in listTrajectories :
				tax.plot(trajectory, linewidth = 2, color = listColors[cpt % len(listColors)], linestyle = listStyles[cpt % len(listStyles)], label = listLabels[cpt % len(listLabels)])

				cpt += 1

			tax.boundary(linewidth=2.0)
			tax.gridlines(color="black", multiple=10)

			# ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
			# ticks = range(0, scale + 1, 20)
			# tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
		 	# tax.ticks(axis='lbr', linewidth=1)
			tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

			# Remove default Matplotlib Axes
			tax.clear_matplotlib_ticks()

			fontsize = 25
			fontweight = 'bold'
			tax.left_axis_label("Solo", (0.0 - 0.09, 1.0 + 0.17, 0.5), 0.0, fontsize = fontsize, fontweight = fontweight)
			tax.right_axis_label("Follower", (1.0 - 0.06, 0.1, 0.0), -120, fontsize = fontsize, fontweight = fontweight)
			tax.bottom_axis_label("Turner", (-0.04, 0.1, 1.0), 120, fontsize = fontsize, fontweight = fontweight)
			legend = plt.legend(frameon = True)
			frame = legend.get_frame()
			frame.set_facecolor('0.9')
			frame.set_edgecolor('0.9')

			plt.tight_layout()
			plt.savefig("./GraphsResults/ExpectationsTrajectory.svg", bbox_inches = 'tight')
			plt.savefig("./GraphsResults/ExpectationsTrajectory.png", bbox_inches = 'tight')



	if args.scatter != None :
		listScatters = list()
		for fileScatter in args.scatter :
			if os.path.isfile(fileScatter) :
				scatter = list()
				regexpLine = re.compile(r"^\((.+),(.+),(.+)\)$")
				with open(fileScatter, 'r') as fileRead :
					fileRead = fileRead.readlines()
					for line in fileRead :
						s = regexpLine.search(line.rstrip('\n'))

						if s :
							scatter.append((int(float(s.group(1)) * 100), int(float(s.group(2)) * 100), int(float(s.group(3)) * 100)))

				listScatters.append(scatter)

		if len(listScatters) > 0 :
			# -- Expectation All Full with trajectory --
			fig, ax = plt.subplots(ncols = 1, figsize = size)
			ax.axis("off")
			figure, tax = ternary.figure(ax = ax, scale = scale)
			tax.get_axes().set_aspect(1.)

			cpt = 0
			for scatter in listScatters :
				tax.scatter(scatter, color = listColors[cpt % len(listColors)], marker = listMarkers[cpt % len(listMarkers)], s = 75, label = listLabels[cpt % len(listLabels)])

				cpt += 1

			# tax.heatmap(ZexpectationAllFull, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000, colorbar = False)
			tax.plot([pA, pB, pC], color = 'black', linewidth = 2, linestyle = "--")
			tax.plot([pA, pB, pD], color = 'black', linewidth = 2, linestyle = "--")

			tax.boundary(linewidth=2.0)
			tax.gridlines(color="black", multiple=10)

			# ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
			# ticks = range(0, scale + 1, 20)
			# tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
		 	# tax.ticks(axis='lbr', linewidth=1)
			tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

			# Remove default Matplotlib Axes
			tax.clear_matplotlib_ticks()

			fontsize = 25
			fontweight = 'bold'
			tax.left_axis_label("Solo", (0.0 - 0.09, 1.0 + 0.17, 0.5), 0.0, fontsize = fontsize, fontweight = fontweight)
			tax.right_axis_label("Follower", (1.0 - 0.06, 0.1, 0.0), -120, fontsize = fontsize, fontweight = fontweight)
			tax.bottom_axis_label("Turner", (-0.04, 0.1, 1.0), 120, fontsize = fontsize, fontweight = fontweight)
			legend = plt.legend(frameon = True)
			frame = legend.get_frame()
			frame.set_facecolor('0.9')
			frame.set_edgecolor('0.9')

			plt.tight_layout()
			plt.savefig("./GraphsResults/ExpectationsScatter.svg", bbox_inches = 'tight')
			plt.savefig("./GraphsResults/ExpectationsScatter.png", bbox_inches = 'tight')



	if args.timeProp != None :
		hashTimeProp = dict()

		if os.path.isfile(args.timeProp) :
			regexpRun = re.compile(r"^Run (\d+)$")
			regexpLine = re.compile(r"^\((.+),(.+),(.+)\)$")

			curRun = None
			histTimeProp = dict()
			with open(args.timeProp, 'r') as fileRead :
				fileRead = fileRead.readlines()
				for line in fileRead :
					s = regexpRun.search(line.rstrip('\n'))

					if s :
						if curRun != None :
							hashTimeProp[curRun] = histTimeProp
							histTimeProp = dict()

						curRun = int(s.group(1))
					else :
						s = regexpLine.search(line.rstrip('\n'))

						if s :
							if curRun != None :

								proportion = (int(float(s.group(1)) * 100), int(float(s.group(2)) * 100), int(float(s.group(3)) * 100))

								if proportion not in histTimeProp.keys() :
									histTimeProp[proportion] = 1
								else :
									histTimeProp[proportion] += 1

							else :
								print("Error ! No curRun !")

			if curRun != None :
				hashTimeProp[curRun] = histTimeProp

		# for run in hashTimeProp.keys() :
		# 	print("Run : " + str(run))

		# 	# -- Expectation All Full with trajectory --
		# 	fig, ax = plt.subplots(ncols = 1, figsize = size)
		# 	ax.axis("off")
		# 	figure, tax = ternary.figure(ax = ax, scale = scale)

		# 	for prop in ZexpectationAllFull :
		# 		if prop not in hashTimeProp[run] :
		# 			hashTimeProp[run][prop] = 0

		# 	tax.get_axes().set_aspect(1.)
		# 	tax.heatmap(hashTimeProp[run], cmap = cm.jet, style="triangular", colorbar = True)#, vmin = 0, vmax = 5000)
		# 	# tax.heatmap(test, cmap = cm.jet, style="triangular", colorbar = True)#, vmin = 0, vmax = 5000)

		# 	tax.plot([pA, pB, pC], color = 'black', linewidth = 2, linestyle = "--")
		# 	tax.plot([pA, pB, pD], color = 'black', linewidth = 2, linestyle = "--")

		# 	tax.boundary(linewidth=2.0)
		# 	tax.gridlines(color="black", multiple=10)

		# 	tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

		# 	# Remove default Matplotlib Axes
		# 	tax.clear_matplotlib_ticks()

		# 	plt.tight_layout()
		# 	plt.savefig("./GraphsResults/ExpectationsTimePropRun" + str(run) + ".svg", bbox_inches = 'tight')
		# 	plt.savefig("./GraphsResults/ExpectationsTimePropRun" + str(run) + ".png", bbox_inches = 'tight')


		# -- Expectation All Full with trajectory --
		fig, ax = plt.subplots(ncols = 1, figsize = size)
		ax.axis("off")
		figure, tax = ternary.figure(ax = ax, scale = scale)

		totalTimeProp = dict()
		for prop in ZexpectationAllFull :
			totalTimeProp[prop] = 0

			for run in hashTimeProp.keys() :
				if prop in hashTimeProp[run] :
					totalTimeProp[prop] += hashTimeProp[run][prop]

		tax.get_axes().set_aspect(1.)
		tax.heatmap(totalTimeProp, cmap = cm.jet, style="triangular", colorbar = False)#, vmin = 0, vmax = 5000)

		tax.plot([pA, pB, pC], color = 'black', linewidth = 2, linestyle = "--")
		tax.plot([pA, pB, pD], color = 'black', linewidth = 2, linestyle = "--")

		tax.boundary(linewidth=2.0)
		tax.gridlines(color="black", multiple=10)

		tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

		# Remove default Matplotlib Axes
		tax.clear_matplotlib_ticks()

		plt.tight_layout()
		plt.savefig("./GraphsResults/ExpectationsTimeProp.svg", bbox_inches = 'tight')
		plt.savefig("./GraphsResults/ExpectationsTimeProp.png", bbox_inches = 'tight')



	# # -- Front Solo --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# # tax.scatter(frontSolo, color = 'red')
	# # tax.scatter(frontFollower, color = 'blue')
	# # tax.scatter(frontTurner, color = 'green')
	# tax.plot(frontSolo, color = 'red')
	# tax.plot(frontFollower, color = 'blue')
	# tax.plot(frontTurner, color = 'green')
	# tax.boundary(linewidth=2.0)
	# tax.gridlines(color="black", multiple=10)

	# # ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	# # ticks = range(0, scale + 1, 20)
	# # tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True)#, offset=0.03)
 # 	# tax.ticks(axis='lbr', linewidth=1)
	# tax.ticks(axis = 'lbr', multiple = 20, linewidth = 1, clockwise = True)

	# # Remove default Matplotlib Axes
	# tax.clear_matplotlib_ticks()

	# tax.left_axis_label("Solo")
	# tax.right_axis_label("Follower")
	# tax.bottom_axis_label("Turner")

	# plt.tight_layout()
	# plt.savefig("./GraphsResults/Front.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/Front.png", bbox_inches = 'tight')


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	# parser.add_argument('file', help = "Genome file")
	parser.add_argument('-p', '--precision', help = "Precision", default = 0.01)
	parser.add_argument('-t', '--trajectory', help = "Load trajectory", type = str, default = None, nargs = '+')
	parser.add_argument('-T', '--timeProp', help = "Load time proportion", type = str, default = None)
	parser.add_argument('-s', '--scatter', help = "Load scatter points", type = str, default = None, nargs = '+')
	parser.add_argument('-v', '--vector', help = "Draw the vector field", default = False, action = "store_true")
	parser.add_argument('-b', '--bestchoice', help = "Individuals always chooses the best partner", default = False, action = "store_true")
	args = parser.parse_args()

	main(args)

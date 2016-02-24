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



def main(args) :
	sns.set()
	sns.set_style('white')
	sns.set_context('paper')
	palette = sns.color_palette("husl", 4)

	dpi = 96
	size = (1680/dpi, 1024/dpi)
	# fig, (ax0, ax1, ax2) = plt.subplots(ncols=3, figsize = size)

	# fig = plt.figure(figsize = size)	
	# ax0 = plt.subplot2grid((4,3), (0,0))
	# ax1 = plt.subplot2grid((4,3), (0,1))
	# ax2 = plt.subplot2grid((4,3), (0,2))
	# ax3 = plt.subplot2grid((4,3), (1,0))
	# ax4 = plt.subplot2grid((4,3), (1,1))
	# ax5 = plt.subplot2grid((4,3), (1,2))
	# ax6 = plt.subplot2grid((4,3), (2,0))
	# ax7 = plt.subplot2grid((4,3), (2,1))
	# ax8 = plt.subplot2grid((4,3), (3,0))
	# ax9 = plt.subplot2grid((4,3), (3,1))
	# ax0 = plt.subplot2grid((2,6), (0,0), colspan = 2)
	# ax1 = plt.subplot2grid((2,6), (0,2), colspan = 2)
	# ax2 = plt.subplot2grid((2,6), (0,4), colspan = 2)
	# ax3 = plt.subplot2grid((2,6), (1,0))
	# ax4 = plt.subplot2grid((2,6), (1,1))
	# ax5 = plt.subplot2grid((2,6), (1,2))
	# ax6 = plt.subplot2grid((2,6), (1,3))
	# ax7 = plt.subplot2grid((2,6), (1,4))
	# ax8 = plt.subplot2grid((2,6), (1,5))

	# # -- Solo VS Follower --
	# Yexpectation = []
	# tabProportions = {}
	# for proportion in Xproportions :
	# 	tabProportions['Solo'] = proportion
	# 	tabProportions['Follower'] = 1.0 - proportion
	# 	Yexpectation.append(computeExpectation('Solo', tabProportions))

	# ax0.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)
	# ax0.set_xlabel('Proportion of solo')
	# ax0.set_ylabel('Expected value')
	# ax0.set_ylim(0.0, 5000.0)
	# ax0.set_title('Expected value of solo individuals against followers')	


	# # -- Follower VS Turner --
	# Yexpectation = []
	# tabProportions = {}
	# for proportion in Xproportions :
	# 	tabProportions['Follower'] = proportion
	# 	tabProportions['Turner'] = 1.0 - proportion
	# 	Yexpectation.append(computeExpectation('Follower', tabProportions))

	# ax1.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)
	# ax1.set_xlabel('Proportion of followers')
	# ax1.set_ylabel('Expected value')
	# ax1.set_ylim(0.0, 5000.0)
	# ax1.set_title('Expected value of follower individuals against turners')	


	# # -- Turner VS Solo --
	# Yexpectation = []
	# tabProportions = {}
	# for proportion in Xproportions :
	# 	tabProportions['Turner'] = proportion
	# 	tabProportions['Solo'] = 1.0 - proportion
	# 	Yexpectation.append(computeExpectation('Turner', tabProportions))

	# ax2.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)
	# ax2.set_xlabel('Proportion of turners')
	# ax2.set_ylabel('Expected value')
	# ax2.set_ylim(0.0, 5000.0)
	# ax2.set_title('Expected value of turner individuals against solo')	

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

			cptY += 1
		cptX += 1


	scale = 100


	# # -- Expectation Followers --
	# fig, ax = plt.subplots(ncols = 1, figsize = size)
	# ax.axis("off")
	# figure, tax = ternary.figure(ax = ax, scale = scale)

	# # print(ZexpectationFollower)
	# tax.heatmap(ZexpectationFollower, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
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

	# tax.heatmap(ZexpectationSolo, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
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

	# -- Expectation All Full --
	fig, ax = plt.subplots(ncols = 1, figsize = size)
	ax.axis("off")
	figure, tax = ternary.figure(ax = ax, scale = scale)

	tax.heatmap(ZexpectationAllFull, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.heatmap(ZexpectationFollowerPart, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.heatmap(ZexpectationSoloPart, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
	# tax.heatmap(ZexpectationTurnerPart, cmap = cm.jet, style="triangular", vmin = 0, vmax = 5000)
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

	tax.left_axis_label("Solo")
	tax.right_axis_label("Follower")
	tax.bottom_axis_label("Turner")

	plt.tight_layout()
	plt.savefig("./GraphsResults/ExpectationsAllFull.svg", bbox_inches = 'tight')
	plt.savefig("./GraphsResults/ExpectationsAllFull.png", bbox_inches = 'tight')



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
	args = parser.parse_args()

	main(args)
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

	Xproportions = np.arange(0.0, 1.0, args.precision)	

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
	Yproportions = np.arange(0.0, 1.0, args.precision)	

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

	# # -- Follower VS Solo VS Turner --
	# Zexpectation = hashExpectations['Follower']
	# Zexpectation = np.array(Zexpectation)
	# heatmap = ax3.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	# ax3.set_xlabel('Proportion of solo')
	# ax3.set_xticks(ticks)
	# ax3.set_xticklabels([Yproportions[t] for t in ticks])
	# ax3.set_ylabel('Proportion of followers')
	# ax3.set_yticks(ticks)
	# ax3.set_yticklabels([Xproportions[t] for t in ticks])
	# ax3.invert_yaxis()
	# ax3.set_title('Expected value of follower individuals against solo and turners')



	# # -- Solo VS Turner VS Follower --
	# Zexpectation = hashExpectations['Solo']
	# Zexpectation = np.array(Zexpectation)
	# heatmap = ax4.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	# ax4.set_xlabel('Proportion of solo')
	# ax4.set_xticks(ticks)
	# ax4.set_xticklabels([Yproportions[t] for t in ticks])
	# ax4.set_ylabel('Proportion of followers')
	# ax4.set_yticks(ticks)
	# ax4.set_yticklabels([Xproportions[t] for t in ticks])
	# ax4.invert_yaxis()
	# ax4.set_title('Expected value of solo individuals against turners and followers')



	# # -- Turner VS Follower VS Solo --
	# Zexpectation = hashExpectations['Turner']
	# Zexpectation = np.array(Zexpectation)
	# heatmap = ax5.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	# ax5.set_xlabel('Proportion of solo')
	# ax5.set_xticks(ticks)
	# ax5.set_xticklabels([Yproportions[t] for t in ticks])
	# ax5.set_ylabel('Proportion of followers')
	# ax5.set_yticks(ticks)
	# ax5.set_yticklabels([Xproportions[t] for t in ticks])
	# ax5.invert_yaxis()
	# ax5.set_title('Expected value of turner individuals against followers and solo')
	# # plt.colorbar(heatmap)

	# divider = make_axes_locatable(ax5)
	# cax = divider.append_axes("right", size="5%", pad=0.05)

	# plt.colorbar(heatmap, cax=cax)


	# # -- Expected values WRT Followers' proportion
	# proportionSolo = 0.5
	# Yexpectation = [line[int(len(hashExpectations['Follower'][0]) * proportionSolo)] for line in hashExpectations['Follower'][:]]
	# ax6.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)

	# Yexpectation = [line[int(len(hashExpectations['Solo'][0]) * proportionSolo)] for line in hashExpectations['Solo'][:]]
	# ax6.plot(Xproportions, Yexpectation, color = palette[1], linestyle = '-', linewidth = 2, marker = None)

	# Yexpectation = [line[int(len(hashExpectations['Turner'][0]) * proportionSolo)] for line in hashExpectations['Turner'][:]]
	# ax6.plot(Xproportions, Yexpectation, color = palette[2], linestyle = '-', linewidth = 2, marker = None)

	# ax6.set_xlabel('Proportion of followers')
	# ax6.set_xlim(0.0, 0.5)
	# ax6.invert_xaxis()
	# ax6.set_ylabel('Expected value')
	# ax6.set_ylim(0.0, 5000.0)
	# ax6.set_title("Expected values with respect to followers' proportion with proportion solo = 0.5")


	# # -- Expected values WRT Solo proportion
	# proportionFollower = 0.5
	# Yexpectation = hashExpectations['Follower'][int(len(hashExpectations['Follower'][0]) * proportionFollower)][:]
	# ax7.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)

	# Yexpectation = hashExpectations['Solo'][int(len(hashExpectations['Solo'][0]) * proportionFollower)][:]
	# ax7.plot(Xproportions, Yexpectation, color = palette[1], linestyle = '-', linewidth = 2, marker = None)

	# Yexpectation = hashExpectations['Turner'][int(len(hashExpectations['Turner'][0]) * proportionFollower)][:]
	# ax7.plot(Xproportions, Yexpectation, color = palette[2], linestyle = '-', linewidth = 2, marker = None)

	# ax7.set_xlabel('Proportion of solo')
	# ax7.set_xlim(0.0, 0.5)
	# ax7.invert_xaxis()
	# ax7.set_ylabel('Expected value')
	# ax7.set_ylim(0.0, 5000.0)
	# ax7.set_title("Expected values with respect to solo proportion with proportion followers = 0.5")


	# # -- Expected values WRT Followers' proportion
	# proportionSolo = 0.0
	# Yexpectation = [line[int(len(hashExpectations['Follower'][0]) * proportionSolo)] for line in hashExpectations['Follower'][:]]
	# ax8.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)

	# Yexpectation = [line[int(len(hashExpectations['Solo'][0]) * proportionSolo)] for line in hashExpectations['Solo'][:]]
	# ax8.plot(Xproportions, Yexpectation, color = palette[1], linestyle = '-', linewidth = 2, marker = None)

	# Yexpectation = [line[int(len(hashExpectations['Turner'][0]) * proportionSolo)] for line in hashExpectations['Turner'][:]]
	# ax8.plot(Xproportions, Yexpectation, color = palette[2], linestyle = '-', linewidth = 2, marker = None)

	# ax8.set_xlabel('Proportion of followers')
	# ax8.set_xlim(0.0, 0.5)
	# ax8.invert_xaxis()
	# ax8.set_ylabel('Expected value')
	# ax8.set_ylim(0.0, 5000.0)
	# ax8.set_title("Expected values with respect to followers' proportion with proportion solo = 0.0")


	# # -- Expected values WRT Solo proportion
	# proportionFollower = 0.0
	# Yexpectation = hashExpectations['Follower'][int(len(hashExpectations['Follower'][0]) * proportionFollower)][:]
	# pl1 = ax9.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)

	# Yexpectation = hashExpectations['Solo'][int(len(hashExpectations['Solo'][0]) * proportionFollower)][:]
	# pl2 = ax9.plot(Xproportions, Yexpectation, color = palette[1], linestyle = '-', linewidth = 2, marker = None)

	# Yexpectation = hashExpectations['Turner'][int(len(hashExpectations['Turner'][0]) * proportionFollower)][:]
	# pl3 = ax9.plot(Xproportions, Yexpectation, color = palette[2], linestyle = '-', linewidth = 2, marker = None)

	# ax9.set_xlabel('Proportion of solo')
	# ax9.set_xlim(0.0, 0.5)
	# ax9.invert_xaxis()
	# ax9.set_ylabel('Expected value')
	# ax9.set_ylim(0.0, 5000.0)
	# ax9.set_title("Expected values with respect to solo proportion with proportion followers = 0.0")

	# fig.tight_layout()

	# plt.savefig("./GraphsResults/Expectations.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/Expectations.png", bbox_inches = 'tight')
	# plt.close()

	# handles, labels = ax9.get_legend_handles_labels()
	# ax9.legend()

	# legend = plt.legend([pl1, pl2, pl3], ['Follower', 'Solo', 'Turner'], frameon=True)
	# frame = legend.get_frame()
	# frame.set_facecolor('0.9')
	# frame.set_edgecolor('0.9')

	# fig.tight_layout()
	# plt.show()


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

	# fig, ax0 = plt.subplots(ncols = 1, figsize = size)
	# # plt.grid()

	# # -- Follower VS Solo VS Turner --
	# Zexpectation = hashExpectations['Follower']
	# Zexpectation = np.array(Zexpectation)
	# heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	
	# if len(Xproportions) - 1 not in ticks :
	# 	ticks.append(len(Xproportions) - 1)

	# ax0.add_line(lines.Line2D([0, ticks[-1]], [0, ticks[-1]], color="black", linewidth = 2))
	# ax0.set_xlabel('Proportion of leaders')
	# ax0.set_xticks(ticks)
	# ax0.set_xticklabels([Yproportions[t] for t in ticks])
	# ax0.set_ylabel('Proportion of followers')
	# ax0.set_yticks(ticks)
	# ax0.set_yticklabels([Xproportions[t] for t in ticks])
	# ax0.invert_yaxis()
	# ax0.set_title('Expected value of follower individuals')

	# plt.savefig("./GraphsResults/ExpectationsFollowers.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsFollowers.png", bbox_inches = 'tight')
	# plt.close()



	# fig, ax0 = plt.subplots(ncols = 1, figsize = size)
	# # plt.grid()

	# # -- Solo VS Turner VS Follower --
	# Zexpectation = hashExpectations['Solo']
	# Zexpectation = np.array(Zexpectation)
	# heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	
	# if len(Xproportions) - 1 not in ticks :
	# 	ticks.append(len(Xproportions) - 1)

	# ax0.add_line(lines.Line2D([0, ticks[-1]], [0, ticks[-1]], color="black", linewidth = 2))
	# ax0.set_xlabel('Proportion of leaders')
	# ax0.set_xticks(ticks)
	# ax0.set_xticklabels([Yproportions[t] for t in ticks])
	# ax0.set_ylabel('Proportion of followers')
	# ax0.set_yticks(ticks)
	# ax0.set_yticklabels([Xproportions[t] for t in ticks])
	# ax0.invert_yaxis()
	# ax0.set_title('Expected value of solo individuals')

	# plt.savefig("./GraphsResults/ExpectationsSolo.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsSolo.png", bbox_inches = 'tight')
	# plt.close()



	# fig, ax0 = plt.subplots(ncols = 1, figsize = size)
	# # plt.grid()

	# # -- Turner VS Follower VS Solo --
	# Zexpectation = hashExpectations['Turner']
	# Zexpectation = np.array(Zexpectation)
	# heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	
	# if len(Xproportions) - 1 not in ticks :
	# 	ticks.append(len(Xproportions) - 1)

	# ax0.add_line(lines.Line2D([0, ticks[-1]], [0, ticks[-1]], color="black", linewidth = 2))
	# ax0.set_xlabel('Proportion of leaders')
	# ax0.set_xticks(ticks)
	# ax0.set_xticklabels([Yproportions[t] for t in ticks])
	# ax0.set_ylabel('Proportion of followers')
	# ax0.set_yticks(ticks)
	# ax0.set_yticklabels([Xproportions[t] for t in ticks])
	# ax0.invert_yaxis()
	# ax0.set_title('Expected value of turner individuals')
	# # plt.colorbar(heatmap)

	# divider = make_axes_locatable(ax0)
	# cax = divider.append_axes("right", size="5%", pad=0.05)

	# plt.colorbar(heatmap, cax=cax)

	# plt.savefig("./GraphsResults/ExpectationsTurners.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/ExpectationsTurners.png", bbox_inches = 'tight')
	# plt.close()


	ZexpectationFollower = hashExpectations['Follower']
	ZexpectationSolo = hashExpectations['Solo']
	ZexpectationTurner = hashExpectations['Turner']
	ZexpectationFollowerSolo = []
	ZexpectationFollowerTurner = []
	ZexpectationSoloFollower = []
	ZexpectationSoloTurner = []
	ZexpectationTurnerFollower = []
	ZexpectationTurnerSolo = []
	ZexpectationFollowerFull = []
	ZexpectationSoloFull = []
	ZexpectationTurnerFull = []
	ZexpectationTest = dict()
	cptX = 0
	while cptX < len(ZexpectationFollower) :
		tmpArrayFollowerSolo = []
		tmpArrayFollowerTurner = []
		tmpArraySoloFollower = []
		tmpArraySoloTurner = []
		tmpArrayTurnerFollower = []
		tmpArrayTurnerSolo = []

		tmpArrayFollowerFull = []
		tmpArraySoloFull = []
		tmpArrayTurnerFull = []

		cptY = 0
		while cptY < len(ZexpectationFollower[cptX]) :
			# tmpArrayFollowerSolo.append(ZexpectationFollower[cptX][cptY] - ZexpectationSolo[cptX][cptY])
			# tmpArrayFollowerTurner.append(ZexpectationFollower[cptX][cptY] - ZexpectationTurner[cptX][cptY])
			# tmpArraySoloFollower.append(ZexpectationSolo[cptX][cptY] - ZexpectationFollower[cptX][cptY])
			# tmpArraySoloTurner.append(ZexpectationSolo[cptX][cptY] - ZexpectationTurner[cptX][cptY])
			# tmpArrayTurnerFollower.append(ZexpectationTurner[cptX][cptY] - ZexpectationFollower[cptX][cptY])
			# tmpArrayTurnerSolo.append(ZexpectationTurner[cptX][cptY] - ZexpectationSolo[cptX][cptY])
			tmpArrayFollowerSolo.append(ZexpectationFollower[cptX][cptY] if ZexpectationFollower[cptX][cptY] - ZexpectationSolo[cptX][cptY] > 0 else 0)
			tmpArrayFollowerTurner.append(ZexpectationFollower[cptX][cptY] if ZexpectationFollower[cptX][cptY] - ZexpectationTurner[cptX][cptY] > 0 else 0)
			tmpArraySoloFollower.append(ZexpectationSolo[cptX][cptY] if ZexpectationSolo[cptX][cptY] - ZexpectationFollower[cptX][cptY] > 0 else 0)
			tmpArraySoloTurner.append(ZexpectationSolo[cptX][cptY] if ZexpectationSolo[cptX][cptY] - ZexpectationTurner[cptX][cptY] > 0 else 0)
			tmpArrayTurnerFollower.append(ZexpectationTurner[cptX][cptY] if ZexpectationTurner[cptX][cptY] - ZexpectationFollower[cptX][cptY] > 0 else 0)
			tmpArrayTurnerSolo.append(ZexpectationTurner[cptX][cptY] if ZexpectationTurner[cptX][cptY] - ZexpectationSolo[cptX][cptY] > 0 else 0)


			tmpArrayFollowerFull.append(ZexpectationFollower[cptX][cptY] if (tmpArrayFollowerSolo[cptY] > 0 and tmpArrayFollowerTurner[cptY] > 0) else 0)
			tmpArraySoloFull.append(ZexpectationSolo[cptX][cptY] if (tmpArraySoloTurner[cptY] > 0 and tmpArraySoloFollower[cptY] > 0) else 0)
			tmpArrayTurnerFull.append(ZexpectationTurner[cptX][cptY] if (tmpArrayTurnerSolo[cptY] > 0 and tmpArrayTurnerFollower[cptY] > 0) else 0)

			if (cptX + cptY) <= 100 :
				ZexpectationTest[(cptX, cptY, 100 - (cptX + cptY))] = ZexpectationFollower[cptX][cptY] if ZexpectationFollower[cptX][cptY] - ZexpectationSolo[cptX][cptY] > 0 else 0

			cptY += 1

		ZexpectationFollowerSolo.append(tmpArrayFollowerSolo)
		ZexpectationFollowerTurner.append(tmpArrayFollowerTurner)
		ZexpectationSoloFollower.append(tmpArraySoloFollower)
		ZexpectationSoloTurner.append(tmpArraySoloTurner)
		ZexpectationTurnerFollower.append(tmpArrayTurnerFollower)
		ZexpectationTurnerSolo.append(tmpArrayTurnerSolo)
		ZexpectationFollowerFull.append(tmpArrayFollowerFull)
		ZexpectationSoloFull.append(tmpArraySoloFull)
		ZexpectationTurnerFull.append(tmpArrayTurnerFull)

		cptX += 1
	

	# # -- Follower - Solo
	# fig, ax0 = plt.subplots(ncols = 1, figsize = size)

	# Zexpectation = np.array(ZexpectationFollowerSolo)
	# heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)
	# # heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = -5000.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	
	# if len(Xproportions) - 1 not in ticks :
	# 	ticks.append(len(Xproportions) - 1)

	# ax0.add_line(lines.Line2D([0, ticks[-1]], [0, ticks[-1]], color="black", linewidth = 2))
	# ax0.set_xlabel('Proportion of leaders')
	# ax0.set_xticks(ticks)
	# ax0.set_xticklabels([Yproportions[t] for t in ticks])
	# ax0.set_ylabel('Proportion of followers')
	# ax0.set_yticks(ticks)
	# ax0.set_yticklabels([Xproportions[t] for t in ticks])
	# ax0.invert_yaxis()
	# ax0.set_title('Substraction between followers and solo')

	# plt.savefig("./GraphsResults/SubstractionFollowersSolo.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/SubstractionFollowersSolo.png", bbox_inches = 'tight')
	# plt.close()


	# # -- Solo - Turner
	# fig, ax0 = plt.subplots(ncols = 1, figsize = size)
	
	# Zexpectation = np.array(ZexpectationSoloTurner)
	# heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)
	# # heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = -5000.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	
	# if len(Xproportions) - 1 not in ticks :
	# 	ticks.append(len(Xproportions) - 1)

	# ax0.add_line(lines.Line2D([0, ticks[-1]], [0, ticks[-1]], color="black", linewidth = 2))
	# ax0.set_xlabel('Proportion of leaders')
	# ax0.set_xticks(ticks)
	# ax0.set_xticklabels([Yproportions[t] for t in ticks])
	# ax0.set_ylabel('Proportion of followers')
	# ax0.set_yticks(ticks)
	# ax0.set_yticklabels([Xproportions[t] for t in ticks])
	# ax0.invert_yaxis()
	# ax0.set_title('Substraction between solo and turners')

	# plt.savefig("./GraphsResults/SubstractionSoloTurners.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/SubstractionSoloTurners.png", bbox_inches = 'tight')
	# plt.close()


	# # -- Turner - Solo
	# fig, ax0 = plt.subplots(ncols = 1, figsize = size)
	
	# Zexpectation = np.array(ZexpectationTurnerSolo)
	# heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)
	# # heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = -5000.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	
	# if len(Xproportions) - 1 not in ticks :
	# 	ticks.append(len(Xproportions) - 1)

	# ax0.add_line(lines.Line2D([0, ticks[-1]], [0, ticks[-1]], color="black", linewidth = 2))
	# ax0.set_xlabel('Proportion of leaders')
	# ax0.set_xticks(ticks)
	# ax0.set_xticklabels([Yproportions[t] for t in ticks])
	# ax0.set_ylabel('Proportion of followers')
	# ax0.set_yticks(ticks)
	# ax0.set_yticklabels([Xproportions[t] for t in ticks])
	# ax0.invert_yaxis()
	# ax0.set_title('Substraction between turners and solo')

	# plt.savefig("./GraphsResults/SubstractionTurnersSolo.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/SubstractionTurnersSolo.png", bbox_inches = 'tight')
	# plt.close()

	# # -- Turner - Follower
	# fig, ax0 = plt.subplots(ncols = 1, figsize = size)
	
	# Zexpectation = np.array(ZexpectationTurnerFollower)

	# heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)
	# # heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = -5000.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	
	# if len(Xproportions) - 1 not in ticks :
	# 	ticks.append(len(Xproportions) - 1)

	# ax0.add_line(lines.Line2D([0, ticks[-1]], [0, ticks[-1]], color="black", linewidth = 2))
	# ax0.set_xlabel('Proportion of leaders')
	# ax0.set_xticks(ticks)
	# ax0.set_xticklabels([Yproportions[t] for t in ticks])
	# ax0.set_ylabel('Proportion of followers')
	# ax0.set_yticks(ticks)
	# ax0.set_yticklabels([Xproportions[t] for t in ticks])
	# ax0.invert_yaxis()

	# ax0.set_title('Substraction between turners and followers')

	# divider = make_axes_locatable(ax0)
	# cax = divider.append_axes("right", size="5%", pad=0.05)

	# plt.colorbar(heatmap, cax=cax)

	# plt.savefig("./GraphsResults/SubstractionTurnersFollowers.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/SubstractionTurnersFollowers.png", bbox_inches = 'tight')
	# plt.close()

	
	# fig, ax0 = plt.subplots(ncols = 1, figsize = size)

	# Zexpectation = np.array(ZexpectationFollowerFull)
	# heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)
	# # heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = -5000.0, vmax = 5000.0)


	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	
	# if len(Xproportions) - 1 not in ticks :
	# 	ticks.append(len(Xproportions) - 1)

	# ax0.add_line(lines.Line2D([0, ticks[-1]], [0, ticks[-1]], color="black", linewidth = 2))
	# ax0.set_xlabel('Proportion of leaders')
	# ax0.set_xticks(ticks)
	# ax0.set_xticklabels([Yproportions[t] for t in ticks])
	# ax0.set_ylabel('Proportion of followers')
	# ax0.set_yticks(ticks)
	# ax0.set_yticklabels([Xproportions[t] for t in ticks])
	# ax0.invert_yaxis()

	# ax0.set_title('Substraction between followers and solo')

	# plt.savefig("./GraphsResults/SubstractionFollowersFull.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/SubstractionFollowersFull.png", bbox_inches = 'tight')
	# plt.close()


	# # -- Solo - Turner
	# fig, ax0 = plt.subplots(ncols = 1, figsize = size)
	
	# Zexpectation = np.array(ZexpectationSoloFull)
	# heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)
	# # heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = -5000.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	
	# if len(Xproportions) - 1 not in ticks :
	# 	ticks.append(len(Xproportions) - 1)

	# ax0.add_line(lines.Line2D([0, ticks[-1]], [0, ticks[-1]], color="black", linewidth = 2))
	# ax0.set_xlabel('Proportion of leaders')
	# ax0.set_xticks(ticks)
	# ax0.set_xticklabels([Yproportions[t] for t in ticks])
	# ax0.set_ylabel('Proportion of followers')
	# ax0.set_yticks(ticks)
	# ax0.set_yticklabels([Xproportions[t] for t in ticks])
	# ax0.invert_yaxis()
	# ax0.set_title('Substraction between solo and turners')

	# plt.savefig("./GraphsResults/SubstractionSoloFull.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/SubstractionSoloFull.png", bbox_inches = 'tight')
	# plt.close()


	# # -- Turner - Follower
	# fig, ax0 = plt.subplots(ncols = 1, figsize = size)
	
	# Zexpectation = np.array(ZexpectationTurnerFull)
	# heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = 2500.0, vmax = 3500.0)
	# # heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = -5000.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	
	# if len(Xproportions) - 1 not in ticks :
	# 	ticks.append(len(Xproportions) - 1)

	# ax0.add_line(lines.Line2D([0, ticks[-1]], [0, ticks[-1]], color="black", linewidth = 2))
	# ax0.set_xlabel('Proportion of leaders')
	# ax0.set_xticks(ticks)
	# ax0.set_xticklabels([Yproportions[t] for t in ticks])
	# ax0.set_ylabel('Proportion of followers')
	# ax0.set_yticks(ticks)
	# ax0.set_yticklabels([Xproportions[t] for t in ticks])
	# ax0.invert_yaxis()
	# ax0.set_title('Substraction between turners and followers')

	# divider = make_axes_locatable(ax0)
	# cax = divider.append_axes("right", size="5%", pad=0.05)

	# plt.colorbar(heatmap, cax=cax)

	# plt.savefig("./GraphsResults/SubstractionTurnersFull.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/SubstractionTurnersFull.png", bbox_inches = 'tight')
	# plt.close()


	scale = 100
	figure, tax = ternary.figure(scale = scale)

	# Zexpectation = np.array(ZexpectationTest)
	# print(ZexpectationTest)
	tax.heatmap(ZexpectationTest, cmap = cm.jet, style="triangular")#, vmin = 0, vmax = 5000)
	tax.boundary(linewidth=2.0)

	# ticks = [round(i / float(scale), 1) for i in range(scale + 1)]
	ticks = range(0, scale + 1, 20)
	tax.ticks(ticks=ticks, axis='rlb', linewidth=1, clockwise=True,
	          offset=0.03)
 	# tax.ticks(axis='lbr', linewidth=1)

	# Remove default Matplotlib Axes
	tax.clear_matplotlib_ticks()

	tax.left_axis_label("Left label $\\alpha^2$")
	tax.right_axis_label("Right label $\\beta^2$")
	tax.bottom_axis_label("Bottom label $\\Gamma - \\Omega$")

	# tax.set_title("Test")

	tax.show()




	# k = 0.5
	# s = 1000

	# data = vstack((
	#     array([k,0,0]) + rand(s,3), 
	#     array([0,k,0]) + rand(s,3), 
	#     array([0,0,k]) + rand(s,3)
	# ))
	# color = array([[1,0,0]]*s + [[0,1,0]]*s + [[0,0,1]]*s)
	# print("Length : " + str(len(data)))
	# print(data)
	# print(color)

	# newdata,ax = ternaryPlot(data)
	# print(newdata)

	# ax.scatter(
	#     newdata[:,0],
	#     newdata[:,1],
	#     s=2,
	#     alpha=0.5,
	#     color=color
	#     )
	# show()


	# -- All
	# fig, ax0 = plt.subplots(ncols = 1, figsize = size)
	
	# Zexpectation = np.array(ZexpectationFollowerSolo)
	# plt.contourf(Xproportions, Yproportions, Zexpectation)

	# heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = 2500.0, vmax = 3500.0)
	# # heatmap = ax0.imshow(Zexpectation, cmap = cm.jet, vmin = -5000.0, vmax = 5000.0)

	# ticks = range(0, len(Xproportions), len(Xproportions)/5)
	
	# if len(Xproportions) - 1 not in ticks :
	# 	ticks.append(len(Xproportions) - 1)

	# ax0.add_line(lines.Line2D([0, ticks[-1]], [0, ticks[-1]], color="black", linewidth = 2))
	# ax0.set_xlabel('Proportion of leaders')
	# ax0.set_xticks(ticks)
	# ax0.set_xticklabels([Yproportions[t] for t in ticks])
	# ax0.set_ylabel('Proportion of followers')
	# ax0.set_yticks(ticks)
	# ax0.set_yticklabels([Xproportions[t] for t in ticks])
	# ax0.invert_yaxis()
	# ax0.set_title('Substraction between turners and followers')

	# divider = make_axes_locatable(ax0)
	# cax = divider.append_axes("right", size="5%", pad=0.05)

	# plt.colorbar(heatmap, cax=cax)

	# plt.savefig("./GraphsResults/All.svg", bbox_inches = 'tight')
	# plt.savefig("./GraphsResults/All.png", bbox_inches = 'tight')
	# plt.close()

	# Zexpectation = ZexpectationFollower - ZexpectationSolo
	# print(ZexpectationFollower)
	# print(ZexpectationSolo)




# def ternaryPlot(
#             data,

#             # Scale data for ternary plot (i.e. a + b + c = 1)
#             scaling = True,

#             # Direction of first vertex.
#             start_angle = 90,

#             # Orient labels perpendicular to vertices.
#             rotate_labels = True,

#             # Labels for vertices.
#             labels = ('Solo', 'Follower', 'Turner'),

#             # Offset for label from vertex (percent of distance from origin).
#             label_offset = 0.10,

#             # Any matplotlib keyword args for plots.
#             edge_args = {'color':'black','linewidth':2},

#             # Any matplotlib keyword args for figures.
#             fig_args = {'figsize':(8,8),'facecolor':'white','edgecolor':'white'},
#         ):

#   # This will create a basic "ternary" plot (or quaternary, etc.)
#   basis = array(
#                   [
#                       [
#                           cos(2*_*pi/3 + start_angle*pi/180),
#                           sin(2*_*pi/3 + start_angle*pi/180)
#                       ] 
#                       for _ in range(3)
#                   ]
#               )

#   # If data is Nx3, newdata is Nx2.
#   if scaling:
#       # Scales data for you.
#       newdata = dot((data.T / data.sum(-1)).T,basis)
#   else:
#       # Assumes data already sums to 1.
#       newdata = dot(data,basis)

#   fig = figure(**fig_args)
#   ax = fig.add_subplot(111)

#   for i,l in enumerate(labels):
#       if i >= 3:
#           break
#       x = basis[i,0]
#       y = basis[i,1]
#       if rotate_labels:
#           angle = 180*arctan(y/x)/pi + 90
#           if angle > 90 and angle <= 270:
#               angle = mod(angle + 180,360)
#       else:
#           angle = 0
#       ax.text(
#               x*(1 + label_offset),
#               y*(1 + label_offset),
#               l,
#               horizontalalignment='center',
#               verticalalignment='center',
#               rotation=angle
#           )

#   # Clear normal matplotlib axes graphics.
#   ax.set_xticks(())
#   ax.set_yticks(())
#   ax.set_frame_on(False)

#   # Plot border
#   ax.plot(
#       [basis[_,0] for _ in range(3) + [0,]],
#       [basis[_,1] for _ in range(3) + [0,]],
#       **edge_args
#   )

#   return newdata,ax


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	# parser.add_argument('file', help = "Genome file")
	parser.add_argument('-p', '--precision', help = "Precision", default = 0.01)
	args = parser.parse_args()

	main(args)
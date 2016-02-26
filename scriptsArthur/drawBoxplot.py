#!/usr/bin/env python

import matplotlib
from pylab import *
import numpy as np
import seaborn as sns
import argparse
from scipy import stats

import re
import os


outputDir = "./GraphsResults"
nbTrials = 20


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


def main(args) :
	regexpBeg = re.compile(r"^--")
	regexpTrial = re.compile(r"^Trial (\d+) :")
	regexpFinal = re.compile(r"^Final :")
	regexpFood1 = re.compile(r"^Food 1 : (\d+)$")
	regexpFood2 = re.compile(r"^Food 2 : (\d+)$")
	regexpLeadership = re.compile(r"^Leadership : (.*)$")

	if os.path.isfile(args.file) :

		dataHash = dict()
		with open(args.file, 'r') as fileRead :
			fileRead = fileRead.readlines()

			cptList = 0
			curList = np.zeros((20, 3))
			curTrial = -1
			curFood1 = -1
			curFood2 = -1
			curLeadership = -1

			cpt = 0
			while cpt < len(fileRead) :
				line = fileRead[cpt].rstrip('\n')
				if regexpBeg.search(line) :
					if cptList != 0 :
						curList[curTrial, 0] = curFood1
						curList[curTrial, 1] = curFood2
						curList[curTrial, 2] = curLeadership

						curTrial = -1
						curFood1 = -1
						curFood2 = -1
						curLeadership = -1

						if cptList == 1 :
							dataHash['SF'] = curList
							curList = np.zeros((20, 3))
						elif cptList == 2 :
							dataHash['TT'] = curList
							break

					cptList += 1
				else :
					s = regexpTrial.search(line)

					if s :
						trial = int(s.group(1))

						if curTrial != -1 :
							curList[curTrial, 0] = curFood1
							curList[curTrial, 1] = curFood2
							curList[curTrial, 2] = curLeadership

						curTrial = trial
					else :
						s = regexpFood1.search(line)

						if s :
							food = int(s.group(1))

							if curTrial != -1 :
								curFood1 = food
						else :
							s = regexpFood2.search(line)

							if s :
								food = int(s.group(1))

								if curTrial != -1 :
									curFood2 = food
							else :
								s = regexpLeadership.search(line)

								if s : 
									if curTrial != -1 :
										curLeadership = float(s.group(1))
								else :								
									s = regexpFinal.search(line)

									if s :
										curTrial = -1
									else :
										print('wat : ' + line)

				cpt += 1


	# print(dataHash)

	# Statistical analyses Fitness
	U, P = stats.mannwhitneyu(dataHash['SF'][:, 0], dataHash['TT'][:, 0])
	print("Mann-Whitney -> U = " + str(U) + "/P = " + str(P))

	stars = "-"
	if P < 0.0001:
	   stars = "****"
	elif (P < 0.001):
	   stars = "***"
	elif (P < 0.01):
	   stars = "**"
	elif (P < 0.05):
	   stars = "*"



	# Boxplots fitness
	fig, ax = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# plt.grid()

	bp = ax.boxplot([dataHash['SF'][:, 0], dataHash['TT'][:, 0]])
	
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	ax.spines['left'].set_visible(False)
	ax.get_xaxis().tick_bottom()
	ax.get_yaxis().tick_left()
	ax.tick_params(axis='x', direction='out')
	ax.tick_params(axis='y', length=0)

	ax.set_ylim(0, 6000)

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
	   bp['fliers'][0].set(markerfacecolor=palette[i],
	                   marker='o', alpha=0.75, markersize=6,
	                   markeredgecolor='none')
	   bp['fliers'][1].set(markerfacecolor=palette[i],
	                   marker='o', alpha=0.75, markersize=6,
	                   markeredgecolor='none')
	   # bp['fliers'][i * 2].set(markerfacecolor=palette[i],
	   #                 marker='o', alpha=0.75, markersize=6,
	   #                 markeredgecolor='none')
	   # bp['fliers'][i * 2 + 1].set(markerfacecolor=palette[i],
	   #                 marker='o', alpha=0.75, markersize=6,
	   #                 markeredgecolor='none')
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

	ax.set_xticklabels(['Leader/Follower\nstrategy', 'Turner\nstrategy'])

	y_max = np.max(np.concatenate((dataHash['SF'][:, 0], dataHash['TT'][:, 0])))
	# y_min = np.min(np.concatenate((dataHash['SF'][:, 0], dataHash['TT'][:, 0])))
	y_min = 0

	# print y_max

	ax.annotate("", xy=(1, y_max), xycoords='data',
	           xytext=(2, y_max), textcoords='data',
	           arrowprops=dict(arrowstyle="-", ec='#000000',
	                           connectionstyle="bar,fraction=0.05"))
	ax.text(1.5, y_max + abs(y_max - y_min)*0.05, stars,
	       horizontalalignment='center',
	       verticalalignment='center')

	plt.savefig(outputDir + "/boxplotFitness.png", bbox_inches = 'tight')
	plt.savefig(outputDir + "/boxplotFitness.svg", bbox_inches = 'tight')



	# Statistical analyses Leadership
	U, P = stats.mannwhitneyu(dataHash['SF'][:, 2], dataHash['TT'][:, 2])
	print("Mann-Whitney -> U = " + str(U) + "/P = " + str(P))

	stars = "-"
	if P < 0.0001:
	   stars = "****"
	elif (P < 0.001):
	   stars = "***"
	elif (P < 0.01):
	   stars = "**"
	elif (P < 0.05):
	   stars = "*"



	# Boxplots Leadership
	fig, ax = plt.subplots(nrows = 1, ncols = 1, figsize = size)
	# plt.grid()

	bp = ax.boxplot([dataHash['SF'][:, 2], dataHash['TT'][:, 2]])
	
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	ax.spines['left'].set_visible(False)
	ax.get_xaxis().tick_bottom()
	ax.get_yaxis().tick_left()
	ax.tick_params(axis='x', direction='out')
	ax.tick_params(axis='y', length=0)

	ax.set_ylim(-0.1, 1.1)

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
	   bp['fliers'][0].set(markerfacecolor=palette[i],
	                   marker='o', alpha=0.75, markersize=6,
	                   markeredgecolor='none')
	   bp['fliers'][1].set(markerfacecolor=palette[i],
	                   marker='o', alpha=0.75, markersize=6,
	                   markeredgecolor='none')
	   # bp['fliers'][i * 2].set(markerfacecolor=palette[i],
	   #                 marker='o', alpha=0.75, markersize=6,
	   #                 markeredgecolor='none')
	   # bp['fliers'][i * 2 + 1].set(markerfacecolor=palette[i],
	   #                 marker='o', alpha=0.75, markersize=6,
	   #                 markeredgecolor='none')
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

	ax.set_xticklabels(['Leader/Follower\nstrategy', 'Turner\nstrategy'])

	y_max = np.max(np.concatenate((dataHash['SF'][:, 2], dataHash['TT'][:, 2])))
	# y_min = np.min(np.concatenate((dataHash['SF'][:, 0], dataHash['TT'][:, 0])))
	y_min = -0.1

	# print y_max

	ax.annotate("", xy=(1, y_max), xycoords='data',
	           xytext=(2, y_max), textcoords='data',
	           arrowprops=dict(arrowstyle="-", ec='#000000',
	                           connectionstyle="bar,fraction=0.05"))
	ax.text(1.5, y_max + abs(y_max - y_min)*0.05, stars,
	       horizontalalignment='center',
	       verticalalignment='center')

	plt.savefig(outputDir + "/boxplotLeadership.png", bbox_inches = 'tight')
	plt.savefig(outputDir + "/boxplotLeadership.svg", bbox_inches = 'tight')



if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('file', help = "Results file")
	args = parser.parse_args()

	main(args)
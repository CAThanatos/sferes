#!/usr/bin/env python

import os
import argparse
import re

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

THRESHOLD_COOP_SOLO = 5.0


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




def main(args) :
	fileIn = os.path.join(args.directory, 'allgenomestrace.dat')
	regexpLine = re.compile(r"^([^,]+),([^,]+),([^,]+),([^,]+),?([^,]+)?$")
	phyloTree = {}
	behaviourTree = {}
	if os.path.isfile(fileIn) :
		with open(fileIn, 'r') as fileRead :
			fileRead = fileRead.readlines()

			for line in fileRead :
				line = line.rstrip('\n')

				s = regexpLine.search(line)
				if s :
					eval = int(s.group(1))

					if eval not in phyloTree :
						phyloTree[eval] = []
						behaviourTree[eval] = []

					ancestor = int(s.group(2))
					phyloTree[eval].append(ancestor)

					nb_ind1_leader_first = float(s.group(3))
					nb_preys_killed_coop = float(s.group(4))
					behaviour = None

					if len(s.groups()) > 4 :
						nb_preys_killed = float(s.group(5))

						if nb_preys_killed > 5 :
							if nb_preys_killed_coop < 5 :
								behaviour = 'S'
							else :
								behaviour = 'T'
						else :
							behaviour = 'F'

					behaviourTree[eval].append(behaviour)


		listEval = sorted(phyloTree.keys(), reverse = True)
		listAncestors = []

		evaluationChild = listEval[0]

		if args.evaluation != -1 and args.evaluation in listEval :
			evaluationChild = args.evaluation

		ancestor = args.genome
		listAncestors.append(ancestor)
		cpt = listEval.index(evaluationChild)
		while cpt < len(listEval) :
			ancestor = phyloTree[listEval[cpt]][ancestor]
			listAncestors.append(ancestor)
			cpt += 1

		print(listAncestors)
		print('\t-> Oldest ancestor : ' + str(listAncestors[-1]))

		if args.coalescence != -1 :
			listAncestors = []

			ancestor = args.coalescence
			listAncestors.append(ancestor)
			cpt = listEval.index(evaluationChild)
			while cpt < len(listEval) :
				ancestor = phyloTree[listEval[cpt]][ancestor]
				listAncestors.append(ancestor)
				cpt += 1

			print(listAncestors)
			print('\t-> Oldest ancestor : ' + str(listAncestors[-1]))

			divergenceIndex = listEval.index(evaluationChild)

			ancestor1 = args.genome
			ancestor2 = args.coalescence
			while divergenceIndex < len(listEval):
				evaluation = listEval[divergenceIndex]
				ancestor1 = phyloTree[evaluation][ancestor1]
				ancestor2 = phyloTree[evaluation][ancestor2]

				if ancestor1 != ancestor2 :
					divergenceIndex += 1
				else :
					break

			if divergenceIndex >= len(listEval) :
				print('No common ancestor between these two genomes.')
			else :
				print('Divergence after evaluation ' + str(listEval[divergenceIndex]) + ' from common ancestor ' + str(ancestor1))


		# -- Evolution of the proportions of phenotypes
		if args.behaviour :
			fig, ax0 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

			plt.grid()

			tabEvalPlot = [sorted(listEval)[i] for i in range(0, len(listEval), args.precision)]
			proportionsSolo = []
			proportionsTurner = []
			proportionsFollower = []
			for eval in tabEvalPlot :
				proportionsSolo.append((behaviourTree[eval].count('S')))
				proportionsTurner.append((behaviourTree[eval].count('T')))
				proportionsFollower.append((behaviourTree[eval].count('F')))


			ax0.plot(range(len(proportionsSolo)), proportionsSolo, color=palette[0], linestyle=linestyles[0], linewidth=linewidth, marker=markers[0])
			ax0.plot(range(len(proportionsTurner)), proportionsTurner, color=palette[1], linestyle=linestyles[1], linewidth=linewidth, marker=markers[1])
			ax0.plot(range(len(proportionsFollower)), proportionsFollower, color=palette[2], linestyle=linestyles[2], linewidth=linewidth, marker=markers[2])

			tabPlotTicks = tabEvalPlot
			ticks = range(0, len(tabEvalPlot), int(len(tabEvalPlot)/5))
			if len(tabEvalPlot) - 1 not in ticks :
				ticks.append(len(tabEvalPlot) - 1)

			ax0.set_xticks(ticks)
			ax0.set_xticklabels([tabPlotTicks[x] for x in ticks])
			ax0.set_xlabel("Evaluation")
			# ax0.set_xlim(0, len(tabEvalPlot) - 1)

			ax0.set_ylabel("Proportion of Phenotype")
			ax0.set_ylim(-1, 11)

			legend = plt.legend(['Solo', 'Turner', 'Follower'], loc = 1, frameon=True)
			frame = legend.get_frame()
			frame.set_facecolor('0.9')
			frame.set_edgecolor('0.9')

			# axe1.set_title('Boxplot of best fitness')

			# plt.savefig(outputDir + "/proportionStags.png", bbox_inches = 'tight')
			# plt.savefig(outputDir + "/proportionStags.svg", bbox_inches = 'tight')
			# plt.close()
			plt.show()







if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('genome', help = "Child genome for which we want to find the ancestor", type = int)
	parser.add_argument('-e', '--evaluation', help = "Evaluation of the child for which we look for the ancestor", type = int, default = -1)
	parser.add_argument('-c', '--coalescence', help = "Second child genome for which we want to find the point of divergence with the first genome", type = int, default = -1)
	parser.add_argument('-b', '--behaviour', help = "Plot the evolution of each type of behaviour", default = False, action = "store_true")
	parser.add_argument('-p', '--precision', help = "Precision of plotting", default = 1000, type = int)
	args = parser.parse_args()

	main(args)

#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import lines
import matplotlib.cm as cm

import seaborn as sns
import numpy as np
import argparse
import re
import os
import math

import makeData
import Tools


def main(args) :
	if os.path.isdir(args.directory) :
		listFiles = [os.path.join(args.directory, file) for file in os.listdir(args.directory) if (not os.path.isdir(file) and file == "trace_leader.dat")]

		if len(listFiles) == 1:
			maxEval = int(args.max)

			tabEvaluation = []
			tabPropotion = []
			with open(listFiles[0], "r") as fileRead :
				fileRead = fileRead.readlines();
				lines = [line.rstrip('\n').split(',') for line in fileRead]

				for line in lines :
					eval = int(line[0])

					if eval > maxEval :
						break

					proportion = float(line[1])

					if math.isnan(proportion) :
						proportion = 0.5

					nb_leader_first = int(line[2])
					nb_coop = None
					nb_total = None

					if len(line) > 4 :
						nb_coop = int(line[3])
						nb_total = int(line[4])
					else :
						nb_total = int(line[3])

					tabEvaluation.append(eval)
					tabPropotion.append(proportion - 0.5)


		lastEval = tabEvaluation[-1]
		diffEvals = lastEval - tabEvaluation[-2]

		while lastEval <= maxEval :
			lastEval += diffEvals
			tabEvaluation.append(lastEval)


		# SEABORN
		sns.set()
		sns.set_style('white')
		sns.set_context('paper')
		palette = sns.color_palette("husl", len(tabPropotion))

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

		# --- PLOT PROPORTION ---
		fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

		axe1.plot(range(len(tabPropotion)), tabPropotion)

		# Divide the x axis by 10
		tabEvaluationTicks = [indice for indice in range(len(tabPlotEvaluation)) if indice % (int(len(tabPlotEvaluation)/10)) == 0]

		axe1.set_xticks(tabEvaluationTicks)
		axe1.set_xticklabels([tabPlotEvaluation[indice] for indice in tabEvaluationTicks])
		axe1.set_xlabel('Evaluation')

		axe1.set_ylabel('Proportion')
		axe1.set_ylim(-0.6, 0.6)

		axe1.set_title('Leadership Proportion', fontsize = 10)

		plt.savefig(args.directory + "/proportionLeadership.png", bbox_inches = 'tight')
		plt.close()




if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")

	parser.add_argument('-m', '--max', help = "Max evaluation", default='20000')
	parser.add_argument('-p', '--precision', help = "Precision", default='100')
	args = parser.parse_args()

	main(args)

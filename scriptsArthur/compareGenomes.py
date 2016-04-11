#!/usr/bin/env python

import os
import path
import re
import argparse
import math
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import sys
import shutil
import random

import Tools


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

beginningEval = {run : (beginningGen[run] - 1) * 20 + 30 for run in beginningGen.keys()}

# SEABORN
sns.set()
sns.set_style('white')
sns.set_context('paper')
palette = sns.color_palette("husl", 3)


# GRAPHS GLOBAL VARIABLES
linewidth = 2
linestyles = ['-', '--', '-.']
linestylesOff = ['-', '-', '-']
markers = [None, None, None] #['o', '+', '*']

dpi = 96
size = (1280/dpi, 1024/dpi)


def distance(gen1, gen2) :
	assert(len(gen1) == len(gen2))

	cpt = 0;
	distance = 0
	while cpt < len(gen1) :
		distance += pow(gen1[cpt] - gen2[cpt], 2)
		cpt += 1

	return math.sqrt(distance)/math.sqrt(len(gen1))

def similarity(gen1, gen2) :
	return 1.0 - distance(gen1, gen2)


def main(args) :
	listTopDirectories = Tools.searchTopDirectories(args.directory)

	for topDirectory in listTopDirectories :
		print("Treating : " + topDirectory)

		dirName = os.path.basename(topDirectory)
		outputDir = os.path.join(args.output, dirName)

		print('-> ' + outputDir)
		if os.path.isdir(outputDir) :
			shutil.rmtree(outputDir)

		os.makedirs(outputDir)

		listSubDirs = [subDir for subDir in os.listdir(topDirectory) if re.search(r"^Dir\d+$", subDir)]

		for subDir in listSubDirs :
			fileInput = os.path.join(os.path.join(topDirectory, subDir), args.file)

			hashGenotypes = {}
			tabEval = []

			regexp = re.compile(r"^(\d+),")
			regexpSubDir = re.compile(r"^Dir(\d+)$")
			if os.path.isfile(fileInput) :
				with open(fileInput, 'r') as fileRead :
					fileRead = fileRead.readlines()

					cumulEval = args.precision
					lastEval = None
					firstEval = True
					listGenotypes = []
					for line in fileRead :
						s = regexp.search(line)

						if s :
							eval = int(s.group(1))

							if (args.maximum == -1) or (eval < args.maximum) :
								if lastEval == None :
									lastEval = eval

								if eval > lastEval :
									if cumulEval >= args.precision :
										cumulEval = 0

									firstEval = False

									cumulEval += eval - lastEval
									lastEval = eval

								if cumulEval >= args.precision or firstEval :
									genotype = [float(gene) for gene in line.rstrip('\n').split(',')[1:]]

									if eval not in hashGenotypes.keys() :
										hashGenotypes[eval] = []
										tabEval.append(eval)

									hashGenotypes[eval].append(genotype)

				hashSimilarities = {}
				hashMeans = {}
				for eval in hashGenotypes :
					listGenotypes = hashGenotypes[eval]
					hashSimilarities[eval] = [None] * len(listGenotypes)
					for i in range(len(listGenotypes)) :
						hashSimilarities[eval][i] = [None] * len(listGenotypes)

					genoMean = [None] * len(listGenotypes[0])
					cpt = 0
					while cpt < len(genoMean) :
						genoMean[cpt] = 0
						cpt += 1

					for i in range(0, len(listGenotypes)) :
						curArray = []
						for j in range(i, len(listGenotypes)) :
							# sim = similarity(listGenotypes[i], listGenotypes[j])
							sim = distance(listGenotypes[i], listGenotypes[j])
							hashSimilarities[eval][i][j] = sim
							hashSimilarities[eval][j][i] = sim

						for j in range(0, len(listGenotypes[i])) :
							genoMean[j] += listGenotypes[i][j]

					cpt = 0
					while cpt < len(genoMean) :
						genoMean[cpt] /= len(listGenotypes)
						cpt += 1

					hashMeans[eval] = genoMean


				hashDistance = {}
				for eval in hashMeans :
					distanceMean = 0

					listGenotypes = hashGenotypes[eval]
					for genotype in listGenotypes :
						distanceMean += distance(genotype, hashMeans[eval])

					distanceMean /= len(listGenotypes)
					hashDistance[eval] = distanceMean

				column_labels = range(0, len(hashSimilarities[tabEval[-1]]))
				row_labels = range(0, len(hashSimilarities[tabEval[-1]]))

				fig, (ax0, ax1, ax2) = plt.subplots(ncols=3, figsize = size)

				dataPlot = [hashDistance[eval] for eval in tabEval]
				ax0.plot(range(len(dataPlot)), dataPlot, color=palette[0], linestyle='-', linewidth=2, marker=None)

				# axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
				# axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])

				ticks = range(0, len(dataPlot), int(len(dataPlot)/5))
				ax0.set_xticks(ticks)
				ax0.set_xticklabels([tabEval[x] for x in ticks])

				num_bins = 10

				randIndiv = random.randint(0, len(hashSimilarities[tabEval[-1]]) - 1)
				ax1.hist(hashSimilarities[tabEval[-1]][randIndiv], num_bins, facecolor='green', alpha=0.5)
				ax1.set_xlim(0.0, 1.0)
				# ax1.set_ylim(0.0, mu)
				ax1.set_xlabel('Distance')
				ax1.set_ylabel('Number')
				ax1.set_title('Distance at evaluation ' + str(tabEval[-1]))

				dataHeat = np.array(hashSimilarities[tabEval[-1]])
				heatmap = ax2.pcolor(dataHeat, cmap=plt.cm.Blues, vmin = 0.0, vmax = 1.0)
				plt.colorbar(heatmap)

				# put the major ticks at the middle of each cell
				ax2.set_xticks(np.arange(dataHeat.shape[0]) + 0.5, minor=False)
				ax2.set_yticks(np.arange(dataHeat.shape[1]) + 0.5, minor=False)

				# want a more natural, table-like display
				ax2.invert_yaxis()
				# ax2.xaxis.tick_top()

				ax2.set_xticklabels(row_labels, minor=False)
				ax2.set_yticklabels(column_labels, minor=False)
				ax2.set_title('Distance at evaluation ' + str(tabEval[-1]))


				numDir = regexpSubDir.search(subDir).group(1)
				plt.savefig(os.path.join(outputDir, "graphs" + str(numDir) + ".png"), bbox_inches = 'tight')
				plt.savefig(os.path.join(outputDir, "graphs" + str(numDir) + ".png"), bbox_inches = 'tight')
				# plt.show()
				plt.close()


				if args.leadership :
					fileLeadership = os.path.join(os.path.join(topDirectory, subDir), "bestleadership.dat")
					hashProportion = {}

					regexpLeadership = re.compile(r"^([^,]+),([^,]+),([^,]+),")
					if os.path.isfile(fileLeadership) :
						with open(fileLeadership, 'r') as fileRead :
							fileRead = fileRead.readlines()

							cumulEval = args.precision
							lastEval = None
							firstEval = True
							for line in fileRead :
								s = regexpLeadership.search(line)

								if s :
									eval = int(s.group(1))

									if lastEval == None :
										lastEval = eval

									cumulEval += eval - lastEval
									lastEval = eval

									if cumulEval >= args.precision or firstEval :
										hashProportion[eval] = float(s.group(3))
										firstEval = False


					# MATPLOTLIB PARAMS
					matplotlib.rcParams['font.size'] = 15
					matplotlib.rcParams['font.weight'] = 'bold'
					matplotlib.rcParams['axes.labelsize'] = 25
					matplotlib.rcParams['axes.labelweight'] = 'bold'
					matplotlib.rcParams['xtick.labelsize'] = 25
					matplotlib.rcParams['ytick.labelsize'] = 25
					matplotlib.rcParams['legend.fontsize'] = 25

					fig, ax0 = plt.subplots(ncols = 1, figsize = size)

					plt.grid()

					startIndex = 0
					dataPlot = [hashDistance[eval] for eval in tabEval]
					if args.beginningGen :
						cpt = 0
						while cpt < len(tabEval) :
							if beginningEval[int(numDir)] == tabEval[cpt] :
								startIndex = cpt
								break

							cpt += 1
						dataPlot = [hashDistance[eval] for eval in tabEval if eval >= beginningEval[int(numDir)]]

					ax0.plot(range(len(dataPlot)), dataPlot, color=palette[0], linestyle='-', linewidth=2, marker=None)

					dataPlot = [hashProportion[eval] for eval in tabEval]
					if args.beginningGen :
						dataPlot = [hashProportion[eval] for eval in tabEval if eval >= beginningEval[int(numDir)]]

					ax0.plot(range(len(dataPlot)), dataPlot, color=palette[1], linestyle='--', linewidth=2, marker=None)

					# axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
					# axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])


					tabPlotTicks = []
					for eval in tabEval :
						# tabPlotTicks.append(eval)
						if args.beginningGen :
							if eval >= beginningEval[int(numDir)] :
								tabPlotTicks.append((eval - beginningEval[int(numDir)])/20)
						else :
							tabPlotTicks.append((eval - 30)/20)

					ticks = range(0, len(dataPlot), int(len(dataPlot)/2))
					if len(dataPlot) - 1 not in ticks :
						ticks.append(len(dataPlot) - 1)

					# tabPlotTicks[ticks[0]] = 0
					# tabPlotTicks[ticks[1]] = 20000
					# tabPlotTicks[ticks[2]] = 40000

					ax0.set_xticks(ticks)
					ax0.set_xticklabels([tabPlotTicks[x] for x in ticks])

					# ticks = range(0, len(dataPlot), int(len(dataPlot)/5))
					ax0.set_xlabel('Generation')
					ax0.set_xlim(0, len(dataPlot) - 1)
					# ax0.set_xlim(startIndex, len(dataPlot) - 1)

					ax0.set_ylabel('Value')
					ax0.set_ylim(0.0, 1.0)

					legend = plt.legend(['Genotype variance', 'Leadership ratio'], loc = 0, frameon=True)
					frame = legend.get_frame()
					frame.set_facecolor('0.9')
					frame.set_edgecolor('0.9')

					plt.savefig(os.path.join(outputDir, "distancePlusLeadershipRun" + str(numDir) + ".png"), bbox_inches = 'tight')
					plt.savefig(os.path.join(outputDir, "distancePlusLeadershipRun" + str(numDir) + ".svg"), bbox_inches = 'tight')
					# plt.show()
					plt.close()

				# print("Run " + str(numDir) + " : ")
				# X = [np.array(genotype) for genotype in hashGenotypes[tabEval[-1]]]
				# ks, logWks, logWkbs, sk = gap_statistic(X)
				# print("\tks = " + str(ks))
				# print("\tlogWks = " + str(logWkbs))
				# print("\tlogWkbs = " + str(logWkbs))
				# print("\tsk = " + str(sk))

				# # The optimal number of clusters is the smallest k such that gap(k) - (gap(k + 1) - sk+1) >= 0
				# nbClusters = None
				# for indk, k in enumerate(ks) :
				# 	if indk < len(ks) - 1 :
				# 		Gapk = logWkbs[indk] - logWks[indk]
				# 		Gapk2 = logWkbs[indk + 1] - logWks[indk + 1]

				# 		if Gapk - (Gapk2 - sk[indk + 1]) >= 0 :
				# 			nbClusters = k
				# 			break

				# print("Optimal number of clusters : " + str(nbClusters))

				# fig, ax0 = plt.subplots(ncols = 1, figsize = size)

				# plt.grid()

				# dataPlot = logWks
				# ax0.plot(range(len(logWks)), dataPlot, color=palette[0], linestyle='-', linewidth=2, marker=None)
				# plt.show()

					# if args.unique != -1 :
					# 	# Proportion Leadership unique run
					# 	fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)
					# 	# plt.axes(frameon=0)
					# 	plt.grid()

					# 	dataPlot = [hashProportion[eval] for eval in tabEval]
					# 	axe1.plot(range(len(dataPlot)), dataPlot, color=palette[0], linestyle='-', linewidth=2, marker=None)

					# 	# axe1.set_xticks(range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10)))
					# 	# axe1.set_xticklabels([tabPlotEvaluation[x] for x in range(0, len(tabPlotEvaluation), int(len(tabPlotEvaluation)/10))])

					# 	ticks = range(0, len(dataPlot), int(len(dataPlot)/5))
					# 	axe1.set_xticks(ticks)
					# 	axe1.set_xticklabels([tabPlotEvaluation[x] for x in ticks])

					# 	axe1.set_ylim(0.0, 1.0)

					# 	plt.savefig(outputDir + "/uniqueProportionRun" + str(args.unique) + ".png", bbox_inches = 'tight')
					# 	plt.savefig(outputDir + "/uniqueProportionRun" + str(args.unique) + ".svg", bbox_inches = 'tight')
					# 	# plt.show()
					# 	plt.close()


				# print("\t\t--> Dir" + str(numDir) + " : ")
				# listEval = sorted([eval for eval in hashDistance.keys() if hashDistance[eval] > 0.2])
				# print(listEval)


def Wk(mu, clusters):
    K = len(mu)
    return sum([np.linalg.norm(mu[i]-c)**2/(2*len(c)) \
               for i in range(K) for c in clusters[i]])
	
def gap_statistic(X):
    # Dispersion for real distribution
    ks = range(1,10)
    Wks = np.zeros(len(ks))
    Wkbs = np.zeros(len(ks))
    sk = np.zeros(len(ks))

    for indk, k in enumerate(ks):
        mu, clusters = find_centers(X, k)

        Wks[indk] = np.log(Wk(mu, clusters))
        # Create B reference datasets
        B = 10
        BWkbs = np.zeros(B)
        for i in range(B):
            Xb = []

            for n in range(len(X)):
            	curB = []

            	for value in range(len(X[0])) :
            		curB.append(random.uniform(0.0, 1.0))

            	Xb.append(curB)

            Xb = np.array(Xb)
            mu, clusters = find_centers(Xb,k)
            BWkbs[i] = np.log(Wk(mu, clusters))

        Wkbs[indk] = sum(BWkbs)/B
        sk[indk] = np.sqrt(sum((BWkbs-Wkbs[indk])**2)/B)

    sk = sk*np.sqrt(1+1/B)
    return(ks, Wks, Wkbs, sk)


def cluster_points(X, mu):
		clusters  = {}

		for x in X:
			distArrays = [(i[0], np.linalg.norm(x-mu[i[0]])) for i in enumerate(mu)]
			minValue = min(distArrays, key=lambda t:t[1])[1]
			listMins = [couple[0] for couple in distArrays if couple[1] == minValue]

			bestmukey = None
			# for minInd in listMins :
			# 	if minInd not in clusters.keys() :
			# 		bestmukey = minInd
			# 		break

			if bestmukey == None :
				bestmukey = listMins[0]
			try:
				clusters[bestmukey].append(x)
			except KeyError:
				clusters[bestmukey] = [x]

		# print(str(len(clusters)) + "/" + str(len(mu)))

    # for i in enumerate(mu) :
    # 	found = False
    # 	for x in clusters[i[0]] :
    # 		if np.array_equal(i[1], x) :
    # 			found = True
    # 			break

    # 	if not found :
    # 		print("yep")

    # 	if i[0] not in clusters.keys() :
    # 		print('mdr')
    # 		clusters[i[0]] = []

    # print(str(len(clusters)) + "/" + str(len(mu)))

		return clusters
 
def reevaluate_centers(mu, clusters):
    newmu = []
    keys = sorted(clusters.keys())
    for k in keys:
        newmu.append(np.mean(clusters[k], axis = 0))
    return newmu
 
def has_converged(mu, oldmu):
    return set([tuple(a) for a in mu]) == set([tuple(a) for a in oldmu])
 
def find_centers(X, K):

    # Initialize to K random centers
    # oldmu = random.sample(X, K)
    # mu = random.sample(X, K)
    oldmu = []
    mu = []

    for i in range(0, K) :
    	tmpOldMu = []
    	tmpMu = []

    	for j in range(0, len(X[0])) :
     		tmpOldMu.append(random.uniform(0.0, 1.0))
     		tmpMu.append(random.uniform(0.0, 1.0))

     	oldmu.append(tmpOldMu)
     	mu.append(tmpMu)

    clusters = {}
    firstTime = True
    # print('prout : ' + str(K) + "/" + str(len(X)) + "/" + str(len(oldmu)) + "/" + str(len(mu)))
    while firstTime or not has_converged(mu, oldmu):
        oldmu = mu
        # print('caca')

        # Assign all points in X to clusters
        clusters = cluster_points(X, mu)
        # print(str(len(clusters)) + "/" + str(len(mu)))

        # Reevaluate centers
        mu = reevaluate_centers(oldmu, clusters)

        if firstTime :
        	firstTime = False

    # print('mdr')
    # print(str(K) + "/" + str(len(mu)))
    return(mu, clusters)

if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('-f', '--file', help = "Genome file", default = "allgenomes.dat")
	parser.add_argument('-p', '--precision', help = "Evaluation precision", type = int, default = 1000)
	parser.add_argument('-o', '--output', help = "Output directory", default = "GraphsResults")
	parser.add_argument('-l', '--leadership', help = "Draw best leadership", action = "store_true", default = False)
	parser.add_argument('-b', '--beginningGen', help = "First generation from which we draw", default = False, action = 'store_true')
	parser.add_argument('-m', '--maximum', help = "Maximum evaluation", default = -1, type = int)
	# parser.add_argument('-g', '--generation', help = "Draw by generation", default = False, action = 'store_true')
	args = parser.parse_args()

	main(args)

#!/usr/bin/env python

import os
import path
import re
import argparse
import math
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import sys
import shutil
import random

import Tools

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
					listGenotypes = []
					for line in fileRead :
						s = regexp.search(line)

						if s :
							eval = int(s.group(1))

							if lastEval == None :
								lastEval = eval

							if eval > lastEval :
								if cumulEval >= args.precision :
									cumulEval = 0

								cumulEval += eval - lastEval
								lastEval = eval

							if cumulEval >= args.precision:
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


				sns.set()
				sns.set_style('white')
				sns.set_context('paper')
				palette = sns.color_palette("husl", 4)

				column_labels = range(0, len(hashSimilarities[tabEval[-1]]))
				row_labels = range(0, len(hashSimilarities[tabEval[-1]]))

				dpi = 96
				size = (1680/dpi, 1024/dpi)
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
				ax2.set_xticks(np.arange(dataHeat.shape[0])+0.5, minor=False)
				ax2.set_yticks(np.arange(dataHeat.shape[1])+0.5, minor=False)

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


# def Wk(mu, clusters):
#     K = len(mu)
#     return sum([np.linalg.norm(mu[i]-c)**2/(2*len(c)) \
#                for i in range(K) for c in clusters[i]])
	
# def bounding_box(X):
#     xmin, xmax = min(X,key=lambda a:a[0])[0], max(X,key=lambda a:a[0])[0]
#     ymin, ymax = min(X,key=lambda a:a[1])[1], max(X,key=lambda a:a[1])[1]
#     return (xmin,xmax), (ymin,ymax)
 
# def gap_statistic(X):
#     (xmin,xmax), (ymin,ymax) = bounding_box(X)
#     # Dispersion for real distribution
#     ks = range(1,10)
#     Wks = zeros(len(ks))
#     Wkbs = zeros(len(ks))
#     sk = zeros(len(ks))
#     for indk, k in enumerate(ks):
#         mu, clusters = find_centers(X,k)
#         Wks[indk] = np.log(Wk(mu, clusters))
#         # Create B reference datasets
#         B = 10
#         BWkbs = zeros(B)
#         for i in range(B):
#             Xb = []
#             for n in range(len(X)):
#                 Xb.append([random.uniform(xmin,xmax),
#                           random.uniform(ymin,ymax)])
#             Xb = np.array(Xb)
#             mu, clusters = find_centers(Xb,k)
#             BWkbs[i] = np.log(Wk(mu, clusters))
#         Wkbs[indk] = sum(BWkbs)/B
#         sk[indk] = np.sqrt(sum((BWkbs-Wkbs[indk])**2)/B)
#     sk = sk*np.sqrt(1+1/B)


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Results directory")
	parser.add_argument('-f', '--file', help = "Genome file", default = "allgenomes.dat")
	parser.add_argument('-p', '--precision', help = "Evaluation precision", type = int, default = 1000)
	parser.add_argument('-o', '--output', help = "Output directory", default = "GraphsResults")
	args = parser.parse_args()

	main(args)

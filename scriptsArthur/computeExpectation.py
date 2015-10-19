#!/usr/bin/env python

import argparse
import math
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable



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

	fig = plt.figure(figsize = size)	
	ax0 = plt.subplot2grid((4,3), (0,0))
	ax1 = plt.subplot2grid((4,3), (0,1))
	ax2 = plt.subplot2grid((4,3), (0,2))
	ax3 = plt.subplot2grid((4,3), (1,0))
	ax4 = plt.subplot2grid((4,3), (1,1))
	ax5 = plt.subplot2grid((4,3), (1,2))
	ax6 = plt.subplot2grid((4,3), (2,0))
	ax7 = plt.subplot2grid((4,3), (2,1))
	ax8 = plt.subplot2grid((4,3), (3,0))
	ax9 = plt.subplot2grid((4,3), (3,1))
	# ax0 = plt.subplot2grid((2,6), (0,0), colspan = 2)
	# ax1 = plt.subplot2grid((2,6), (0,2), colspan = 2)
	# ax2 = plt.subplot2grid((2,6), (0,4), colspan = 2)
	# ax3 = plt.subplot2grid((2,6), (1,0))
	# ax4 = plt.subplot2grid((2,6), (1,1))
	# ax5 = plt.subplot2grid((2,6), (1,2))
	# ax6 = plt.subplot2grid((2,6), (1,3))
	# ax7 = plt.subplot2grid((2,6), (1,4))
	# ax8 = plt.subplot2grid((2,6), (1,5))

	# -- Solo VS Follower --
	Yexpectation = []
	tabProportions = {}
	for proportion in Xproportions :
		tabProportions['Solo'] = proportion
		tabProportions['Follower'] = 1.0 - proportion
		Yexpectation.append(computeExpectation('Solo', tabProportions))

	ax0.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)
	ax0.set_xlabel('Proportion of solo')
	ax0.set_ylabel('Expected value')
	ax0.set_ylim(0.0, 5000.0)
	ax0.set_title('Expected value of solo individuals against followers')	


	# -- Follower VS Turner --
	Yexpectation = []
	tabProportions = {}
	for proportion in Xproportions :
		tabProportions['Follower'] = proportion
		tabProportions['Turner'] = 1.0 - proportion
		Yexpectation.append(computeExpectation('Follower', tabProportions))

	ax1.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)
	ax1.set_xlabel('Proportion of followers')
	ax1.set_ylabel('Expected value')
	ax1.set_ylim(0.0, 5000.0)
	ax1.set_title('Expected value of follower individuals against turners')	


	# -- Turner VS Solo --
	Yexpectation = []
	tabProportions = {}
	for proportion in Xproportions :
		tabProportions['Turner'] = proportion
		tabProportions['Solo'] = 1.0 - proportion
		Yexpectation.append(computeExpectation('Turner', tabProportions))

	ax2.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)
	ax2.set_xlabel('Proportion of turners')
	ax2.set_ylabel('Expected value')
	ax2.set_ylim(0.0, 5000.0)
	ax2.set_title('Expected value of turner individuals against solo')	

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

	# -- Follower VS Solo VS Turner --
	Zexpectation = hashExpectations['Follower']
	Zexpectation = np.array(Zexpectation)
	heatmap = ax3.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)

	ticks = range(0, len(Xproportions), len(Xproportions)/5)
	ax3.set_xlabel('Proportion of solo')
	ax3.set_xticks(ticks)
	ax3.set_xticklabels([Yproportions[t] for t in ticks])
	ax3.set_ylabel('Proportion of followers')
	ax3.set_yticks(ticks)
	ax3.set_yticklabels([Xproportions[t] for t in ticks])
	ax3.invert_yaxis()
	ax3.set_title('Expected value of follower individuals against solo and turners')



	# -- Solo VS Turner VS Follower --
	Zexpectation = hashExpectations['Solo']
	Zexpectation = np.array(Zexpectation)
	heatmap = ax4.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)

	ticks = range(0, len(Xproportions), len(Xproportions)/5)
	ax4.set_xlabel('Proportion of solo')
	ax4.set_xticks(ticks)
	ax4.set_xticklabels([Yproportions[t] for t in ticks])
	ax4.set_ylabel('Proportion of followers')
	ax4.set_yticks(ticks)
	ax4.set_yticklabels([Xproportions[t] for t in ticks])
	ax4.invert_yaxis()
	ax4.set_title('Expected value of solo individuals against turners and followers')



	# -- Turner VS Follower VS Solo --
	Zexpectation = hashExpectations['Turner']
	Zexpectation = np.array(Zexpectation)
	heatmap = ax5.imshow(Zexpectation, cmap = cm.jet, vmin = 0.0, vmax = 5000.0)

	ticks = range(0, len(Xproportions), len(Xproportions)/5)
	ax5.set_xlabel('Proportion of solo')
	ax5.set_xticks(ticks)
	ax5.set_xticklabels([Yproportions[t] for t in ticks])
	ax5.set_ylabel('Proportion of followers')
	ax5.set_yticks(ticks)
	ax5.set_yticklabels([Xproportions[t] for t in ticks])
	ax5.invert_yaxis()
	ax5.set_title('Expected value of turner individuals against followers and solo')
	# plt.colorbar(heatmap)

	divider = make_axes_locatable(ax5)
	cax = divider.append_axes("right", size="5%", pad=0.05)

	plt.colorbar(heatmap, cax=cax)


	# -- Expected values WRT Followers' proportion
	proportionSolo = 0.5
	Yexpectation = [line[int(len(hashExpectations['Follower'][0]) * proportionSolo)] for line in hashExpectations['Follower'][:]]
	ax6.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)

	Yexpectation = [line[int(len(hashExpectations['Solo'][0]) * proportionSolo)] for line in hashExpectations['Solo'][:]]
	ax6.plot(Xproportions, Yexpectation, color = palette[1], linestyle = '-', linewidth = 2, marker = None)

	Yexpectation = [line[int(len(hashExpectations['Turner'][0]) * proportionSolo)] for line in hashExpectations['Turner'][:]]
	ax6.plot(Xproportions, Yexpectation, color = palette[2], linestyle = '-', linewidth = 2, marker = None)

	ax6.set_xlabel('Proportion of followers')
	ax6.set_xlim(0.0, 0.5)
	ax6.invert_xaxis()
	ax6.set_ylabel('Expected value')
	ax6.set_ylim(0.0, 5000.0)
	ax6.set_title("Expected values with respect to followers' proportion with proportion solo = 0.5")


	# -- Expected values WRT Solo proportion
	proportionFollower = 0.5
	Yexpectation = hashExpectations['Follower'][int(len(hashExpectations['Follower'][0]) * proportionFollower)][:]
	ax7.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)

	Yexpectation = hashExpectations['Solo'][int(len(hashExpectations['Solo'][0]) * proportionFollower)][:]
	ax7.plot(Xproportions, Yexpectation, color = palette[1], linestyle = '-', linewidth = 2, marker = None)

	Yexpectation = hashExpectations['Turner'][int(len(hashExpectations['Turner'][0]) * proportionFollower)][:]
	ax7.plot(Xproportions, Yexpectation, color = palette[2], linestyle = '-', linewidth = 2, marker = None)

	ax7.set_xlabel('Proportion of solo')
	ax7.set_xlim(0.0, 0.5)
	ax7.invert_xaxis()
	ax7.set_ylabel('Expected value')
	ax7.set_ylim(0.0, 5000.0)
	ax7.set_title("Expected values with respect to solo proportion with proportion followers = 0.5")


	# -- Expected values WRT Followers' proportion
	proportionSolo = 0.0
	Yexpectation = [line[int(len(hashExpectations['Follower'][0]) * proportionSolo)] for line in hashExpectations['Follower'][:]]
	ax8.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)

	Yexpectation = [line[int(len(hashExpectations['Solo'][0]) * proportionSolo)] for line in hashExpectations['Solo'][:]]
	ax8.plot(Xproportions, Yexpectation, color = palette[1], linestyle = '-', linewidth = 2, marker = None)

	Yexpectation = [line[int(len(hashExpectations['Turner'][0]) * proportionSolo)] for line in hashExpectations['Turner'][:]]
	ax8.plot(Xproportions, Yexpectation, color = palette[2], linestyle = '-', linewidth = 2, marker = None)

	ax8.set_xlabel('Proportion of followers')
	ax8.set_xlim(0.0, 0.5)
	ax8.invert_xaxis()
	ax8.set_ylabel('Expected value')
	ax8.set_ylim(0.0, 5000.0)
	ax8.set_title("Expected values with respect to followers' proportion with proportion solo = 0.0")


	# -- Expected values WRT Solo proportion
	proportionFollower = 0.0
	Yexpectation = hashExpectations['Follower'][int(len(hashExpectations['Follower'][0]) * proportionFollower)][:]
	pl1 = ax9.plot(Xproportions, Yexpectation, color = palette[0], linestyle = '-', linewidth = 2, marker = None)

	Yexpectation = hashExpectations['Solo'][int(len(hashExpectations['Solo'][0]) * proportionFollower)][:]
	pl2 = ax9.plot(Xproportions, Yexpectation, color = palette[1], linestyle = '-', linewidth = 2, marker = None)

	Yexpectation = hashExpectations['Turner'][int(len(hashExpectations['Turner'][0]) * proportionFollower)][:]
	pl3 = ax9.plot(Xproportions, Yexpectation, color = palette[2], linestyle = '-', linewidth = 2, marker = None)

	ax9.set_xlabel('Proportion of solo')
	ax9.set_xlim(0.0, 0.5)
	ax9.invert_xaxis()
	ax9.set_ylabel('Expected value')
	ax9.set_ylim(0.0, 5000.0)
	ax9.set_title("Expected values with respect to solo proportion with proportion followers = 0.0")

	# handles, labels = ax9.get_legend_handles_labels()
	# ax9.legend()

	# legend = plt.legend([pl1, pl2, pl3], ['Follower', 'Solo', 'Turner'], frameon=True)
	# frame = legend.get_frame()
	# frame.set_facecolor('0.9')
	# frame.set_edgecolor('0.9')

	fig.tight_layout()
	plt.show()



if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	# parser.add_argument('file', help = "Genome file")
	parser.add_argument('-p', '--precision', help = "Precision", default = 0.01)
	args = parser.parse_args()

	main(args)
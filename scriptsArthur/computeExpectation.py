#!/usr/bin/env python

import argparse
import math
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np



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
	fig, (ax0, ax1, ax2) = plt.subplots(ncols=3, nrows=1 figsize = size)


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
	ax0.set_ylim(0.0, 7000.0)
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
	ax1.set_ylim(0.0, 7000.0)
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
	ax2.set_ylim(0.0, 7000.0)
	ax2.set_title('Expected value of turner individuals against solo')	


	plt.show()



if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	# parser.add_argument('file', help = "Genome file")
	parser.add_argument('-p', '--precision', help = "Precision", default = 0.01)
	args = parser.parse_args()

	main(args)
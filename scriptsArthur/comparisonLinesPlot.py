#!/usr/bin/env python

"""
Line plot + legend: names close to the corresponding lines
"""

########### IMPORTS AND BASE GLOBALS ########### {{{1

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
#import matplotlib.cm as cm
#import matplotlib.ticker as plticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from operator import itemgetter
import seaborn as sns

# }}}


########### PLOT FUNCTIONS ########### {{{1
def createComparisonLinesPlot(data, captions, fig):
	"""
		data: 2D array-like of datas for each entry
		captions: array-like of the names of every entry
		return: created axes
	"""
	sns.set_style("whitegrid")

	# Create color + line styles
	palette = sns.color_palette("Set2", 5)
	linestyles = ('-', '--', '-.', ':')
	styles = [(color, linestyle) for linestyle in linestyles for color in palette]

	ax = fig.add_subplot(111)
	dataLines = []
	for d, i in zip(data.T, range(data.shape[1])):
		l = ax.plot(d, c = styles[i][0], ls = styles[i][1])
		dataLines.append(l[0])
	assert dataLines

	lastVals = np.array(data)[-1]
	# Sort the captions
	sortedVals = zip(*(sorted(zip(lastVals, range(data.shape[1])), key = itemgetter(0))))
	sortedLastVals = sortedVals[0]
	sortedIndexes = sortedVals[1]

	# Create new axes on the right containing captions
	divider = make_axes_locatable(ax)
	rax = divider.append_axes("right", size="5%", pad=0.00)
	#rax = inset_axes(ax, width="5%", height="100%", bbox_transform=ax.transAxes,
	#		bbox_to_anchor=(0.025, -0.1, 1.175, 1.00), loc=1)

	# Add captions text on axis, and lines
	yCaptionsCoords = np.linspace(0., 1., len(sortedIndexes))
	connectionLinesCoords = []
	for y, i in zip(yCaptionsCoords, sortedIndexes):
		cap = captions[i]
		lastVal = lastVals[i]
		color = styles[i][0]
		ls = styles[i][1]
		rax.text(3.00, y, cap,
				horizontalalignment='center',
				verticalalignment='center',
				transform = rax.transAxes)

		# Add lines
		normalizedLastVal = float(lastVal) / float(ax.get_ylim()[1])
		normalizedY = float(y) * float(ax.get_ylim()[1])
		rax.plot([lastVal, normalizedY], color=color, ls=ls)
		#print lastVal, normalizedY, cap

	rax.set_axis_off()
	rax.set_ylim(ax.get_ylim())

# }}}


########### TESTS + MAIN FUNCTIONS ########### {{{1
if __name__ == "__main__":
	# Parse command line parameters
	from optparse import OptionParser
	usage = "%prog [options]"
	parser = OptionParser(usage=usage)
	parser.add_option("-f", "--nbFunctions", dest="nbFunctions", default=10,
			help="Nb test functions")
	parser.add_option("-e", "--nbEvals", dest="nbEvals", default=1000,
			help="Nb of evaluations (x-axis)")
	parser.add_option("-o", "--outputFileName", dest="outputFileName", default="out.pdf",
			help="Filename of generated pdf plot")
	options, cmdLineArgs = parser.parse_args()
	nbFunctions = options.nbFunctions
	nbEvals = options.nbEvals

	# Generate sample data
	data = np.array([np.cumsum(np.random.lognormal(0.0, 3.0, size=[nbEvals])) for _ in range(nbFunctions)]).T
	# Create captions
	captions = ["Function " + str(i) for i in range(nbEvals)]
	# Plot data
	fig = plt.figure()
	ax = createComparisonLinesPlot(data, captions, fig)
	# Save figure
	fig.savefig(options.outputFileName, bbox_inches='tight')
	plt.close(fig)

# }}}

# MODELINE	"{{{1
# vim:noexpandtab:softtabstop=4:shiftwidth=4:fileencoding=utf-8
# vim:foldmethod=marker

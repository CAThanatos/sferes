#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import lines
import matplotlib.cm as cm
from matplotlib import animation
import seaborn as sns
import numpy as np
import argparse
import re
import os
import math

import makeData
import Tools

colorHaresSolo = 'lime'
colorHaresDuo = 'green'
colorErrorHares = 'black'
alphaHares = 1
colorBStagsSolo = 'magenta'
colorBStagsDuo = 'purple'
colorErrorBStags = 'black'
alphaBStags = 1
colorSStagsSolo = 'cyan'
colorSStagsDuo = 'steelblue'
colorErrorSStags = 'black'
alphaSStags = 1
colorTotal = 'grey'
colorErrorTotal = 'black'
alphaTotal = 1

sns.set()
sns.set_style('white')
sns.set_context('paper')

matplotlib.rcParams['font.size'] = 15
matplotlib.rcParams['font.weight'] = 'bold'
matplotlib.rcParams['axes.labelsize'] = 15
matplotlib.rcParams['axes.labelweight'] = 'bold'
matplotlib.rcParams['xtick.labelsize'] = 15
matplotlib.rcParams['ytick.labelsize'] = 15
matplotlib.rcParams['legend.fontsize'] = 15

dpi = 96
size = (1280/dpi, 1024/dpi)


# --- BARS LEADERSHIP ---
fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

width = 0.3
tabExpe = ["Control reward 100", "Experiment reward 100", "Control reward 250", "Experiment reward 250"]
tabNbRunHares = [11, 8, 9, 3]
tabNbRunStags = [0, 3, 2, 8]

barNbRunHares = axe1.bar(np.add(range(len(tabNbRunHares)), width), tabNbRunHares, width = width, color = 'lime', alpha = 0.5)
barNbRunStags = axe1.bar(np.add(range(len(tabNbRunStags)), width), tabNbRunStags, bottom = tabNbRunHares, width = width, color = 'magenta', alpha = 0.5)

axe1.set_xticks(np.add(np.arange(len(tabExpe)), 3*width/2))
axe1.set_xticklabels(tabExpe)
axe1.set_xlim(0, len(tabExpe) + width)
axe1.set_xlabel('Setting')

axe1.set_ylabel('Number of simulations')

# plt.legend([barNbRunHares, barNbRunStags], ['Hares', 'Stags'], frameon = True)

plt.savefig("./figureBarsLeadership.png", bbox_inches = 'tight')


# --- BARS SIMILARITY ---
fig, axe1 = plt.subplots(nrows = 1, ncols = 1, figsize = size)

width = 0.3
tabExpe = ["Fitness only", "Fitness + Diversity", "Fitness + Sim. Sensors", "Fitness + Sim. Activity"]
tabNbRunHares = [11, 10, 7, 5]
tabNbRunStags = [0, 1, 4, 6]

barNbRunHares = axe1.bar(np.add(range(len(tabNbRunHares)), width), tabNbRunHares, width = width, color = 'lime', alpha = 0.5)
barNbRunStags = axe1.bar(np.add(range(len(tabNbRunStags)), width), tabNbRunStags, bottom = tabNbRunHares, width = width, color = 'magenta', alpha = 0.5)

axe1.set_xticks(np.add(np.arange(len(tabExpe)), 3*width/2))
axe1.set_xticklabels(tabExpe)
axe1.set_xlim(0, len(tabExpe) + width)
axe1.set_xlabel('Setting')

axe1.set_ylabel('Number of simulations')

# plt.legend([barNbRunHares, barNbRunStags], ['Hares', 'Stags'], frameon = True)

plt.savefig("./figureBarsDiversity.png", bbox_inches = 'tight')

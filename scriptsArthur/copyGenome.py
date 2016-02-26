#!/usr/bin/env python

import re
import os
import sys
import shutil

genomeFile = sys.argv[1]
dirOut = sys.argv[2]

regexpDir = re.compile("^Dir\d+$")

listSubDir = [os.path.join(dirOut, subDir) for subDir in os.listdir(dirOut) if regexpDir.search(subDir)]
for subDir in listSubDir :
	print("Copy " + genomeFile + " to " + os.path.join(subDir, "genome.dat"))
	shutil.copyfile(genomeFile, os.path.join(subDir, "genome.dat"))
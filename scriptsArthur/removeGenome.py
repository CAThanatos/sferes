#!/usr/bin/env python

import re
import os
import sys

dirRm = sys.argv[1]

regexpSubDir = re.compile(r"^Dir\d+$")
listSubDir = [os.path.join(dirRm, subDir) for subDir in os.listdir(dirRm) if regexpSubDir.search(subDir)]

for subDir in listSubDir :
	if os.path.isfile(os.path.join(subDir, "genome.dat")) :
		print("Removing " + os.path.join(subDir, "genome.dat"))
		os.remove(os.path.join(subDir, "genome.dat"))
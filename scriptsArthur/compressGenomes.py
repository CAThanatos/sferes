#!/usr/bin/env python

import os
import re
import argparse
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', help = "Results directory", default = ".")
args = parser.parse_args()

regexp = re.compile(r"\.grid5000\.fr_")

listDir = [os.path.join(args.directory, d) for d in os.listdir(args.directory) if os.path.isdir(os.path.join(args.directory, d)) and regexp.search(d)]

for curDir in listDir :
	shutil.make_archive(os.path.join(curDir, "allgenomes"), 'gztar', os.path.join(curDir, "allgenomes.dat"))
#!/usr/bin/env python

import os
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('directory', help = "Results directory")
parser.add_argument('-f', '--first', help = "First evaluation from which to begin")
args = parser.parse_args()

subDirs = [os.path.join(args.directory, d) for d in os.listdir(args.directory) if (os.path.isdir(args.directory + "/" + d) and re.search(r"^Dir", d))]
for subDir in subDirs :
	listFiles = [os.path.join(subDir, f) for f in os.listdir(subDir) if (os.path.isfile(subDir + "/" + f) and re.search(r"\.dat$", f))]

	for fileDat in listFiles :
		lines = None
		with open(fileDat, "r") as fileRead :
			fileRead = fileRead.readlines()
			lines = [line.rstrip("\n") for line in fileRead]

		newFile = re.sub(r"\.dat$", ".dat2", fileDat)

		with open(newFile, "w") as fileOut :
			for line in lines :
				m = re.search(r"^(\d+),", line)
				if m :
					evaluation = int(m.group(1))

					if evaluation >= int(args.first) :
						fileOut.write(line + "\n")
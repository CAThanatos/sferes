#!/usr/bin/env python
# -*- coding: utf8 -*-


import os
import re
import argparse
import shutil
import time

parser = argparse.ArgumentParser()
parser.add_argument('directory', help = "Experiment's directory")
parser.add_argument('-f', '--file', help = "Exp to continue file", default='expToContinu.txt')
parser.add_argument('-r', '--remove', help = "Remove the previous output directory", default=False, action="store_true")
parser.add_argument('-g', '--genome', help = "Copy genome file", default=False, action="store_true")
args = parser.parse_args()

directory = args.directory
fileToContinu = args.file

lastGenPopDir = "./lastGenPop"
templateFile = "TemplateExp.exp"
date = time.strftime("%Y_%m_%d")

if os.path.isdir(lastGenPopDir) :
	if args.remove :
		shutil.rmtree(lastGenPopDir)
		os.mkdir(lastGenPopDir)
else :
	os.mkdir(lastGenPopDir)

stringOut = ""

if os.path.isfile(templateFile) :
	if not args.remove :
		with open(templateFile, "r") as fileRead :
			fileRead = fileRead.readlines()

			for line in fileRead :
				stringOut += line


# We read the file of experiments to continue
dicExp = {}
with open(fileToContinu, "r") as fileRead :
	fileRead = fileRead.readlines()
	lines = [line.rstrip('\n').split('\t') for line in fileRead if not line.startswith("#")]

	dicExp = {}
	dicRuns = {}
	for line in lines :
		if len(line) > 1 :
			dicExp[line[0]] = line[1]

			if len(line) > 2 :
				runs = line[2].split(',')
				dicRuns[line[0]] = [int(run) for run in runs]


# We scan across all the directories
reFileGen = re.compile(r"^popGen_(\d+)$")
reDir = re.compile(r"^Dir(\d+)$")
reExp = re.compile(r"build/default/exp/([^/]+)/")
listDirs = [dir for dir in os.listdir(directory) if os.path.isdir(directory)]
nbRuns = 0
for dir in listDirs :
	if dicExp.has_key(dir) :
		listSubDirs = [subDir for subDir in os.listdir(os.path.join(directory, dir)) if (os.path.isdir(os.path.join(directory, dir)) and reDir.search(subDir))]

		# And across all the results directories
		for subDir in listSubDirs :
			if not dicRuns.has_key(dir) or (int(reDir.search(subDir).group(1)) in dicRuns[dir]) :
				curDir = os.path.join(os.path.join(directory, dir), subDir)
				listFilesGen = [fileGen for fileGen in os.listdir(curDir) if (os.path.isfile(os.path.join(curDir, fileGen)) and reFileGen.search(fileGen))]

				# We then look for the file corresponding to the last generation
				max = 0
				fileGenMax = None
				for fileGen in listFilesGen :
					r = reFileGen.search(fileGen)
					gen = int(r.group(1))

					if gen >= max :
						max = gen
						fileGenMax = fileGen

				# The file is copied to the output directory
				dirOut = os.path.abspath(os.path.join(lastGenPopDir, os.path.join(dir, subDir)))
				os.makedirs(dirOut)
				shutil.copy(os.path.join(curDir, fileGenMax), dirOut)

				if args.genome and os.path.isfile(os.path.join(curDir, 'genome.dat')) :
					shutil.copy(os.path.join(curDir, 'genome.dat'), dirOut)

				# And we then update the string which will be written in the experiment file
				r = reDir.search(subDir)
				e = reExp.search(dicExp[dir])
				stringOut += "[" + dir.replace("_", " ") + " DIR" + str(r.group(1)) + "]\n"
				stringOut += "nb_runs:1\n"
				stringOut += "exec:" + dicExp[dir] + " -c " + os.path.join(dirOut, fileGenMax) + "\n"
				stringOut += "res:ResultatsG5K/" + date + "/" + str(e.group(1)) + "/" + dir + "/" + subDir + "\n"
				stringOut += "build:./sferes2-0.99/waf --exp " + str(e.group(1)) + "\n\n"
				# stringOut += "res:ResultatsG5K/" + date + "/StagHuntExp3-Duo/" + dir + "/" + subDir + "\n"
				# stringOut += "build:./sferes2-0.99/waf --exp StagHuntExp3-Duo\n\n"

				nbRuns += 1

		print("L'expérience " + dir + " sera continuée")
	else :
		print("L'expérience " + dir + " ne sera pas continuée")

print("\t-> " + str(nbRuns) + " runs seront continués")

with open(templateFile, "w") as fileWrite :
	fileWrite.write(stringOut)

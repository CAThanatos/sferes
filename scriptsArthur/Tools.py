#!/usr/bin/env python

import sys
import os
import subprocess
import re
import shutil


def searchTopDirectoriesPrefix(directory, prefix) :
	if os.path.isdir(directory) :
		listSubDirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

		found = False
		regexp = re.compile(r"^" + prefix)
		for subDir in listSubDirs :
			if regexp.search(subDir) :
				found = True
				break

		listDirectories = []
		if found :
			listDirectories = [directory]
		else :
			for subDir in listSubDirs :
				listDirectories += searchTopDirectoriesPrefix(os.path.join(directory, subDir), prefix)

		return listDirectories


def searchTopDirectories(directory) :
	if os.path.isdir(directory) :
		listDirs = [os.path.join(directory, d) for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

		found = False
		for curDir in listDirs:
			listFiles = [f for f in os.listdir(curDir)]

			regexp = re.compile(r"\.dat$")
			for curFile in listFiles :
				if os.path.isfile(os.path.join(curDir, curFile)) and regexp.search(curFile) :
					found = True
					break

			if found :
				break

		listDirectories = []
		if found :
			listDirectories = [directory]
		else :
			for subDir in listDirs :
				listDirectories += searchTopDirectories(subDir)

		return listDirectories



def getDirectories(directory, fullPath = False, regexp = None) :
	if regexp == None :
		return [os.path.join(directory, dir) if fullPath else dir for dir in os.listdir(directory) if os.path.isdir(os.path.join(directory, dir))]
	else :
		return [os.path.join(directory, dir) if fullPath else dir for dir in os.listdir(directory) if os.path.isdir(os.path.join(directory, dir)) and regexp.search(dir)]


def makeVideo(dossier, type = ".png") :
	if os.path.isdir(dossier) :
		regexp = re.compile(r"^paretoEval\d+.png$")

		def cmpFunction(x, y) :
			reg = re.compile(r"paretoEval(\d+).png$")
			m = reg.search(x)

			numX = 0
			numY = 0
			if m :
				numX = int(m.group(1))
			m = reg.search(y)
			if m :
				numY = int(m.group(1))

			return cmp(numX, numY)

		listImages = [os.path.join(dossier, image) for image in os.listdir(dossier) if regexp.search(image)]
		listImages.sort(cmpFunction)

		cpt = 0
		for image in listImages :
			if cpt < 10 :
				imageId = "0" + str(cpt)
			else :
				imageId = str(cpt)
			shutil.copyfile(image, os.path.join(dossier, "paretoImgTmp" + imageId + ".png"))
			cpt += 1

		os.chdir(dossier)
		subprocess.call("avconv -f image2 -r 1 -i paretoImgTmp%02d.png -r 12 videoParetoFrontier.mp4", shell = True)
		subprocess.call("rm paretoImgTmp*", shell = True)





if __name__ == "__main__" :
	print(searchTopDirectories(sys.argv[1]))
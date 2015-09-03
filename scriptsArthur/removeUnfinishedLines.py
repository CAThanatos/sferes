#!/usr/bin/env python

import os
import argparse
import re

import Tools


def main(args) :
	listTopDirectories = Tools.searchTopDirectories(args.directory)

	regFile = re.compile(r"^bestfit\.dat$")
	regLine = re.compile(r"^(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+)$")
	regSubDir = re.compile(r"^Dir(\d+)$")
	for topDir in listTopDirectories :

		listSubDir = [subDir for subDir in os.listdir(topDir) if regSubDir.search(subDir)]

		for subDir in listSubDir :

			listFiles = [file for file in os.listdir(os.path.join(topDir, subDir))]

			for curFile in listFiles :
				if regFile.search(curFile) :

					content = None
					with open(os.path.join(os.path.join(topDir, subDir), curFile), 'r') as fileRead :
						fileRead = fileRead.readlines()

						lastLine = fileRead[-1].rstrip('\n')
						if regLine.search(lastLine) :
							break
						else :
							content = fileRead[:-1]

					# with open(os.path.join(os.path.join(args.directory, subDir), curFile), 'w') as fileWrite :
					with open(os.path.join(os.path.join(topDir, subDir), curFile), 'w') as fileWrite :
						# print(os.path.join(os.path.join(topDir, subDir), "bestfit2.dat"))

						cpt = 0
						while cpt < len(content) :
							line = content[cpt].rstrip('\n')

							if cpt < (len(content) - 1) :
								fileWrite.write(line + "\n")
							else :
								fileWrite.write(line)

							cpt += 1


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', help = "Directory")
	args = parser.parse_args()

	main(args)
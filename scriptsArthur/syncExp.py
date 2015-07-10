#!/usr/bin/env python

import os
import subprocess
import re
import argparse


PATH_FILE_OUT = "./TemplateExp.tmp"

def main(args) :
	fileExp = args.fileExp
	if os.path.isfile(fileExp) :
		with open(fileExp, 'r') as fileIn :
			lines = [line.rstrip('\n') for line in fileIn.readlines()]

			curSite = None
			curExp = []
			regExpSite = re.compile(r"^\[\[(.*)\]\]$")
			for line in lines :
				s = regExpSite.search(line)
				if s :
					site = s.group(1)

					if curSite != None :
						with open(PATH_FILE_OUT, 'w') as fileOut :
							for line in curExp :
								fileOut.write(line + "\n")
							curExp = []

						proc = subprocess.Popen(['scp', PATH_FILE_OUT, curSite + ".g5k:./StagHuntExp3.exp"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
						proc.wait()

					curSite = site.lower()
				else :
					if curSite :
						curExp.append(line)

			if curSite and curExp :
				with open(PATH_FILE_OUT, 'w') as fileOut :
					for line in curExp :
						fileOut.write(line + "\n")
					curExp = []

				proc = subprocess.Popen(['scp', PATH_FILE_OUT, curSite + ".g5k:./StagHuntExp3.exp"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
				proc.wait()


	if os.path.isfile(PATH_FILE_OUT) :
		os.remove(PATH_FILE_OUT)
						



if __name__ == '__main__' :
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--fileExp', help = "File experiment", default='TemplateExp.exp')
	args = parser.parse_args()

	main(args)

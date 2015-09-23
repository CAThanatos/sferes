#!/usr/bin/env python

import os
import argparse
import re
import time
import shutil
import sys


def main(args) :
	regExp = re.compile(r"^\[(.*)\]$")
	regLine = re.compile(r"^([^:]+):(.*)$")

	if os.path.isfile(args.file) :
		with open(args.file, 'r') as fileRead :
			fileRead = fileRead.readlines()

			curExp = None
			for line in fileRead :
				line = line.rstrip('\n')

				s = regExp.search(line)
				if s :
					if curExp != None :
						if os.path.isdir(os.path.join('./res', curExp['res'])) :
							shutil.rmtree(os.path.join('./res', curExp['res']))

						os.makedirs(os.path.join('./res', curExp['res']))
						tmpFile = "./submitTmp.sh"

						with open(tmpFile, 'w') as fileWrite :
							fileWrite.write('#! /bin/sh\n')
							fileWrite.write('#PBS -N ' + curExp['name'].replace(' ', '_') + '\n')
							fileWrite.write('#PBS -o test_job.out\n')
							fileWrite.write('#PBS -b test_job.err\n')
							fileWrite.write('#PBS -M arthur.bernard1204@gmail.com\n')
							fileWrite.write('#PBS -l walltime=11:59:00\n')
							fileWrite.write('#PBS -d ' + os.path.join('./res', curExp['res']) + '\n')
							fileWrite.write(os.path.join('/home/abernard/', curExp['exec']) + '\n')

						for i in range(0, int(curExp['nb_runs'])) :
							os.system('qsub ' + tmpFile)
							time.sleep(1)
					else :
						curExp = {}


					curExp['name'] = s.group(1)
				else :
					s = regLine.search(line)

					if s :
						att = s.group(1)
						value = s.group(2)
						curExp[att] = value

			if curExp != None :
				if os.path.isdir(os.path.join('./res', curExp['res'])) :
					shutil.rmtree(os.path.join('./res', curExp['res']))

				os.makedirs(os.path.join('./res', curExp['res']))
				tmpFile = "./submitTmp.sh"

				with open(tmpFile, 'w') as fileWrite :
					fileWrite.write('#! /bin/sh\n')
					fileWrite.write('#PBS -N ' + curExp['name'].replace(' ', '_') + '\n')
					fileWrite.write('#PBS -o test_job.out\n')
					fileWrite.write('#PBS -b test_job.err\n')
					fileWrite.write('#PBS -M arthur.bernard1204@gmail.com\n')
					fileWrite.write('#PBS -l walltime=11:59:00\n')
					fileWrite.write('#PBS -d ' + os.path.join('./res', curExp['res']) + '\n')
					fileWrite.write(os.path.join('/home/abernard/', curExp['exec']) + '\n')

				for i in range(0, int(curExp['nb_runs'])) :
					os.system('qsub ' + tmpFile)
					time.sleep(1)


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help = "Exp file", default='TemplateExp.exp')
	args = parser.parse_args()

	main(args)
#!/usr/bin/env python

import os
import re
import sys


regexp = re.compile(r"^(\d+),")
if os.path.isdir(sys.argv[1]) :
	# bestFitDir = os.path.join(sys.argv[1], "BestFit")
	bestFitDir = os.path.join(sys.argv[1], "BestLeadership")

	if os.path.isdir(bestFitDir) :
		# listFiles = [os.path.join(bestFitDir, file) for file in os.listdir(bestFitDir) if re.search(r"^bestfit", file)]
		listFiles = [os.path.join(bestFitDir, file) for file in os.listdir(bestFitDir) if re.search(r"^bestleadership", file)]

		for file in listFiles :
			with open(file, "r") as fileRead :
				fileRead = fileRead.readlines()

				lastEval = None
				for line in fileRead :
					s = regexp.search(line)

					if s :
						eval = int(s.group(1))

						if lastEval == None :
							lastEval = 10
						else :
							diff = eval - lastEval

							if diff != 20 :
								print(file)
								print("\t -> " + str(lastEval) + " - " + str(eval))
								break
							else :
								lastEval = eval
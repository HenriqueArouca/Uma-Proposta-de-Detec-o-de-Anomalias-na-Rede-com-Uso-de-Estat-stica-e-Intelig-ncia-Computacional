#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from statisticalAnalyzes import *
import pandas as pd

class normBib(object):

	def rescale(self, fileCSV, ignoreColList):
		sta       = statisticAnalyzes(fileCSV)

		inputFile = pd.read_csv(fileCSV,sep="\\t|,|;|:| ", engine='python')	
		header    = list(inputFile.columns)

		for i in ignoreColList:
			for j in header:
				if j.find(i) != -1:
					header.remove(j)	

		for i in header:
			for j in range(len(inputFile)):
				amp = float(inputFile[i].max() - inputFile[i].min())
				
				if amp != 0.0:
					inputFile.loc[j, i] = float(inputFile.loc[j, i]) / amp  # P = X / max(x) - min(x)
				else:	
					inputFile.loc[j, i] = 0.00000

		name, ext = str(fileCSV).split('.')
		name     += '_rescale' + '.' + ext
		inputFile.to_csv(name, index=False)

		return inputFile
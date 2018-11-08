#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

import pandas as pd

class statisticAnalyzes(object):

	def __init__(self, fileCSV):
		#loads the dataframe for the analyzes
		self.df = pd.read_csv(fileCSV)

	def __init__(self, dataframe):
		self.df = dataframe	

	def min(self, column, descritionOn):
		if descritionOn:
			return 'Min: ' + str(self.df[column].min())
		else:	
			return self.df[column].min()

	def max(self, column, descritionOn):
		if descritionOn:
			return 'Max: ' + str(self.df[column].max())
		else:	
			return self.df[column].max()		

	def amplitude(self, column, descritionOn):
		if descritionOn:
			return 'Amp: ' + str(self.df[column].max() - self.df[column].min())
		else:
			return self.df[column].max() - self.df[column].min()

	def mean(self, column, descritionOn):
		if descritionOn:
			return 'Mean: ' + str(self.df[column].mean())
		else:
			return self.df[column].mean()	

	def sd(self, column, descritionOn):
		if descritionOn:
			return 'SD: ' + str(self.df[column].std())
		else:
			return self.df[column].std()

	def cv(self, column, descritionOn):
		if descritionOn:
			if self.mean(column, False) != 0.0:
				return 'CV: ' + str(self.sd(column, False) / self.mean(column, False))
			else:
				return 'CV: 0.0'
		else:
			if self.mean(column, False) != 0.0:
				return self.sd(column, False) / self.mean(column, False)
			else:
				return 0.0	

	def median(self, column, descritionOn):
		if descritionOn:
			return 'Median: ' +str(self.df[column].median())	
		else:
			return self.df[column].median()

	def floatingAvg(self, column, descritionOn):
		if descritionOn:
			for i in self.df[column]:
				pass		

	def mode(self, column, descritionOn):
		if descritionOn:
			return 'Mode: ' + str(self.df[column].mode())
		else:
			return self.df[column].mode()	

	def variance(self, column, descritionOn):
		if descritionOn:
			return 'Var: ' + str(self.df[column].var())

		else:
			return self.df[column].var()

	def acuracy(self, testCol, respFile, respCol, descritionOn):
		count = 0
		resp  = pd.read_csv(respFile)
		resp  = resp.loc[respCol].values
		s     = self.df[testCol].values

		for i in len(self.df[testCol]):
			if resp[i] == s[i]:
				count += 1
		
		if descritionOn:
			return 'CV: ' + str(count/len(self.df[testCol]))
		else:
			return count/len(self.df[testCol])	

	def countTypesAnomalies(self,column):	
		return dict(self.df[column].value_counts())

	#Method that account for types of anomalies and have output as a disctionary

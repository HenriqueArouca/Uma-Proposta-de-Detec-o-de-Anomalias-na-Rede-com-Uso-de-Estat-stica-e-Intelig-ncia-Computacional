#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from sklearn.ensemble import RandomForestClassifier 
from matplotlib import pyplot as plt
import pandas as pd
import pickle
import sys
import os
import subprocess
from normBib import *
#import time


class RandomForestIDS(object):
    #A class that runs the random forest algorithm to identify network anomalies in data sets

    __train            = None
    __test             = None
    __output           = None
    
    def __init__(self):
        self.output = ''

        if sys.argv[1]   == '-t': # <-t> to just train the classifier s
            self.train  = pd.read_csv(sys.argv[2],sep="\\t|,|;|:| ", engine='python')

            self.runRFAD(sys.argv[1])

        elif sys.argv[1] == '-u': # <-u> to use the classifier in a test 
            norm = normBib()

            self.backupTest = pd.read_csv(sys.argv[2],sep="\\t|,|;|:| ", engine='python')
            self.test       = norm.rescale(sys.argv[2],['"timestamp"'])
            
            self.nameInFig, trash = str(sys.argv[2]).split('.') 
            
            self.output = sys.argv[3]

            prediction = self.runRFAD(sys.argv[1])

            self.createPlotsImages(prediction)
            self.dataLogHTMLRescale()
            self.createPlotsImagesOri(prediction)
            self.dataLogHTMLOrgirnal()

        elif sys.argv[1] == '-b':
            self.train      = pd.read_csv(sys.argv[2],sep="\\t|,|;|:| ", engine='python')  
            self.backupTest = pd.read_csv(sys.argv[3],sep="\\t|,|;|:| ", engine='python')
            self.test       = pd.read_csv(sys.argv[3],sep="\\t|,|;|:| ", engine='python')

            self.runRFAD(sys.argv[1])

            prediction = self.runRFAD(sys.argv[1])

            self.createPlotsImages(prediction)
            self.dataLogHTMLRescale()
            self.createPlotsImagesOri(prediction)
            self.dataLogHTMLOrgirnal()

    def runRFAD(self, typeOf):
        if typeOf == '-t':
            featureColsList = []

            for i in list(self.train.columns):
                if i.find('timestamp')  != -1:
                    continue
                elif i.find('Class') != -1:
                    continue
                elif i.find('Anomalous') != -1:
                    targeColName = i.strip()
                    continue       
                else:
                    featureColsList.append(i)

            dfTrain = pd.DataFrame(self.train, columns=featureColsList) 

            x = dfTrain                                    # x is the data training with the feature columns selected   
            y = self.train.loc[:,targeColName]              # Selected column to be a target(y) in RF algorithm

            classifier = RandomForestClassifier(n_estimators=10, warm_start=True, criterion='gini')
            classifier.fit(x, y)

            self.writePickleFile(classifier)

        elif typeOf == '-u':
            temp = list(self.test.columns)

            featureColsTest = []

            for i in temp:              
                if i.find('timestamp') != -1:
                    continue

                elif i.find('Class') != -1:
                    continue

                elif i.find('Anomalous') != -1:
                    continue

                elif i.find('Prediction') != -1:
                    continue    

                else:
                    featureColsTest.append(i)


            dftest  = pd.DataFrame(self.test, columns=featureColsTest) # testX are the data to be classify

            self.outputFile              = self.test
            self.outputFile['Anomalous'] = 0

            tOut, err = subprocess.Popen("ls *.pickle", stdout=subprocess.PIPE, shell=True).communicate()
            out = tOut.splitlines()  

            p = subprocess.Popen("ls *.pickle | wc -l", stdout=subprocess.PIPE, shell=True)
            cou, err = p.communicate()           

            out.remove('trainigSetFileNames.pickle')
            out.remove('useSetFileNames.pickle')

            countAnom = (float(cou)-2) * 0.5
            finalPred = []
            count     = []

            for i in range(len(dftest)):
                count.append(0)

            for i in out:

                pickle_in  = open (i,'rb')
                classifier = pickle.load(pickle_in)
                                   
                tPred = classifier.predict(dftest) # Prediction 

                tempList = list(tPred)

                for i in range(len(dftest)):                    
                    temp     = count[i] + tempList[i]
                    count[i] = temp 

            for i in range(len(count)):
                if count[i] > countAnom : 
                    self.outputFile.loc[i,'Anomalous'] = 1
                    finalPred.append(1)

                else:
                    self.outputFile.loc[i,'Anomalous'] = 0
                    finalPred.append(0)        

            self.outputFile.to_csv(self.output,index=False) 

            return finalPred
            

        # Function that arrange the variables with the respective data and cals the random forest algorithm
            # Param 0 : self

    def writePickleFile(self, objectToPick):
        name = 'RFAD_Pickle' + str(sys.argv[2]) + '.pickle'
        with open (name,'wb') as file:
            pickle.dump(objectToPick, file)

    def createPlotsImages(self, objectToPlot): 
        xColumn = ''
        tempJ   = ''
        count   = 0
        header  =  list(self.test.columns)

        for i in header:
            if i.find('timestamp') != -1:
                xColumn = i
                header.remove(i) 

            if i.find('Anomalous') != -1:
                header.remove(i)             

        x          = self.test[xColumn]
        yAnomalous = []

        for j in header:
            for i in range(len(self.test)):

                if objectToPlot[i] == 1:
                    yAnomalous.append(self.test[j][i])

                else:
                    yAnomalous.append(-1) 

            tempJ   = j.replace('"""', '') + '/ max_' + j.replace('"""', '')  
            title   = 'timestamp X ' + tempJ
            nameFig = self.nameInFig + '_Graph_' + 'RF_timestamp_X_' + j.replace('"""', '').replace('%','').replace('"','')

            fig,ax = plt.subplots(figsize=(12,6))

            y = self.test[j]

            data  = ax.plot(x, y, label=title, color='orange',linewidth=0.7)

            ver = 0
            for i in range(len(yAnomalous)):
                if yAnomalous[i] != -1:
                    xseg = [x[i-1],x[i]]
                    yseg = [y[i-1],y[i]]
                    AnoLine  = ax.plot(xseg, yseg , label='Lines Considered Anomalous' if ver == 0 else "" , linestyle='-', color='black',linewidth=0.7)
                    ver     += 1
            
            plt.xlabel('timestamp')
            plt.ylabel(tempJ)

            xlim = ax.get_xlim()
            ax.set_xlim(xlim)
            ax.set_ylim(0,2)
            
            legend   = ax.legend(loc='best')   

            titleFig = 'timestamp X ' + j.replace('"""', '').replace('%','')

            plt.title(titleFig)        
            plt.savefig(nameFig, dpi=150)   

            yAnomalous = []
            ver = 0

    def dataLogHTMLRescale(self):
        header  =  list(self.test.columns)

        for i in header:
            if i.find('timestamp') != -1:
                header.remove(i) 

            if i.find('Anomalous') != -1:
                header.remove(i)    

        name = 'DataLog_RF_' + self.nameInFig +'.html'
        file = open(name, 'w')

        text = [] 

        text.append('<!DOCTYPE html>\n')
        text.append('<html lang=\"pt-br\">\n')
        text.append('  <head>\n')
        text.append('     <title> File: ' + self.nameInFig + '.csv </title>\n')
        text.append('     <meta charset=\"utf-8\">\n')
        text.append('  </head>\n')
        text.append('  <body>\n')

        text.append('     <b> Number of Tuples: ' + str(len(self.test)) + '</b>  <br />\n')

        resultPerc  = self.calcPercCol('Anomalous')

        text.append('     <b> Anomalous: ' + str(round(resultPerc,5)) + '% </b> <br />\n')
        text.append('     <b> Number of Anomalous Tuples: ' + str(self.resultTuples) + '<b><br /> \n\n')

        text.append('  <center>\n')
        
        for i in header:
            name = self.nameInFig + '_Graph_RF_timestamp_X_' + str(i).replace('"','').replace('%','') 
            text.append('    <img src="'+ name +'.png"/>\n') 

        text.append('  </center>\n')

        text.append('  <center>\n')
        text.append('       <footer>\n')
        text.append('           <p> Completion of course work - Bachelor of Science in Computer Science </p>\n')
        text.append('           <p>Author: Henrique Matheus Silva Arouca</p>\n')
        text.append('           <p>Contact information: henriquematheus.arouca@gmail.com.</p>\n')
        text.append('       </footer>\n')
        text.append('  </center>\n')

        text.append(' </body>\n')
        text.append('</html>\n')

        file.writelines(text) 
        file.close()  

    def createPlotsImagesOri(self, objectToPlot):
        xColumn = ''
        tempJ   = ''
        count   = 0
        header  =  list(self.backupTest.columns)

        for i in header:
            if i.find('timestamp') != -1:
                xColumn = i
                header.remove(i) 

            if i.find('Anomalous') != -1:
                header.remove(i)             

        x          = self.backupTest[xColumn]
        yAnomalous = []

        for j in header:
            for i in range(len(self.backupTest)):

                if objectToPlot[i] == 1:
                    yAnomalous.append(self.backupTest[j][i])

                else:
                    yAnomalous.append(-1) 

            tempJ   = j.replace('"""', '')  
            title   = 'timestamp X ' + tempJ
            nameFig = self.nameInFig + 'Ori_Graph_RF_timestamp_X_' + j.replace('"""', '').replace('%','').replace('"','')

            fig,ax = plt.subplots(figsize=(12,6))

            y = self.backupTest[j]

            data  = ax.plot(x, y, label=title, color='orange',linewidth=0.7)

            ver = 0
            for i in range(len(yAnomalous)):
                if yAnomalous[i] != -1:
                    xseg = [x[i-1],x[i]]
                    yseg = [y[i-1],y[i]]
                    AnoLine  = ax.plot(xseg, yseg , label='Lines Considered Anomalous' if ver == 0 else "" , linestyle='-', color='black',linewidth=0.7)
                    ver     += 1
            
            plt.xlabel('timestamp')
            plt.ylabel(tempJ)

            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            
            legend   = ax.legend(loc='best')   

            titleFig = 'timestamp X ' + j.replace('"""', '').replace('%','')

            plt.title(titleFig)        
            plt.savefig(nameFig, dpi=150)   

            yAnomalous = []
            ver = 0    

    def dataLogHTMLOrgirnal(self):
        header  =  list(self.backupTest.columns)

        for i in header:
            if i.find('timestamp') != -1:
                header.remove(i) 

            if i.find('Anomalous') != -1:
                header.remove(i)    

        name = 'DataLog_' + self.nameInFig +'_OriginalData.html'
        file = open(name, 'w')

        text = [] 

        text.append('<!DOCTYPE html>\n')
        text.append('<html lang=\"pt-br\">\n')
        text.append('  <head>\n')
        text.append('     <title> File: ' + self.nameInFig + '.csv </title>\n')
        text.append('     <meta charset=\"utf-8\">\n')
        text.append('  </head>\n')
        text.append('  <body>\n')

        text.append('     <b> Number of Tuples: ' + str(len(self.backupTest)) + '</b>  <br />\n')

        resultPerc  = self.calcPercCol('Anomalous')

        text.append('     <b> Anomalous: ' + str(round(resultPerc,5)) + '% </b> <br />\n')
        text.append('     <b> Number of Anomalous Tuples: ' + str(self.resultTuples) + '<b><br /> \n\n')

        text.append('  <center>\n')
        
        for i in header:
            name = self.nameInFig + 'Ori_Graph_RF_timestamp_X_' + str(i).replace('"','').replace('%','') 
            text.append('    <img src="'+ name +'.png"/>\n') 

        text.append('  </center>\n')

        text.append('  <center>\n')
        text.append('       <footer>\n')
        text.append('           <p> Completion of course work - Bachelor of Science in Computer Science </p>\n')
        text.append('           <p>Author: Henrique Matheus Silva Arouca</p>\n')
        text.append('           <p>Contact information: henriquematheus.arouca@gmail.com.</p>\n')
        text.append('       </footer>\n')
        text.append('  </center>\n')

        text.append(' </body>\n')
        text.append('</html>\n')

        file.writelines(text) 
        file.close()

    def calcPercCol(self, column):              # Function that calculates the occurrence of the result and returns the percentage and the color of it
        self.resultTuples = 0
        count             = 0
        color             = ''

        for i in self.outputFile[column].values: 
            if i == 1:
                count += 1
                if column == 'Anomalous':
                    self.resultTuples += 1

        perc = float((float(count) / float(len(self.outputFile))) *100) 
        
        return  perc

rf = RandomForestIDS()

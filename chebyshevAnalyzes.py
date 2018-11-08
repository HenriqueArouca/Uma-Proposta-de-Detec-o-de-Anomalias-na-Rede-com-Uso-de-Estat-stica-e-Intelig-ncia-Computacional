#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from statisticalAnalyzes import *
from normBib import *
from matplotlib import pyplot as plt
import pandas as pd
import numpy  as np 
import sys
import os
import re 

class chebyshevAnalyzes(object):
    
    __inputFile        = None
    __outputFile       = None
    __typeOfLog        = None
    __kList            = None
    __colNotUsedList   = None
    __staGeralMeanDict = None
    __staMeanDict      = None
    __staGeralSDDict   = None
    __staSDDict        = None
    __newClasses       = None 
    __resultColumn     = None
    __resultTuples     = None
    __xColumnGraph     = None
    __percResult       = None
    __countDict        = None 

    def __init__(self):
        self.kList          = []
        self.colNotUsedList = []
        self.resultColumn   = ''
        self.resultTuples   = 0
        self.xColumnGraph   = ''
        self.percResult     = 0.0

        self.loadConfFile(sys.argv[3]) 

        normb = normBib()

        #self.inputFile  = pd.read_csv(sys.argv[1],sep="\\t|,|;|:| ", engine='python')  # Intput file         
        self.inputFile  = normb.rescale(sys.argv[1], self.colNotUsedList)
        self.outputFile = self.inputFile  

        self.typeOfLog  = sys.argv[4]  # <-t> to log in text or <-h> to log in html table 

        self.sta              = statisticAnalyzes(self.inputFile) 
        self.header           = []
        self.newClasses       = []
        self.staMeanDict      = {}
        self.staSDDict        = {}
        self.staGeralMeanDict = {}
        self.staGeralSDDict   = {}
        self.countDict        = {}

        self.runAnalyzes() 

    def loadConfFile(self,confFile):                           # Function that loads the configuration file to do the calculations
        file = open(confFile, 'r')                                 # Param 1: Name of the configutations file     
        text = file.readlines()                                    

        for i in text:
            if i.find('#') != -1:
                continue

            elif i.find('R') != -1:
                trash, temp = i.split(' ')
                self.colNotUsedList.append(str(temp).strip())

            elif i.find('K') != -1:
                trash, temp = i.split(' ')
                self.kList.append(float(temp))

            elif i.find('F') != -1:
                trash, self.resultColumn = i.split(' ')
                self.resultColumn = self.resultColumn.strip().replace('"','')  

            elif i.find('X') != -1:
                trash, self.xColumnGraph = i.split(' ') 
                self.xColumnGraph =  self.xColumnGraph.strip() 

            elif i.find('P') != -1:
                trash, temp = i.split(' ')
                self.percResult = float(temp)

        file.close()     

    def runAnalyzes(self):                           # Function that runs all the functions to analyze the dataset
        self.prepareData(self.colNotUsedList)                 

        for i in self.header:
            self.staGeralMeanDict.update({i:self.sta.mean(i, False)})
            self.staMeanDict.update({i:list(self.outputFile[i].rolling(window=8640).mean())})

            self.staGeralSDDict.update({i:self.sta.sd(i, False)})
            self.staSDDict.update({i:list(self.outputFile[i].rolling(window=8640).std())})

            self.countDict.update({i:0})   # Initializing the count dictionary of results for each column
            

        self.analyzesTuples()

        self.finalAnalyzes()

        for i in self.header:
            self.createPlotsImages(self.xColumnGraph, i)

        self.dataLog()

        self.outputFile.to_csv(sys.argv[2],index=False)

    def prepareData(self, colNotUsedList):                                  # Function that prepare the dataset, taking the header and treating it as it should 
        toRem       = []                                                        # Param 1: Columns that will not be used in the caracterization    
        self.header =  list(self.inputFile.columns) 
        
        if len(colNotUsedList) > 0:
            for i in self.header:
                for j in colNotUsedList:             # Walking through the header and if one in the columns is not required it is deleted from the header list
                    if i.find(j) != -1:
                        toRem.append(i)

            for i in toRem:
                self.header.remove(i)          

        if ((len(self.kList) < len(self.header)) or (len(self.kList) > len(self.header))):  # Verification of number of Ks given by argv parameter
            print ('Wrong number of Ks in list, please give the right number of columns')
            sys.exit(1)

        self.creatNewCols(self.inputFile, self.header) # Updating the dataset with the columns 


    def creatNewCols(self, dataFrame, ColstoAddList):                   # Function that create the new columns to the analyzes in the dataset
        for i in ColstoAddList:                                             # Param 1: The dataframe
            colName = 'Class_' + i                                          # Param 2: Columns that will be the subject of statistical analysis
            dataFrame[colName] = 0
            self.newClasses.append(colName)

        dataFrame[self.resultColumn] = 0   # Final column that will be have the result of analyses

        return dataFrame

    def analyzesTuples(self):                        # Function that analyze each cell acording the mean and the standart deesviation of column to caracterization
        for j in range(len(self.header)):
            for i in range(len(self.outputFile)):
               
                bigger  = self.staMeanDict[self.header[j]][i] + (self.kList[j] * self.staSDDict[self.header[j]][i])
                smaller = self.staMeanDict[self.header[j]][i] - (self.kList[j] * self.staSDDict[self.header[j]][i])

                if self.outputFile[self.header[j]][i] > bigger:   # If the element > mean + (k . sd)  
                    self.outputFile.loc[i, self.newClasses[j]] = 1 #Possible Anomaly, is outlier
                    tempcount = int(self.countDict[self.header[j]]) + 1
                    self.countDict.update({self.header[j]:tempcount})


                elif self.outputFile[self.header[j]][i] < smaller: # If the element < mean - (k . sd)
                    self.outputFile.loc[i, self.newClasses[j]] = 1 #Possible Anomaly, is outlier
                    tempcount = int(self.countDict[self.header[j]]) + 1
                    self.countDict.update({self.header[j]:tempcount})

    def finalAnalyzes(self):                 # Function that do the count of votes in the other columns and says if that tuple is outlier
        countVotes = 0

        for i in range(len(self.outputFile)):
            for j in range(len(self.newClasses)):

                if self.outputFile[self.newClasses[j]][i] == 1: # If this cell is consider outlier, a vote is counted
                    countVotes += 1

            if countVotes > (len(self.newClasses) * self.percResult): # The votes count has to be bigger than % passed by the configuration file
                self.outputFile.loc[i, self.resultColumn] = 1

            countVotes = 0  


    def createPlotsImages(self, xColumn, yColumn):         # Function that creates the graphs images
        pos = 0                                                 # Param 1: column that will be the X axis  
        for i in xrange(len(self.header)):                      # Param 2: column that will be the Y axis
            if self.header[i] == yColumn:
                pos = i                  

        chebPlus = []
        chebMin  = []
        for i in range(len(self.staMeanDict[yColumn])):
            chebPlus.append(self.staMeanDict[yColumn][i] + (self.kList[pos] * self.staSDDict[yColumn][i]))
            chebMin.append(self.staMeanDict[yColumn][i]  - (self.kList[pos] * self.staSDDict[yColumn][i])) 

        yResult = []    
        for i in range(len(self.outputFile)):
            if self.outputFile[self.resultColumn][i] == 1:
                yResult.append(self.outputFile[yColumn][i])

            else:
                yResult.append(-1)

        for i in list(self.outputFile.columns):
            if i.find(xColumn.strip()) != -1:
                Xcol = i        

        x   = self.outputFile[Xcol]
        y   = self.outputFile[yColumn]

        
        perc, colCell = self.calcPercCol(self.newClasses[pos])

        tempYColumn = yColumn.replace('"""', '') + '/ max_' + yColumn.replace('"""', '')  
    
        title   = xColumn.replace('"""', '').replace('"','') + ' X ' + tempYColumn

        name, ext =  str(sys.argv[1]).split('.')
        nameFig = name + '_Graph_' + xColumn.replace('"""', '').replace('"','') + 'X' + yColumn.replace('"""', '').replace('"','').replace('%','')

        fig,ax = plt.subplots(figsize=(10,6))

        data   = ax.plot(x, y, label=title, color='orange',linewidth=0.7)

        meanLine  = ax.plot(x, self.staMeanDict[yColumn] , label='Mean'                    , linestyle='-.', color='blue')
        CbyPline  = ax.plot(x, chebPlus                  , label='Mean + k.SD'             , linestyle='--', color='red')
        CbyMLine  = ax.plot(x, chebMin                   , label='Mean - k.SD'             , linestyle=':' , color='red')        

        ver = 0
        for i in range(len(yResult)):
                if yResult[i] != -1:
                    xseg = [x[i-1],x[i]]
                    yseg = [y[i-1],y[i]]
                    AnoLine  = ax.plot(xseg, yseg , label='Considered outlier' if ver == 0 else "" , linestyle='-', color='black',linewidth=0.7)
                    ver     += 1  
        
        plt.xlabel(xColumn.replace('"""', '').replace('"',''))
        plt.ylabel(tempYColumn)

        xlim = ax.get_xlim()
        ax.set_xlim(xlim)
        ax.set_ylim(0,2)

        legend   = ax.legend(loc='best')   

        titleFig = xColumn.replace('"""', '') + ' X ' + yColumn.replace('"""', '') + ' - Mean: ' + str(round(self.staGeralMeanDict[yColumn],5)) + ', SD: ' + str(round(self.staGeralSDDict[yColumn],5)) + ', ' + self.resultColumn + ': ' + str(self.countDict[yColumn]) + ' or ' + str(round(perc,5)) + '%'     

        plt.title(titleFig)        
        plt.savefig(nameFig, dpi=150)

        ver = 0       

    def dataLog(self):                                           # Function that release the log of calculations made before, in text or HTML mode
        if self.typeOfLog == '-t':
            fileName =  str(sys.argv[1])
            fileName, trash = fileName.split('.')
            name = 'DataLog_' + fileName + '.txt'
            file = open(name, 'w')

            text = [] 

            text.append('                File: ' + sys.argv[1] + '\n\n\n')
            text.append('Number of Tuples: ' + str(len(self.inputFile)) + '\n')
            text.append(self.resultColumn + ': ' + str(self.calcPercCol(self.resultColumn)) + '%\n')
            text.append('Number of ' + self.resultColumn + ' Tuples: ' + str(self.resultTuples) + '\n\n')

            for i in range(len(self.header)):
                text.append('Col_' + self.header[i] + '.Mean: ' + str(self.staGeralSDDict[self.header[i]])   + '\n')          
                text.append('Col_' + self.header[i] + '.SD: '   + str(self.staGeralSDDict[self.header[i]])     + '\n')
                text.append('Col_' + self.header[i] + '.CV: '   + str(self.sta.cv(self.header[i], False)) + '\n')
                text.append('Col_' + self.header[i] + '.K: '    + str(self.kList[i])                      + '\n')
                text.append('col_:'+ self.header[i] + '.' + self.resultColumn + ': ' + str(self.calcPercCol(self.newClasses[i])) + '% \n\n')
                text.append('-------------------------------//----------------------------------\n\n')

            text.append('All graphs are in the same folder of the dataset')    

            file.writelines(text) 
            file.close()    

        elif self.typeOfLog == '-h':
            fileName =  str(sys.argv[2])
            fileName, trash = fileName.split('.')
            name = 'DataLog_' + fileName + '_K'+ str(self.kList[0])  +'.html'
            file = open(name, 'w')

            text = [] 

            text.append('<!DOCTYPE html>\n')
            text.append('<html lang=\"pt-br\">\n')
            text.append('  <head>\n')
            text.append('     <title> File: ' + sys.argv[1] + ' </title>\n')
            text.append('     <meta charset=\"utf-8\">\n')
            text.append('  </head>\n')
            text.append('  <body>\n')

            text.append('     <b> Number of Tuples: ' + str(len(self.inputFile)) + '</b>  <br />\n')

            resultPerc, colCell = self.calcPercCol(self.resultColumn)

            text.append('     <b>'+ self.resultColumn + ': ' + str(round(resultPerc,5)) + '% </b> <br />\n')
            text.append('     <b> Number of ' + self.resultColumn + ' Tuples: ' + str(self.resultTuples) + '<b><br /> \n\n')

            text.append(' <div id="header" style="height:15%;width:100%;">\n')
            
            text.append('  <center>\n')
            
            text.append(' <div>\n')
            text.append('    <img src="TableLegend.png" style="float: right;">\n')
            text.append(' </div>\n')

            text.append(' <div>\n')
            text.append('    <table style=\"width:75%\" border=\"3\">\n')
            text.append('    <tr>\n')
            text.append('       <td colspan="9" BGCOLOR=#94989B> <center> <b> Data Log Analizes, File: ' +  fileName + '.csv </b> </center> </td>\n')
            text.append('    </tr>\n')
            text.append('    <tr>\n')
            text.append('      <th> # </th> <th> Column / Statictics </th> <th> Mean(x&#772) </th> <th> SD(&#963;)</th> <th> CV </th> <th> K </th>  <th> # '+ str(self.resultColumn).strip() +'</th> <th>' + str(self.resultColumn).strip() + '(Per/Var)</th> <th> &#8804;P(|x-&#181;| &#8805; K.&#963;) &#8804; 1/K<sup>2</sup>(.100)%</th>\n') 
            text.append('    </tr>\n')

            for i in range(len(self.header)):
                perc, colCell = self.calcPercCol(self.newClasses[i])                                                                                       
                text.append('    <tr> <td><center>' + str(i) + '</center></td> <td><b> Col.'+ self.header[i].replace('"', '') +' </b></td> <td> <center> '+ str(round(self.staGeralMeanDict[self.header[i]],5)) +' </center></td> <td><center> '+ str(round(self.staGeralSDDict[self.header[i]],5)) +' </center></td>')
                text.append('         <td><center> '+ str(round(self.sta.cv(self.header[i], False),5)) +' </center></td> <td><center> '+ str(self.kList[i]) +' </center></td> <td><center>'+ str(self.countDict[self.header[i]]) +'</center></td><td bgcolor='+ colCell +'><center> '+ str(round(perc,5)) +'% </center></td> <td><center>'+ str(round((1/self.kList[0]**2)*100,5)) +'%</center></td>') 
                text.append('   </tr>\n')


            text.append('   </table>\n')
            text.append('  </center>\n')
            text.append(' </div>')
            text.append(' </div>')

            text.append('  <center>\n')
            
            for i in self.header:
                self.xColumnGraph = str(self.xColumnGraph).strip()
                nfig, ext =  str(sys.argv[1]).split('.')
                name = nfig + '_Graph_' + self.xColumnGraph.replace('"','') + 'X' + str(i).replace('"','').replace('%','') 
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

        else:
            print ('Wrong Parameter, use <-t> to log in text or <-h> to log in html table')   # Verification of data log parameter given by argv 
            sys.exit(1)               

    def calcPercCol(self, column):                             # Function that calculates the occurrence of the result and returns the percentage and the color of it
        count = 0
        color = ''

        for i in self.outputFile[column].values: 
            if i == 1:
                count += 1
                if column == self.resultColumn:
                    self.resultTuples += 1

        perc = float((float(count) / float(len(self.outputFile))) *100) 

        if perc <= 30.0:
            color = '#05B738' # Green
        elif ((perc >= 31.0) and (perc <= 50.0)):
            color = '#D6C50B' # Yellow
        elif perc >= 51.0:
            color = '#EC4957' # Red
        
        return  perc, color

ca = chebyshevAnalyzes()
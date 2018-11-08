#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import random
import subprocess
import os
import pickle
from os import path
import sys

class slctTrainingUseSets(object):

    def __init__(self):
        self.trainigSetFileNames = []
        self.useSetFileNames     = []

        if path.exists('trainigSetFileNames.pickle'):
            pickle_inTrain           = open ('trainigSetFileNames.pickle','rb')
            pickle_inUse             = open ('useSetFileNames.pickle','rb')

            self.trainigSetFileNames = pickle.load(pickle_inTrain)
            self.useSetFileNames     = pickle.load(pickle_inUse)

        else:        
            self.trainigSetFileNames, self.useSetFileNames = self.selectSets()

        self.callChebyEachFile(self.trainigSetFileNames)
        self.callRFEachTrainFile(self.trainigSetFileNames)
        self.callRFEachUseFile(self.useSetFileNames)
        self.separateInFolders(self.trainigSetFileNames)

    def selectSets(self):
        tempTrainSet = []
        tempUseSet   = []

        p = subprocess.Popen("ls -lR Machines_Original_First/ | grep '^-' | wc -l", stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate() 

        n = int(out)

        tempTrainSet = random.sample(range(1, n), n/2) 

        with open ('trainigSetFileNames.pickle','wb') as file:
            pickle.dump(tempTrainSet, file)         

        for i in range(1,n+1):
            if i not in tempTrainSet:
                tempUseSet.append(i)    

        with open ('useSetFileNames.pickle','wb') as file:
            pickle.dump(tempUseSet, file)        

        return tempTrainSet, tempUseSet


    def callChebyEachFile(self, trainFileNames):
        for i in trainFileNames:
            name = 'machine' + str(i) + '.csv'

            print 'Running the Chebyshev Analyzes to ' + name

            cmd = 'time python chebyshevAnalyzes.py '+ name + ' machine'+ str(i) +'_rescaleAnalizes.csv ConfigurationFile.txt -h' 

            os.system(cmd)

            print 'Done!'
            print '--------------------------------//-----------------------------------------\n'

        print '--------------------------------//-----------------------------------------'
        print '--------------------------------//-----------------------------------------\n'    

    def callRFEachTrainFile(self, trainFileNames):
        sampleSlc         =  int(float(len(trainFileNames) * 0.4))
        perTrainFileNames =  []

        for i in range(sampleSlc):
            pos  = random.sample(range(0, len(trainFileNames)), 1)
            perTrainFileNames.append(trainFileNames[pos[0]])

        for i in perTrainFileNames:
            name = 'machine' + str(i) + '_rescaleAnalizes.csv' 
            out, trash  = name.split('.')

            print 'Running the training of the RF DA Algorithm to ' + name 

            cmd = 'time python randomForest_DA.py -t ' + name

            os.system(cmd)

            print 'Done!'
            print '--------------------------------//-----------------------------------------\n'

        print '--------------------------------//-----------------------------------------'
        print '--------------------------------//-----------------------------------------\n'    

    def callRFEachUseFile(self, useFileNames):
        for i in useFileNames:
            name = 'machine' + str(i) + '.csv'
            rf, trash = name.split('.')  

            print 'Running the use of the RF DA Algorithm to ' + name 

            cmd = 'time python randomForest_DA_DiffAnaly.py -u ' + name + ' ' + rf + '_RF.csv'

            os.system(cmd)

            print 'Done!'
            print '--------------------------------//-----------------------------------------\n'

        print '--------------------------------//-----------------------------------------'
        print '--------------------------------//-----------------------------------------\n'    
            

    def separateInFolders(self, trainFileNames):

        for i in trainFileNames:
            cmdMK = 'mkdir -p Anlmch_' + str(i) 
            sys.os(cmdMK)

            cmdLS = 'ls machine' + str(i) + '* | mv pwd Anlmch_' + str(i)     
            sys.os(cmdLS)

slc = slctTrainingUseSets()
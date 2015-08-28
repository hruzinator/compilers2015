#!/usr/bin/python

'''
Input Handler version 0.1 for CS 4013, Project 0
Matthew Hruz, 2015, The University of Tulsa

This python file will handle input from source files and reserved word
files. Project 0 only requires that the program read in input from the
source file and output each line with a line number associated with it.
'''

import sys

#takes in a file and outputs an array of lines
def readLines(inFile):
    sourceFile = open(inFile, "r")
    return sourceFile.readlines()

def printHelp():
    print "Usage:"
    print "python inputHandler.py sourceFile"

if len(sys.argv) is not 2:
    printHelp()
    sys.exit()
lines = readLines(sys.argv[1])
lineNum=1
listingFile = open('lineListing.txt', 'w')

for l in lines:
    listingFile.write(str(lineNum) + ": " + l[:-1] + '\n')
    lineNum+=1

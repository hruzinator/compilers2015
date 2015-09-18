#!/usr/bin/python

'''
Pascal Compiler version 0.1 for CS 4013, Project 1
Matthew Hruz, 2015, The University of Tulsa

This python file will handle input from source files and reserved word
files. Project 0 only requires that the program read in input from the
source file and output each line with a line number associated with it.
'''

import sys
import lexer

def printHelp():
    print "Usage:"
    print "python main.py sourceFile"

#process args and begin process
if len(sys.argv) is not 2:
    printHelp()
    sys.exit()

#get an array of lines
lines = open(sys.argv[1], "r").readlines()
lineNum=1
listingFile = open('lineListing.txt', 'w')

for l in lines:
    listingFile.write(str(lineNum) + ": " + l[:-1] + '\n')
    lexer.feedLexer(l)
    nextToken=lexer.getToken()
    while nextToken is not None:
        listingFile.write(str(nextToken) + '\n')
        nextToken=lexer.getToken()
    lineNum+=1

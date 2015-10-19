#!/usr/bin/python

'''
Pascal Compiler version 0.1 for CS 4013, Project 1
Matthew Hruz, 2015, The University of Tulsa

This python file will handle input from source files and reserved word
files.
'''

import sys
import lexer
from symbolTable import symbolTable

def printHelp():
    print "Usage:"
    print "python main.py sourceFile"

#process args and begin process
if len(sys.argv) is not 2:
    printHelp()
    sys.exit()

#process reserved words file and store into symbol table
lines = open('reservedWords.rwf', 'r').readlines()
symTable=symbolTable()
for l in lines:
    words=l.split()
    #TODO assert proper form is adhered to and that tokenType and attribute are valid
    lexeme=words[0].translate(None, '\"')
    tokenType=words[1]
    attribute=words[2]
    token={'lexeme':lexeme, 'tokenType':tokenType, 'attribute':attribute}
    symTable.insert(token)

#get an array of lines
lines = open(sys.argv[1], "r").readlines()
lineNum=1
listingFile = open('lineListing.txt', 'w')

lexer.defineSymTable(symTable)
for l in lines:
    listingFile.write(str(lineNum) + ": " + l[:-1] + '\n')
    lexer.feedLexer(l)
    nextToken=lexer.getToken()
    while type(nextToken) is not str:
        if nextToken != None:
			listingFile.write(str(nextToken) + '\n')
        nextToken=lexer.getToken()
    assert nextToken is "noTokens"
    lineNum+=1

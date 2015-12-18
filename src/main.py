#!/usr/bin/python

'''
Pascal Compiler version 0.1 for CS 4013, Project 1
Matthew Hruz, 2015, The University of Tulsa

This python file will handle input from source files and reserved word
files.
'''

import sys
import lexer
import parser
from symbolTable import symbolTable

def printHelp():
    print "Usage:"
    print "python main.py sourceFile"

#process args and begin process
if len(sys.argv) is not 2:
    printHelp()
    sys.exit()

#process reserved words file and store into reserved words table
lines = open('reservedWords.rwf', 'r').readlines()
rwTable=symbolTable()
for l in lines:
    words=l.split()
    #TODO assert proper form is adhered to and that tokenType and attribute are valid
    lexeme=words[0].translate(None, '\"')
    tokenType=words[1]
    attribute=words[2]
    token={'lexeme':lexeme, 'tokenType':tokenType, 'attribute':attribute}
    rwTable.insert(token)

lexer.defineReservedWordTable(rwTable)

#get an array of lines
lines = open(sys.argv[1], "r").readlines()
lines[-1]+='\x03'

listingFile = open('lineListing.txt', 'w')
tokenFile = open('tokenFile.txt', 'w')

#tokenFile.write()

lineNum=1
for l in lines:
    lexer.feedLexer(l)
    nextToken=lexer.getToken()
    listingFile.write(str(lineNum) + ": " + l[:-1] + '\n')
    while nextToken is not "noTokens":
        if nextToken != None:
            if nextToken['tokenType'] == 'LEXERR':
                listingFile.write(str(nextToken) + '\n')
            tokenFile.write(str(lineNum) + ": " + str(nextToken) + '\n')
            nextToken=lexer.getToken()
    lineNum+=1
print "lexical analysis is complete"

#parser.setup(lexer, rwTable)
#parser.parse()

#!/usr/bin/python

'''
Pascal Compiler version 0.1 for CS 4013, Project 2
Matthew Hruz, 2015, The University of Tulsa

This python file will handle input from source files 
and reserved word files.
'''

import sys
import lexer
import parser
from symbolTable import symbolTable
import os.path

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
    lexeme=words[0].translate(None, '\"')
    tokenType=words[1]
    attribute=words[2]
    token={'lexeme':lexeme, 'tokenType':tokenType, 'attribute':attribute}
    rwTable.insert(token)

#get an array of lines
if not os.path.isfile(sys.argv[1]):
    print 'The file you tried to compile does not exist'
    sys.exit()
lines = open(sys.argv[1], "r").readlines()
lines[-1]+='\x03'

listingFile = open('lineListing.txt', 'w')
tokenFile = open('tokenFile.txt', 'w')

tokenFile.write("line No.".center(10) + "Lexeme".ljust(17) \
+ "Token Type".ljust(15) + "attribute".ljust(40) + '\n')

lexer.setup(listingFile, tokenFile, lines, rwTable)

for l in lines:
    lexer.feedLexer(l)
print "lexical analysis is complete"

parser.setup(lexer, rwTable, listingFile)
parser.parse()
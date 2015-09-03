#!/usr/bin/python
'''
Lexer for compiler
'''
from types import *

class LexerFSM:
	def __init__(self):
		self.states = {}
		self.startState = None
		self.currentState = None
		self.isRunning = False

	def isRunning(self):
		return self.isRunning

	#handler is a function type
	def addState(self, name, handler):
		#input validation
		if type(name) is not str:
			raise TypeErr("Argument \'name\' in addState must be of type string")
			return
		
		if type(handler) is not FunctionType:
			raise TypeErr("Argument \'handler\' in addState must be of type function")
			return
		
		if name in self.states:
			print "Warning! Adding state that already exists. This replaces the old state"
		self.states[name]=handler
	
	def setStart(self, name):
		#input validation
		if type(name) is not str:
			raise TypeErr("Argument \'name\' in setStart must be of type string")
			return

		if name not in self.states:
			print "ERROR! Cannot define the start state without first adding it.\n---StartState has been left undefined"
			return
		self.startState=name

	def start(self, char=None):
		#begin by checking that inital conditions are ok for starting the machine
		if len(self.states) == 0:
			print "States must be added with addState(), and a startState needs to be defined, before the Finite State Machine can run"
			return #TODO empty returns (here and elsewhere) could cause problems
		if self.startState is None:
			print "Error! Cannot run until the startState has been defined with setStart"
			return

		#initialize the machine
		self.currentState=self.startState
		self.isRunning=True
		if type(char) is not NoneType:
			feedChar(char)

	def feedChar(self, char):
		assert(self.isRunning)
		#input validation
		if type(char) is not str or len(char) is not 1:
			raise TypeError("trying to feedChar in lexer without a string of length 1 (a char)")
			return

		newState=self.states[self.currentState](char)
		
		if type(newState) is str:
			#newState is indeed a new state
			#make sure currentState is a valid state
			if self.currentState not in self.states:
				raise KeyError("A lexer FSM tried to go to a state that doesn't exist ("+currentState+")")
				assert(False)
			self.currentState=newState
			return True

		if type(newState) is dict:
			#the FSM has found a valid token. NewState holds that token
			assert 'tokenType' in newState and 'tokenStr' in newState
			self.isRunning=False
			return newState
		
		if type(newState) is NoneType:
			#the FSM cannot determine the token type
			self.isRunning=False
			return False
#end lexerFSM class

'''
Main code of lexer.py.
'''

#define module fields
buff=[]
buffPtr=0
machines=[] #order is important. Make sure machines are priority ordered

#define RELOP machine
relopMachine=LexerFSM()
def handle(c): #''
	assert type(c) is str and len(c)==1
	if c == '<': return '<'
	elif c == '>': return '>'
	elif c == '=': return {'tokenType': "RELOP", 'tokenStr':"="}
	else: 
		global buffPtr
		buffPtr-=1 #we saw another charachter, so buffPtr needs to be moved back 1
		return None #FSM has determined the current token is not a relational operator
relopMachine.addState("__start__", handle)
def handle(c): #'<'
	assert type(c) is str and len(c)==1
	if c == '>': return {'tokenType': "RELOP", 'tokenStr':"<>"}
	elif c == '=': return {'tokenType': "RELOP", 'tokenStr':"<="}
	else:
		global buffPtr
		buffPtr-=1 
		return {'tokenType': "RELOP", 'tokenStr':"<"}
relopMachine.addState("<", handle)
def handle(c): #'>'
	assert type(c) is str and len(c)==1
	if c == '=': return {'tokenType': "RELOP", 'tokenStr':">="}
	else: 
		global buffPtr
		buffPtr-=1
		return {'tokenType': "RELOP", 'tokenStr':">"}
relopMachine.addState(">", handle)
relopMachine.setStart("__start__")
machines.append(relopMachine)

#define ID machine
#TODO implement restrictions on the size of ID
idMachine=LexerFSM()
def handle(c): #start
	assert type(c) is str and len(c)==1
	#convert c to ascii number representation
	l=ord(c)
	#check if l is a capital or lowercase letter
	if (65<=l<=90) or (97<=l<=122):
		return  "letterNum"
	else:
		global buffPtr
		buffPtr-=1
		return None
idMachine.addState("__start__", handle)
def handle(c): #letterNum
	assert type(c) is str and len(c)==1
	ld=ord(c)
	#check if ld is a letter
	if (65<=ld<=90) or (97<=ld<=122):
		return  "letterNum"
	#check if ld is a number
	elif (48<=ld<=57):
		return  "letterNum"
	else:
		#TODO symbol table
		global buffPtr
		global buff
		lexeme="".join(buff[:buffPtr])
		buffPtr-=1
		return {'tokenType':"ID", 'tokenStr':lexeme}
idMachine.addState("letterNum", handle)
idMachine.setStart("__start__")
machines.append(idMachine)

#define whitespace machine
wsMachine=LexerFSM()
def handle(c):
	assert type(c) is str and len(c)==1
	#TODO may just want whitespace only. Not the different types of space.
	if c is ' ': return {'tokenType':"Whitespace", 'tokenStr':"space"}
	elif c is '\t': return {'tokenType':"Whitespace", 'tokenStr':"tab"}
	elif c is '\b': return {'tokenType':"Whitespace", 'tokenStr':"backspace"}
	else:
		global buffPtr
		buffPtr-=1
		return None
wsMachine.addState("__start__", handle)
wsMachine.setStart("__start__")
machines.append(wsMachine)

#define newline manchine
nlMachine=LexerFSM()
def handle(c):
	assert type(c) is str and len(c)==1
	if ord(c) is 10: return {'tokenType':"Newline", 'tokenStr':"linefeed newline"}
	#TODO more for different OS types? (namely, Windows, and the unicode encoding?)
	else:
		global buffPtr
		buffPtr-=1
		return None
nlMachine.addState("__start__", handle)
nlMachine.setStart("__start__")
machines.append(nlMachine)


#TODO define longreal machine (must be before reals to ensure we don't premeturely tokenize a real out of a longreal)
lrMachine=LexerFSM()
def handle(c): #start
	assert type(c) is str and len(c)==1
	d=ord(c)
	#check if d is a number
	if (48<=d<=57):
		return  "x"
	else:
		global buffPtr
		buffPtr-=1
		return None
lrMachine.addState("__start__", handle)
def handle(c):#x
	assert type(c) is str and len(c)==1
	d=ord(c)
	#check if d is a number
	if (48<=d<=57):
		return  "x"
	elif c is '.':
		return "y"
	else:
		global buffPtr
		buffPtr-=1
		return None
lrMachine.addState("x", handle)
def handle(c):#y
	assert type(c) is str and len(c)==1
	d=ord(c)
	#check if d is a number
	if (48<=d<=57):
		return  "y"
	elif c is 'e':
		return "z"
	else:
		global buffPtr
		buffPtr-=1
		return None
lrMachine.addState("y", handle)
def handle(c):#z
	assert type(c) is str and len(c)==1
	d=ord(c)
	#check if d is a number
	if (48<=d<=57):
		return  "z"
	else:
		global buffPtr
		global buff
		lexeme="".join(buff[:buffPtr])
		buffPtr-=1
		return {'tokenType':"LONGREAL", 'tokenStr':lexeme}
lrMachine.addState("z", handle)
lrMachine.setStart("__start__")
machines.append(lrMachine)

#TODO define reals machine (must be before ints to ensure we don't ppremeturely tokenize an int out of a real)
rMachine=LexerFSM()
def handle(c): #start
	assert type(c) is str and len(c)==1
	d=ord(c)
	#check if d is a number
	if (48<=d<=57):
		return  "x"
	else:
		global buffPtr
		buffPtr-=1
		return None
rMachine.addState("__start__", handle)
def handle(c):#x
	assert type(c) is str and len(c)==1
	d=ord(c)
	#check if d is a number
	if (48<=d<=57):
		return  "x"
	elif c is '.':
		return "y"
	else:
		global buffPtr
		buffPtr-=1
		return None
rMachine.addState("x", handle)
def handle(c):#y
	assert type(c) is str and len(c)==1
	d=ord(c)
	#check if d is a number
	if (48<=d<=57):
		return  "y"
	else:
		global buffPtr
		global buff
		lexeme="".join(buff[:buffPtr])
		buffPtr-=1
		return {'tokenType':"REAL", 'tokenStr':lexeme}
rMachine.addState("y", handle)
rMachine.setStart("__start__")
machines.append(rMachine)

#TODO define int machine
intMachine=LexerFSM()
def handle(c):
	assert type(c) is str and len(c)==1
	d=ord(c)
	if (48<=d<=57):
		return "num"
	else:
		global buffPtr
		buffPtr-=1
		return None
intMachine.addState("__start__", handle)
def handle(c):
	assert type(c) is str and len(c)==1
	d=ord(c)
	#check if d is a number
	if (48<=d<=57):
		return  "num"
	else:
		global buffPtr
		global buff
		lexeme="".join(buff[0:buffPtr])
		buffPtr-=1
		return {'tokenType':"INTEGER", 'tokenStr':lexeme}
intMachine.addState("num", handle)
intMachine.setStart("__start__")
machines.append(intMachine)

#define module methods
def tryMachine(machine):
	global buff
	global buffPtr
	machine.start()
	result=True
	while result is True:
		if buffPtr >= len(buff):
			return None #TODO perhaps extra indication that buff is not empty, just waiting?
		result=machine.feedChar(buff[buffPtr])
		buffPtr+=1
	if type(result) is dict:
		buff=buff[buffPtr:]
		buffPtr=0
		return result
	assert result is False #should be False when moving to next machine
	buffPtr=0
	return result

def feedLexer(sourceString):
	assert type(sourceString) is str
	global buff
	buff+=list(sourceString)

def getToken():
	global buff
	global buffPtr
	global machines
	if len(buff) is 0:
		return None

	machineWorked=False
	i=0
	while machineWorked is False and i < len(machines):
		machineWorked=tryMachine(machines[i])
		i+=1
	#false if all else fails
	if machineWorked is False:
		#remove 1 element of buffer to move past bad char. TODO will this cause any errors?
		print str(buff[0:1]) + " " + str(ord(buff[0])) #TODO remove at end
		buff=buff[1:]
		return {'tokenType':"LEXERR", 'tokenStr':"Lexer could not determine token type"}
	assert type(machineWorked) is dict
	return machineWorked


'''
The code below is for testing only. Remove before submission
'''
lines=open("test.txt", 'r').readlines()
for l in lines:
	feedLexer(l)
	result=getToken()
	while result is not None:
		assert type(result) is dict
		print result
		result=getToken()

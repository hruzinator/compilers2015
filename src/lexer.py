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

#define RELOP machine
relopMachine=LexerFSM()
def handle(c): #''
	assert type(c) is str and len(c)==1
	if c == '<': return '<'
	if c == '>': return '>'
	if c == '=': return {'tokenType': "RELOP", 'tokenStr':"="}
	else: 
		global buffPtr
		buffPtr-=1 #we saw another charachter, so buffPtr needs to be moved back 1
		return None #FSM has determined the current token is not a relational operator
relopMachine.addState("__start__", handle)
def handle(c): #'<'
	assert type(c) is str and len(c)==1
	if c == '>': return {'tokenType': "RELOP", 'tokenStr':"<>"}
	if c == '=': return {'tokenType': "RELOP", 'tokenStr':"<="}
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

#define module methods
def feedLexer(sourceString):
	assert type(sourceString) is str
	global buff
	buff+=list(sourceString)

def getToken():
	global buff
	global buffPtr
	if len(buff) is 0:
		return None
	#try relop machine
	relopMachine.start()
	result=True
	while result is True:
		if buffPtr >= len(buff):
			return None #TODO perhaps extra indication that buff is not empty, just waiting?
		result=relopMachine.feedChar(buff[buffPtr])
		buffPtr+=1
	if type(result) is dict:
		buff=buff[buffPtr:]
		buffPtr=0
		return result
	assert result is False #should be False when moving to next machine
	buffPtr=0
	
	#all else fails, return LEXERR as token and continue
	
	#remove 1 element of buffer to move past bad char. TODO will this cause any errors?
	print ord(buff[0])
	buff=buff[1:]
	return {'tokenType':"LEXERR", 'tokenStr':"Lexer could not determine token type"}


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

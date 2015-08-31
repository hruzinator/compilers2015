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
		self.token_string = ""

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

	def run(self, inLine):
		#input validation
		if type(inLine) is not str:
			raise TypeError("trying to run a lexer FSM with an input string not of type string")
			return

		#begin by checking that inital conditions are ok for starting the machine
		if len(self.states) == 0:
			print "States must be added with addState(), and a startState needs to be defined, before the Finite State Machine can run"
			return #TODO empty returns (here and elsewhere) could cause problems
		if self.startState is None:
			print "Error! Cannot run until the startState has been defined with setStart"
			return

		#initialize the run function
		currentState=self.startState
		tokenIdx=0

		while type(currentState) is str:
			#make sure currentState is a valid state
			if currentState not in self.states:
				raise KeyError("A lexer FSM tried to go to a state that doesn't exist ("+currentState+")")

			#make sure there is more line to parse
			try:
				c=inLine[tokenIdx]
				tokenIdx+=1
			except IndexError: #TODO is exception the best way to handle this?
				print "Error! Line ended before end of token"
				return {'tokenType':"LEXERR", 'tokenStr':"End of line before end of token"}
			currentState=self.states[currentState](c)
		
		'''
		once we exit the loop (when currentState isn't a string), it means that we have exited the FSM.
		We now check to make sure currentState is a token (properly-formed dictionary returned), or if 
		the FSM just couldn't parse the string. If neither are the case, there was a program error.
		'''
		assert type(currentState) is dict or type(currentState) is NoneType
		if type(currentState) is dict:
			assert 'tokenType' in currentState and 'tokenStr' in currentState
		elif type(currentState) is None:
			print "Still working on this"
			#TODO This FSM could not determine the token type
		#token string is determined based on the placement of tokenIdx. We can also return what still needs to be parsed from this.
		#TODO finish this by coding solution to multi-token per line scenarios.
		print currentState


#define RELOP machine
relopMachine=LexerFSM()
def handle(c): #''
	assert type(c) is str and len(c)==1
	if c == '<': return '<'
	if c == '>': return '>'
	if c == '=': return {'tokenType': "RELOP", 'tokenStr':"="}
	else: return None #TODO plan. If FSM does not "fit the bill"
relopMachine.addState("__start__", handle)
def handle(c): #'<'
	assert type(c) is str and len(c)==1
	if c == '>': return {'tokenType': "RELOP", 'tokenStr':"<>"}
	if c == '=': return {'tokenType': "RELOP", 'tokenStr':"<="}
	else: return {'tokenType': "RELOP", 'tokenStr':"<"}
relopMachine.addState("<", handle)
def handle(c): #'>'
	assert type(c) is str and len(c)==1
	if c == '=': return {'tokenType': "RELOP", 'tokenStr':">="}
	else: return {'tokenType': "RELOP", 'tokenStr':">"}
relopMachine.addState(">", handle)
relopMachine.setStart("__start__")
'''for the sake of testing, we will use file to see what happens here'''
lines=open('test.txt', 'r').readlines()
for l in lines:
	relopMachine.run(l)

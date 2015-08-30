#!/usr/bin/python
'''
Lexer for compiler
'''
from Types import FunctionType

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
		states[name]=handler
	
	def setStart(self, name):
		#input validation
		if type(name) is not str:
			raise TypeErr("Argument \'name\' in setStart must be of type string")
			return

		if name not in self.states:
			print "ERROR! Cannot define the start state without first adding it.\n---StartState has been left undefined"
			return
		self.startState=name

	def run(inStr):
		#input validation
		if type(inStr) is not str:
			raise TypeError("trying to run a lexer FSM with an input string not of type string")
			return

		#begin by checking that inital conditions are ok for starting the machine
		if len(states) == 0:
			print "States must be added with addState(), and a startState needs to be defined, before the Finite State Machine can run"
			return
		if startState is None:
			print "Error! Cannot run until the startState has been defined with setStart"
			return

		#initialize the run function
		currentState=startState
		while type(currentState) is str:
			#TODO
			currentState=None
			print "implement me"

		if type(currentState) is set:
			print "implement me"
			#TODO
		else:
			print "an internal error occurred. A lexer FSM is not giving us a token after completing execution"

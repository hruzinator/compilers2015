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
            #the FSM has found a valid token. NewState holds that token (or an empty dict if tokenless)
            assert bool(newState) is False or ('tokenType' in newState and 'lexeme' in newState and 'attribute' in newState)
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
    elif c == '=': return {'tokenType': "RELOP", 'lexeme':"=", 'attribute':"equals"}
    else:
        global buffPtr
        buffPtr-=1 #we saw another charachter, so buffPtr needs to be moved back 1
        return None #FSM has determined the current token is not a relational operator
relopMachine.addState("__start__", handle)
def handle(c): #'<'
    assert type(c) is str and len(c)==1
    if c == '>': return {'tokenType': "RELOP", 'lexeme':"<>", 'attribute':"not equals"}
    elif c == '=': return {'tokenType': "RELOP", 'lexeme':"<=", 'attribute':"less than or equals"}
    else:
        global buffPtr
        buffPtr-=1
        return {'tokenType': "RELOP", 'lexeme':"<", 'attribute':"less than"}
relopMachine.addState("<", handle)
def handle(c): #'>'
    assert type(c) is str and len(c)==1
    if c == '=': return {'tokenType': "RELOP", 'lexeme':">=", 'attribute':"greater than or equals"}
    else:
        global buffPtr
        buffPtr-=1
        return {'tokenType': "RELOP", 'lexeme':">", 'attribute':"greater than"}
relopMachine.addState(">", handle)
relopMachine.setStart("__start__")
machines.append(relopMachine)

#define assignOp machine
assignopMachine=LexerFSM()
def handle(c):
    assert type(c) is str and len(c)==1
    if c == ":": return ":"
    else:
        global buffPtr
        buffPtr-=1
        return None
assignopMachine.addState("__start__", handle)
def handle(c):#":"
    assert type(c) is str and len(c)==1
    if c == "=": return {'tokenType': "ASSIGNOP", 'lexeme':":=", 'attribute':"assign to"}
    else:
        global buffPtr
        buffPtr-=2
        return None
assignopMachine.addState(":", handle)
assignopMachine.setStart("__start__")
machines.append(assignopMachine)

#define addOp machine
addopMachine=LexerFSM()
def handle(c):
    assert type(c) is str and len(c)==1
    if c == '+': return {'tokenType': "ADDOP", 'lexeme':'+', 'attribute':"add"}
    elif c == '-': return {'tokenType':"ADDOP", 'lexeme':"-", 'attribute':"subtract"}
    elif c == 'o' : return "o"
    else:
        global buffPtr
        buffPtr-=1
        return None
addopMachine.addState("__start__", handle)
def handle(c):#'o'
    assert type(c) is str and len(c)==1
    if c == 'r': return "or"
    else: #what we thought was an or really wasn't an or
        global buffPtr
        buffPtr-=2 #go back to o
        return None
addopMachine.addState("o", handle)
def handle(c):#'or' -> must make sure word ends (i.e. oreo is technically an ID or reserved word)
    assert type(c) is str and len(c)==1
    #check to see if the next char is a letter
    if (65<=ord(c)<=90) or (97<=ord(c)<=122):
        global buffPtr
        buffPtr-=3
        return None
    else:
        return {'tokenType': "ADDOP", 'lexeme':'or', 'attribute':"logical or"}
addopMachine.addState("or", handle)
addopMachine.setStart("__start__")
machines.append(addopMachine)

#define multOp machine
multopMachine=LexerFSM()
def handle(c):
    global buff
    global buffPtr
    assert type(c) is str and len(c)==1
    if c == '*': return {'tokenType': "MULTOP", 'lexeme':'*'}
    elif c == '/': return {'tokenType':"multop", 'lexeme':"/"}
    elif c == 'd': #handle it all here to reduce excess code
        if buffPtr+3>=len(buff):
            return None
        if buff[buffPtr+1] == 'i' and buff[buffPtr+2] == 'v':
            #make sure next char is not another a-z or A-Z
            l=ord(buff[buffPtr+3])
            if (65<=l<=90) or (97<=l<=122):
                buffPtr-=2
                return None
            buffPtr+=2
            return {'tokenType':"multop", 'lexeme':"/"}
        else:
            buffPtr-=1
            return None
    elif c == 'm' :#handle it all here to reduce excess code
        if buffPtr+3>=len(buff):
            return None
        if buff[buffPtr+1] == 'o' and buff[buffPtr+2] == 'd':
            #make sure next char is not another a-z or A-Z
            l=ord(buff[buffPtr+3])
            if (65<=l<=90) or (97<=l<=122):
                buffPtr-=2
                return None
            buffPtr+=2
            return {'tokenType':"multop", 'lexeme':"mod", 'attribute':"modulus"}
        else:
            buffPtr-=1
            return None
    elif c == 'a' :#handle it all here to reduce excess code
        if buffPtr+3>=len(buff):
            return None
        if buff[buffPtr+1] == 'n' and buff[buffPtr+2] == 'd':
            #make sure next char is not another a-z or A-Z
            l=ord(buff[buffPtr+3])
            if (65<=l<=90) or (97<=l<=122):
                buffPtr-=2
                return None
            buffPtr+=2
            return {'tokenType':"multop", 'lexeme':"and", 'attribute':"logical and"}
        else:
            buffPtr-=1
            return None
    else:
        buffPtr-=1
        return None
multopMachine.addState("__start__", handle)
multopMachine.setStart("__start__")
machines.append(multopMachine)

#define ID machine
#TODO implement restrictions on the size of ID
idMachine=LexerFSM()
def handle(c): #start
    global buffPtr
    assert type(c) is str and len(c)==1
    #convert c to ascii number representation
    l=ord(c)
    #check if l is a capital or lowercase letter
    if (65<=l<=90) or (97<=l<=122):
        return  "letterNum"
    else:
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
        global buffPtr
        global buff
        lexeme="".join(buff[:buffPtr])
        buffPtr-=1
        token={'tokenType':"ID", 'lexeme':lexeme, 'attribute':""} #TODO do we even need attribute here?
        global symTable
        result=symTable.insert(token)
        if result is not None:
            ptr=hex(id(result))
            token['attribute']=ptr
        else:
            result=symTable.lookup(token['lexeme'])
        return result 
idMachine.addState("letterNum", handle)
idMachine.setStart("__start__")
machines.append(idMachine)

#define whitespace machine
wsMachine=LexerFSM()
def handle(c):
    assert type(c) is str and len(c)==1
    #TODO may just want whitespace only. Not the different types of space.
    if c is ' ' or c is '\t' or c is '\b': return {}
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
    if ord(c) is 10: return {}
    #TODO more for different OS types? (namely, Windows, and the unicode encoding?)
    else:
        global buffPtr
        buffPtr-=1
        return None
nlMachine.addState("__start__", handle)
nlMachine.setStart("__start__")
machines.append(nlMachine)

#define comments machine
commentMachine=LexerFSM()
def handle(c): #start
	assert type(c) is str and len(c)==1
	if c is '{': return "commentChars"
	else:
		global buffPtr
		buffPtr-=1
		return None
commentMachine.addState("__start__", handle)
def handle(c): #commentChars
	assert type(c) is str and len(c)==1
	if c is "}": return {}
	else: return "commentChars"
commentMachine.addState("commentChars", handle)
commentMachine.setStart("__start__")
machines.append(commentMachine)

#define longreal machine (must be before reals to ensure we don't premeturely tokenize a real out of a longreal)
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
        return {'tokenType':"LONGREAL", 'lexeme':lexeme, 'attribute':"LONGREAL"}
lrMachine.addState("z", handle)
lrMachine.setStart("__start__")
machines.append(lrMachine)

#define reals machine (must be before ints to ensure we don't ppremeturely tokenize an int out of a real)
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
        return {'tokenType':"REAL", 'lexeme':lexeme, 'attribute':"Real Number"} #TODO what are we doing with this attribute???
rMachine.addState("y", handle)
rMachine.setStart("__start__")
machines.append(rMachine)

#define int machine
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
        return {'tokenType':"INTEGER", 'lexeme':lexeme, 'attribute':"Integer"} #TODO what to do about attribute???
intMachine.addState("num", handle)
intMachine.setStart("__start__")
machines.append(intMachine)

#define catch-all machine
catchallMachine=LexerFSM()
def handle(c):#start state
	assert type(c) is str and len(c)==1
	if c == '(': return {'tokenType':"SYMBOL", 'lexeme':"(", 'attribute':"openParen"}
	if c == ')': return {'tokenType':"SYMBOL", 'lexeme':")", 'attribute':"closeParen"}
	if c == ';': return {'tokenType':"SYMBOL", 'lexeme':";", 'attribute':"endStmt"}
	if c == '[': return {'tokenType':"SYMBOL", 'lexeme':"[", 'attribute':"openBracket"}
	if c == ']': return {'tokenType':"SYMBOL", 'lexeme':"]", 'attribute':"closeBracket"}
	if c == ',': return {'tokenType':"SYMBOL", 'lexeme':",", 'attribute':"listDelim"}
	if c == '.': return "periods"
	else:
		global buffPtr
		buffPtr-=1
		return None
catchallMachine.addState("__start__", handle)
def handle(c):#periods
	#NOTE if token is indeed ., it is possible to hit end of file. Does python add EOF to the file?
	assert type(c) is str and len(c)==1
	if c == '.': return {'tokenType':"SYMBOL", 'lexeme':"..", 'attribute':"arrayRange"}
	else: 
		#just one period. End of program. Anything left in buffer should be just whitespace/newline, but that's for later stages to sort out
		global buffPtr
		buffPtr-=1
		return {'tokenType':"SYMBOL", 'lexeme':".", 'attribute':"endProg"}
catchallMachine.addState("periods", handle)
catchallMachine.setStart("__start__")
machines.append(catchallMachine) #XXX stitch this in once we are ready

#symbol table variable
symTable = None

#define module methods
def tryMachine(machine):
    global buff
    global buffPtr
    machine.start()
    result=True
    while result is True:
        if buffPtr >= len(buff):
            return {'tokenType':"LEXERR", 'lexeme':"Incomplete token at the end of the buffer", 'attribute':""}
        result=machine.feedChar(buff[buffPtr])
        buffPtr+=1
    if type(result) is None: #None is used for whitespace, comments, or other non-token generating items
	return None
    elif type(result) is dict:
        buff=buff[buffPtr:]
        buffPtr=0
        return result
    assert result is False #should be False when moving to next machine
    buffPtr=0
    return result

def defineSymTable(s):
    global symTable
    if symTable is not None:
        print "Warning! Symbol table has already been defined. Overriding"
    symTable=s

def feedLexer(sourceString):
    global symTable
    if symTable is None:
        print "Error! must pass in symbol table with defineSymTable(s) first"
        assert(False)
    assert type(sourceString) is str
    global buff
    buff+=list(sourceString)

# Get the next token
#returns:
#   None if there are no complete tokens in the buffer
#   The three tuple of the next token if the next token exists
def getToken():
    global buff
    global buffPtr
    global machines
    if len(buff) is 0:
        return "noTokens"

    machineResult=False
    i=0
    while machineResult is False and i < len(machines):
        machineResult=tryMachine(machines[i])
        i+=1
    
	if machineResult is None: #machine passed by a non-token generating substring
		return None
	#false if all else fails
    if machineResult is False:
        #remove 1 element of buffer to move past bad char. TODO will this cause any errors?
        lexeme=buff[0]
        buff=buff[1:]
        return {'tokenType':"lexerr", 'lexeme':lexeme, 'attribute':"Unrecognized Symbol"}
    assert type(machineResult) is dict
    if bool(machineResult) is True: #the result was not tokenless
    	return machineResult

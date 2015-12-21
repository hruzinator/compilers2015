#!/usr/bin/python
'''
Lexer for compiler
'''
from types import *
import sys

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
            return
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

counter=0 #a counter available for use by some of the machines

#define whitespace machine
wsMachine=LexerFSM()
def handle(c):
    assert type(c) is str and len(c)==1
    if c == ' ' or c == '\t' or c == '\b': return {}
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
    if c == '\n': return {}
    else:
        global buffPtr
        buffPtr-=1
        return None
nlMachine.addState("__start__", handle)
nlMachine.setStart("__start__")
machines.append(nlMachine)

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
    if c == '>': return {'tokenType': "RELOP", 'lexeme':"<>", 'attribute':"notEquals"}
    elif c == '=': return {'tokenType': "RELOP", 'lexeme':"<=", 'attribute':"lessThanOrEquals"}
    else:
        global buffPtr
        buffPtr-=1
        return {'tokenType': "RELOP", 'lexeme':"<", 'attribute':"lessThan"}
relopMachine.addState("<", handle)
def handle(c): #'>'
    assert type(c) is str and len(c)==1
    if c == '=': return {'tokenType': "RELOP", 'lexeme':">=", 'attribute':"greaterThanOrEquals"}
    else:
        global buffPtr
        buffPtr-=1
        return {'tokenType': "RELOP", 'lexeme':">", 'attribute':"greaterThan"}
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
    if c == "=": return {'tokenType': "ASSIGNOP", 'lexeme':":=", 'attribute':"assignTo"}
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
        buffPtr-=2
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
        return {'tokenType': "ADDOP", 'lexeme':'or', 'attribute':"booleanOr"}
addopMachine.addState("or", handle)
addopMachine.setStart("__start__")
machines.append(addopMachine)

#define multOp machine
multopMachine=LexerFSM()
def handle(c):
    global buff
    global buffPtr
    assert type(c) is str and len(c)==1
    if c == '*': return {'tokenType': "MULTOP", 'lexeme':'*', 'attribute':"multiply"}
    elif c == '/': return {'tokenType':"MULTOP", 'lexeme':"/", 'attribute':"divide"}
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
            return {'tokenType':"MULTOP", 'lexeme':"div", 'attribute':"integerDivide"}
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
            return {'tokenType':"MULTOP", 'lexeme':"mod", 'attribute':"modulo"}
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
            return {'tokenType':"multop", 'lexeme':"and", 'attribute':"booleanAnd"}
        else:
            buffPtr-=1
            return None
    else:
        buffPtr-=1
        return None
multopMachine.addState("__start__", handle)
multopMachine.setStart("__start__")
machines.append(multopMachine)


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
#note: only longreal machine has to perform length checks, as any errors with lengths will be checked here. If
#we were to put this in the other machines, which run after, it would be redundant and never run.
lrMachine=LexerFSM()
def handle(c): #start
    assert type(c) is str and len(c)==1
    d=ord(c)
    #check if d is a number
    if (48<=d<=57):
        global counter
        counter=1
        return  "x"
    else:
        global buffPtr
        buffPtr-=1
        return None
lrMachine.addState("__start__", handle)

def handle(c):#x
    assert type(c) is str and len(c)==1

    global buffPtr
    global buff
    global counter
    lexeme="".join(buff[:buffPtr])

    
    d=ord(c)
    #check if d is a number
    if (48<=d<=57):
        if counter>=5:
            return {'tokenType':"LEXERR", 'lexeme':lexeme, 'attribute':"Extra Long Integer"} 
        counter+=1
        return  "x"
    elif c is '.':
        if lexeme[0]=='0':
            return {'tokenType':"LEXERR", 'lexeme':lexeme, 'attribute':"trailing zeroes in integer part"}
        counter=0
        return "y"
    else:
        buffPtr=0
        return None
lrMachine.addState("x", handle)
def handle(c):#y
    assert type(c) is str and len(c)==1

    global buff
    global buffPtr
    global counter
    lexeme="".join(buff[:buffPtr]) 

    d=ord(c)
    #check if d is a number
    if (48<=d<=57):
        if counter>=5:
            return {'tokenType':"LEXERR", 'lexeme':lexeme, 'attribute':"Extra Long Fractional Part"}
        counter+=1
        return  "y"
    elif c is 'E' and counter is not 0:
        if lexeme[-1]=='0':
            return {'tokenType':"LEXERR", 'lexeme':lexeme, 'attribute':"trailing zeroes in fractional part"}
        counter=0
        return "z"
    else:
        if lexeme[-1]=='0':
            return {'tokenType':"LEXERR", 'lexeme':lexeme, 'attribute':"trailing zeroes in fractional part"}
        buffPtr=0
        return None
lrMachine.addState("y", handle)
def handle(c):#z
    assert type(c) is str and len(c)==1

    global buffPtr
    global buff
    global counter
    lexeme="".join(buff[:buffPtr])

    d=ord(c)
    #check if d is a number
    if (48<=d<=57):
        if counter>=2:
            return {'tokenType':"LEXERR", 'lexeme':lexeme, 'attribute':"Extra Long Exponent part"} 
        counter+=1
        return  "z"
    else:
        if counter==0:
            buffPtr-=1
            return None
        if lexeme[-1]=='0':
            return {'tokenType':"LEXERR", 'lexeme':lexeme, 'attribute':"trailing zeroes in exponential part"}
        lexeme="".join(buff[:buffPtr])
        buffPtr-=1
        return {'tokenType':"NUMBER", 'lexeme':lexeme, 'attribute':"longReal"}
lrMachine.addState("z", handle)
lrMachine.setStart("__start__")
machines.append(lrMachine)

#define reals machine (must be before ints to ensure we don't ppremeturely tokenize an int out of a real)
rMachine=LexerFSM()
def handle(c): #start
    assert type(c) is str and len(c)==1
    d=ord(c)
    # check if d is a number
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
        global counter
        counter=0 #ensure we have > 0 y digits following
        return "y"
    else:
        global buffPtr
        buffPtr-=1
        return None
rMachine.addState("x", handle)
def handle(c):#y
    global counter
    assert type(c) is str and len(c)==1
    d=ord(c)
    #check if d is a number
    if (48<=d<=57):
        counter+=1
        return  "y"
    else:
        global buffPtr
        if counter==0:
            buffPtr-=1
            return None
        global buff
        lexeme="".join(buff[:buffPtr])
        buffPtr-=1
        return {'tokenType':"NUMBER", 'lexeme':lexeme, 'attribute':"realNum"}
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
        return {'tokenType':"NUMBER", 'lexeme':lexeme, 'attribute':"intNum"}
intMachine.addState("num", handle)
intMachine.setStart("__start__")
machines.append(intMachine)

#define ID machine
idMachine=LexerFSM()
def handle(c): #start
    global buffPtr
    assert type(c) is str and len(c)==1
    #convert c to ascii number representation
    l=ord(c)
    #check if l is a capital or lowercase letter
    if (65<=l<=90) or (97<=l<=122):
        global counter
        counter=1
        return  "letterNum"
    else:
        buffPtr-=1
        return None
idMachine.addState("__start__", handle)
def handle(c): #letterNum
    assert type(c) is str and len(c)==1

    global buffPtr
    global buff
    global counter
    lexeme="".join(buff[:buffPtr])

    if counter>10:
        return {'tokenType':"LEXERR", 'lexeme':lexeme, 'attribute':"Extra Long Identifier"} 

    ld=ord(c)
    #check if ld is a letter
    if (65<=ld<=90) or (97<=ld<=122):
        counter+=1
        return  "letterNum"
    #check if ld is a number
    elif (48<=ld<=57):
        counter+=1
        return  "letterNum"
    else:
        buffPtr-=1
		#check if lexeme is a reserved word
        result=reservedWordTable.lookup(lexeme)
        if result is not None:
            return result
        token={'tokenType':"ID", 'lexeme':lexeme, 'attribute':""} 
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


#define keyword machine
catchAllMachine=LexerFSM()
def handle(c):#start state
    assert type(c) is str and len(c)==1
    global buff
    global buffPtr
    if ord(c) is 3 :  #end of file
    	return {'tokenType':'EOF', 'lexeme':"$", 'attribute':"endOfFile"}
    seq=c
    while reservedWordTable.hasStartsWith(seq):
        buffPtr+=1
        if buffPtr >= len(buff):
            break
        seq+=buff[buffPtr]

    if len(seq) is not 1: #did not got through loop
        buffPtr-=1
        seq=seq[:-1]
    lookupResult = reservedWordTable.lookup(seq)
    if lookupResult is not None:
        return lookupResult
    else:	
	   return {'tokenType':"LEXERR", 'lexeme':seq, 'attribute':"Unrecognized Symbol"}
catchAllMachine.addState("__start__", handle)
catchAllMachine.setStart("__start__")
machines.append(catchAllMachine)


#symbol tables
from symbolTable import symbolTable
symTable = symbolTable()
reservedWordTable = None

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

def defineReservedWordTable(s):
    global reservedWordTable
    if reservedWordTable is not None:
        print "Warning! Symbol table has already been defined. Overriding"
    reservedWordTable=s

def feedLexer(sourceString):
    global reservedWordTable
    if reservedWordTable is None:
        print "Error! must pass in reserved word table with defineReservedWordTable(s) first"
        sys.exit()
    assert type(sourceString) is str
    global buff
    buff+=list(sourceString)

# Get the next token
#returns:
#   None if there are no complete tokens in the buffer.
#   The three tuple of the next token if the next token exists
def getToken():
    global buff
    global buffPtr
    global machines

    isToken = False
    while not isToken:

        if len(buff) is 0:
            return "noTokens"

        machineResult=False
        i=0
        #try all the machines
        while (machineResult is False or machineResult is None) and i < len(machines):
            machineResult=tryMachine(machines[i])
            i+=1
    
	#check if machineResult is a non-empty token
	if type(machineResult) is dict and bool(machineResult) is True:
	    isToken = True
    #if machineResult['tokenType'] is 'LEXERR':       
	#print "Lexical Error! " + str(machineResult['lexeme'])+ " is not a valid token."
        #sys.exit()
    return machineResult

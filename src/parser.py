'''
Takes as input a list of tokens and outputs a parse tree based on the grammar. The grammar has been transformed into an LL(1) grammar. 
'''
	
tok = None
lexer = None
symTable = None
rwTable = None

def setup(l, rwt):
	global lexer
	global symTable
	global rwTable
	lexer = l
	symTable = l.symTable
	rwTable = rwt
'''
checks to see if the current token's lexeme matches the string, t
'''
def matchByLexeme(t):
	#TODO continue to build parse tree
	global tok
	assert type(tok) is dict
	if tok['lexeme']==t:
		if tok['tokenType']=='EOF':
			print "Parsing is complete"
			return
		else: #get next token
			tok = lexer.getToken() 
	else: #syntax error
		print "Syntax error! Expecting " + t + ", got " + str(tok['lexeme'])
		tok = lexer.getToken()
		matchByLexeme(t)

def matchByType(t):
	#TODO continue to build parse tree
	global tok
	assert type(tok) is dict
	if tok['tokenType']==t:
		if tok['tokenType']=='EOF':
			print "Parsing is complete"
			return
		else: #get next token
			tok = lexer.getToken() 
	else: #syntax error
		print "Syntax error! Expecting token of type " + t + ", got a token of type " + str(tok['tokenType'])
		tok = lexer.getToken()
		matchByType(t)

#TODO implement production methods here
def identifier_list1():
	global tok
	if tok['lexeme'] is ",":
		matchByLexeme(',')
		matchByType('ID')
	elif tok['lexeme'] is ")":	
		return
	else:
		print "Syntax error! Expecting \')\' or \',\', got " + str(tok['lexeme'])	
		tok = lexer.getToken()
		identifier_list1()
	return

def identifier_list():
	matchByType('ID')
	identifier_list1()	
	return

def program1():
	global tok
	if tok['lexeme'] is "var":
		declarations()
		program1_1()
	elif tok['lexeme'] is "function":
		subprogram_declarations()
		
	elif tok['lexeme'] is "begin":
	return

def program():
	#TODO one unified way of matching tokens
	matchByLexeme('program')
	matchByType('ID')
	matchByLexeme('(')
	identifier_list()
	matchByLexeme(')')
	matchByLexeme(';')
	program1()
	return



#begins the main work of parsing
def parse():
	global tok
	tok = lexer.getToken()
	program() #starting production
	matchByType('EOF')




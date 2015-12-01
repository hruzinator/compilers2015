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
checks to see if the current token matches t
'''
def match(t):
	global tok
	assert type(tok) is dict
	if tok==t:
		if t['tokenType']=='EOF':
			print "Parsing is complete"
			return
		else:
			#TODO modify lexer and main to use this method?
			tok = lexer.getToken() 
	else: #syntax error
		print "Syntax error! Expecting " + str(t['lexeme']) + " got " + str(tok['lexeme']) + "."
		tok = lexer.getToken()

#TODO implement production methods here
def program():
	return

#begins the main work of parsing
def parse():
	global tok
	tok = lexer.getToken()
	#program() #starting production
	#TODO externalize token types
	match(rwTable.lookup('$'))




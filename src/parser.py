'''
Takes as input a list of tokens and outputs a parse tree based on the grammar. The grammar has been transformed into an LL(1) grammar. 
'''

'''
checks to see if the current token matches t
'''
tok = ''

fun match(t):
	global tok
	if tok==t:
		t['tokenType']=='EOF':
			#TODO parse is complete
			pass
		else:
			tok = gettoken() #TODO modify lexer and main to use this method?
	else: #syntax error
		print "Syntax error! Expecting " + t + " got " + tok "."
		tok = gettoken()

#TODO implement production methods here

#begins the main work of parsing
fun parse():
	global tok
	tok = gettoken()
	call program()

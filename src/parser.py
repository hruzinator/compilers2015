'''
Takes as input a list of tokens and outputs a parse tree based on the grammar. The grammar has been transformed into an LL(1) grammar. 
'''

import sys
	
tok = None
lexer = None
symTable = None
rwTable = None
#flag to indicate if code is syntax error free
hasSyntaxErrors = False

def setup(l, rwt):
	global lexer
	global symTable
	global rwTable
	lexer = l
	symTable = l.symTable
	rwTable = rwt

#a single class that handles syntax errors (to reduce redundant code). expectedVals is a list of strings that will be
#placed in the error message when the error message lists the things it was expecting to see.
def syntaxError(expectedVals):
	global tok
	print tok #TODO remove
	hasSyntaxErrors = True
	assert type(expectedVals) is list
	if tok['tokenType']=='EOF':
		print "Syntax error! Expected lexemes are [" + ', '.join(str(v) for v in expectedVals) + "] Got End of file."
		print "Parsing completed with errors"
		sys.exit()
	print "Syntax error! Expected lexemes are [" + ', '.join(str(v) for v in expectedVals) + "]. Got " + str(tok['lexeme'])
	tok = lexer.getToken()

'''
begin match methods
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
		syntaxError([t])
		matchByLexeme(t)

def matchByType(t):
	#TODO continue to build parse tree
	global tok
	assert type(tok) is dict
	if tok['tokenType']==t:
		if tok['tokenType']!='EOF':
			tok = lexer.getToken() 
	else: #syntax error
		print tok #TODO remove
		print "Syntax error! Expecting token of type " + t + ", got \'" + str(tok['lexeme']) + "\' of type " + str(tok['tokenType'])
		tok = lexer.getToken()
		matchByType(t)

'''
Begin production methods
'''
def sign():
	global tok
	if tok['lexeme']=='+'
		matchByLexeme('+')
	elif tok['lexeme']=='-':
		matchByLexeme('-')
	else:
		syntaxError(['+', '-'])
		sign()

def factor1():
	global tok
	if tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' or tok['lexeme']=='else' or tok['lexeme']=='[' or tok['lexeme']==']' or tok['tokenType']=='MULTOP' or tok['tokenType']=='ADDOP' or tok['tokenType']=='RELOP' or tok['tokenType']=='MULTOP' or tok['lexeme']=='then' or tok['lexeme']=='do':
		variable1()
	elif tok['lexeme']=='(':
		matchByLexeme('(')
		expression_list()
		
	else:
		syntaxError([',', ')', ';', 'end', 'else', '[', ']', 'then', 'do', 'type: MULTOP', 'type: ADDOP', 'type: MULTOP'])
		factor1()

def factor():
	global tok
	if tok['lexeme']=='(':
		matchByLexeme('(')
		expression()
		matchByLexeme(')')
	elif tok['lexeme']=='not':
		matchByLexeme('not')
		factor()
	elif tok['tokenType']=='ID':
		matchByType('ID')
		factor1()
	elif tok['tokenType']=='NUMBER':
		matchByType('NUMBER')
	else:
		syntaxError(['(', ')', 'not', 'type: ID', 'type: NUMBER'])
		factor()

def term1():
	global tok
	if tok['tokenType']=='MULTOP':
		matchByType("MULTOP")
		factor()
		term1()
	elif tok['tokenType']=='ADDOP' or tok['tokenType']=='RELOP' or tok['lexeme']==';' or tok['lexeme']=='else' or tok['lexeme']=='end' or tok['lexeme']=='then' or tok['lexeme']=='do' or tok['lexeme']==']' or tok['lexeme']==',' or tok['lexeme']==')':
		return
	else:
		syntaxError([';', 'else', 'end', 'then', 'do', ']', ',', ')', 'type: ADDOP', 'type: RELOP', 'type: MULTOP'])
		term1()

def term():
	global tok
	if tok['lexeme']=='(' or tok['lexeme']=='not' or tok['tokenType']=='ID' or tok['tokenType']=='NUMBER':
		factor()
		term1()
	else:
		syntaxError(['(', 'not', 'ID', 'NUMBER'])
		term()

def simple_expression1():
	global tok
	tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' or tok['lexeme']=='else' or tok['lexeme']==']' or tok['lexeme']=='then' or tok['lexeme']=='do' or tok['tokenType']=='RELOP':
		return
	elif tok['tokenType']=='ADDOP':
		matchByType('ADDOP')
		term()
		simple_expression1()
	else:
		syntaxError([',', ')', ';', 'end', 'else', ']', 'then', 'do', 'type: RELOP', 'type: ADDOP'])
		simple_expression1()

def simple_expression():
	global tok
	if tok['tokenType']=='ID' or tok['lexeme']=='(' or tok['lexeme']=='not' or tok['tokenType']=='NUMBER':
		term()
		simple_expression1()
	elif tok['lexeme']=='+' or tok['lexeme']=='-':
		sign()
		term()
		simple_expression1()
	else:
		syntaxError(['type: ID', '(', '+', '-', 'not', 'type: NUMBER'])
		simple_expression()

def expression1():
	global tok
	if tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' or tok['lexeme']=='else' or tok['lexeme']==']' or tok['lexeme']=='then' or tok['lexeme']=='do':
		return
	elif tok['tokenType']=='RELOP':
		matchByType('RELOP')
		simple_expression()
	else:
		syntaxError([',', ')', ';', 'end', 'else', ']', 'then', 'do', 'type: RELOP'])
		expression1()

def expression():
	global tok
	if tok['tokenType']=='ID' or tok['lexeme']=='(' or tok['lexeme']=='+' or tok['lexeme']=='-' or tok['lexeme']=='not' or tok['tokenType']=='NUMBER':
		simple_expression()
		expression1()
	else:
		syntaxError(['type: ID', '(', '+', '-', 'not', 'type: NUMBER'])
		expression()

def expression_list1():
	global tok
	if tok['lexeme']==',':
		matchByLexeme(',')
		expression()
	elif tok['lexeme']==')':
		return
	else:
		syntaxError([',', ')'])
		expression_list1()

def expression_list():
	global tok
	if tok['tokenType']=='ID' or tok['lexeme']=='(' or tok['lexeme']=='+' or tok['lexeme']=='-' or tok['lexeme']=='not' or tok['tokenType']=='NUMBER':
		expression()
		expression_list1()
	else:
		syntaxError(['type: ID', '(', '+', '-', 'not', 'type: NUMBER'])
		expression_list()

def variable1():
	global tok
	if tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' or tok['lexeme']=='else' or tok['lexeme']==']' or tok['tokenType']=='ASSIGNOP' or tok['tokenType']=='MULTOP' or tok['tokenType']=='ADDOP' or tok['tokenType']=='RELOP' or tok['lexeme']=='then' or tok['lexeme']=='do':
		return
	elif tok['lexeme']=='[':
		matchByLexeme('[')
		expression()
		matchByLexeme(']')
	else:
		syntaxError([])
		variable1()

def variable():
	global tok
	if tok['tokenType']=='ID':
		matchByType('ID')
		variable1()
	else:
		syntaxError(['type: ID'])
		variable()

def statement1():
	global tok
	if tok['lexeme']==';' or tok['lexeme']=='end':
		return
	elif tok['lexeme']=='else':
		matchByLexeme('else')
		statement()
	else:
		syntaxError([';', 'end', 'else'])
		statement1()

def statement():
	global tok
	if tok['lexeme']=='begin':
		compound_statement()
	elif tok['tokenType']=='ID':
		variable()
		matchByType('ASSIGNOP')
		expression()
	elif tok['lexeme']=='if':
		matchByLexeme('if')
		expression()
		matchByLexeme('then')
		statement()
		statement1()
	elif tok['lexeme']=='while':
		matchByLexeme('while')
		expression()
		matchByLexeme('do')
		statement()
	else:
		syntaxError(['begin', 'if', 'while'])
		statement()

def statement_list1():
	global tok
	if tok['lexeme']==';':
		statement()
		statement_list1()
	elif tok['lexeme']=='end':
		return
	else:
		syntaxError([';', 'end'])

def statement_list():
	global tok
	if tok['lexeme']=='begin' or tok['lexeme']=='if' or tok['lexeme']=='while' or tok['tokentype']=='ID':
		statement()
		statement_list1()
	else:
		syntaxError(['begin', 'if', 'while', 'type: ID'])
		statement_list()

def compound_statement1():
	global tok
	if tok['lexeme']=='begin' or tok['lexeme']=='if' or tok['lexeme']=='while' or tok['tokentype']=='ID':
		statement_list()
		matchByLexeme('end')
	elif tok['lexeme']=='end':
		matchByLexeme('end')
	else:
		syntaxError(['begin', 'if', 'while', 'end', 'type: ID'])
		compound_statement1()

def compound_statement():
	global tok
	if tok['lexeme']=='begin':
		matchByLexeme('begin')
		compound_statement1()
	else:
		syntaxError(['begin'])
		compound_statement()

def parameter_list1():
	global tok
	if tok['lexeme']==')':
		return
	elif tok['lexeme']==';':
		matchByLexeme(";")
		matchByType("ID")
		matchByLexeme(":")
		typeProd()
		parameter_list1()
	else:
		syntaxError([')', ';'])
		parameter_list1()


def parameter_list():
	global tok
	if tok['tokenType']=="ID":
		matchByByType('ID')
		matchByLexeme(':')
		typeProd()
		parameter_list1()
	else:
		syntaxError(['type: ID'])
		parameter_list()

def subprogram_head1():
	global tok
	if tok['lexeme']=='(':
		matchByLexeme('(')
		parameter_list()
		matchByLexeme(')')
		matchByLexeme(':')
		standard_type()
		matchByLexeme(';')
	elif tok['lexeme']==':':
		matchByLexeme(':')
		standard_type()
		matchByLexeme(';')
	else:
		syntaxError(['(', ':'])
		subprogram_head1()

def subprogram_head():
	global tok
	if tok['lexeme']=='function':
		matchByLexeme('function')
		matchByType('ID')
		subprogram_head1()
	else:
		syntaxError(['function'])
		subprogram_head()

def subprogram_declaration1_1():
	global tok
	if tok['lexeme']=='function':
		subprogram_declarations()
		compound_statement()
	elif tok['lexeme']=='begin':
		compound_statement()
	else:
		syntaxError(['function', 'begin'])
		subprogram_declaration1_1()

def subprogram_declaration1():
	global tok
	if tok['lexeme']=='var':
		declarations()
		subprogram_declaration1()
	elif tok['lexeme']=='function':
		subprogram_declarations()
		compound_statement()
	elif tok['lexeme']=='begin':
		compound_statement()
	else:
		syntaxError(['var', 'function', 'begin'])
		subprogram_declaration1()

def subprogram_declaration():
	global tok
	if tok['lexeme']=='function':
		subprogram_head()
		subprogram_declaration1()
	else:
		syntaxError(['function'])
		subprogram_declaration()

def subprogram_declarations1():
	global tok
	if tok['lexeme']=='function':
		subprogram_declaration()
		matchByLexeme(';')
		subprogram_declarations1()
	elif tok['lexeme']=='begin':	
		return
	else:
		syntaxError(['function', 'begin'])
		subprogram_declarations1()

def subprogram_declarations():
	global tok
	if tok['lexeme']=='function':
		subprogram_declaration()
		matchByLexeme(';')
		subprogram_declarations1()
	else:
		syntaxError(['function'])
		subrpogram_declarations()

def standard_type():
	global tok
	if tok['lexeme']=='integer':
		matchByLexeme('integer')
	elif tok['lexeme']=='real':
		matchByLexeme('real')
	else:
		syntaxError(['integer', 'real'])
		standard_type()

def typeProd():
	global tok
	if tok['lexeme']=='integer' or tok['lexeme']=='real':
		standard_type()
	elif tok['lexeme']=='array':
		matchByLexeme('array')
		matchByLexeme('[')
		matchByType('NUMBER')
		matchByLexeme('..')
		matchByType('NUMBER')
		matchByLexeme(']')
		matchByLexeme('of')
		standard_type()
	else:
		syntaxError(['integer', 'real', 'array'])
		typeProd()

def declarations1():
	global tok
	if tok['lexeme']=='var':
		matchByLexeme('var')
		matchByType('ID')
		matchByLexeme(':')
		typeProd()
		matchByLexeme(';')
		declarations1()
	elif tok['lexeme']=='function' or tok['lexeme']=='begin':
		return
	else:
		syntaxError(['var', 'function', 'begin'])
		declarations1()

def declarations():
	global tok
	if tok['lexeme']=='var':
		matchByLexeme('var')
		matchByType('ID')
		matchByLexeme(":")
		typeProd()
		matchByLexeme(";")
		declarations1()
	else:
		syntaxError(['var'])
		declarations()

def identifier_list1():
	global tok
	if tok['lexeme']==",":
		matchByLexeme(',')
		matchByType('ID')
	elif tok['lexeme']==")":	
		return
	else:
		syntaxError([')', ','])	
		identifier_list1()

def identifier_list():
	global tok
	if tok['tokenType']=="ID":
		matchByType('ID')
		identifier_list1()
	else:
		syntaxError(['type: ID'])
		identifier_list()

def program1_1():
	global tok
	if tok['lexeme']=='function':	
		subprogram_declarations()
		compound_statement()
		matchByLexeme('.')
	elif tok['lexeme']=='begin':	
		compound_statement()
		matchByLexeme('.')
	else:
		syntaxError(['function', 'begin'])
		program1_1()

def program1():
	global tok
	if tok['lexeme']=="var":
		declarations()
		program1_1()
	elif tok['lexeme']=="function":
		subprogram_declarations()
		compound_statement()
		matchByLexeme('.')
		
	elif tok['lexeme']=="begin":
		compound_statement()
		matchByLexeme('.')
	else:
		syntaxError(["var", "function", "begin"])
		program1()
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
	if hasSyntaxErrors is True:
		print "Parsing completed with errors"
		sys.exit()
	else:
		print "Parsing is complete"


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

def finish():
	if hasSyntaxErrors is True:
		print "Parsing completed with errors"
		sys.exit()
	else:
		print "Parsing is complete"
		sys.exit()

def synch(lexemes, types):
	assert type(lexemes) is list and type(types) is list
	global tok

	while tok['lexeme'] not in lexemes and tok['tokenType'] not in types:
		hasSyntaxErrors = True
		print "discarding token: " + str(tok)
		#print "Syntax Error: Got " + tok['lexeme'] + " of type " + tok['tokenType'] + ". Expecting  lexemes " + \
		#	str(lexemes) + " or types " + str(types) #TODO have it not print out EOF
		if tok['tokenType'] == 'EOF':
			print "Parsing completed with errors"
			sys.exit()
		elif tok['lexeme'] == ';': #just brace for a new line
			tok = lexer.getToken()
			break
		tok = lexer.getToken()

def syntaxError(expected, actual):
	assert type(expected) is str and type(actual) is str
	print "Syntax error! expecting " + expected + ", got " + actual

'''
begin match methods
'''
def matchByLexeme(t):
	global tok
	assert type(tok) is dict
	if tok['lexeme']==t:
		if tok['tokenType']!='EOF': #do not overrun the buffer
			print "matched: " + str(tok)
			tok = lexer.getToken()
		else:
			finish()
	else: #syntax error
		hasSyntaxErrors = True
		syntaxError(t, tok['lexeme'])
		tok = lexer.getToken()

def matchByType(t):
	#TODO continue to build parse tree
	global tok
	assert type(tok) is dict
	if tok['tokenType']==t:
		if tok['tokenType']!='EOF': #do not overrun the buffer
			print "matched: " + str(tok)
			tok = lexer.getToken() 
		else:
			finish()
			sys.exit() #TODO is this what we need?
	else: #syntax error
		hasSyntaxErrors = True
		syntaxError(t, tok['tokenType'])
		tok = lexer.getToken()

'''
Begin production methods
'''
def sign():
	global tok
	if tok['lexeme']=='+':
		matchByLexeme('+')
	elif tok['lexeme']=='-':
		matchByLexeme('-')
	else:
		syntaxError("+ or -", tok['lexeme'])
		synch(['+', '-', '(' , 'not'], ['ID', 'NUMBER'])
		if tok['lexeme'] in ['+', '-']: #first
			sign()
			return
		elif tok['lexeme'] in ['(', 'not'] or tok['tokenType'] in ['ID', 'NUMBER']: #follow
			return
		else:
			print "An error occurred. Check your synch set"
			assert False

def factor1():
	global tok
	if tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' \
	or tok['lexeme']=='else' or tok['lexeme']=='[' or tok['lexeme']==']' or \
	tok['tokenType']=='MULTOP' or tok['tokenType']=='ADDOP' or tok['tokenType']=='RELOP' \
	or tok['lexeme']=='then' or tok['lexeme']=='do':
		variable1()
	elif tok['lexeme']=='(':
		matchByLexeme('(')
		expression_list()
		matchByLexeme(')')
	else:
		syntaxError("factor1", tok['lexeme'])
		synch([',', ')', ';', 'end', 'else', '[', ']', 'then', 'do'], ['MULTOP', 'ADDOP', 'RELOP'])
		if tok['lexeme'] in ['(', '[', ';', 'else', 'end', 'then', 'do', ']', ',', ')'] or \
			tok['tokenType'] in ['MULTOP', 'RELOP', 'ADDOP']: #first or follow
			factor1() #TODO is this right?
			return
		else:
			print "An error occurred. Check your synch set"
			assert False

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
		syntaxError("factor", tok['lexeme'])
		synch(['(', ')', 'not', ';', 'else', 'end', 'then', 'do', ']', ',', ')'], \
		['NUMBER', 'MULTOP', 'ADDOP', 'RELOP'])
		if tok['lexeme'] in ['(', 'not'] or tok['tokenType'] in ['NUMBER', 'ID']: #first
			factor()
		return #else, follow. We want to return after factor anyway to help us in project 3

def term1():
	global tok
	if tok['tokenType']=='MULTOP':
		matchByType("MULTOP")
		factor()
		term1()
	elif tok['tokenType']=='ADDOP' or tok['tokenType']=='RELOP' or tok['lexeme']==';' \
	or tok['lexeme']=='else' or tok['lexeme']=='end' or tok['lexeme']=='then' or \
	tok['lexeme']=='do' or tok['lexeme']==']' or tok['lexeme']==',' or tok['lexeme']==')' \
	or tok['tokenType']=='EOF': #TODO REMOVE EOF from term1! For testing only!!!
		return
	else:
		syntaxError("term1", tok['lexeme'])
		synch([';', 'else', 'end', 'then', 'do', ']', ',', ')'], ['ADDOP', 'RELOP', 'MULTOP'])
		if tok['tokenType'] == 'MULTOP':
			term1()
		return

def term():
	global tok
	if tok['lexeme']=='(' or tok['lexeme']=='not' or tok['tokenType']=='ID' or tok['tokenType']=='NUMBER':
		factor()
		term1()
	else:
		syntaxError("term", tok['lexeme'])
		synch(['(', 'not', ';', 'else', 'end', 'then', 'do', ']', ',', ')'], ['ID', 'NUMBER', 'ADDOP', 'RELOP'])
		if tok['lexeme'] in ['not', '('] or tok['tokenType'] in ['ID', 'NUMBER']:
			term()
		return

def simple_expression1():
	global tok
	if tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' \
	or tok['lexeme']=='else' or tok['lexeme']==']' or tok['lexeme']=='then' \
	or tok['lexeme']=='do' or tok['tokenType']=='RELOP':
		return
	elif tok['tokenType']=='ADDOP':
		matchByType('ADDOP')
		term()
		simple_expression1()
	else:
		syntaxError("simple_expression1", tok['lexeme'])
		synch([',', ')', ';', 'end', 'else', ']', 'then', 'do'], ['RELOP', 'ADDOP'])
		if tok['tokenType'] == 'ADDOP':
			simple_expression1()
		return

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
		syntaxError("simple_expression", tok['lexeme'])
		synch(['(', '+', '-', 'not'], ['ID', 'NUMBER'])
		if tok['lexeme'] in ['(', 'not', '+', '-'] or tok['tokenType'] in ['NUMBER', 'ID']:
			simple_expression()
		return

def expression1():
	global tok
	if tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' or \
	tok['lexeme']=='else' or tok['lexeme']==']' or tok['lexeme']=='then' or tok['lexeme']=='do':
		return
	elif tok['tokenType']=='RELOP':
		matchByType('RELOP')
		simple_expression()
	else:
		syntaxError("expression1", tok['lexeme'])
		synch([',', ')', ';', 'end', 'else', ']', 'then', 'do'], ['RELOP'])
		if tok['tokenType'] == 'RELOP':
			expression1()
		return

def expression():
	global tok
	if tok['tokenType']=='ID' or tok['lexeme']=='(' or tok['lexeme']=='+' or \
	tok['lexeme']=='-' or tok['lexeme']=='not' or tok['tokenType']=='NUMBER':
		simple_expression()
		expression1()
	else:
		syntaxError("expression", tok['lexeme'])
		synch(['(', '+', '-', 'not', 'else', 'then', 'end', 'do', ']', ',', ')', ';'], ['NUMBER', 'ID'])
		if tok['lexeme'] in ['(', 'not', '+', '-'] or tok['tokenType'] in ['ID', 'NUMBER']:
			expression()
		return

def expression_list1():
	global tok
	if tok['lexeme']==',':
		matchByLexeme(',')
		expression()
	elif tok['lexeme']==')':
		return
	else:
		syntaxError("expression_list1", tok['lexeme'])
		synch([',', ')'])
		if tok['lexeme'] == ',':
			expression_list1()
		return

def expression_list():
	global tok
	if tok['tokenType']=='ID' or tok['lexeme']=='(' or tok['lexeme']=='+' or tok['lexeme']=='-'\
	or tok['lexeme']=='not' or tok['tokenType']=='NUMBER':
		expression()
		expression_list1()
	else:
		syntaxError("expression_list", tok['lexeme'])
		synch(['(', '+', '-', 'not', ')'], ['ID', 'NUMBER'])
		if tok['lexeme'] in ['(', 'not', '+', '-'] or tok['tokenType'] in ['ID', 'NUMBER']:
			expression_list()
		return

def variable1():
	global tok
	if tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' \
	or tok['lexeme']=='else' or tok['lexeme']==']' or tok['tokenType']=='ASSIGNOP' or \
	tok['tokenType']=='MULTOP' or tok['tokenType']=='ADDOP' or tok['tokenType']=='RELOP' or \
	tok['lexeme']=='then' or tok['lexeme']=='do':
		return
	elif tok['lexeme']=='[':
		matchByLexeme('[')
		expression()
		matchByLexeme(']')
	else:
		syntaxError("variable1", tok['lexeme'])
		synch(['[', 'else', 'end', 'then', 'do', ']', ',', ')', ';'], ['ASSIGNOP', 'MULTOP', 'ADDOP', 'RELOP'])
		variable1()

def variable():
	global tok
	if tok['tokenType']=='ID':
		matchByType('ID')
		variable1()
	else:
		syntaxError("an identifier", tok['lexeme'])
		synch([], ['ID', 'ASSIGNOP'])
		if tok['tokenType']=='ID':
			variable()
		return

def statement1():
	global tok
	if tok['lexeme']==';' or tok['lexeme']=='end':
		return
	elif tok['lexeme']=='else':
		matchByLexeme('else')
		statement()
	else:
		syntaxError("statement1", tok['lexeme'])
		synch([';', 'end', 'else'])
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
		syntaxError("statement", tok['lexeme'])
		synch(['begin', 'if', 'while', 'else', 'end'], ['ID'])
		if tok['lexeme'] in ['begin', 'if', 'while'] or tok['tokenType']=='ID':
			statement()
		return

def statement_list1():
	global tok
	if tok['lexeme']==';':
		statement()
		statement_list1()
	elif tok['lexeme']=='end':
		return
	else:
		syntaxError("statement_list1", tok['lexeme'])
		synch([';', 'end'], [])
		statement_list1()
		return

def statement_list():
	global tok
	if tok['lexeme']=='begin' or tok['lexeme']=='if' or tok['lexeme']=='while' or tok['tokenType']=='ID':
		statement()
		statement_list1()
	else:
		syntaxError("statement_list", tok['lexeme'])
		synch(['begin', 'if', 'while'], ['ID'])
		if tok['lexeme']!='end': #just easier
			statement_list()
		return

def compound_statement1():
	global tok
	if tok['lexeme']=='begin' or tok['lexeme']=='if' or tok['lexeme']=='while' or tok['tokenType']=='ID':
		statement_list()
		matchByLexeme('end')
	elif tok['lexeme']=='end':
		matchByLexeme('end')
	else:
		syntaxError("compound_statement1", tok['lexeme'])
		synch(['begin', 'if', 'while', 'end', '.', ';'], ['ID'])
		#again, easier.excluding end as I want to try it as FIRST first
		if tok['lexeme'] not in ['.', ';', 'else']:
			compound_statement1()
		return

def compound_statement():
	global tok
	if tok['lexeme']=='begin':
		matchByLexeme('begin')
		compound_statement1()
	else:
		syntaxError("compound_statement", tok['lexeme'])
		synch(['begin', '.', ';', 'else', 'end'])
		if tok['lexeme']=='begin':
			compound_statement()
		return

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
		syntaxError("parameter_list1", tok['lexeme'])
		synch([')', ';'])
		parameter_list1()


def parameter_list():
	global tok
	if tok['tokenType']=="ID":
		matchByType('ID')
		matchByLexeme(':')
		typeProd()
		parameter_list1()
	else:
		syntaxError("parameter_list", tok['lexeme'])
		synch([')'], ['ID'])
		if tok['tokenType'] == 'ID':
			parameter_list()
		return

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
		syntaxError("subprogram_head1", tok['lexeme'])
		synch(['(', ':', 'var'], [])
		if tok['lexeme']!='var':
			subprogram_head1()
		return

def subprogram_head():
	global tok
	if tok['lexeme']=='function':
		matchByLexeme('function')
		matchByType('ID')
		subprogram_head1()
	else:
		syntaxError("subprogram_head", tok['lexeme'])
		synch(['function', 'var', 'begin'])
		if tok['lexeme']=='function':
			subprogram_head()
		return

def subprogram_declaration1_1():
	global tok
	if tok['lexeme']=='function':
		subprogram_declarations()
		compound_statement()
	elif tok['lexeme']=='begin':
		compound_statement()
	else:
		syntaxError("subprogram_declaration1_1", tok['lexeme'])
		synch(['function', 'begin', ';'])
		if tok['lexeme']!=';':
			subprogram_declaration1_1()
		return

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
		syntaxError("subprogram_declaration1", tok['lexeme'])
		synch(['var', 'function', 'begin', ';'])
		if tok['lexeme']!=';':
			subprogram_declaration1()
		return

def subprogram_declaration():
	global tok
	if tok['lexeme']=='function':
		subprogram_head()
		subprogram_declaration1()
	else:
		syntaxError("subprogram_declaration", tok['lexeme'])
		synch(['function', ';'])
		if tok['lexeme']!=';':
			subprogram_declaration()
		return

def subprogram_declarations1():
	global tok
	if tok['lexeme']=='function':
		subprogram_declaration()
		matchByLexeme(';')
		subprogram_declarations1()
	elif tok['lexeme']=='begin':	
		return
	else:
		syntaxError("subprogram_declarations1", tok['lexeme'])
		synch(['function', 'begin'])
		subprogram_declarations1()

def subprogram_declarations():
	global tok
	if tok['lexeme']=='function':
		subprogram_declaration()
		matchByLexeme(';')
		subprogram_declarations1()
	else:
		syntaxError("subprogram_declarations", tok['lexeme'])
		synch(['function', 'begin'])
		if tok['lexeme']=='funciton':
			subrpogram_declarations()
		return

def standard_type():
	global tok
	if tok['lexeme']=='integer':
		matchByLexeme('integer')
	elif tok['lexeme']=='real':
		matchByLexeme('real')
	else:
		syntaxError("standard_type", tok['lexeme'])
		synch(['integer', 'real', ';', ')'])
		if tok['lexeme'] in ['integer', 'real']:
			standard_type()
		return

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
		syntaxError("type", tok['lexeme'])
		synch(['integer', 'real', 'array', ';', ')'], [])
		if tok['lexeme'] in ['integer', 'real', 'array']:
			typeProd()
		return

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
		syntaxError("declarations1", tok['lexeme'])
		synch(['var', 'function', 'begin'], [])
		declarations1()
		return

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
		syntaxError("declarations", tok['lexeme'])
		synch(['var', 'function', 'begin'])
		if tok['lexeme']=='var':
			declarations()
		return

def identifier_list1():
	global tok
	if tok['lexeme']==",":
		matchByLexeme(',')
		matchByType('ID')
	elif tok['lexeme']==")":	
		return
	else:
		syntaxError("identifier_list1", tok['lexeme'])
		synch([')', ','])	
		identifier_list1()
		return

def identifier_list():
	global tok
	if tok['tokenType']=="ID":
		matchByType('ID')
		identifier_list1()
	else:
		syntaxError("identifier_list", tok['lexeme'])
		synch([')'], ['ID'])
		if tok['tokenType']=='ID':
			identifier_list()
		return

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
		syntaxError("program1_1", tok['lexeme'])
		synch(['function', 'begin'])
		program1_1()
		return

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
		syntaxError("program1", tok['lexeme'])
		synch(["var", "function", "begin"])
		program1()
		return

def program():
	#TODO one unified way of matching tokens
	if tok['lexeme']=='program':
		matchByLexeme('program')
		matchByType('ID')
		matchByLexeme('(')
		identifier_list()
		matchByLexeme(')')
		matchByLexeme(';')
		program1()
	else:
		syntaxError("program", tok['lexeme'])
		synch('program')
		program()
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
'''
Takes as input a list of tokens and outputs a parse tree based on the grammar. The grammar has been transformed into an LL(1) grammar. 
'''

import sys
	
tok = None
lexer = None
symTable = None
rwTable = None
listingFile = None

#flag to indicate if code is error free
hasSyntaxErrors = False
hasSemanticErrors = False

def setup(l, rwt, lf):
	global lexer
	global symTable
	global rwTable
	global listingFile
	lexer = l
	symTable = l.symTable
	rwTable = rwt
	listingFile = lf

def finish():
	if hasSyntaxErrors is True:
		print "Syntax Analysis completed with errors"
		sys.exit()
	else:
		print "Syntax Analysis is complete"
	if hasSemanticErrors is True:
		print "Semantic analysis completed with errors"
		sys.exit()
	else:
		print "Semantic Analysis is complete"

def synch(lexemes, types):
	assert type(lexemes) is list and type(types) is list
	global tok

	while tok['lexeme'] not in lexemes and tok['tokenType'] not in types:
		hasSyntaxErrors = True
		# print "discarding token: " + str(tok)
		if tok['tokenType'] == 'EOF':
			finish()
		elif tok['lexeme'] == ';': #just brace for a new line
			tok = lexer.getToken()
			break
		tok = lexer.getToken()
'''
def getType(token):
	if token['tokenType'] is 'ID':
		tokType = 
	else:
		syntaxError('an identifier to be declared prior to use', 'an undefined identifier')
		return {'type':'ERR'}
'''

def syntaxError(expected, actual):
	global hasSyntaxErrors
	hasSyntaxErrors = True
	assert type(expected) is str and type(actual) is str
	listingFile.write("Syntax error! expecting " + expected + ", got " + actual + "\n")

def semanticError(expected, actual):
	global hasSemanticErrors
	hasSemanticErrors = True
	assert type(expected) is str and type(actual) is str
	listingFile.write("Semantic error! Expecting " + expected + ", got " + actual + "\n")

'''
begin match methods
'''
def matchByLexeme(t):
	global tok
	assert type(tok) is dict
	if tok['lexeme']==t:
		if tok['tokenType']!='EOF': #do not overrun the buffer
			# print "matched: " + str(tok)
			tok = lexer.getToken()
		else:
			finish()
	else: #syntax error
		syntaxError(t, tok['lexeme'])
		tok = lexer.getToken()

def matchByType(t):
	global tok
	assert type(tok) is dict
	if tok['tokenType']==t:
		if tok['tokenType']!='EOF': #do not overrun the buffer
			# print "matched: " + str(tok)
			tok = lexer.getToken() 
		else:
			finish()
	else: #syntax error
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
		syntaxError("+, -,  '(' or 'not'", tok['lexeme'])
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
		syntaxError("',', ')', ';', 'end', 'else', '[', ']', 'then', 'do', 'MULTOP', 'ADDOP' or 'RELOP'", tok['lexeme'])
		synch([',', ')', ';', 'end', 'else', '[', ']', 'then', 'do'], ['MULTOP', 'ADDOP', 'RELOP'])
		if tok['lexeme'] in ['(', '[', ';', 'else', 'end', 'then', 'do', ']', ',', ')'] or \
			tok['tokenType'] in ['MULTOP', 'RELOP', 'ADDOP']: #first or follow
			factor1()
			return
		else:
			print "An error occurred. Check your synch set"
			assert False

def factor():
	global tok
	if tok['lexeme']=='(':
		matchByLexeme('(')
		e=expression()
		matchByLexeme(')')
		return e #no changes or checks here
	elif tok['lexeme']=='not':
		matchByLexeme('not')
		f1=factor()
		print f1
		if f1['type'] == "BOOL":
			return {'type':"BOOL"}
		elif f1['type'] == "ERR":
			return {'type':"ERR"}
		else:
			semanticError("BOOL type", f1['type'])
			return {'type':"ERR"}
	elif tok['tokenType']=='ID':
		matchByType('ID')
		factor1()
	elif tok['tokenType']=='NUMBER':
		matchByType('NUMBER')
	else:
		syntaxError("'(', ')', 'not', ';', 'else', 'end', 'then', 'do', ']', ',', ')', 'NUMBER', 'MULTOP', 'ADDOP' or 'RELOP'", tok['lexeme'])
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
		syntaxError("';', 'else', 'end', 'then', 'do', ']', ',', ')', 'ADDOP', 'RELOP' or 'MULTOP'", tok['lexeme'])
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
		syntaxError("'(', 'not', ';', 'else', 'end', 'then', 'do', ']', ',', ')', 'ID', 'NUMBER', 'ADDOP' or 'RELOP'", tok['lexeme'])
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
		syntaxError(",', ')', ';', 'end', 'else', ']', 'then', 'do', 'RELOP' or 'ADDOP'", tok['lexeme'])
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
		syntaxError("'(', '+', '-', 'not', 'ID' or 'NUMBER'", tok['lexeme'])
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
		syntaxError("',', ')', ';', 'end', 'else', ']', 'then', 'do' or RELOP", tok['lexeme'])
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
		return {'type':"BOOL"}
	else:
		syntaxError("'(', '+', '-', 'not', 'else', 'then', 'end', 'do', ']', ',', ')', ';', 'NUMBER' or 'ID'", tok['lexeme'])
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
		syntaxError("',' or ')'", tok['lexeme'])
		synch([',', ')'], [])
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
		syntaxError("'(', '+', '-', 'not', ')', 'ID' or 'NUMBER'", tok['lexeme'])
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
		syntaxError("'[', 'else', 'end', 'then', 'do', ']', ',', ')', ';', 'ASSIGNOP', 'MULTOP', 'ADDOP' or 'RELOP'", tok['lexeme'])
		synch(['[', 'else', 'end', 'then', 'do', ']', ',', ')', ';'], ['ASSIGNOP', 'MULTOP', 'ADDOP', 'RELOP'])
		variable1()

def variable():
	global tok
	if tok['tokenType']=='ID':
		matchByType('ID')
		variable1()
	else:
		syntaxError("'ID' or 'ASSIGNOP'", tok['lexeme'])
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
		syntaxError("end, else", tok['lexeme'])
		synch([';', 'end', 'else'], [])
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
		syntaxError("'begin', 'if', 'while', 'else', 'end' or ID", tok['lexeme'])
		synch(['begin', 'if', 'while', 'else', 'end'], ['ID'])
		if tok['lexeme'] in ['begin', 'if', 'while'] or tok['tokenType']=='ID':
			statement()
		return

def statement_list1():
	global tok
	if tok['lexeme']==';':
		matchByLexeme(';')
		statement()
		statement_list1()
	elif tok['lexeme']=='end':
		return
	else:
		syntaxError("';', 'end'", tok['lexeme'])
		synch([';', 'end'], [])
		statement_list1()
		return

def statement_list():
	global tok
	if tok['lexeme']=='begin' or tok['lexeme']=='if' or tok['lexeme']=='while' or tok['tokenType']=='ID':
		statement()
		statement_list1()
	else:
		syntaxError("'begin', 'if', 'while' or ID", tok['lexeme'])
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
		syntaxError("'begin', 'if', 'while', 'end', '.', ';' or ID", tok['lexeme'])
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
		syntaxError("'begin', '.', ';', 'else', or 'end'", tok['lexeme'])
		synch(['begin', '.', ';', 'else', 'end'], [])
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
		syntaxError("')' or ';'", tok['lexeme'])
		synch([')', ';'], [])
		parameter_list1()


def parameter_list():
	global tok
	if tok['tokenType']=="ID":
		matchByType('ID')
		matchByLexeme(':')
		typeProd()
		parameter_list1()
	else:
		syntaxError(") or ID", tok['lexeme'])
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
		syntaxError("'(', ':', or 'var'", tok['lexeme'])
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
		syntaxError("'function', 'var', or 'begin'", tok['lexeme'])
		synch(['function', 'var', 'begin'], [])
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
		syntaxError("'function', 'begin', or ';'", tok['lexeme'])
		synch(['function', 'begin', ';'], [])
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
		syntaxError("'function' or ';'", tok['lexeme'])
		synch(['var', 'function', 'begin', ';'], [])
		if tok['lexeme']!=';':
			subprogram_declaration1()
		return

def subprogram_declaration():
	global tok
	if tok['lexeme']=='function':
		subprogram_head()
		subprogram_declaration1()
	else:
		syntaxError("'function' or ';'", tok['lexeme'])
		synch(['function', ';'], [])
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
		syntaxError("'function', or 'begin'", tok['lexeme'])
		synch(['function', 'begin'], [])
		subprogram_declarations1()

def subprogram_declarations():
	global tok
	if tok['lexeme']=='function':
		subprogram_declaration()
		matchByLexeme(';')
		subprogram_declarations1()
	else:
		syntaxError("'function', or 'begin'", tok['lexeme'])
		synch(['function', 'begin'], [])
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
		syntaxError("'integer', 'real', ';', or ')'", tok['lexeme'])
		synch(['integer', 'real', ';', ')'], [])
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
		syntaxError("'integer', 'real', 'array', ';', or ')'", tok['lexeme'])
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
		syntaxError("'var', 'function', or 'begin'", tok['lexeme'])
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
		syntaxError("'var', 'function', or 'begin'", tok['lexeme'])
		synch(['var', 'function', 'begin'],[])
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
		syntaxError("')' or ','", tok['lexeme'])
		synch([')', ','], [])	
		identifier_list1()
		return

def identifier_list():
	global tok
	if tok['tokenType']=="ID":
		matchByType('ID')
		identifier_list1()
	else:
		syntaxError("')' or 'ID'", tok['lexeme'])
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
		syntaxError("function or begin", tok['lexeme'])
		synch(['function', 'begin'], [])
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
		syntaxError("'var', 'function', or 'begin'", tok['lexeme'])
		synch(["var", "function", "begin"], [])
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
		synch(['program'], [])
		program()
		return

#begins the main work of parsing
def parse():
	global tok
	tok = lexer.getToken()
	program() #starting production
	#factor() #temporary start production
	matchByType('EOF')
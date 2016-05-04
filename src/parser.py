'''
Takes as input a list of tokens and outputs a parse tree based on the grammar. The grammar has been transformed into an LL(1) grammar. 
'''

import sys
import blueGreenTree as bgTree
	
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
		return
	else:
		print "Syntax Analysis is complete"
	if hasSemanticErrors is True:
		print "Semantic analysis completed with errors"
		return
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
Checks the actualList array of types against the expected array of types, which 
should be provided by a blueGreenTree lookup of the identifier.

Returns: True if expected matches the actual list. False if it does not  
'''
def checkExpList(actualList, identifier):
	if actualList is 'ERR':
		return False
	assert type(actualList) is list and type(identifier) is str
	expected = bgTree.getGreenNodeTypes(identifier)
	if expected == "ERR":
		return False
	assert type(expected) is list
	for e in range(len(expected)):
		assert type(expected[e]) is str
		if expected[e][-2:] == 'FP':
			expected[e] = expected[e][:-2]
	for a in range(len(actualList)):
		assert type(actualList[a]) is str
		if actualList[a][-2:] =='FP':
			actualList[a] = actualList[a][:-2]
	# print '***Actual for ' + identifier + ': ' + str(actualList)
	# print "***Expected: " + str(expected)
	return actualList == expected

def syntaxError(expected, actual):
	global hasSyntaxErrors
	hasSyntaxErrors = True
	assert type(expected) is str and type(actual) is str
	listingFile.write("Syntax error! expecting " + expected + ", got " + actual + "\n")

def semanticError(expected, actual=None):
	global hasSemanticErrors
	hasSemanticErrors = True
	assert type(expected) is str
	if actual==None:
		listingFile.write("Semantic error! " + expected + "\n")
	else:
		listingFile.write("Semantic error! Expecting " + expected + ", got " + actual + "\n")

'''
begin match methods
'''

'''
Returns the token matched
'''
def matchByLexeme(t):
	global tok
	assert type(tok) is dict
	if tok['lexeme']==t:
		if tok['tokenType']!='EOF': #do not overrun the buffer
			# print "matched: " + str(tok)
			tempTok = tok
			tok = lexer.getToken()
			return tok
		else:
			finish()
	else: #syntax error
		syntaxError(t, tok['lexeme'])
		tok = lexer.getToken()

'''
Returns the matched token
'''
def matchByType(t):
	global tok
	assert type(tok) is dict
	if tok['tokenType']==t:
		if tok['tokenType']!='EOF': #do not overrun the buffer
			# print "matched: " + str(tok)
			tempTok = tok
			tok = lexer.getToken()
			return tempTok
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

def factor1(inherited):
	global tok
	if tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' \
	or tok['lexeme']=='else' or tok['lexeme']=='[' or tok['lexeme']==']' or \
	tok['tokenType']=='MULTOP' or tok['tokenType']=='ADDOP' or tok['tokenType']=='RELOP' \
	or tok['lexeme']=='then' or tok['lexeme']=='do':
		var1 = variable1(inherited['type'])
		return {'type':var1['type']}
	elif tok['lexeme']=='(':
		matchByLexeme('(')
		elAttr = expression_list()
		matchByLexeme(')')
		if inherited['type'] is not 'ERR' and checkExpList(elAttr['type'], inherited['name']):
			return elAttr
		else:
			if elAttr['type'] is not 'ERR' and inherited['type'] is not 'ERR':
				semanticError('arguments that match expected values', 'arguments that do not match expected values')
			return {'type':"ERR"}
	else:
		syntaxError("',', ')', ';', 'end', 'else', '[', ']', 'then', 'do', 'MULTOP', 'ADDOP' or 'RELOP'", tok['lexeme'])
		synch([',', ')', ';', 'end', 'else', '[', ']', 'then', 'do'], ['MULTOP', 'ADDOP', 'RELOP'])
		if tok['lexeme'] in ['(', '[', ';', 'else', 'end', 'then', 'do', ']', ',', ')'] or \
			tok['tokenType'] in ['MULTOP', 'RELOP', 'ADDOP']: #first or follow
			return factor1(inherited)
		else:
			print "An error occurred. Check your synch set"


def factor():
	global tok
	if tok['lexeme']=='(':
		matchByLexeme('(')
		e=expression()
		matchByLexeme(')')
		return {'type':e['type']}

	elif tok['lexeme']=='not':
		matchByLexeme('not')
		f1=factor()
		if f1['type'] == "BOOL":
			return {'type':"BOOL"}
		else:
			if f1['type'] != "ERR":
				semanticError("BOOL type", f1['type'])
			return {'type':"ERR"}

	elif tok['tokenType']=='ID':
		idTok = matchByType('ID')
		idType = bgTree.getType(idTok['lexeme'])
		if idType is 'ERR':
			semanticError('The identifier ' + idTok['lexeme'] + ' has not been initialized yet or is not in the current scope')
		f1=factor1({'name':idTok['lexeme'], 'type':idType})
		if type(f1['type']) is type([]) and idType is 'FNAME': #function calls
			return {'type': bgTree.getGreenNodeReturnType(idTok['lexeme'])} #return the return type of the function
		elif idType in ['intNumArray', 'realNumArray', 'intNumArrayFP', 'realNumArrayFP']:
			if f1['type'][:5]==idType[:5]: #came from variable1 and was an array. SUPER HACKY!
				return {'type':f1['type']}
			elif f1['type'] == 'VOID':
				return {'type':idType}
			else:
				if f1['type'] != 'ERR':
					semanticError('Mismatch! Identifier ' + idTok['lexeme']  + ' is of type' + idType + ' and was followed by some illegitimate statement')
				return {'type':'ERR'}
		elif idType in ['intNum', 'realNum', 'intNumFP', 'realNumFP'] and f1['type'] == 'VOID': #came from variable1 and was an intNum or a realNum
			return {'type':idType}
		else:
			if f1['type'] != "ERR":
				semanticError('Valid usage of an identifier or parenthesized expression', 'an invalid identifier or parenthesized expression')
			return {'type':"ERR"}

	elif tok['tokenType']=='NUMBER':
		numTok = matchByType('NUMBER')
		if numTok['attribute'] is 'intNum':
			return {'type':"intNum"}
		else: #reals and long reals
			return {'type':"realNum"}

	else:
		syntaxError("'(', ')', 'not', ';', 'else', 'end', 'then', 'do', ']', ',', ')', 'NUMBER', 'MULTOP', 'ADDOP' or 'RELOP'", tok['lexeme'])
		synch(['(', ')', 'not', ';', 'else', 'end', 'then', 'do', ']', ',', ')'], \
		['NUMBER', 'MULTOP', 'ADDOP', 'RELOP'])
		if tok['lexeme'] in ['(', 'not'] or tok['tokenType'] in ['NUMBER', 'ID']: #first
			return factor()
		return {'type':"ERR"}#else, follow. We want to return after factor anyway to help us in project 3

def term1():
	global tok
	if tok['tokenType']=='MULTOP':
		matchByType("MULTOP")
		f=factor()
		t=term1()
		#this is almost too hacky for my comfort
		fMod = f['type']
		tMod = t['type']
		if fMod[-2:] == 'FP':
			fMod = fMod[:-2]
		if tMod[-2:] == 'FP':
			tMod = tMod[:-2]
		if fMod == tMod or t['type'] == 'VOID': 
			return {'type': f['type']}
		else:
			if f['type'] != 'ERR' and t['type'] != 'ERR':
				semanticError('matching types on both sides of a MULTOP', 'unmatched types')
			return {'type':"ERR"}
	elif tok['tokenType']=='ADDOP' or tok['tokenType']=='RELOP' or tok['lexeme']==';' \
	or tok['lexeme']=='else' or tok['lexeme']=='end' or tok['lexeme']=='then' or \
	tok['lexeme']=='do' or tok['lexeme']==']' or tok['lexeme']==',' or tok['lexeme']==')':
		return {'type':"VOID"}
	else:
		syntaxError("';', 'else', 'end', 'then', 'do', ']', ',', ')', 'ADDOP', 'RELOP' or 'MULTOP'", tok['lexeme'])
		synch([';', 'else', 'end', 'then', 'do', ']', ',', ')'], ['ADDOP', 'RELOP', 'MULTOP'])
		if tok['tokenType'] == 'MULTOP':
			return term1()
		return {'type':"ERR"}

def term():
	global tok
	if tok['lexeme']=='(' or tok['lexeme']=='not' or tok['tokenType']=='ID' or tok['tokenType']=='NUMBER':
		f = factor()
		t1 = term1()
		fMod = f['type']
		tMod = t1['type']
		if fMod[-2:] == 'FP':
			fMod = fMod[:-2]
		if tMod[-2:] == 'FP':
			tMod = tMod[:-2]
		if fMod == tMod or t1['type'] == 'VOID':
			return {'type':f['type']}
		else:
			if f['type'] != "ERR" and t1['type'] != "ERR":
				semanticError("matching types on both sides of a MULTOP", "unmatched types")
			return {"type":"ERR"}
	else:
		syntaxError("'(', 'not', ';', 'else', 'end', 'then', 'do', ']', ',', ')', 'ID', 'NUMBER', 'ADDOP' or 'RELOP'", tok['lexeme'])
		synch(['(', 'not', ';', 'else', 'end', 'then', 'do', ']', ',', ')'], ['ID', 'NUMBER', 'ADDOP', 'RELOP'])
		if tok['lexeme'] in ['not', '('] or tok['tokenType'] in ['ID', 'NUMBER']:
			return term()
		return {'type':"ERR"}

def simple_expression1():
	global tok
	if tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' \
	or tok['lexeme']=='else' or tok['lexeme']==']' or tok['lexeme']=='then' \
	or tok['lexeme']=='do' or tok['tokenType']=='RELOP':
		return {'type':"VOID"}
	elif tok['tokenType']=='ADDOP':
		matchByType('ADDOP')
		t=term()
		se1=simple_expression1()
		tMod = t['type']
		seMod = se1['type']
		if tMod[-2:] == 'FP':
			tMod = tMod[:-2]
		if seMod[-2:] == 'FP':
			seMod = seMod[:-2]
		if tMod == seMod or se1['type'] == 'VOID':
			return {'type':t['type']}
		else:
			if t['type'] != 'ERR' and se1['type'] != 'ERR':
				semanticError('matching types on both sides of the ADDOP', 'unmatched types')
			return {'type':'ERR'}
	else:
		syntaxError(",', ')', ';', 'end', 'else', ']', 'then', 'do', 'RELOP' or 'ADDOP'", tok['lexeme'])
		synch([',', ')', ';', 'end', 'else', ']', 'then', 'do'], ['RELOP', 'ADDOP'])
		if tok['tokenType'] == 'ADDOP':
			return simple_expression1()
		return {'type':"ERR"}

def simple_expression():
	global tok
	if tok['tokenType']=='ID' or tok['lexeme']=='(' or tok['lexeme']=='not' or tok['tokenType']=='NUMBER':
		t=term()
		se1=simple_expression1()
		tMod = t['type']
		seMod = se1['type']
		if tMod[-2:] == 'FP':
			tMod = tMod[:-2]
		if seMod[-2:] == 'FP':
			seMod = seMod[:-2]
		if tMod == seMod or se1['type'] == 'VOID':
			return {'type':t['type']}
		else:
			if t['type'] != 'ERR' and se1['type'] != 'ERR':
				semanticError('matching types on both sides of the ADDOP', 'unmatched types')
			return {'type':'ERR'}
	elif tok['lexeme']=='+' or tok['lexeme']=='-':
		sign()
		t=term()
		se1=simple_expression1()
		tMod = t['type']
		seMod = se1['type']
		if tMod[-2:] == 'FP':
			tMod = tMod[:-2]
		if seMod[-2:] == 'FP':
			seMod = seMod[:-2]
		if tMod == seMod or se1['type'] == 'VOID':
			return {'type':t['type']}
		else:
			if t['type'] != 'ERR' and se1['type'] != 'ERR':
				semanticError('matching types on both sides of the ADDOP', 'unmatched types')
			return {'type':'ERR'}
	else:
		syntaxError("'(', '+', '-', 'not', 'ID' or 'NUMBER'", tok['lexeme'])
		synch(['(', '+', '-', 'not'], ['ID', 'NUMBER'])
		if tok['lexeme'] in ['(', 'not', '+', '-'] or tok['tokenType'] in ['NUMBER', 'ID']:
			return simple_expression()
		return {'type':"ERR"}

def expression1(inherited):
	global tok
	if tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' or \
	tok['lexeme']=='else' or tok['lexeme']==']' or tok['lexeme']=='then' or tok['lexeme']=='do':
		return {'type':'VOID'}
	elif tok['tokenType']=='RELOP':
		matchByType('RELOP')
		se=simple_expression()
		if inherited in ['intNum', 'realNum', 'intNumFP', 'realNumFP'] and se['type'] in ['intNum', 'realNum', 'intNumFP', 'realNumFP'] \
		and inherited[:4] == se['type'][:4]: #check first 5 chars because I'm lazy. intNum can match up with intNumFP
			return {'type':"BOOL"}
		else:
			if inherited != 'ERR' and se['type'] != 'ERR':
				semanticError('Identical types on both sides of a RELOP expression. Types must also be either an int or a real', '')
			return {'type':'ERR'}
	else:
		syntaxError("',', ')', ';', 'end', 'else', ']', 'then', 'do' or RELOP", tok['lexeme'])
		synch([',', ')', ';', 'end', 'else', ']', 'then', 'do'], ['RELOP'])
		if tok['tokenType'] == 'RELOP':
			return expression1(inherited)
		return {'type':"ERR"}

def expression():
	global tok
	if tok['tokenType']=='ID' or tok['lexeme']=='(' or tok['lexeme']=='+' or \
	tok['lexeme']=='-' or tok['lexeme']=='not' or tok['tokenType']=='NUMBER':
		se=simple_expression()
		e1=expression1(se['type'])
		if e1['type'] == 'VOID':
			return {'type':se['type']}
		else:
			return {'type':e1['type']}
	else:
		syntaxError("'(', '+', '-', 'not', 'else', 'then', 'end', 'do', ']', ',', ')', ';', 'NUMBER' or 'ID'", tok['lexeme'])
		synch(['(', '+', '-', 'not', 'else', 'then', 'end', 'do', ']', ',', ')', ';'], ['NUMBER', 'ID'])
		if tok['lexeme'] in ['(', 'not', '+', '-'] or tok['tokenType'] in ['ID', 'NUMBER']:
			return expression()
		return {'type':"ERR"}

def expression_list1():
	global tok
	if tok['lexeme']==',':
		matchByLexeme(',')
		e = expression()
		el1 = expression_list1()
		if type(el1) is dict and type(el1['type']) is list and e['type'] is not "ERR":
			el1['type'].insert(0, e['type'])
			return el1
		else:
			if e['type'] != 'ERR' and el1['type'] != 'ERR':
				semanticError('The expression list is not valid.')
			return {'type':'ERR'}
	elif tok['lexeme']==')':
		return {'type':[]}
	else:
		syntaxError("',' or ')'", tok['lexeme'])
		synch([',', ')'], [])
		if tok['lexeme'] == ',':
			return expression_list1()
		return {'type':"ERR"}

def expression_list():
	global tok
	if tok['tokenType']=='ID' or tok['lexeme']=='(' or tok['lexeme']=='+' or tok['lexeme']=='-'\
	or tok['lexeme']=='not' or tok['tokenType']=='NUMBER':
		e = expression()
		el1 = expression_list1()
		if type(el1) is dict and type(el1['type']) is list:
			el1['type'].insert(0, e['type'])
			return el1
		else:
			if e['type'] != 'ERR' and el1['type'] != 'ERR':
				semanticError('expecting a list of expressions')
			return {'type':'ERR'}
	else:
		syntaxError("'(', '+', '-', 'not', ')', 'ID' or 'NUMBER'", tok['lexeme'])
		synch(['(', '+', '-', 'not', ')'], ['ID', 'NUMBER'])
		if tok['lexeme'] in ['(', 'not', '+', '-'] or tok['tokenType'] in ['ID', 'NUMBER']:
			return expression_list()
		return {'type':"ERR"}

def variable1(inherited):
	global tok
	if tok['lexeme']==',' or tok['lexeme']==')' or tok['lexeme']==';' or tok['lexeme']=='end' \
	or tok['lexeme']=='else' or tok['lexeme']==']' or tok['tokenType']=='ASSIGNOP' or \
	tok['tokenType']=='MULTOP' or tok['tokenType']=='ADDOP' or tok['tokenType']=='RELOP' or \
	tok['lexeme']=='then' or tok['lexeme']=='do':
		return {'type':'VOID'}
	elif tok['lexeme']=='[':
		matchByLexeme('[')
		e = expression()
		matchByLexeme(']')
		if e['type'] == 'intNum':
			if inherited.startswith('intNumArray'):
				return {'type':'intNum'}
			if inherited.startswith('realNumArray'):
				return {'type':'realNum'}
		#if we make it here, we have some sort of error
		if e['type'] != 'ERR' and inherited != 'ERR':
			semanticError('Invalid array index')
		return {'type':'ERR'}

	else:
		syntaxError("'[', 'else', 'end', 'then', 'do', ']', ',', ')', ';', 'ASSIGNOP', 'MULTOP', 'ADDOP' or 'RELOP'", tok['lexeme'])
		synch(['[', 'else', 'end', 'then', 'do', ']', ',', ')', ';'], ['ASSIGNOP', 'MULTOP', 'ADDOP', 'RELOP'])
		return variable1(inherited)

def variable():
	global tok
	if tok['tokenType']=='ID':
		storeVarName = tok['lexeme']
		idTok = matchByType('ID')
		idType = bgTree.getType(idTok['lexeme'])
		v1 = variable1(idType)
		if idType == 'ERR':
			semanticError('The variable \'' + storeVarName + '\' has not been declared or is not in the current scope')
			return {'type':'ERR'}
		if idType == "FNAME":
			return {'type':bgTree.getGreenNodeReturnType(idTok['lexeme'])}
		if v1['type'] == 'VOID':
			return {'type':idType}
		else:
			return {'type':v1['type']}
	else:
		syntaxError("'ID' or 'ASSIGNOP'", tok['lexeme'])
		synch([], ['ID', 'ASSIGNOP'])
		if tok['tokenType']=='ID':
			variable()
		return {'type':"ERR"}

def statement1():
	global tok
	if tok['lexeme']==';' or tok['lexeme']=='end':
		return {'type':'VOID'}
	elif tok['lexeme']=='else':
		matchByLexeme('else')
		statement()
		return
	else:
		syntaxError("end, else", tok['lexeme'])
		synch([';', 'end', 'else'], [])
		return statement1()

def statement():
	global tok
	if tok['lexeme']=='begin':
		compound_statement()
		return
	elif tok['tokenType']=='ID':
		v = variable()
		matchByType('ASSIGNOP')
		e = expression()
		#strip out function paramater descriptors to avoid false positive errors (yeah, this is super hacky. Whatever)
		if v['type'].endswith('FP'):
			v['type'] = v['type'][:-2]
		if e['type'].endswith('Array'):
			e['type'] = e['type'][:-5]
		if v['type'] == e['type']:
			return
		else:
			if v['type'] != 'ERR' and e['type'] != 'ERR':
				semanticError('a valid ASSIGNOP expression', 'an invalid ASSIGNOP expression')
			return
	elif tok['lexeme']=='if':
		matchByLexeme('if')
		e = expression()
		matchByLexeme('then')
		statement()
		statement1()
		if e['type'] == 'BOOL':
			return
		else:
			if e['type'] != 'ERR':
				semanticError('a valid if statement', 'an invalid if statement with an expression type of ' + e['type'])
			return
	elif tok['lexeme']=='while':
		matchByLexeme('while')
		e = expression()
		matchByLexeme('do')
		statement()
		if e['type'] == 'BOOL':
			return
		else:
			if e['type'] != 'ERR':
				semanticError('a valid while statement', 'an invalid while expression')
			return
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
		i = matchByType("ID")
		matchByLexeme(":")
		t = typeProd()
		if t['isArray'] == False:
			noNameConflict = bgTree.checkAddBlueNode(i['lexeme'], t['type']+'FP') #converts type to "function parameter type"
		else:
			noNameConflict = bgTree.checkAddBlueNode(i['lexeme'], t['type']+'FP', t['arrayLength'])
		if not noNameConflict:
			semanticError('the identifier ' + i['lexeme'] + ' has already been defined in the scope')
		parameter_list1()
	else:
		syntaxError("')' or ';'", tok['lexeme'])
		synch([')', ';'], [])
		parameter_list1()


def parameter_list():
	global tok
	if tok['tokenType']=="ID":
		i = matchByType('ID')
		matchByLexeme(':')
		t = typeProd()
		if t['isArray'] == False:
			noNameConflict = bgTree.checkAddBlueNode(i['lexeme'], t['type']+'FP') #converts type to "function parameter type"
		else:
			noNameConflict = bgTree.checkAddBlueNode(i['lexeme'], t['type']+'FP', t['arrayLength'])
		if not noNameConflict:
			semanticError('the identifier ' + i['lexeme'] + ' has already been defined in the scope')
		parameter_list1()
		return
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
		st = standard_type()
		matchByLexeme(';')
		return {'type': st['type']}
	elif tok['lexeme']==':':
		matchByLexeme(':')
		st = standard_type()
		matchByLexeme(';')
		return {'type': st['type']}
	else:
		syntaxError("'(', ':', or 'var'", tok['lexeme'])
		synch(['(', ':', 'var'], [])
		if tok['lexeme']!='var':
			return subprogram_head1()
		return {'type': 'ERR'} #TODO is this what we are supposed to be doing?

def subprogram_head():
	global tok
	if tok['lexeme']=='function':
		matchByLexeme('function')
		i = matchByType('ID')
		noTypeConflict = bgTree.checkAddGreenNode(i['lexeme'], 'FNAME')
		if not noTypeConflict:
			semanticError('Type Conflict. The name ' + i['lexeme'] + \
				' was already defined in the scope')
		sh = subprogram_head1()
		if noTypeConflict:
			bgTree.setGreenNodeReturnType(i['lexeme'], sh['type'])
		return {'type': sh['type']}
	else:
		syntaxError("'function', 'var', or 'begin'", tok['lexeme'])
		synch(['function', 'var', 'begin'], [])
		if tok['lexeme']=='function':
			return subprogram_head()
		return {'type':'ERR'} #TODO is this what we are supposed to be doing?

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
		bgTree.popStack()
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
		return {'type':'intNum'}
	elif tok['lexeme']=='real':
		matchByLexeme('real')
		return {'type': 'realNum'}
	else:
		syntaxError("'integer', 'real', ';', or ')'", tok['lexeme'])
		synch(['integer', 'real', ';', ')'], [])
		if tok['lexeme'] in ['integer', 'real']:
			return standard_type()
		return {'type': 'ERR'} #TODO is this what we should be doing?

def typeProd():
	global tok
	if tok['lexeme']=='integer' or tok['lexeme']=='real':
		st = standard_type()
		return {'type': st['type'], 'isArray':False}
	elif tok['lexeme']=='array':
		matchByLexeme('array')
		matchByLexeme('[')
		leftIndex = int(matchByType('NUMBER')['lexeme'])
		matchByLexeme('..')
		rightIndex = int(matchByType('NUMBER')['lexeme'])
		matchByLexeme(']')
		matchByLexeme('of')
		st = standard_type()
		if st['type'] is not 'ERR':
			if rightIndex < leftIndex:
				print "Index Error! left index was " + str(leftIndex) + " and right index was " + str(rightIndex) + \
				". Left index cannot be greater than the right index"
				global hasSemanticErrors
				hasSemanticErrors = True
			#XXX Assumes inclusive range
			return {'type': st['type']+'Array', 'isArray':True, 'arrayLength':rightIndex-leftIndex+1} #converts standard type to array type
		else:
			return {'type':'ERR'}
	else:
		syntaxError("'integer', 'real', 'array', ';', or ')'", tok['lexeme'])
		synch(['integer', 'real', 'array', ';', ')'], [])
		if tok['lexeme'] in ['integer', 'real', 'array']:
			return typeProd()
		return {'type':'ERR'} #TODO is this what we should be doing?

def declarations1():
	global tok
	if tok['lexeme']=='var':
		matchByLexeme('var')
		i = matchByType('ID')
		matchByLexeme(':')
		t = typeProd()
		if t['isArray'] == False:
			noNameConflict = bgTree.checkAddBlueNode(i['lexeme'], t['type'])
		else: #has an array
			noNameConflict = bgTree.checkAddBlueNode(i['lexeme'], t['type'], t['arrayLength'])
		if not noNameConflict:
			semanticError('the identifier ' + i['lexeme'] + ' has already been used')
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
		i = matchByType('ID')
		matchByLexeme(":")
		t = typeProd()
		if t['isArray'] == False:
			noNameConflict = bgTree.checkAddBlueNode(i['lexeme'], t['type'])
		else:
			noNameConflict = bgTree.checkAddBlueNode(i['lexeme'], t['type'], t['arrayLength'])
		if not noNameConflict:
			semanticError('the identifier ' + i['lexeme'] + ' has already been used')
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
		i = matchByType('ID')
		noNameConflict = bgTree.checkAddBlueNode(i['lexeme'], 'PPARAM')
		if not noNameConflict:
			print 'just processed the error 2'
			semanticError('the identifier ' + i['lexeme'] + ' has alrady been used');
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
		i = matchByType('ID')
		noNameConflict = bgTree.checkAddBlueNode(i['lexeme'], 'PPARAM')
		if not noNameConflict:
			semanticError('the identifier ' + i['lexeme'] + ' has alrady been used');
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
		i = matchByType('ID')
		noNameConflict = bgTree.checkAddGreenNode(i['lexeme'], 'PNAME')
		if not noNameConflict:
			semanticError('the identifier ' + i['lexeme'] + ' has alrady been used');
		matchByLexeme('(')
		identifier_list()
		matchByLexeme(')')
		matchByLexeme(';')
		program1()
		return
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
	#factor() #temporary test start production
	#variable1() #temporary test start production
	matchByType('EOF')
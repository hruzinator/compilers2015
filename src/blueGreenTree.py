class GreenNode:
	def __init__(self, lexeme, nodeType):
		self.nodeLex = lexeme
		self.nodeType = nodeType
		self.numParams = 0
		self.subNodes = []

	def addParam(self):
		self.numParams += 1

	def getParamTypes(self):
		types = []
		for x in range(self.numParams):
			types.append(self.subNodes[x].nodeType)
		return types

class BlueNode:
	def __init__(self, lexeme, nodeType):
		self.nodeLex = lexeme
		self.nodeType = nodeType


callStack = []

'''
returns True if a new green node was added.
Returns False if there was a name conflict
'''
def checkAddGreenNode(lexeme, nodeType):
	assert nodeType in ['PNAME', 'FNAME']
	assert type(lexeme) is str
	#check type
	for node in callStack:
		if node.nodeLex == lexeme:
			return False
	#add type
	callStack.append(GreenNode(lexeme, nodeType))
	return True

'''
returns True if a new blue node was added.
Returns False if there was a name conflict
'''
def checkAddBlueNode(lexeme, nodeType):
	assert nodeType in ['PPARAM', 'intNumFP', 'realNumFP', 'intNumArrayFP', 'realNumArrayFP',\
	 					'intNum', 'realNum', 'intNumArray', 'realNumArray']
	assert type(lexeme) is str
	#check type
	for node in callStack[-1].subNodes:
		if node.nodeLex == lexeme:
			return False
	if callStack[-1].nodeLex == lexeme:
		#name cannot conflict with current green node either
		return False
	#add type
	callStack[-1].subNodes.append(BlueNode(lexeme, nodeType))
	if nodeType in ['PPARAM', 'intNumFP', 'realNumFP', 'intNumArrayFP', 'realNumArrayFP']:
		#we can update the number of params in above green node
		callStack[-1].addParam()
		 #TODO perhaps more internal checks here (like making sure params are before
		 #local vars, and that PPARAMS are matched with PNAME green nodes, etc.)?
	return True

'''
Returns the type of the lexeme based on the current static scope.
If the lexeme cannot be found in the current scope, ERR will be 
returned
'''
def getType(lexeme):
	index=len(callStack)-1
	while index>=0:
		gn=callStack[index]
		for node in gn.subNodes:
			if node.nodeLex == lexeme:
				return node.nodeType
		index-=1
	return 'ERR'

'''
Returns ERR if green node was not found
'''
def getGreenNode(lexeme):
	index=len(callStack)-1
	while index>=0:
		node=callStack[index]
		if node.nodeLex == lexeme:
			return node
		index-=1
	return 'ERR'

'''
Returns ERR if green node was not found
'''
def getGreenNodeTypes(lexeme):
	gn = getGreenNode(lexeme)
	if gn == 'ERR':
		return gn
	else:
		return gn.getParamTypes()


def popStack():
	callStack.pop()
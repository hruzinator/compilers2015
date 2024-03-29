class GreenNode:
	def __init__(self, lexeme, nodeType):
		self.nodeLex = lexeme
		self.nodeType = nodeType
		self.numParams = 0
		self.subNodes = []
		self.returnType = None #for Functions only!
		self.memOffset = 0 #project 4 variable offset calculations
		self.memOffsetFile = None

	def addParam(self):
		# print "Added a parameter to the " + self.nodeLex + " green node"
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
	gn = GreenNode(lexeme, nodeType)
	if nodeType is 'FNAME':
		callStack[-1].subNodes.append(gn) #add to scope of parent, if not program
	gn.memOffsetFile = open(lexeme+'offsets.txt', 'w')
	callStack.append(gn)
	#print 'Added GREEN node with name: ' + lexeme
	return True

'''
Array length is an optional argument that is passed in
in case the node type is an array type

Returns True if a new blue node was added.
Returns False if there was a name conflict.
'''
def checkAddBlueNode(lexeme, nodeType, arrayLength=-1):
	assert type(lexeme) is str
	assert nodeType in ['PPARAM', 'intNumFP', 'realNumFP', 'intNumArrayFP', 'realNumArrayFP',\
	 	'intNum', 'realNum', 'intNumArray', 'realNumArray']

	#check type
	for node in callStack[-1].subNodes:
		if node.nodeLex == lexeme:
			return False
	if callStack[-1].nodeLex == lexeme:
		#name cannot conflict with current green node either
		return False
	#add type
	gn = callStack[-1]
	if nodeType is not 'PPARAM':
		gn.memOffsetFile.write(lexeme + ": " + str(gn.memOffset) + "\n")
	gn.subNodes.append(BlueNode(lexeme, nodeType))
	if nodeType in ['intNum', 'intNumFP']:
		gn.memOffset += 4
	elif nodeType in ['realNum', 'realNumFP']:
		gn.memOffset += 8
	elif nodeType in ['intNumArray', 'intNumArrayFP']:
		assert arrayLength != -1
		gn.memOffset += 4*arrayLength
	elif nodeType in ["realNumArray", "realNumArrayFP"]:
		assert arrayLength != -1
		gn.memOffset += 8*arrayLength
	else:
		#TODO gotta figure out what to do about PPARAMS
		pass

	if nodeType in ['PPARAM', 'intNumFP', 'realNumFP', 'intNumArrayFP', 'realNumArrayFP']:
		#we can update the number of params in above green node
		callStack[-1].addParam()
		 #TODO perhaps more internal checks here (like making sure params are before
		 #local vars, and that PPARAMS are matched with PNAME green nodes, etc.)?
	#print 'Added BLUE node with name: ' + lexeme
	return True

'''
Returns the type of the lexeme based on the current static scope.
If the lexeme cannot be found in the current scope, ERR will be 
returned
'''
def getType(lexeme):
	# printWholeTree()
	index=len(callStack)-1
	# print '---The call stack is:---'
	# for b in callStack:
	# 	print b.nodeLex
	while index>=0:
		gn=callStack[index]
		# print "currently checking: " + gn.nodeLex
		if gn.nodeLex == lexeme:
			return gn.nodeType
		for node in gn.subNodes:
			if node.nodeLex == lexeme:
				return node.nodeType
		index-=1
	return 'ERR'

# def printWholeTree():
# 	index=len(callStack)-1
# 	print "------Whole Tree------"
# 	while index>=0:
# 		gn=callStack[index]
# 		print "green node: " + gn.nodeLex
# 		for node in gn.subNodes:
# 			print "blue node: " + node.nodeLex
# 		index-=1
# 	return 'ERR'

'''
Returns ERR if green node was not found
'''
def getGreenNode(lexeme):
	index=len(callStack)-1
	while index>=0:
		node=callStack[index]
		if node.nodeLex == lexeme:
			return node
		else:
			for child in node.subNodes:
				if isinstance(child, GreenNode) and child.nodeLex == lexeme:
					return child
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

def setGreenNodeReturnType(lexeme, returnType):
	assert type(lexeme) is str and type(returnType) is str
	if returnType not in ['intNum', 'realNum', 'intNumArray', 'realNumArray']:
		print nodeType + " is not a valid type"
		assert False
	gn = getGreenNode(lexeme)
	if gn is 'ERR':
		assert False
	gn.returnType = returnType

def getGreenNodeReturnType(lexeme):
	assert type(lexeme) is str
	gn = getGreenNode(lexeme)
	assert gn is not 'ERR'
	assert gn.returnType is not None
	assert gn.nodeType is not "PPARAM"
	return gn.returnType

def addArrayLength(lexeme, length):
	assert type(lexeme) is str and type(length) is int and length >= 0
	#TODO find blue node by lexeme
	#modify arrayLength attribute

def popStack():
	#TODO move memory address calculation down here
	# print 'popped ' + str(callStack[-1].nodeLex) + ' off the stack'
	callStack.pop()
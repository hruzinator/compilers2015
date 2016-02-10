import blueGreenTree as bgTree

bgTree.checkAddGreenNode('aProg', 'PNAME')
bgTree.checkAddBlueNode('input', 'PPARAM')
bgTree.checkAddBlueNode('output', 'PPARAM')
bgTree.checkAddBlueNode('a', 'intNum')
bgTree.checkAddBlueNode('b', 'realNumArray')
print bgTree.getType('a')
bgTree.checkAddGreenNode('f1', 'FNAME')
bgTree.checkAddBlueNode('a', 'intNumFP')
bgTree.checkAddBlueNode('b', 'realNumFP')
bgTree.checkAddBlueNode('c', 'realNum')
print bgTree.getType('a')
bgTree.checkAddGreenNode('f2', 'FNAME')
bgTree.checkAddBlueNode('x', 'intNumArrayFP')
bgTree.checkAddBlueNode('y', 'realNumFP')
print bgTree.getType('a')
print bgTree.getGreenNodeTypes('aProg')
print bgTree.getGreenNodeTypes('f1')
print bgTree.getGreenNodeTypes('f2')
bgTree.popStack()
print bgTree.getType('a')
bgTree.popStack()
print bgTree.getType('a')
print bgTree.getType('bogusVar')
bgTree.checkAddGreenNode('f3', 'FNAME')
bgTree.checkAddBlueNode('c', 'intNumFP')
bgTree.checkAddBlueNode('c', 'realNum')
print bgTree.getType('a')

'''
expected output

intNum
intNumFP
intNumFP
['PPARAM', 'PPARAM']
['intNumFP', 'realNumFP']
['intNumArrayFP', 'realNumFP']
intNumFP
intNum
ERR
intNum
'''
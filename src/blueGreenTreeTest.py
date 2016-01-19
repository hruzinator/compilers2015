import blueGreenTree as bgTree

bgTree.checkAddGreenNode('aProg', 'PNAME')
bgTree.checkAddBlueNode('input', 'PPARAM')
bgTree.checkAddBlueNode('output', 'PPARAM')
bgTree.checkAddBlueNode('a', 'INT')
bgTree.checkAddBlueNode('b', 'AREAL')
print bgTree.getType('a')
bgTree.checkAddGreenNode('f1', 'FNAME')
bgTree.checkAddBlueNode('a', 'FPINT')
bgTree.checkAddBlueNode('b', 'FPREAL')
bgTree.checkAddBlueNode('c', 'REAL')
print bgTree.getType('a')
bgTree.checkAddGreenNode('f2', 'FNAME')
bgTree.checkAddBlueNode('x', 'FPAINT')
bgTree.checkAddBlueNode('y', 'FPREAL')
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
bgTree.checkAddBlueNode('c', 'FPINT')
bgTree.checkAddBlueNode('c', 'REAL')
print bgTree.getType('a')

'''
expected output

INT
FPINT
FPINT
[PPARAM, PPARAM]
[FPINT, FPREAL]
[FPAINT, FPREAL]
FPINT
INT
ERR
INT
'''
'''
A python implementation of the symbol table abstract data type. The symbol table
is to be used througout the compilation process as new tokens and symbols are
assigned.
'''
class symbolTable:
    def __init__(self):
        self.symtable = []
    
    def insert(self, token):
        assert type(token) is dict
        assert 'lexeme' in token
        assert 'tokenType' in token
        for t in self.symtable:
            if t['lexeme'] == token['lexeme']:
                return None
        self.symtable.append(token)
        return self.symtable[-1]

    def lookup(self, token):
        if type(token) is dict:
            tokName = token["lexeme"]
        elif type(token) is str:
            tokName = token
        else:
            assert False
        for symToken in self.symtable:
            if tokName==symToken['lexeme']:
                return symToken
        return None

    def getIDType(self, token):
        assert token['tokenType'] is 'ID'
        tokAddr = token['attribute']
        for symToken in self.symtable:
            if tokAddr==symToken['attribute']:
                return symToken['attribute'] #TODO store ID types

    #looks to see if there is a lexeme that starts with a character sequence
    def hasStartsWith(self, sequence):
        assert type(sequence) is str
        for symToken in self.symtable:
            if str(symToken['lexeme']).startswith(sequence):
                return True
        return False

    def printSymbolTable(self):
        for symToken in self.symtable:
            print symToken

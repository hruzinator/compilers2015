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
        if token not in self.symtable:
            self.symtable.append(token)
            return self.symtable[-1]
        return None

    def lookup(self, token):
        if type(token) is dict:
            tokName = token["lexeme"]
        elif type(token) is str:
            tokName = token
        else:
            assert(False)
        for symToken in self.symtable:
            if tokName==symToken['lexeme']:
                return symToken
        else:
            return None


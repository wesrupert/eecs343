"""
This is a Python (2.7) implementation of the CFGtoPDA algorithm.

Author: Wes Rupert
"""

EPS = '-'
ALPHABET = ('a', 'b', 'char', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', \
        'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')

class GrammarStatement:
    """
    A statement in a context-free grammar.
    """
    def __init__(self, left, right, alphabet):
        self.left = left
        self.right = right
        self.alphabet = alphabet

    def get_left(self):
        """
        Gets the lhs of the statement.
        """
        return self.left
    
    def get_right(self):
        """
        Gets the rhs of the statement.
        """
        return self.right

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash(self.left) ^ hash(self.right)

    def __str__(self):
        return "%s -> %s" % (self.left, self.right)

class Grammar:
    """
    A context-free grammar.
    """
    def __init__(self, name, alphabet, start, *args):
        self._char = 0
        self.name = name
        self.alphabet = alphabet
        self.start = start
        self.statements = set()
        for arg in args:
            self.add(arg[0], arg[1])

    def add(self, left, right):
        """
        Adds a statement to the grammar.
        """
        self.statements.add(GrammarStatement(left, right, self.alphabet))

    def find(self, left, right):
        """
        Finds the matching statement in the grammar, if any.
        """
        for statement in self.statements:
            if statement.left == left and statement.right == right:
                return statement
        return None

    def __str__(self):
        string = self.name + ':'
        for statement in sorted( \
                self.statements, \
                key = str):
            if statement.left == self.start:
                string += '\nS|' + str(statement)
        for statement in sorted( \
                self.statements, \
                key = str):
            if statement.left != self.start:
                string += '\n |' + str(statement)
        return string

class PDAStatement:
    """
    A statement in a push-down automata.
    """
    def __init__(self, name, read, pop, goto, push):
        self.name = name
        self.read = read
        self.pop = pop
        self.goto = goto
        self.push = push

    def __hash__(self):
        return hash(self.name)    \
                ^ hash(self.read) \
                ^ hash(self.pop)  \
                ^ hash(self.goto) \
                ^ hash(self.push)

    def __str__(self):
        return "(%s, %s, %s), (%s, %s)" % ( \
                self.name, self.read, self.pop, self.goto, self.push)

class PDA:
    """
    A push-down automata.
    """
    def __init__(self, name, *args):
        self.name = name
        self.statements = set()
        for arg in args:
            self.add(*arg)

    def add(self, name, read, pop, goto, push):
        """
        Adds a statement to the PDA.
        """
        self.statements.add(PDAStatement( \
                name, read, pop, goto, push))

    def __str__(self):
        string = self.name + ':'
        for statement in sorted( \
                self.statements, \
                key = str):
            string += '\n' + str(statement)
        return string

def main():
    """
    The main function. Converts a sample CFG.
    """
    grammar = Grammar('Example', ALPHABET, 'S', \
            ('S', 'aA'),   \
            ('A', 'B'),    \
            ('A', 'CDCD'), \
            ('B', EPS),    \
            ('B', 'a'),    \
            ('C', 'BDD'),  \
            ('D', 'b'),    \
            ('D', EPS))
    print 'Converting the following to PDA. ' + str(grammar)
    cfgtopda(grammar, logging = True)

def cfgtopda(grammar, logging = False):
    nonterminals = set()
    terminals = set()
    _log(logging, 'Finding nonterminals: ', newline = False)
    for statement in grammar.statements:
        nonterminals.add(statement.left)
        _log(logging, statement.left + ', ', newline = False)
    _log(logging, '\nFinding terminals: ', newline = False)
    for statement in grammar.statements:
        for c in statement.right:
            if c not in nonterminals:
                terminals.add(c)
                _log(logging, c + ', ', newline = False)
    _log(logging, '\nCreating PDA.')
    pda = PDA(grammar.name, ('p', EPS, EPS, 'q', grammar.start))
    for statement in grammar.statements:
        newstatement = PDAStatement('q', EPS, statement.left, 'q', statement.right)
        _log(logging, '| Adding statement: ' + str(newstatement))
        pda.statements.add(newstatement)
    for terminal in terminals:
        newstatement = PDAStatement('q', terminal, terminal, 'q', EPS)
        _log(logging, '| Adding statement: ' + str(newstatement))
        pda.statements.add(newstatement)
    _log(logging, 'PDA complete. Result is: ' + str(pda))
    return pda

def _log(logging, string, newline = True):
    """
    Logs the string if logging is on.
    """
    if logging:
        if newline:
            print string
        else:
            print string,

if __name__ == "__main__":
    main()

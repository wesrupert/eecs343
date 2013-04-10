"""
This is a Python (2.7) implementation of the CFGtoCNF algorithm.

Author: Wes Rupert
"""

EPS = '-'
ALPHABET = ('a', 'b', 'char', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', \
        'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')

class Statement:
    """
    A statement in a context-free grammar.
    """
    def __init__(self, left, right, alphabet):
        self.left = left
        self.right = right
        self.alphabet = alphabet

    def is_eps(self):
        """
        Returns whether the statement has an epsilon in it.
        """
        for char in self.right:
            if char == EPS:
                return True
        return False

    def is_mixed(self):
        """
        Returns whether the statement has any terminals in it, and is not unit.
        """
        if len(self.right) == 1:
            return False
        for char in self.right:
            if char in self.alphabet:
                return True
        return False

    def is_unit(self):
        """
        Returns whether the statement has only a single rhs non-terminal.
        """
        return len(self.right) == 1 and self.right[0] not in self.alphabet

    def is_long(self):
        """
        Returns whether the statement is long.
        """
        return len(self.right) > 2

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
    def __init__(self, name, alphabet, *args):
        self._char = 0
        self.name = name
        self.alphabet = alphabet
        self.statements = set()
        for arg in args:
            self.statements.add(Statement(arg[0], arg[1], alphabet))

    def find(self, left, right):
        """
        Finds the matching statement in the grammar, if any.
        """
        for statement in self.statements:
            if statement.left == left and statement.right == right:
                return statement
        return None

    def is_nullable(self, production):
        """
        Returns whether the production in the context is nullable.
        """
        for statement in self.statements:
            if statement.left == production:
                if statement.is_eps():
                    return True
                elif not statement.is_mixed():
                    nullable = True
                    for char in statement.right:
                        nullable = nullable and self.is_nullable(char)
                    if nullable:
                        return True
        return False

    def remove_eps(self):
        """
        Removes all epsilon transitions from the context.
        """
        while True:
            new_grammar = set()
            to_remove = set()
            for statement in self.statements:
                for char in statement.right:
                    if char not in self.alphabet and self.is_nullable(char):
                        stmt = Statement(statement.left, \
                                statement.right.replace(char, ''), \
                                self.alphabet)
                        if len(stmt.right) == 0:
                            stmt.right = EPS
                        new_grammar.add(stmt)
                        to_remove.add(self.find(char, EPS))
            for statement in self.statements:
                if statement not in new_grammar and statement not in to_remove:
                    new_grammar.add(statement)
            if new_grammar == self.statements:
                break
            self.statements = new_grammar

    def remove_unit(self):
        """
        Removes all unit productions frm the grammar.
        """
        while True:
            new_grammar = set()
            to_remove = set()
            for statement in self.statements:
                if not statement.is_unit():
                    continue
                for stmt in self.statements:
                    if stmt.left == statement.right:
                        new_grammar.add(Statement( \
                                statement.left, \
                                stmt.right, \
                                self.alphabet))
                to_remove.add(statement)
            for statement in self.statements:
                if statement not in new_grammar and statement not in to_remove:
                    new_grammar.add(statement)
            if new_grammar == self.statements:
                break
            self.statements = new_grammar

    def remove_mixed(self):
        """
        Removes all mixed productions from the grammar.
        """
        while True:
            new_grammar = set()
            to_remove = set()
            for statement in self.statements:
                if not statement.is_mixed():
                    continue
                for char in statement.right:
                    if char not in self.alphabet:
                        continue
                    for stmt in self.statements:
                        if stmt.left == statement.left and len(stmt.right) > 1:
                            new_grammar.add(Statement( \
                                    statement.left, \
                                    stmt.right.replace(char, str(self._char)), \
                                    self.alphabet))
                    new_grammar.add(Statement( \
                            str(self._char), \
                            char, \
                            self.alphabet))
                    self._char += 1
                to_remove.add(statement)
            for statement in self.statements:
                if statement not in new_grammar and statement not in to_remove:
                    new_grammar.add(statement)
            if new_grammar == self.statements:
                break
            self.statements = new_grammar

    def remove_long(self):
        """
        Removes all long productions from the grammar.
        """
        while True:
            new_grammar = set()
            to_remove = set()
            for statement in self.statements:
                if not statement.is_long():
                    continue
                new_grammar.add(Statement( \
                        statement.left, \
                        statement.right[0] + str(self._char), \
                        self.alphabet))
                for i in range(1, len(statement.right) - 2):
                    new_grammar.add(Statement( \
                            str(self._char),  \
                            statement.right[i] + str(self._char + 1),  \
                            self.alphabet))
                    self._char += 1
                new_grammar.add(Statement( \
                        str(self._char),  \
                        statement.right[-2:],  \
                        self.alphabet))
                self._char += 1
                to_remove.add(statement)
            for statement in self.statements:
                if statement not in new_grammar and statement not in to_remove:
                    new_grammar.add(statement)
            if new_grammar == self.statements:
                break
            self.statements = new_grammar

    def __str__(self):
        string = self.name + ':'
        for statement in sorted( \
                self.statements, \
                key = str):
            if self.is_nullable(statement.left):
                string += '\nN'
            else:
                string += '\n '
            if statement.is_unit():
                string += 'U'
            else:
                string += ' '
            if statement.is_mixed():
                string += 'M'
            else:
                string += ' '
            if statement.is_long():
                string += 'L|'
            else:
                string += ' |'
            string += str(statement)
        return string

def main():
    """
    The main function. Converts a sample CFG.
    """
    grammar = Grammar('Example', ALPHABET, \
            ('S', 'aA'), \
            ('A', 'B'), \
            ('A', 'CDCD'), \
            ('B', EPS), \
            ('B', 'a'), \
            ('C', 'BDD'), \
            ('D', 'b'), \
            ('D', EPS))
    print 'Converting the following to CNF. ' + str(grammar)
    cfgtocnf(grammar, logging = True)

def cfgtocnf(grammar, logging = False):
    """
    Converts a given grammar to Chomsky Normal Form.
    """
    grammar.remove_eps()
    if logging:
        print 'Removing Eps. ' + str(grammar)
    grammar.remove_unit()
    if logging:
        print 'Removing Units. ' + str(grammar)
    grammar.remove_mixed()
    if logging:
        print 'Removing Mixed. ' + str(grammar)
    grammar.remove_long()
    if logging:
        print 'Removing Long. ' + str(grammar)
        print 'Conversion complete.'
    return grammar

if __name__ == "__main__":
    main()

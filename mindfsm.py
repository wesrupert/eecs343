"""
This is a Python (2.7) implementation of the minDFSM algorithm.

Author: Wes Rupert
"""

INIT = '_'

class Vertex:
    """
    A vertex directing a label to a target.
    """
    def __init__(self, label, target):
        """
        A vertex going frm one node to another.
        """
        self.label = label
        self.target = target

    def get_label(self):
        """
        Gets the label.
        """
        return self.label

    def get_target(self):
        """
        Gets the target.
        """
        return self.target

    def __str__(self):
        return "%s -> %s" % (self.label, self.target.name)

class Node:
    """
    A node in a finite state machine.

    Fields: name, init, final, vertices
    """
    def __init__(self, isinit, isfinal, *args, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs['name']
        else:
            self.name = "n"
        self.init = isinit
        self.final = isfinal
        self.vertices = []
        for vertextuple in args:
            label, target = vertextuple
            self.vertices.append(Vertex(label, target))

    def add(self, *args):
        """
        Adds a vertex to the list of vertices.
        """
        for arg in args:
            self.vertices.append(Vertex(arg[0], arg[1]))

    def set(self, *args):
        """
        Updates the vertices with the given label to the new target.
        """
        for arg in args:
            found = False
            for vertex in self.vertices:
                if vertex.label == arg[0]:
                    found = True
                    vertex.target = arg[1]
            if not found:
                self.vertices.append(Vertex(arg[0], arg[1]))

    def go_to(self, label):
        """
        Returns the first destination found matching the given label.
        """
        for vertex in self.vertices:
            if vertex.label == label:
                return vertex.target
        return None

    def similar(self, node):
        """
        Returns whether two Nodes have similar properties.

        Returns whether either both or neither is final or initial.
        """
        if node is None:
            return False
        return self.final == node.final

    def __eq__(self, other):
        if not self.similar(other):
            return False
        if self.name is not other.name:
            return False
        for vertex in self.vertices:
            if vertex not in other.vertices:
                return False
        for vertex in other.vertices:
            if vertex not in self.vertices:
                return False
        return True

    def __str__(self):
        string = '['
        if self.init:
            string += 'I'
        else:
            string += '_'
        if self.final:
            string += 'F'
        else:
            string += '_'
        string += '] %s' % self.name
        for vertex in self.vertices:
            string += ', ' + str(vertex)
        return string

NA = Node(True,  False, name = '1')
NB = Node(False, True,  name = '2')
NC = Node(False, False, name = '3')
ND = Node(False, True,  name = '4')
NE = Node(False, False, name = '5')
NF = Node(False, False, name = '6')
NA.add(('a', NB), ('b', ND))
NB.add(('a', NC), ('b', NF))
NC.add(('a', NB), ('b', ND))
ND.add(('a', NF), ('b', NE))
NE.add(('a', NB), ('b', ND))
NF.add(('a', NF), ('b', NF))
NODES = (NA, NB, NC, ND, NE, NF)

def main():
    """
    The main method.
    """
    print 'Minimizing the following DFSM:'
    print NA
    print NB
    print NC
    print ND
    print NE
    print NF
    print ''
    mindfsm(NODES, ('a', 'b'), logging = True)
    return 0

def mindfsm(nodes, labels, logging = False):
    """
    Minimizes the given DFSM.
    """
    names = [node.name for node in nodes]
    num_passes = 0
    old_grid = None
    grid = _init_grid(names)
    for row in range(len(names)):
        for col in range(row + 1, len(names)):
            if not nodes[row].similar(nodes[col]):
                grid[names[row]][names[col]] = False
    while (old_grid != grid):
        num_passes += 1
        if logging:
            print 'STARTING PASS %d\n' % num_passes
        old_grid = grid
        grid = _copy_grid(old_grid)
        if logging:
            _print_grid(grid)
        table = {INIT : []}
        for label in labels:
            table[label] = []
        for row in range(len(names)):
            for col in range(row + 1, len(names)):
                if grid[names[row]][names[col]]:
                    table[INIT].append((nodes[row], nodes[col]))
                    for label in labels:
                        gos = (nodes[row].go_to(label), nodes[col].go_to(label))
                        table[label].append(gos)
                        grid[names[row]][names[col]] = \
                                grid[names[row]][names[col]] and \
                                (_is_cell_set(grid, gos[0].name, gos[1].name) \
                                or gos[0] == gos[1])
        if logging:
            print '\nEND OF PASS %d\n' % num_passes
            _print_table(table)
            print ''

def _copy_grid(grid):
    """
    Copies the grid.
    """
    new_grid = dict(grid)
    for key in grid.keys():
        new_grid[key] = dict(grid[key])
    return new_grid

def _init_grid(labels):
    """
    Creates a new minDFSM grid.

    Grid is of the form:
        T T T T T
        X T T T T
        X X T T T
        X X X T T
        X X X X T
    """
    grid = {}
    donelabels = []
    for row in labels:
        curr = {}
        for col in labels:
            if col not in donelabels:
                curr[col] = True
            else:
                curr[col] = None
        grid[row] = curr
        donelabels.append(row)
    return grid

def _grid_eq(grid1, grid2):
    """
    Checks if two grids are equal.
    """
    if grid1 is None or grid2 is None:
        return False
    if len(grid1) is not len(grid2) or len(grid1[0]) is not len(grid2[0]):
        return False
    for row in range(len(grid1)):
        for col in range(row, len(grid1)):
            if grid1[row][col] is not grid2[row][col]:
                return False
    return True

def _is_cell_set(grid, row, col):
    """
    Returns true if the cell is not False, otherwise False.
    """
    if grid[row][col] is None:
        return grid[col][row]
    return grid[row][col]

def _print_grid(grid):
    """
    Prints the grid.
    """
    string = '___'
    for key in sorted(grid.keys()):
        string += '_' + key + '_'
    print string
    for key, val in sorted(grid.iteritems()):
        string = key + ' |'
        for i in sorted(grid.keys()):
            if val[i] is None:
                string += ' - '
            elif val[i]:
                string += '   '
            else:
                string += ' X '
        print string

def _print_table(table):
    """
    Prints the table.
    """
    for key, value in sorted(table.iteritems()):
        string = '['
        first = True
        for pair in value:
            if not first:
                string += ', '
            else:
                first = False
            string += '(%s, %s)' % (pair[0].name, pair[1].name)
        string += ']'
        print '%s: %s' % (key, string)

if __name__ == '__main__':
    main()

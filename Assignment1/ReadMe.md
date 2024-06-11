# COL719 - Assignment 1

## Submitted By:

`Name:`  Anjali Singh  
`Entry Number:`  2023JCS2565  

## Script Overview

## Prerequisites

- We need to install some python libraries to the run the python script.
  - Ply: 
    - `PLY` stands for "`Python Lex-Yacc`". 
    - It's a Python implementation of the lex and yacc tools for writing parsers for programming languages and other formal languages.
    - `Installation: pip install ply`
  - NetworkX:
    - `NetworkX` is a Python library used for creating, analyzing, and manipulating graphs and networks. 
    - It provides an extensive collection of tools for working with graph structures, algorithms, and visualization. and manipulating graphs.
    - `Installation: pip install networkx`
  - Matplotlib
    - `matplotlib.pyplot`is a comprehensive Python library for creating static, animated, and interactive visualizations in Python.
    - `Installation: pip install matplotlib`
  - Pygraphviz 
    - `PyGraphviz` is a Python interface to the Graphviz graph layout and visualization tool. It allows you to create, manipulate, and visualize graphs using the Graphviz library in Python scripts. 
    -`Installation:` 
    ```
    For macOS :
       brew install graphviz
       pip install pygraphviz

    For windows :
       You can download and install Graphviz from the Graphviz website (https://www.graphviz.org/download/) and then install PyGraphviz via pip.
       pip install pygraphviz

    For Unix :
       sudo apt-get update
       sudo apt-get install graphviz   
       pip install pygraphviz
   
    ```

### Imports and Class Definitions:
- The script imports several modules required for different functionalities:
- Class Definitions:
  - The `Node` class represents a node in a linked list.
  - The `LinkedList` class implements a linked list data structure.

### Lexer and Parser Definitions:
- Lexer and Parser:
  - `ply.lex` and `ply.yacc` are used for defining the lexer and parser, respectively.
  - They handle lexing (tokenization) and parsing (syntax analysis) of input expressions.
- Token Definitions:
  - Regular expressions defined using `tokens` specify the patterns for matching different token types in expressions.
- Error Handling:
  - `p_error` and `t_error` handle syntax errors and illegal characters encountered during lexing and parsing.
  - They ensure graceful error recovery and informative error messages for users.

### SSA Conversion and DFG Construction:
- Static Single Assignment (SSA) Conversion:
  - The `convert_to_ssa` function converts expressions to SSA form.
  - It recursively traverses the parsed expression, identifying variable dependencies and renaming variables if necessary.
- Directed Flow Graph (DFG) Construction:
  - The `construct_dfg` function constructs a DFG from the SSA expressions.
  - It recursively traverses the SSA expressions, creating nodes and edges in the graph based on data dependencies between variables.

### Drawing the AST and DFG:
- AST Drawing:
  - The `draw_ast` function visualizes the Abstract Syntax Trees (ASTs) corresponding to the parsed expressions.
  - It helps users understand the structure of expressions and how they are parsed.
- DFG Visualization:
  - The DFG is visualized using PyGraphviz, a Python interface to the Graphviz graph visualization software.
  -We are also dealing with `common subexpressions elimination` in this function.
  - Node labels and attributes are modified to represent different operations (e.g., '+', '-', '*', '/').
  - The resulting DFG is drawn and displayed as an image using Matplotlib.

### Execution Flow:
- Reading and Parsing:
  - Expressions are read from an input file (`example.txt`), parsed, and converted to SSA form.
- AST Construction from the parsed expressions
- Converting Parsed expressions to SSA xpressions to resolve WAR, WAW and RAW dependencies.
- DFG Construction and Visualization:
  - The DFG is constructed based on the SSA expressions, and node names are modified to represent different operations.
  - The constructed DFG is visualized and displayed as an image using Matplotlib.

Overall, the script provides a comprehensive pipeline for lexing, parsing, SSA conversion, DFG construction, and graph visualization, facilitating analysis of data dependencies and control flow in code.

## Code Segment





```py
import ply.yacc as yacc
import ply.lex as lex
import networkx as nx
import matplotlib.pyplot as plt
import pygraphviz as pgv

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def add_node(self, value):
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
        else:
            current_node = self.head
            while current_node.next is not None:
                current_node = current_node.next
            current_node.next = new_node
            
# Define the grammar
tokens = (
    'ADD',
    'SUB',
    'MUL',
    'DIV',
    'EQU',
    'CONST',
    'VARI',
)

# Token definitions
t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_DIV = r'/'
t_EQU = r'='
t_VARI = r'[a-zA-Z][0-9]*'
t_CONST = r'([0-9])+'

# Ignore spaces and tabs
t_ignore = ' \t\n'

# Build the lexer
lexer = lex.lex()

# Define the precedence and associativity
precedence = (
    ('left', 'EQU'),
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'DIV'),
)

# Define the grammar rules
def p_statement(p):
    '''statement : VARI EQU expression'''
    p[0] = ('EQU', p[1], p[3])

def p_expression(p):
    '''expression : term
                  | expression ADD term
                  | expression SUB term'''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '+':
        p[0] = ('ADD', p[1], p[3])
    elif p[2] == '-':
        p[0] = ('SUB', p[1], p[3])

def p_term(p):
    '''term : factor
            | term MUL factor
            | term DIV factor'''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '*':
        p[0] = ('MUL', p[1], p[3])
    elif p[2] == '/':
        p[0] = ('DIV', p[1], p[3])

def p_factor(p):
    '''factor : VARI
              | CONST'''
    p[0] = p[1]

# Error rule for syntax errors in tokens
def p_error(p):
    if p:
        print(f"Syntax error at token {p.type}")
        # Discard the token and advance to the next
        parser.errok()
    else:
        print("Syntax error at EOF")
    
# Error handling rule
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at index {t.lexpos}")
    t.lexer.skip(1)    

# Build the parser
parser = yacc.yacc()

right_side_variables = set()
left_side_variables =set()
variable_versions = {}
ssa = []
linked_list = LinkedList()

#For DFG
def construct_dfg(ssa, dfg=None):
    if dfg is None:
        dfg = pgv.AGraph(directed=True)

    # Dictionary to store operation nodes
    target_instance = {}
    target = set()
    target_tuple = {}

    def DFG_make(node):
        
        if node in target_tuple:
            return target_tuple[node]
        else:
            target_variable = node[0]
            if target_variable in target:
                target_instance[target_variable] += 1
                target_variable = f"{target_variable}_{target_instance[target_variable]}"
            else:
                target.add(target_variable)
                target_instance[target_variable] = 0
            target_tuple[node] = target_variable
        
        if len(node) == 3:   
            
            operation = node[0]
            operand1 = node[1]
            operand2 = node[2]
            
            dfg.add_node(target_variable)
            
            # Check if operand1 is a tuple representing an operation
            if isinstance(operand1, tuple):
                operand1 = DFG_make(operand1)
            # Check if operand2 is a tuple representing an operation
            if isinstance(operand2, tuple):
                operand2 = DFG_make(operand2)
            # Add edge from operand nodes to target_variable
            
            if isinstance(operand1, str):
                dfg.add_node(operand1)
                dfg.add_edge(operand1, target_variable)
            if isinstance(operand2, str):
                dfg.add_node(operand2)
                dfg.add_edge(operand2, target_variable)

            # if target_variable_copy == 'EQU':
            #     target_variable = node[1]
            #     dfg.add_node(target_variable)
            #     print("YES")
            #     operand2 = node[2]
            #     dfg.add_node(operand2)
            #     dfg.add_edge(operand2, target_variable)
                
        return target_variable
    
    for a in ssa:
        equal = DFG_make(a[2])
        dfg.add_node(a[1])
        dfg.add_edge(equal,a[1])
    return dfg

# Function to draw the AST
def draw_ast(node, indent=0):
    if isinstance(node, tuple):
        print(" " * indent + node[0])
        for child in node[1:]:
            draw_ast(child, indent + 2)
    else:
        print(" " * indent + str(node))
        

def convert_to_ssa(expression):
    count =0
    # Helper function to recursively traverse the parsed AST and convert to SSA
    def convert_to_ssa_helper(node, bites):   
        if isinstance(node, tuple):
            operation = node[0]
            new_children = []
            for child in node[1:]:
                if node[0]=="EQU" and child == node[1]:
                    if (child in left_side_variables or child in right_side_variables):
                        if bites:
                            count = 1
                            Stri= f"{child}_{variable_versions[child]+1}"
                        else:    
                            variable_versions[child] += 1
                            Stri= f"{child}_{variable_versions[child]}"
                        new_children.append(Stri)
                    else:
                        variable_versions[child] = 0
                        new_children.append(child)
                    left_side_variables.add(child)    
                    
                else:    
                    new_children.append(convert_to_ssa_helper(child, bites))
            return (operation,) + tuple(new_children)
        elif isinstance(node, str):
            if node.isdigit():  # Check if it's a constant
                return node
            variable = node
            right_side_variables.add(variable)
            if variable in variable_versions:
                pass
            else:
                variable_versions[variable] = 0
            # Check if the variable has been defined in previous expressions
           
            if variable in left_side_variables and variable_versions[variable]>0:
                return f"{variable}_{variable_versions[variable]}"
            else:
                # This is the first definition of the variable, use the same name
                return variable
            
    bites = False       
    check = parsed[1]
    def dependency(seq):
        for i in seq:
            if i == check:
                return True
            if isinstance(i, tuple):
                dependency(i) 
        
    # parsed = ('EQU', 'd', ('SUB', 'a', 'd'))            
    bites = dependency(parsed[2])
    
    ssa_expression = convert_to_ssa_helper(parsed, bites)
    if count == 1:
         variable_versions[parsed[1]] += 1
    return ssa_expression

def change_node_name():
    for node in dfg.nodes():
        if node.startswith("ADD"):    
            dfg.get_node(node).attr['label'] = '+'
        if node.startswith("MUL"):    
            dfg.get_node(node).attr['label'] = '*'
        if node.startswith("DIV"):    
            dfg.get_node(node).attr['label'] = '/'
        if node.startswith("SUB"):    
            dfg.get_node(node).attr['label'] = '-'
 
def draw_dfg():      
    # Draw the DFG using PyGraphviz
    dfg.layout(prog='dot')
    dfg.draw('dfg_pygraphviz.png')

    # Display the generated DFG image
    img = plt.imread('dfg_pygraphviz.png')
    plt.imshow(img)
    plt.axis('off')
    plt.show()

expressions = []
with open("example.txt", "r") as file:
    for line in file:
        expressions.append(line.strip())

# Parse each expression and add it to a linked list
i=0
for expression in expressions:
    i = i+1
    parsed = parser.parse(expression, lexer=lexer)
    # Convert expression to SSA with dependencies considered
    ssa_expression = convert_to_ssa(parsed)
    print("Expression",i," : ",ssa_expression)
    linked_list.add_node(parsed)
    ssa.append(ssa_expression)
    
# Traverse the linked list and draw the AST for each node
current_node = linked_list.head
idx = 1
while current_node is not None:
    print(f"Expression {idx}: ",ssa[idx-1])
    print(f"Expression {idx}:")
    draw_ast(current_node.value)
    print()
    current_node = current_node.next
    idx += 1
    
dfg = construct_dfg(ssa)

change_node_name()

draw_dfg()


```

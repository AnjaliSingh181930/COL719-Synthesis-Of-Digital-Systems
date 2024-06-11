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
            
        dfg.add_node(target_variable)
        if len(node) == 3:   
            operation = node[0]
            operand1 = node[1]
            operand2 = node[2]
            
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

        elif len(node) == 2:
            operand1 = node[1]
            # Check if operand1 is a tuple representing an operation
            if isinstance(operand1, tuple):
                operand1 = DFG_make(operand1)
            # Add edge from operand node to target_variable
            elif isinstance(operand1, str):
                dfg.add_node(operand1)
                dfg.add_edge(operand1, target_variable)
                
        return target_variable
    
    for a in ssa:
        DFG_make(a)
        
    return dfg

# Function to draw the AST
def draw_ast(node, indent=0):
    if isinstance(node, tuple):
        print(" " * indent + node[0])
        for child in node[1:]:
            draw_ast(child, indent + 2)
    else:
        print(" " * indent + str(node))
        
right_side_variables = set()
left_side_variables =set()
variable_versions = {}

def convert_to_ssa(expression):
    # Helper function to recursively traverse the parsed AST and convert to SSA
    def convert_to_ssa_helper(node):   
        if isinstance(node, tuple):
            operation = node[0]
            new_children = []
            for child in node[1:]:
                if node[0]=="EQU" and child == node[1]:
                    if child in left_side_variables or child in right_side_variables: 
                        variable_versions[child] += 1
                        Stri= f"{child}_{variable_versions[child]}"
                        new_children.append(Stri)
                    else:
                        variable_versions[child] = 0
                        new_children.append(child)
                    left_side_variables.add(child)    
                    
                else:    
                    new_children.append(convert_to_ssa_helper(child))
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

    # Convert the parsed AST to SSA form
    ssa_expression = convert_to_ssa_helper(parsed)

    return ssa_expression

# Example expressions to parse
expressions = []
with open("exampl.txt", "r") as file:
    for line in file:
        expressions.append(line.strip())


ssa = []
# Parse each expression and add it to a linked list
linked_list = LinkedList()
for expression in expressions:
    parsed = parser.parse(expression, lexer=lexer)
    # Convert expression to SSA with dependencies considered
    ssa_expression = convert_to_ssa(parsed)
    linked_list.add_node(parsed)
    ssa.append(ssa_expression)

# Traverse the linked list and draw the AST for each node
current_node = linked_list.head
idx = 1
while current_node is not None:
    print(f"Expression {idx}:")
    draw_ast(current_node.value)
    print()
    current_node = current_node.next
    idx += 1
    

# Construct the DFG
dfg = construct_dfg(ssa)

#Change the names
for node in dfg.nodes():
    if node.startswith("ADD_"):    
        dfg.get_node(node).attr['label'] = 'ADD'
    if node.startswith("MUL_"):    
        dfg.get_node(node).attr['label'] = 'MUL'
    if node.startswith("DIV_"):    
        dfg.get_node(node).attr['label'] = 'DIV'
    if node.startswith("EQU_"):    
        dfg.get_node(node).attr['label'] = 'EQU'
    if node.startswith("SUB_"):    
        dfg.get_node(node).attr['label'] = 'SUB'
    
        
# Draw the DFG using PyGraphviz
dfg.layout(prog='dot')
dfg.draw('dfg_pygraphviz.png')

# Display the generated DFG image
img = plt.imread('dfg_pygraphviz.png')
plt.imshow(img)
plt.axis('off')
plt.show()




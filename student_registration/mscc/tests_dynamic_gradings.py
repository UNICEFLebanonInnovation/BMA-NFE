import re
import ast

def get_ast(path):
    with open(path, 'r') as f:
        return ast.parse(f.read())

print("Testing AST")

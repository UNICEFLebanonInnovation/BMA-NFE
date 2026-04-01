import ast

def get_ast(path):
    with open(path, 'r') as f:
        return ast.parse(f.read())

get_ast('student_registration/mscc/templatetags/education_tags.py')
print("Testing Tags AST")

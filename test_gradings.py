import re

def parse_gradings():
    content = open('student_registration/mscc/education_form.py').read()
    # Simple regex to see what field_init looks like
    matches = re.findall(r"if programme_type in \[(.*?)\]:|if programme_type == \"(.*?)\":([\s\S]*?)(?=if programme_type|$)", content)
    for m in matches:
        pass

parse_gradings()

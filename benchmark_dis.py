import dis
def old_code(key):
    return key in ['life_skills', 'english_development', 'financial_development', 'it_development']

def new_code(key):
    return key in {'life_skills', 'english_development', 'financial_development', 'it_development'}

print("Old:")
dis.dis(old_code)

print("New:")
dis.dis(new_code)

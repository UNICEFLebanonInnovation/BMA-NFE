import timeit

setup = """
post_keys = [
    'math_grade', 'science_grade', 'life_skills', 'english_development',
    'financial_development', 'it_development', 'something_else', 'another_thing'
]
REQUIRED_KEYS = {'life_skills', 'english_development', 'financial_development', 'it_development'}
"""

old_code = """
for key in post_keys:
    if key.endswith('_grade') or key in ['life_skills', 'english_development', 'financial_development', 'it_development']:
        pass
"""

new_code_set = """
for key in post_keys:
    if key.endswith('_grade') or key in REQUIRED_KEYS:
        pass
"""

print("Old code:")
print(timeit.timeit(old_code, setup=setup, number=1000000))

print("New code (set):")
print(timeit.timeit(new_code_set, setup=setup, number=1000000))

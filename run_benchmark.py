import django
import os
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
django.setup()

from student_registration.mscc.views import DashboardView
from student_registration.mscc.models import Registration, EducationProgrammeAssessment

# Create some dummy data
# Just manually run the loop we want to optimize

class DummyPostTest:
    def keys(self):
        return ['math_grade', 'science_grade', 'life_skills', 'english_development',
                'financial_development', 'it_development', 'something_else', 'another_thing']
    def __getitem__(self, item):
        return 50.0

class DummyPreTest:
    def get(self, item, default):
        return 40.0

assessments = [
    {
        'programme_type': 'BLN Level 1',
        'pre_test': DummyPreTest(),
        'post_test': DummyPostTest()
    } for _ in range(1000)
]

def run_old():
    improvements = {}
    for p in assessments:
        ptype = p.get('programme_type') or 'Unknown'
        pre = p.get('pre_test') or {}
        post = p.get('post_test') or {}

        if ptype not in improvements:
            improvements[ptype] = {}

        for key in post.keys():
            if key.endswith('_grade') or key in ['life_skills', 'english_development', 'financial_development', 'it_development']:
                try:
                    post_val = float(post[key])
                    pre_val = float(pre.get(key, 0))
                    if pre_val > 0:
                        imp = ((post_val - pre_val) / pre_val) * 100
                        if key not in improvements[ptype]:
                            improvements[ptype][key] = []
                        improvements[ptype][key].append(imp)
                except (ValueError, TypeError):
                    pass

REQUIRED_KEYS = {'life_skills', 'english_development', 'financial_development', 'it_development'}

def run_new():
    improvements = {}
    for p in assessments:
        ptype = p.get('programme_type') or 'Unknown'
        pre = p.get('pre_test') or {}
        post = p.get('post_test') or {}

        if ptype not in improvements:
            improvements[ptype] = {}

        for key in post.keys():
            if key.endswith('_grade') or key in REQUIRED_KEYS:
                try:
                    post_val = float(post[key])
                    pre_val = float(pre.get(key, 0))
                    if pre_val > 0:
                        imp = ((post_val - pre_val) / pre_val) * 100
                        if key not in improvements[ptype]:
                            improvements[ptype][key] = []
                        improvements[ptype][key].append(imp)
                except (ValueError, TypeError):
                    pass

import timeit
print("Old:", timeit.timeit(run_old, number=100))
print("New:", timeit.timeit(run_new, number=100))

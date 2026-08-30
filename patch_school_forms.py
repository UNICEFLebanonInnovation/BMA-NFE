import re

with open('student_registration/schools/forms.py', 'r') as f:
    content = f.read()

new_fields = """    receive_supplies = forms.ChoiceField(
        label=_("Did the school receive school supplies/stationery?"),
        widget=forms.Select, required=True,
        choices=School.YES_NO
    )
    admin_staff_number = forms.ChoiceField(
        label=_("Number of Admin staff in the school"),
        widget=forms.Select, required=False,
        choices=((x, x) for x in range(0, 300)),
    )
    offer_digital_learning = forms.ChoiceField(
        label=_("Does the school offer digital learning services?"),
        widget=forms.Select, required=False,
        choices=School.YES_NO
    )
    have_digital_hub = forms.ChoiceField(
        label=_("Does the school have a digital hub?"),
        widget=forms.Select, required=False,
        choices=School.YES_NO
    )
    neaby_phcc = forms.CharField(
        label=_("Nearby PHCC name"),
        widget=forms.TextInput(attrs={'placeholder': _('Nearby PHCC name')}),
        required=False
    )
"""

content = content.replace('    receive_supplies = forms.ChoiceField(\n        label=_("Did the school receive school supplies/stationery?"),\n        widget=forms.Select, required=True,\n        choices=School.YES_NO\n    )', new_fields)

new_layout_part = """                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('longitude', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('latitude', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('is_closed', css_class='col-md-3 '),
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('admin_staff_number', css_class='col-md-3 '),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('offer_digital_learning', css_class='col-md-3 '),
                    HTML('<span class="badge-form-2 badge-pill">15</span>'),
                    Div('have_digital_hub', css_class='col-md-3 '),
                    HTML('<span class="badge-form-2 badge-pill">16</span>'),
                    Div('neaby_phcc', css_class='col-md-3 '),
                    css_class='row card-body',
                ),
                css_id='step-1'
"""

content = content.replace("""                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('longitude', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('latitude', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('is_closed', css_class='col-md-3 '),
                    css_class='row card-body',
                ),
                css_id='step-1'""", new_layout_part)


# update fields in Meta
new_meta = """            'academic_year_start',
            'academic_year_end',
            'receive_supplies',
            'admin_staff_number',
            'offer_digital_learning',
            'have_digital_hub',
            'neaby_phcc',
            'number_dirasa_children_disability',"""
content = content.replace("""            'academic_year_start',
            'academic_year_end',
            'receive_supplies',
            'number_dirasa_children_disability',""", new_meta)

with open('student_registration/schools/forms.py', 'w') as f:
    f.write(content)

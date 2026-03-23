from django import forms


class DatePickerInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, attrs=None, format=None):
        super().__init__(attrs)
        if attrs is None:
            attrs = {}
        attrs.setdefault('placeholder', 'YYYY-MM-DD')
        self.attrs = attrs


class TimePickerInput(forms.TimeInput):
    input_type = 'time'


class DateTimePickerInput(forms.DateTimeInput):
    input_type = 'datetime'

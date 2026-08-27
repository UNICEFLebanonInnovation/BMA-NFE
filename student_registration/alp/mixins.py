class ALPSchoolFilterMixin:
    """
    Mixin for ModelForms to filter school-related dropdowns
    so users can only select data within their own school, unless they are superusers.
    """
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and not self.request.user.is_superuser:
            user_school_id = self.request.user.school_id
            if 'school' in self.fields:
                self.fields['school'].queryset = self.fields['school'].queryset.filter(id=user_school_id)
            if 'registration' in self.fields:
                self.fields['registration'].queryset = self.fields['registration'].queryset.filter(school_id=user_school_id)
            if 'teacher' in self.fields:
                self.fields['teacher'].queryset = self.fields['teacher'].queryset.filter(school_id=user_school_id)

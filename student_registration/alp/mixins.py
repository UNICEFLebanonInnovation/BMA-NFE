class ALPSchoolFilterMixin:
    """
    Mixin for ModelForms to filter school-related dropdowns
    so users can only select data within their own school, unless they are superusers.

    The form accepts either ``request=`` (what the views pass) or ``user=``.
    """
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        if self.user is None and self.request is not None:
            self.user = getattr(self.request, 'user', None)
        super().__init__(*args, **kwargs)
        if self.user is not None and not getattr(self.user, 'is_superuser', False):
            user_school_id = getattr(self.user, 'school_id', None)
            if 'school' in self.fields:
                self.fields['school'].queryset = self.fields['school'].queryset.filter(id=user_school_id)
            if 'registration' in self.fields:
                self.fields['registration'].queryset = self.fields['registration'].queryset.filter(
                    school_id=user_school_id, deleted=False,
                )
            if 'teacher' in self.fields:
                self.fields['teacher'].queryset = self.fields['teacher'].queryset.filter(school_id=user_school_id)

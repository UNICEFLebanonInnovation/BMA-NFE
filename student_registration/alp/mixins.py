class ALPSchoolFilterMixin:
    """
    Mixin for ModelForms to filter the 'school' field dropdown
    so users can only select their own school, unless they are superusers.
    """
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and not self.request.user.is_superuser:
            if 'school' in self.fields:
                self.fields['school'].queryset = self.fields['school'].queryset.filter(id=self.request.user.school_id)

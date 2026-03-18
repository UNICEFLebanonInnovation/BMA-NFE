from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db.models import CharField, IntegerField, DateField, DateTimeField, BooleanField

def get_model_fields(model, prefix=''):
    """Recursively get fields for a model, up to 1 level of foreign keys."""
    fields = []
    for field in model._meta.get_fields():
        if field.is_relation and (isinstance(field, ForeignKey) or isinstance(field, OneToOneField)):
            if prefix == '': # Only go 1 level deep to avoid infinite recursion or massive lists
                related_model = field.related_model
                if related_model:
                    fields.extend(get_model_fields(related_model, prefix=f"{field.name}__"))
        elif not field.is_relation:
            # We only want simple fields (strings, ints, dates, bools)
            if isinstance(field, (CharField, IntegerField, DateField, DateTimeField, BooleanField)):
                fields.append({
                    'id': f"{prefix}{field.name}",
                    'label': f"{prefix.replace('__', ' ').title()}{field.verbose_name.title()}",
                    'type': field.get_internal_type()
                })
    return fields

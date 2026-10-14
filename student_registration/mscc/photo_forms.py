"""Validate a standalone replacement for a registered child's photograph."""

import io

from django import forms
from django.utils.translation import gettext_lazy as _
from PIL import Image


class PhotoUploadForm(forms.Form):
    photo = forms.ImageField(
        label=_('Child Photo'),
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
    )

    def clean_photo(self):
        photo = self.cleaned_data['photo']
        try:
            with Image.open(io.BytesIO(photo.read())) as image:
                image.load()
        except (OSError, ValueError, SyntaxError, Image.DecompressionBombError):
            raise forms.ValidationError(_('Upload a valid photograph.'))
        finally:
            photo.seek(0)
        return photo

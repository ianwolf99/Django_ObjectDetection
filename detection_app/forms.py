from django import forms
from .models import UploadedImage

class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']  # Specify the field(s) you want to include in the form
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': False})
        }

from django import forms
from .models import AdminProfile

class PerfilAdminForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ['foto', 'correo']
        widgets = {
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico',
            }),
            'foto': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
            }),
        }

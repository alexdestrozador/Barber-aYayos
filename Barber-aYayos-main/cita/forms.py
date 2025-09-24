from django import forms
from django.contrib.auth.models import User
from .models import AdminProfile, Barbero

class PerfilAdminForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ['foto']  # solo permitimos editar la foto
        widgets = {
            'foto': forms.ClearableFileInput(attrs={
                'class': 'form-control-file text-light'
            }),
        }
        
        

class BarberoPerfilForm(forms.ModelForm):
    username = forms.CharField(label="Nombre de usuario", max_length=150)
    first_name = forms.CharField(label="Nombre", max_length=150)
    telefono = forms.CharField(label="Teléfono", max_length=15, required=False)

    # campos extras solo para edición
    password = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = Barbero
        fields = ["telefono"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # precargar datos del user
        if self.user:
            self.fields["username"].initial = self.user.username
            self.fields["first_name"].initial = self.user.first_name

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.exclude(pk=self.user.pk).filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password or password2:
            if password != password2:
                self.add_error("password2", "Las contraseñas no coinciden.")
            elif len(password) < 6:
                self.add_error("password", "La contraseña debe tener al menos 6 caracteres.")
        return cleaned_data





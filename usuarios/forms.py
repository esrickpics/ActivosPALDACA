import re

from django import forms
from django.contrib.auth import get_user_model

from core.models import Perfil

UserModel = get_user_model()


class UsuarioForm(forms.ModelForm):
    """Gestión en Activos sobre campos nativos de core.UsuarioPaldaca."""

    class Meta:
        model = UserModel
        fields = [
            "first_name",
            "last_name",
            "email",
            "telefono",
            "perfil",
            "is_active",
        ]
        labels = {
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "email": "Correo electrónico",
            "telefono": "Teléfono",
            "perfil": "Perfil",
            "is_active": "Usuario activo",
        }
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombres del usuario"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Apellidos del usuario"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "correo@ejemplo.com"}
            ),
            "telefono": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Número de teléfono"}
            ),
            "perfil": forms.Select(
                attrs={"class": "form-select"},
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = False
        self.fields["telefono"].required = False
        self.fields["perfil"].required = False
        self.fields["perfil"].queryset = Perfil.objects.order_by("nombre")
        self.fields["perfil"].empty_label = "Sin perfil asignado"

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.pk:
            user.set_unusable_password()
            if not user.username:
                user.username = self._nuevo_username(user)
        if commit:
            user.save()
        return user

    @staticmethod
    def _nuevo_username(user):
        if user.email:
            base = user.email.split("@")[0].lower()
        else:
            partes = [user.first_name.strip(), user.last_name.strip()]
            base = ".".join(p for p in partes if p).lower() or "usuario"
        base = re.sub(r"[^\w.@+-]", "", base)[:150] or "usuario"
        username = base
        n = 1
        while UserModel.objects.filter(username=username).exists():
            sufijo = f"-{n}"
            username = f"{base[: 150 - len(sufijo)]}{sufijo}"
            n += 1
        return username

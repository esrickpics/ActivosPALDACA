from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Disciplina, Modulo, Perfil, UsuarioModulo, UsuarioPaldaca


class UsuarioModuloInline(admin.TabularInline):
    model = UsuarioModulo
    extra = 0
    autocomplete_fields = ("modulo",)


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "activo")
    list_filter = ("activo",)
    search_fields = ("codigo", "nombre")
    ordering = ("nombre",)


@admin.register(UsuarioPaldaca)
class UsuarioPaldacaAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "rol",
        "disciplina",
        "perfil",
        "is_staff",
        "is_active",
    )
    list_filter = ("rol", "disciplina", "perfil", "is_staff", "is_active", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    inlines = (UsuarioModuloInline,)
    autocomplete_fields = ("disciplina", "perfil")
    fieldsets = UserAdmin.fieldsets + (
        ("Contexto Paldaca", {"fields": ("rol", "disciplina", "perfil")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Contexto Paldaca", {"fields": ("rol", "disciplina", "perfil")}),
    )

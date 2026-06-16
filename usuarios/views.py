from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from activos.decorators import ModuloActivoRequiredMixin

from .forms import UsuarioForm

UserModel = get_user_model()


def _usuarios_gestion_queryset():
    return UserModel.objects.filter(is_active=True).select_related("perfil")


class UsuarioSearchView(ModuloActivoRequiredMixin, ListView):
    """Buscador de usuarios asignables (core_usuario)."""

    model = UserModel
    template_name = "usuarios/usuario_search.html"
    context_object_name = "usuarios"
    paginate_by = 10

    def get_queryset(self):
        queryset = _usuarios_gestion_queryset()
        buscar = self.request.GET.get("buscar", "").strip()
        if buscar:
            queryset = queryset.filter(
                Q(first_name__icontains=buscar)
                | Q(last_name__icontains=buscar)
                | Q(username__icontains=buscar)
                | Q(email__icontains=buscar)
                | Q(telefono__icontains=buscar)
                | Q(perfil__nombre__icontains=buscar)
            )
        return queryset.order_by("last_name", "first_name", "username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["buscar"] = self.request.GET.get("buscar", "")
        return context


class UsuarioProfileView(ModuloActivoRequiredMixin, DetailView):
    """Perfil con activos asignados."""

    model = UserModel
    template_name = "usuarios/usuario_profile.html"
    context_object_name = "usuario"

    def get_queryset(self):
        return _usuarios_gestion_queryset().prefetch_related(
            "activos_asignados__subcategoria__categoria",
            "activos_asignados__ubicacion",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.object
        context["activos_asignados"] = usuario.activos_asignados.select_related(
            "subcategoria__categoria", "ubicacion"
        )
        return context


class UsuarioCreateView(ModuloActivoRequiredMixin, CreateView):
    model = UserModel
    form_class = UsuarioForm
    template_name = "usuarios/usuario_form.html"
    success_url = reverse_lazy("usuarios:usuario-search")

    def form_valid(self, form):
        messages.success(self.request, "Usuario creado exitosamente.")
        return super().form_valid(form)


class UsuarioUpdateView(ModuloActivoRequiredMixin, UpdateView):
    model = UserModel
    form_class = UsuarioForm
    template_name = "usuarios/usuario_form.html"
    success_url = reverse_lazy("usuarios:usuario-search")

    def get_queryset(self):
        return UserModel.objects.select_related("perfil")

    def form_valid(self, form):
        messages.success(self.request, "Usuario actualizado exitosamente.")
        return super().form_valid(form)


class UsuarioDeleteView(ModuloActivoRequiredMixin, DeleteView):
    """Desactiva el usuario (no borra core_usuario compartido con SSO)."""

    model = UserModel
    template_name = "usuarios/usuario_confirm_delete.html"
    success_url = reverse_lazy("usuarios:usuario-search")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.get_full_name().strip() or self.object.username

        if self.object.activos_asignados.exists():
            messages.error(
                request,
                f'No se puede desactivar al usuario "{nombre}" porque tiene activos asignados.',
            )
            return redirect("usuarios:usuario-search")

        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "Usuario desactivado exitosamente.")
        return redirect(self.success_url)

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from activos.decorators import ModuloActivoRequiredMixin
from .models import UsuarioAsignado
from .forms import UsuarioForm


class UsuarioSearchView(ModuloActivoRequiredMixin, ListView):
    """Vista principal con buscador de usuarios"""
    model = UsuarioAsignado
    template_name = 'usuarios/usuario_search.html'
    context_object_name = 'usuarios'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(activo=True)
        buscar = self.request.GET.get('buscar')
        
        if buscar:
            queryset = queryset.filter(
                Q(nombres__icontains=buscar) |
                Q(apellidos__icontains=buscar) |
                Q(identificacion__icontains=buscar) |
                Q(email__icontains=buscar) |
                Q(cargo__icontains=buscar)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buscar'] = self.request.GET.get('buscar', '')
        return context


class UsuarioProfileView(ModuloActivoRequiredMixin, DetailView):
    """Vista de perfil de usuario con activos asignados"""
    model = UsuarioAsignado
    template_name = 'usuarios/usuario_profile.html'
    context_object_name = 'usuario'
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related('activos__subcategoria__categoria', 'activos__ubicacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.get_object()
        context['activos_asignados'] = usuario.activos.all().select_related(
            'subcategoria__categoria', 'ubicacion'
        )
        return context


class UsuarioCreateView(ModuloActivoRequiredMixin, CreateView):
    """Vista para crear usuario"""
    model = UsuarioAsignado
    form_class = UsuarioForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuarios:usuario-search')
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado exitosamente.')
        return super().form_valid(form)


class UsuarioUpdateView(ModuloActivoRequiredMixin, UpdateView):
    """Vista para editar usuario"""
    model = UsuarioAsignado
    form_class = UsuarioForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuarios:usuario-search')
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado exitosamente.')
        return super().form_valid(form)


class UsuarioDeleteView(ModuloActivoRequiredMixin, DeleteView):
    """Vista para eliminar usuario"""
    model = UsuarioAsignado
    template_name = 'usuarios/usuario_confirm_delete.html'
    success_url = reverse_lazy('usuarios:usuario-search')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar si tiene activos asignados
        if self.object.activos.exists():
            messages.error(self.request, f'No se puede eliminar el usuario "{self.object.nombre_completo}" porque tiene activos asignados.')
            return redirect('usuarios:usuario-search')
        
        messages.success(self.request, 'Usuario eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

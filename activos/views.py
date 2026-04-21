from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count
from .models import Categoria, SubCategoria, Ubicacion, Activo, HistorialMovimiento
from .forms import (
    CategoriaForm, SubCategoriaForm, UbicacionForm, 
    ActivoForm, ActivoFilterForm, ReasignarActivoForm, ReubicarActivoForm
)
from django.contrib.auth.decorators import login_required

# ============== VISTAS DE CATEGORÍA ==============
class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = 'activos/categoria/list.html'
    context_object_name = 'categorias'
    paginate_by = 20


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'activos/categoria/form.html'
    success_url = reverse_lazy('activos:categoria-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoría creada exitosamente.')
        return super().form_valid(form)


class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'activos/categoria/form.html'
    success_url = reverse_lazy('activos:categoria-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada exitosamente.')
        return super().form_valid(form)


class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'activos/categoria/confirm_delete.html'
    success_url = reverse_lazy('activos:categoria-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar si tiene subcategorías asociadas
        if self.object.subcategorias.exists():
            messages.error(self.request, f'No se puede eliminar la categoría "{self.object.nombre}" porque tiene subcategorías asociadas.')
            return redirect('activos:categoria-list')
        
        messages.success(self.request, 'Categoría eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============== VISTAS DE SUBCATEGORÍA ==============

class SubCategoriaListView(LoginRequiredMixin, ListView):
    model = SubCategoria
    template_name = 'activos/subcategoria/list.html'
    context_object_name = 'subcategorias'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('categoria')
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        return context


class SubCategoriaCreateView(LoginRequiredMixin, CreateView):
    model = SubCategoria
    form_class = SubCategoriaForm
    template_name = 'activos/subcategoria/form.html'
    success_url = reverse_lazy('activos:subcategoria-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Subcategoría creada exitosamente.')
        return super().form_valid(form)


class SubCategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = SubCategoria
    form_class = SubCategoriaForm
    template_name = 'activos/subcategoria/form.html'
    success_url = reverse_lazy('activos:subcategoria-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Subcategoría actualizada exitosamente.')
        return super().form_valid(form)


class SubCategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = SubCategoria
    template_name = 'activos/subcategoria/confirm_delete.html'
    success_url = reverse_lazy('activos:subcategoria-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar si tiene activos asociados
        if self.object.activos.exists():
            messages.error(self.request, f'No se puede eliminar la subcategoría "{self.object}" porque tiene activos asociados.')
            return redirect('activos:subcategoria-list')
        
        messages.success(self.request, 'Subcategoría eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============== VISTAS DE UBICACIÓN ==============

class UbicacionListView(LoginRequiredMixin, ListView):
    model = Ubicacion
    template_name = 'activos/ubicacion/list.html'
    context_object_name = 'ubicaciones'
    paginate_by = 20


class UbicacionCreateView(LoginRequiredMixin, CreateView):
    model = Ubicacion
    form_class = UbicacionForm
    template_name = 'activos/ubicacion/form.html'
    success_url = reverse_lazy('activos:ubicacion-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Ubicación creada exitosamente.')
        return super().form_valid(form)


class UbicacionUpdateView(LoginRequiredMixin, UpdateView):
    model = Ubicacion
    form_class = UbicacionForm
    template_name = 'activos/ubicacion/form.html'
    success_url = reverse_lazy('activos:ubicacion-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Ubicación actualizada exitosamente.')
        return super().form_valid(form)


class UbicacionDeleteView(LoginRequiredMixin, DeleteView):
    model = Ubicacion
    template_name = 'activos/ubicacion/confirm_delete.html'
    success_url = reverse_lazy('activos:ubicacion-list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar si tiene activos asociados
        if self.object.activos.exists():
            messages.error(self.request, f'No se puede eliminar la ubicación "{self.object.nombre}" porque tiene activos asociados.')
            return redirect('activos:ubicacion-list')
        
        messages.success(self.request, 'Ubicación eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============== VISTAS DE ACTIVO ==============

class ActivoListView(LoginRequiredMixin, ListView):
    model = Activo
    template_name = 'activos/activo/list.html'
    context_object_name = 'activos'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'subcategoria__categoria', 'ubicacion', 'usuario_asignado'
        )
        
        # Filtros
        categoria_id = self.request.GET.get('categoria')
        subcategoria_id = self.request.GET.get('subcategoria')
        ubicacion_id = self.request.GET.get('ubicacion')
        estado = self.request.GET.get('estado')
        buscar = self.request.GET.get('buscar')
        
        if categoria_id:
            queryset = queryset.filter(subcategoria__categoria_id=categoria_id)
        if subcategoria_id:
            queryset = queryset.filter(subcategoria_id=subcategoria_id)
        if ubicacion_id:
            queryset = queryset.filter(ubicacion_id=ubicacion_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        if buscar:
            queryset = queryset.filter(
                Q(codigo_inventario__icontains=buscar) |
                Q(marca__icontains=buscar) |
                Q(modelo__icontains=buscar) |
                Q(numero_serial__icontains=buscar)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ActivoFilterForm(self.request.GET or None)
        context['total_activos'] = self.get_queryset().count()
        
        # Estadísticas para el dashboard
        # Total de activos por categoría (top 5 con activos)
        context['activos_por_categoria'] = Categoria.objects.annotate(
            total_activos=Count('subcategorias__activos')
        ).filter(total_activos__gt=0).order_by('-total_activos')[:5]
        
        # Total de activos por ubicación (top 5 con activos)
        context['activos_por_ubicacion'] = Ubicacion.objects.annotate(
            total_activos=Count('activos')
        ).filter(total_activos__gt=0).order_by('-total_activos')[:5]
        
        # Estadísticas generales
        context['total_categorias'] = Categoria.objects.count()
        context['total_ubicaciones'] = Ubicacion.objects.count()
        context['total_activos_sistema'] = Activo.objects.count()
        
        return context


class ActivoDetailView(LoginRequiredMixin, DetailView):
    model = Activo
    template_name = 'activos/activo/detail.html'
    context_object_name = 'activo'
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'subcategoria__categoria', 'ubicacion', 'usuario_asignado'
        )


class ActivoCreateView(LoginRequiredMixin, CreateView):
    model = Activo
    form_class = ActivoForm
    template_name = 'activos/activo/form.html'
    success_url = reverse_lazy('activos:activo-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Activo creado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('activos:activo-detail', kwargs={'pk': self.object.pk})


class ActivoUpdateView(LoginRequiredMixin, UpdateView):
    model = Activo
    form_class = ActivoForm
    template_name = 'activos/activo/form.html'
    success_url = reverse_lazy('activos:activo-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Activo actualizado exitosamente.')
        return super().form_valid(form)


class ActivoDeleteView(LoginRequiredMixin, DeleteView):
    model = Activo
    template_name = 'activos/activo/confirm_delete.html'
    success_url = reverse_lazy('activos:activo-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Activo eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============== VISTAS ESPECIALES DE ACTIVO ==============

@login_required
def reasignar_activo(request, pk):
    """Vista para reasignar un activo a otro usuario"""
    activo = get_object_or_404(Activo, pk=pk)
    
    if request.method == 'POST':
        # Guardamos estado original desde BD antes de que el ModelForm
        # muta la instancia en memoria durante is_valid().
        activo_original = Activo.objects.select_related('usuario_asignado').get(pk=pk)
        form = ReasignarActivoForm(request.POST, instance=activo)
        if form.is_valid():
            usuario_anterior = activo_original.usuario_asignado
            activo_actualizado = form.save()
            usuario_nuevo = activo_actualizado.usuario_asignado

            if (usuario_anterior.id if usuario_anterior else None) != (usuario_nuevo.id if usuario_nuevo else None):
                valor_anterior = str(usuario_anterior) if usuario_anterior else 'Sin asignar'
                valor_nuevo = str(usuario_nuevo) if usuario_nuevo else 'Sin asignar'
                HistorialMovimiento.objects.create(
                    activo=activo_actualizado,
                    tipo_movimiento=HistorialMovimiento.TipoMovimiento.REASIGNACION,
                    descripcion=f"Reasignación de usuario: {valor_anterior} -> {valor_nuevo}",
                    campo_modificado='usuario_asignado',
                    valor_anterior=valor_anterior,
                    valor_nuevo=valor_nuevo,
                    usuario=request.user if request.user.is_authenticated else None,
                )

            messages.success(request, f'Activo {activo.codigo_inventario} reasignado exitosamente.')
            return redirect('activos:activo-detail', pk=pk)
    else:
        form = ReasignarActivoForm(instance=activo)
    
    return render(request, 'activos/activo/reasignar.html', {
        'form': form,
        'activo': activo
    })


@login_required
def reubicar_activo(request, pk):
    """Vista para reubicar un activo"""
    activo = get_object_or_404(Activo, pk=pk)
    
    if request.method == 'POST':
        # Guardamos estado original desde BD antes de que el ModelForm
        # muta la instancia en memoria durante is_valid().
        activo_original = Activo.objects.select_related('ubicacion').get(pk=pk)
        form = ReubicarActivoForm(request.POST, instance=activo)
        if form.is_valid():
            ubicacion_anterior = activo_original.ubicacion
            activo_actualizado = form.save()
            ubicacion_nueva = activo_actualizado.ubicacion

            if (ubicacion_anterior.id if ubicacion_anterior else None) != (ubicacion_nueva.id if ubicacion_nueva else None):
                valor_anterior = ubicacion_anterior.nombre if ubicacion_anterior else 'Sin ubicación'
                valor_nuevo = ubicacion_nueva.nombre if ubicacion_nueva else 'Sin ubicación'
                HistorialMovimiento.objects.create(
                    activo=activo_actualizado,
                    tipo_movimiento=HistorialMovimiento.TipoMovimiento.REUBICACION,
                    descripcion=f"Reubicación: {valor_anterior} -> {valor_nuevo}",
                    campo_modificado='ubicacion',
                    valor_anterior=valor_anterior,
                    valor_nuevo=valor_nuevo,
                    usuario=request.user if request.user.is_authenticated else None,
                )

            messages.success(request, f'Activo {activo.codigo_inventario} reubicado exitosamente.')
            return redirect('activos:activo-detail', pk=pk)
    else:
        form = ReubicarActivoForm(instance=activo)
    
    return render(request, 'activos/activo/reubicar.html', {
        'form': form,
        'activo': activo
    })


class ActivoHistorialView(LoginRequiredMixin, DetailView):
    """Vista para mostrar el historial de movimientos de un activo"""
    model = Activo
    template_name = 'activos/activo/historial.html'
    context_object_name = 'activo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activo = self.get_object()
        context['historial'] = activo.historial_movimientos.all().order_by('-fecha_movimiento')
        return context

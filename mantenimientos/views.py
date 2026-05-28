from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.db.models import Q, Sum, Case, When, DecimalField
from django.http import HttpResponseRedirect
from activos.models import Activo
from activos.decorators import ModuloActivoRequiredMixin, requiere_modulo_paldaca
from .models import Mantenimiento
from .forms import MantenimientoForm, MantenimientoFilterForm

class MantenimientoListView(ModuloActivoRequiredMixin, ListView):
    """Vista de lista de mantenimientos"""
    model = Mantenimiento
    template_name = 'mantenimientos/mantenimiento_list.html'
    context_object_name = 'mantenimientos'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('activo__subcategoria__categoria', 'activo__ubicacion')
        
        # Filtros
        estado = self.request.GET.get('estado', '')
        activo_id = self.request.GET.get('activo', '')
        buscar = self.request.GET.get('buscar', '')
        mes = self.request.GET.get('mes', '')
        año = self.request.GET.get('año', '')
        
        if estado:
            queryset = queryset.filter(estado=estado)
        if activo_id:
            queryset = queryset.filter(activo_id=activo_id)
        if buscar:
            queryset = queryset.filter(
                Q(tecnico__icontains=buscar) |
                Q(descripcion__icontains=buscar) |
                Q(activo__codigo_inventario__icontains=buscar)
            )
        if mes:
            queryset = queryset.filter(fecha__month=mes)
        if año:
            queryset = queryset.filter(fecha__year=año)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        from datetime import datetime
        context = super().get_context_data(**kwargs)
        context['filter_form'] = MantenimientoFilterForm(self.request.GET or None)
        
        # Estadísticas generales (sobre la data filtrada)
        queryset = self.get_queryset()
        context['total_mantenimientos'] = queryset.count()
        context['mantenimientos_en_proceso'] = queryset.filter(estado=Mantenimiento.EstadoMantenimiento.EN_PROCESO).count()
        context['mantenimientos_finalizados'] = queryset.filter(estado=Mantenimiento.EstadoMantenimiento.FINALIZADO).count()
        
        # Costos separados por estado (SOLO de la data filtrada)
        en_proceso_queryset = queryset.filter(estado=Mantenimiento.EstadoMantenimiento.EN_PROCESO)
        finalizados_queryset = queryset.filter(estado=Mantenimiento.EstadoMantenimiento.FINALIZADO)
        
        context['costo_en_proceso'] = en_proceso_queryset.aggregate(total=Sum('costo'))['total'] or 0
        context['costo_finalizado'] = finalizados_queryset.aggregate(total=Sum('costo'))['total'] or 0
        context['costo_total'] = context['costo_en_proceso'] + context['costo_finalizado']
        
        # Estadísticas globales (sin filtros de estado, solo fecha)
        # Queryset base para estadísticas temporales
        all_mantenimientos = Mantenimiento.objects.all()
        
        # Filtrar por mes/año si están presentes
        mes = self.request.GET.get('mes', '')
        año = self.request.GET.get('año', '')
        
        if mes:
            all_mantenimientos = all_mantenimientos.filter(fecha__month=mes)
        if año:
            all_mantenimientos = all_mantenimientos.filter(fecha__year=año)
        
        # Costos este mes (mes actual)
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        mantenimientos_mes_actual = Mantenimiento.objects.filter(
            fecha__month=current_month,
            fecha__year=current_year,
            estado=Mantenimiento.EstadoMantenimiento.FINALIZADO
        )
        context['gastos_mes_actual'] = mantenimientos_mes_actual.aggregate(total=Sum('costo'))['total'] or 0
        
        # Costos este año
        mantenimientos_año_actual = Mantenimiento.objects.filter(
            fecha__year=current_year,
            estado=Mantenimiento.EstadoMantenimiento.FINALIZADO
        )
        context['gastos_año_actual'] = mantenimientos_año_actual.aggregate(total=Sum('costo'))['total'] or 0
        
        # Total de costos finalizados del período filtrado
        finalizados_periodo = all_mantenimientos.filter(estado=Mantenimiento.EstadoMantenimiento.FINALIZADO)
        context['total_gastado_periodo'] = finalizados_periodo.aggregate(total=Sum('costo'))['total'] or 0
        
        return context

class MantenimientoCreateView(ModuloActivoRequiredMixin, CreateView):
    """Vista para crear un nuevo mantenimiento"""
    model = Mantenimiento
    form_class = MantenimientoForm
    template_name = 'mantenimientos/mantenimiento_form.html'
    success_url = reverse_lazy('mantenimientos:mantenimiento-list')
    
    def get_initial(self):
        """Pre-cargar el activo si viene por parámetro"""
        initial = super().get_initial()
        activo_id = self.request.GET.get('activo_id')
        if activo_id:
            initial['activo'] = activo_id
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activo_id = self.request.GET.get('activo_id')
        if activo_id:
            context['activo'] = get_object_or_404(Activo, pk=activo_id)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '✅ Mantenimiento agregado correctamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirigir al detalle del activo si viene de ahí"""
        activo_id = self.request.GET.get('activo_id')
        if activo_id:
            return reverse_lazy('activos:activo-detail', kwargs={'pk': activo_id})
        return self.success_url


class MantenimientoUpdateView(ModuloActivoRequiredMixin, UpdateView):
    """Vista para actualizar un mantenimiento"""
    model = Mantenimiento
    form_class = MantenimientoForm
    template_name = 'mantenimientos/mantenimiento_form.html'
    success_url = reverse_lazy('mantenimientos:mantenimiento-list')
    
    def form_valid(self, form):
        messages.success(self.request, '✅ Mantenimiento actualizado correctamente.')
        return super().form_valid(form)

class MantenimientoDetailView(ModuloActivoRequiredMixin, DetailView):
    """Vista de detalle de un mantenimiento"""
    model = Mantenimiento
    template_name = 'mantenimientos/mantenimiento_detail.html'
    context_object_name = 'mantenimiento'
    
    def get_queryset(self):
        return super().get_queryset().select_related('activo__subcategoria__categoria', 'activo__ubicacion', 'activo__usuario_asignado')

@requiere_modulo_paldaca
def finalizar_mantenimiento(request, pk):
    """Vista para finalizar un mantenimiento con un solo click"""
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    
    if mantenimiento.estado == Mantenimiento.EstadoMantenimiento.EN_PROCESO:
        mantenimiento.estado = Mantenimiento.EstadoMantenimiento.FINALIZADO
        mantenimiento.save()
        messages.success(
            request, 
            f'✅ Mantenimiento finalizado correctamente. Costo aplicado: ${mantenimiento.costo}'
        )
    else:
        messages.warning(request, '⚠️ Este mantenimiento ya está finalizado.')
    
    # Redirigir a la página anterior o a la lista
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse_lazy('mantenimientos:mantenimiento-list')))
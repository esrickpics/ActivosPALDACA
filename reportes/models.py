from django.db import models
from django.conf import settings


class ReporteGenerado(models.Model):
    """Modelo para registrar el historial de reportes generados"""
    
    class TipoReporte(models.TextChoices):
        GENERAL = 'GE', 'Reporte General de Activos'
        NOTA_ENTREGA = 'NE', 'Nota de Entrega'
    
    tipo = models.CharField(
        max_length=2,
        choices=TipoReporte.choices,
        verbose_name='Tipo de Reporte'
    )
    fecha_generacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Generación')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario'
    )
    filtros_aplicados = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Filtros Aplicados'
    )
    cantidad_activos = models.PositiveIntegerField(verbose_name='Cantidad de Activos')
    archivo_nombre = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nombre del Archivo'
    )
    
    class Meta:
        verbose_name = "Reporte Generado"
        verbose_name_plural = "Reportes Generados"
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha_generacion.strftime('%d/%m/%Y %H:%M')}"
from django.db import models


class UsuarioAsignado(models.Model):
    """Persona que puede ser asignada a un activo (sin autenticación)"""
    
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    pdf_asignacion = models.FileField(
        upload_to='usuarios/asignaciones_pdf/',
        blank=True,
        null=True
    )
    activo = models.BooleanField(default=True)
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Usuario Asignado"
        verbose_name_plural = "Usuarios Asignados"
        ordering = ['apellidos', 'nombres']
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

from django.core.management.base import BaseCommand

from core.models import Modulo

MODULOS_BASE = [
    ("portal", "Portal Paldaca"),
    ("calidad", "Calidad"),
    ("codigos", "Codigos"),
    ("activos", "Activos"),
    ("hdt", "Hoja de Tiempo"),
    ("ventas", "Ventas"),
    ("inventario", "Inventario"),
    ("rrhh", "Recursos Humanos"),
    ("proyectos", "Proyectos"),
]


class Command(BaseCommand):
    help = "Crea o actualiza el catalogo base de modulos Paldaca (core_modulo)."

    def handle(self, *args, **options):
        for codigo, nombre in MODULOS_BASE:
            modulo, created = Modulo.objects.update_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "activo": True},
            )
            action = "creado" if created else "actualizado"
            self.stdout.write(
                self.style.SUCCESS(f"Modulo '{modulo.codigo}' {action}: {modulo.nombre}")
            )

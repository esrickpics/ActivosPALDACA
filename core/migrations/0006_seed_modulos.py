from django.db import migrations

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


def seed_modulos(apps, schema_editor):
    Modulo = apps.get_model("core", "Modulo")
    for codigo, nombre in MODULOS_BASE:
        Modulo.objects.update_or_create(
            codigo=codigo,
            defaults={"nombre": nombre, "activo": True},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_modulo_usuario_modulo"),
    ]

    operations = [
        migrations.RunPython(seed_modulos, migrations.RunPython.noop),
    ]

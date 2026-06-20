from django.db import migrations

# Catalogo oficial de disciplinas Paldaca (gestionable tambien desde /admin).
DISCIPLINAS_CATALOGO = [
    ("Ambiente", "ingenieria"),
    ("Calidad", "ingenieria"),
    ("Civil", "ingenieria"),
    ("Confiabilidad", "ingenieria"),
    ("Contratos", "gerencia"),
    ("Control de documentos", "administrativo"),
    ("Electricidad", "ingenieria"),
    ("General", "gerencia"),
    ("Mecanica", "ingenieria"),
    ("Instrumentacion", "ingenieria"),
    ("Recursos humanos", "administrativo"),
    ("Telecomunicaciones", "ingenieria"),
    ("Planificacion", "gerencia"),
]


def seed_disciplinas_catalogo(apps, schema_editor):
    Disciplina = apps.get_model("core", "Disciplina")
    for nombre, area in DISCIPLINAS_CATALOGO:
        Disciplina.objects.update_or_create(
            nombre=nombre,
            defaults={"area": area},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_seed_disciplinas"),
    ]

    operations = [
        migrations.RunPython(seed_disciplinas_catalogo, migrations.RunPython.noop),
    ]

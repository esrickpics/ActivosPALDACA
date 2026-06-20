from django.db import migrations

# Disciplinas de semillas antiguas reemplazadas por el catalogo oficial.
DISCIPLINAS_OBSOLETAS = (
    "Compras",
    "Electrica",
    "Gerencia de Proyectos",
    "RRHH",
)


def remove_disciplinas_obsoletas(apps, schema_editor):
    Disciplina = apps.get_model("core", "Disciplina")
    UsuarioPaldaca = apps.get_model("core", "UsuarioPaldaca")

    for nombre in DISCIPLINAS_OBSOLETAS:
        disciplina = Disciplina.objects.filter(nombre=nombre).first()
        if not disciplina:
            continue
        if UsuarioPaldaca.objects.filter(disciplina_id=disciplina.pk).exists():
            continue
        disciplina.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_seed_disciplinas_catalogo"),
    ]

    operations = [
        migrations.RunPython(remove_disciplinas_obsoletas, migrations.RunPython.noop),
    ]

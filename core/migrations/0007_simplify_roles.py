from django.db import migrations, models


def migrate_roles_to_dos_niveles(apps, schema_editor):
    UsuarioPaldaca = apps.get_model("core", "UsuarioPaldaca")
    UsuarioPaldaca.objects.filter(
        rol__in=("admin_global", "admin_modulo")
    ).update(rol="administrador")
    UsuarioPaldaca.objects.filter(
        rol__in=("ingeniero", "usuario_comun")
    ).update(rol="usuario")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_seed_modulos"),
    ]

    operations = [
        migrations.RunPython(migrate_roles_to_dos_niveles, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="usuariopaldaca",
            name="rol",
            field=models.CharField(
                choices=[
                    ("usuario", "Usuario"),
                    ("administrador", "Administrador"),
                ],
                default="usuario",
                max_length=20,
            ),
        ),
        migrations.AlterModelOptions(
            name="usuariopaldaca",
            options={"db_table": "core_usuario"},
        ),
    ]

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0001_initial"),
        ("activos", "0003_usuario_asignado_core"),
    ]

    operations = [
        migrations.DeleteModel(
            name="UsuarioAsignado",
        ),
    ]

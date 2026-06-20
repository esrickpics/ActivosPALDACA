from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mantenimientos", "0001_initial"),
        ("activos", "0004_activos_prefijo_tablas"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="mantenimiento",
            table="activos_mantenimiento",
        ),
    ]

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reportes", "0001_initial"),
        ("activos", "0004_activos_prefijo_tablas"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="reportegenerado",
            table="activos_reporte_generado",
        ),
    ]

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("activos", "0003_usuario_asignado_core"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="categoria",
            table="activos_categoria",
        ),
        migrations.AlterModelTable(
            name="subcategoria",
            table="activos_subcategoria",
        ),
        migrations.AlterModelTable(
            name="ubicacion",
            table="activos_ubicacion",
        ),
        migrations.AlterModelTable(
            name="activo",
            table="activos_activo",
        ),
        migrations.AlterModelTable(
            name="historialmovimiento",
            table="activos_historial_movimiento",
        ),
    ]

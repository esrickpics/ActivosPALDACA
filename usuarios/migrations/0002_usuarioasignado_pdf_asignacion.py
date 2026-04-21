from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuarioasignado',
            name='pdf_asignacion',
            field=models.FileField(blank=True, null=True, upload_to='usuarios/asignaciones_pdf/'),
        ),
    ]

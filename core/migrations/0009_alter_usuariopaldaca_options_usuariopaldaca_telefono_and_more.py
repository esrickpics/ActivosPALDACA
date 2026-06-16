import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_perfil_disciplina_sin_area'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usuariopaldaca',
            options={'ordering': ('username',), 'verbose_name': 'Usuario', 'verbose_name_plural': 'Usuarios'},
        ),
        migrations.AddField(
            model_name='usuariopaldaca',
            name='telefono',
            field=models.CharField(blank=True, help_text='Teléfono del usuario', max_length=20, null=True, verbose_name='Teléfono'),
        ),
        migrations.AlterField(
            model_name='usuariopaldaca',
            name='perfil',
            field=models.ForeignKey(blank=True, help_text='Opcional. No es obligatorio asignarlo a todos los usuarios.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usuarios', to='core.perfil', verbose_name='perfil'),
        ),
    ]

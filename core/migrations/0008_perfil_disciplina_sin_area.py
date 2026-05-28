import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_simplify_roles"),
    ]

    operations = [
        migrations.CreateModel(
            name="Perfil",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100, unique=True)),
            ],
            options={
                "verbose_name": "Perfil",
                "verbose_name_plural": "Perfiles",
                "db_table": "core_perfil",
                "ordering": ("nombre",),
            },
        ),
        migrations.AlterModelOptions(
            name="disciplina",
            options={
                "ordering": ("nombre",),
                "verbose_name": "Disciplina",
                "verbose_name_plural": "Disciplinas",
            },
        ),
        migrations.AlterField(
            model_name="disciplina",
            name="nombre",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.RemoveField(
            model_name="disciplina",
            name="area",
        ),
        migrations.AddField(
            model_name="usuariopaldaca",
            name="perfil",
            field=models.ForeignKey(
                blank=True,
                help_text="Perfil funcional del usuario",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="usuarios",
                to="core.perfil",
            ),
        ),
        migrations.AlterField(
            model_name="usuariopaldaca",
            name="disciplina",
            field=models.ForeignKey(
                blank=True,
                help_text="Disciplina del usuario",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="usuarios",
                to="core.disciplina",
            ),
        ),
    ]

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_remove_disciplinas_obsoletas"),
    ]

    operations = [
        migrations.CreateModel(
            name="Modulo",
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
                (
                    "codigo",
                    models.SlugField(
                        help_text="Identificador estable del programa (ej. portal, hdt).",
                        max_length=32,
                        unique=True,
                    ),
                ),
                ("nombre", models.CharField(max_length=80)),
                ("activo", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Modulo",
                "verbose_name_plural": "Modulos",
                "db_table": "core_modulo",
                "ordering": ("nombre",),
            },
        ),
        migrations.CreateModel(
            name="UsuarioModulo",
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
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                (
                    "modulo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accesos_usuario",
                        to="core.modulo",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accesos_modulo",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Acceso a modulo",
                "verbose_name_plural": "Accesos a modulos",
                "db_table": "core_usuario_modulo",
            },
        ),
        migrations.AddConstraint(
            model_name="usuariomodulo",
            constraint=models.UniqueConstraint(
                fields=("usuario", "modulo"),
                name="core_usuario_modulo_unique",
            ),
        ),
        migrations.AddField(
            model_name="usuariopaldaca",
            name="modulos",
            field=models.ManyToManyField(
                blank=True,
                related_name="usuarios",
                through="core.UsuarioModulo",
                to="core.modulo",
            ),
        ),
    ]

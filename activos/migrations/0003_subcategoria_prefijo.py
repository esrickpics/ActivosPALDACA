from django.db import migrations, models


def poblar_prefijos_subcategoria(apps, schema_editor):
    SubCategoria = apps.get_model('activos', 'SubCategoria')
    usados = set()

    for subcategoria in SubCategoria.objects.order_by('id'):
        nombre = (subcategoria.nombre or '').upper()
        base = ''.join(ch for ch in nombre if ch.isalnum())[:3] or 'SUB'
        base = base[:5]

        candidato = base
        consecutivo = 1
        while candidato in usados:
            sufijo = str(consecutivo)
            candidato = f"{base[:max(1, 5 - len(sufijo))]}{sufijo}"
            consecutivo += 1

        subcategoria.prefijo = candidato
        subcategoria.save(update_fields=['prefijo'])
        usados.add(candidato)


def limpiar_prefijos_subcategoria(apps, schema_editor):
    SubCategoria = apps.get_model('activos', 'SubCategoria')
    SubCategoria.objects.update(prefijo=None)


class Migration(migrations.Migration):

    dependencies = [
        ('activos', '0002_historialmovimiento'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategoria',
            name='prefijo',
            field=models.CharField(blank=True, max_length=5, null=True, unique=True),
        ),
        migrations.RunPython(poblar_prefijos_subcategoria, limpiar_prefijos_subcategoria),
        migrations.AlterField(
            model_name='subcategoria',
            name='prefijo',
            field=models.CharField(max_length=5, unique=True),
        ),
    ]

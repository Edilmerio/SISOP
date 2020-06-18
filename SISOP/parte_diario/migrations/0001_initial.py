# Generated by Django 3.0.2 on 2020-06-18 23:50

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permisos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('estadistico', 'Estadistico'),),
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ClasificacionServicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clasificacion', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClavesInvalidas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clave', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PendientesAux',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.CharField(max_length=100, null=True)),
                ('fechar', models.CharField(max_length=100, null=True)),
                ('horar', models.CharField(max_length=100, null=True)),
                ('fechac', models.CharField(max_length=100, null=True)),
                ('horac', models.CharField(max_length=100, null=True)),
                ('grupo', models.CharField(max_length=100, null=True)),
                ('descgrupo', models.CharField(max_length=100, null=True)),
                ('centro', models.CharField(max_length=100, null=True)),
                ('telefono', models.CharField(max_length=100, null=True)),
                ('tiposerv', models.CharField(max_length=100, null=True)),
                ('categcli', models.CharField(max_length=100, null=True)),
                ('ultimademora', models.CharField(max_length=100, null=True)),
                ('idplantas', models.CharField(max_length=100, null=True)),
                ('nombpta', models.CharField(max_length=100, null=True)),
                ('idcentel', models.CharField(max_length=100, null=True)),
                ('descenttel', models.CharField(max_length=100, null=True)),
                ('iddt', models.CharField(max_length=100, null=True)),
                ('descdt', models.CharField(max_length=100, null=True)),
                ('region', models.CharField(max_length=100, null=True)),
                ('zona', models.CharField(max_length=100, null=True)),
                ('municipio', models.CharField(max_length=100, null=True)),
                ('date_r', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReparadasAux',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.CharField(max_length=100, null=True)),
                ('fechar', models.CharField(max_length=100, null=True)),
                ('horar', models.CharField(max_length=100, null=True)),
                ('fechac', models.CharField(max_length=100, null=True)),
                ('horac', models.CharField(max_length=100, null=True)),
                ('grupo', models.CharField(max_length=100, null=True)),
                ('descgrupo', models.CharField(max_length=100, null=True)),
                ('centro', models.CharField(max_length=100, null=True)),
                ('telefono', models.CharField(max_length=100, null=True)),
                ('tiposerv', models.CharField(max_length=100, null=True)),
                ('categcli', models.CharField(max_length=100, null=True)),
                ('clave', models.CharField(max_length=100, null=True)),
                ('ultimademora', models.CharField(max_length=100, null=True)),
                ('idplantas', models.CharField(max_length=100, null=True)),
                ('nombpta', models.CharField(max_length=100, null=True)),
                ('idcentel', models.CharField(max_length=100, null=True)),
                ('descenttel', models.CharField(max_length=100, null=True)),
                ('iddt', models.CharField(max_length=100, null=True)),
                ('descdt', models.CharField(max_length=100, null=True)),
                ('region', models.CharField(max_length=100, null=True)),
                ('zona', models.CharField(max_length=100, null=True)),
                ('municipio', models.CharField(max_length=100, null=True)),
                ('date_r', models.DateField(null=True)),
                ('date_c', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TipoServicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_servicio', models.CharField(max_length=100, unique=True)),
                ('identificativo', models.CharField(max_length=50, null=True, unique=True)),
                ('clasificacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parte_diario.ClasificacionServicio')),
            ],
        ),
        migrations.CreateModel(
            name='Reparadas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('rep_lte_1d', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')])),
                ('demora_lte_1d', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('rep_lte_3d', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')])),
                ('demora_lte_3d', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('rep_gt_3d', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')])),
                ('demora_gt_3d', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('central', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general.CentralTelefonica')),
                ('clasificacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parte_diario.ClasificacionServicio')),
            ],
        ),
        migrations.CreateModel(
            name='Pendientes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('pendientes', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')])),
                ('central', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general.CentralTelefonica')),
                ('clasificacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parte_diario.ClasificacionServicio')),
            ],
        ),
        migrations.CreateModel(
            name='LineasServicios',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datos', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')])),
                ('abonado', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')])),
                ('fecha', models.DateField()),
                ('centro_asociado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general.CentroAsociado')),
            ],
        ),
    ]
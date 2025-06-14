# Generated by Django 5.2.2 on 2025-06-05 21:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dni', models.CharField(max_length=20, unique=True, verbose_name='DNI/Cédula')),
                ('nombre_completo', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=15)),
                ('direccion', models.TextField()),
                ('fecha_registro', models.DateField(auto_now_add=True)),
                ('estado', models.BooleanField(default=True, verbose_name='Activo')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PerfilUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefono', models.CharField(max_length=15)),
                ('direccion', models.TextField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Prestamo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tasa_interes_mensual', models.DecimalField(decimal_places=2, max_digits=5)),
                ('numero_cuotas', models.PositiveIntegerField()),
                ('fecha_creacion', models.DateField(auto_now_add=True)),
                ('estado', models.CharField(choices=[('VIGENTE', 'Vigente'), ('PAGADO', 'Pagado'), ('MORA', 'En mora')], default='VIGENTE', max_length=10)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prestamos', to='prestamosapp.cliente')),
            ],
        ),
        migrations.CreateModel(
            name='Cuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_cuota', models.PositiveIntegerField()),
                ('valor_cuota', models.DecimalField(decimal_places=2, max_digits=10)),
                ('intereses', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amortizacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('saldo_pendiente', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_pago', models.DateField(blank=True, null=True)),
                ('pagada', models.BooleanField(default=False)),
                ('fecha_vencimiento', models.DateField()),
                ('prestamo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuotas', to='prestamosapp.prestamo')),
            ],
            options={
                'ordering': ['numero_cuota'],
            },
        ),
    ]

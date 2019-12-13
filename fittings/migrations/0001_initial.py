# Generated by Django 2.2.8 on 2019-12-13 03:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fitting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=1000)),
                ('name', models.CharField(max_length=255)),
                ('ship_type_type_id', models.IntegerField()),
            ],
            options={
                'permissions': (('access_fittings', 'Can access the fittings module.'),),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('type_name', models.CharField(max_length=500)),
                ('type_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('group_id', models.IntegerField()),
                ('published', models.BooleanField(default=False)),
                ('mass', models.FloatField(null=True)),
                ('capacity', models.FloatField(null=True)),
                ('description', models.CharField(max_length=5000)),
                ('volume', models.FloatField(null=True)),
                ('packaged_volume', models.FloatField(null=True)),
                ('portion_size', models.IntegerField(null=True)),
                ('radius', models.FloatField(null=True)),
                ('graphic_id', models.IntegerField(null=True)),
                ('icon_id', models.IntegerField(null=True)),
                ('market_group_id', models.IntegerField(null=True)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='FittingItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flag', models.CharField(choices=[('Cargo', 'Cargo'), ('DroneBay', 'DroneBay'), ('FighterBay', 'FighterBay'), ('HiSlot0', 'HiSlot0'), ('HiSlot1', 'HiSlot1'), ('HiSlot2', 'HiSlot2'), ('HiSlot3', 'HiSlot3'), ('HiSlot4', 'HiSlot4'), ('HiSlot5', 'HiSlot5'), ('HiSlot6', 'HiSlot6'), ('HiSlot7', 'HiSlot7'), ('Invalid', 'Invalid'), ('LoSlot0', 'LoSlot0'), ('LoSlot1', 'LoSlot1'), ('LoSlot2', 'LoSlot2'), ('LoSlot3', 'LoSlot3'), ('LoSlot4', 'LoSlot4'), ('LoSlot5', 'LoSlot5'), ('LoSlot6', 'LoSlot6'), ('LoSlot7', 'LoSlot7'), ('MedSlot0', 'MedSlot0'), ('MedSlot1', 'MedSlot1'), ('MedSlot2', 'MedSlot2'), ('MedSlot3', 'MedSlot3'), ('MedSlot4', 'MedSlot4'), ('MedSlot5', 'MedSlot5'), ('MedSlot6', 'MedSlot6'), ('MedSlot7', 'MedSlot7'), ('RigSlot0', 'RigSlot0'), ('RigSlot1', 'RigSlot1'), ('RigSlot2', 'RigSlot2'), ('ServiceSlot0', 'ServiceSlot0'), ('ServiceSlot1', 'ServiceSlot1'), ('ServiceSlot2', 'ServiceSlot2'), ('ServiceSlot3', 'ServiceSlot3'), ('ServiceSlot4', 'ServiceSlot4'), ('ServiceSlot5', 'ServiceSlot5'), ('ServiceSlot6', 'ServiceSlot6'), ('ServiceSlot7', 'ServiceSlot7'), ('SubSystemSlot0', 'SubSystemSlot0'), ('SubSystemSlot1', 'SubSystemSlot1'), ('SubSystemSlot2', 'SubSystemSlot2'), ('SubSystemSlot3', 'SubSystemSlot3')], default='Invalid', max_length=25)),
                ('quantity', models.IntegerField(default=1)),
                ('type_id', models.IntegerField()),
                ('fit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='fittings.Fitting')),
                ('type_fk', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='fittings.Type')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='fitting',
            name='ship_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='fittings.Type'),
        ),
        migrations.CreateModel(
            name='DogmaEffect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('effect_id', models.IntegerField()),
                ('is_default', models.BooleanField()),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='dogma_effects', to='fittings.Type')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='DogmaAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute_id', models.IntegerField()),
                ('value', models.FloatField()),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='dogma_attributes', to='fittings.Type')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Doctrine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('icon_url', models.URLField(null=True)),
                ('description', models.CharField(max_length=1000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(null=True)),
                ('fittings', models.ManyToManyField(related_name='doctrines', to='fittings.Fitting')),
            ],
            options={
                'permissions': (('manage', 'Can manage doctrines and fits.'),),
                'default_permissions': (),
            },
        ),
        migrations.AlterUniqueTogether(
            name='fitting',
            unique_together={('ship_type_type_id', 'name')},
        ),
    ]

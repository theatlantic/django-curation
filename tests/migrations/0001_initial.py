# Generated by Django 2.0.13 on 2020-09-04 00:41

import curation.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CuratedPostGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(help_text='Used for database slug', max_length=75, unique=True)),
            ],
            options={
                'verbose_name': 'Curated Content',
                'verbose_name_plural': 'Curated Content',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CuratedPostItem',
            fields=[
                ('primary_id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('position', models.PositiveSmallIntegerField(verbose_name='Position')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.CuratedPostGroup')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='Handler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', curation.fields.ContentTypeSourceField(blank=True, choices=[({'class': 'curated-content-type-option', 'value': '9'}, 'Post'), ({'class': 'curated-content-type-option', 'value': '10'}, 'Model A'), ({'class': 'curated-content-type-option', 'value': '11'}, 'Model B')], null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='ModelA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('a_field', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ModelB',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('b_field', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='curatedpostitem',
            name='post',
            field=curation.fields.CuratedForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.Post'),
        ),
    ]
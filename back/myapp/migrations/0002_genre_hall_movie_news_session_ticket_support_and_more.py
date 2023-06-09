# Generated by Django 4.1.7 on 2023-06-02 10:27

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import myapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Hall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Hall name')),
                ('rows', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Number of rows')),
                ('seats', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Number of seats')),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description')),
                ('duration', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Duration(minutes)')),
                ('age_limit', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Age Limit')),
                ('genres', models.ManyToManyField(to='myapp.genre')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('photo', models.ImageField(upload_to='images/news', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'jfif'])], verbose_name='Photo')),
            ],
            options={
                'verbose_name': 'New',
                'verbose_name_plural': 'News',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('price', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('hall', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='myapp.hall')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='myapp.movie')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('row', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Row')),
                ('seat', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Seat')),
                ('status', models.IntegerField(default=1, verbose_name='Status')),
                ('phone', models.CharField(max_length=19, validators=[myapp.models.validate_uzb_phone], verbose_name='Phone')),
                ('editor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='editor', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='owner', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.session')),
            ],
            options={
                'verbose_name': 'Ticket',
                'verbose_name_plural': 'Tickets',
                'ordering': ('session',),
            },
        ),
        migrations.CreateModel(
            name='Support',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('file', models.FileField(blank=True, null=True, upload_to='files/support', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'jfif', 'docx', 'doc', 'pdf'])], verbose_name='File')),
                ('solved', models.BooleanField(default=False, verbose_name='Solved')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('solved', '-created_at'),
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('publish', models.BooleanField(default=True, verbose_name='Publish')),
                ('rating', models.FloatField(validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(5.0)])),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]

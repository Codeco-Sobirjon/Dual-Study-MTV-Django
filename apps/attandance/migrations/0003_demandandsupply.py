# Generated by Django 5.1.2 on 2024-11-06 09:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attandance', '0002_alter_customuser_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='DemandandSupply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Taklif va talablar')),
                ('file', models.FileField(blank=True, null=True, upload_to='', verbose_name='Yuboliyotgan Fiyllar')),
                ('created_at', models.DateField(auto_now_add=True, null=True, verbose_name='Yaratilgan sana')),
                ('user_uploader', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_uploader', to=settings.AUTH_USER_MODEL, verbose_name='Yuboruvchi')),
            ],
            options={
                'verbose_name': '6 Talab va Takliflar',
                'verbose_name_plural': '6 Talab va Takliflar',
                'ordering': ['-id'],
            },
        ),
    ]

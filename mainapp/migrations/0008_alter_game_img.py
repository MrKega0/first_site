# Generated by Django 5.1.7 on 2025-07-11 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0007_alter_game_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='img',
            field=models.ImageField(default='game_img/default/default.png', upload_to='game_img/'),
        ),
    ]

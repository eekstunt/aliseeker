# Generated by Django 2.1 on 2018-10-28 16:16

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import tickets.models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0009_auto_20181028_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketdialogue',
            name='form_image',
            field=tickets.models.Image(blank=True, null=True, upload_to=tickets.models.Image.get_path, validators=[tickets.models.Image.validate_image], verbose_name='Изображение снизу (до 1 МБ)'),
        ),
        migrations.AlterField(
            model_name='ticketdialogue',
            name='last_message_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 10, 28, 16, 16, 32, 391154, tzinfo=utc), verbose_name='Время последнего сообщения (часовой пояс UTC)'),
        ),
    ]

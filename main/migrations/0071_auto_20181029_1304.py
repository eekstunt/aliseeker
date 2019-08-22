# Generated by Django 2.1 on 2018-10-29 13:04

from django.db import migrations
import main.models.models
import main.models.preferences


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0070_auto_20181029_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='texts',
            name='notification_delete_button_label_en',
            field=main.models.preferences.BotButtonLabel(default='-', max_length=50, verbose_name='Кнопка удаления оповещения, EN'),
        ),
        migrations.AddField(
            model_name='texts',
            name='notification_delete_button_label_ru',
            field=main.models.preferences.BotButtonLabel(default='-', max_length=50, verbose_name='Кнопка удаления оповещения, RU'),
        ),
        migrations.AddField(
            model_name='texts',
            name='notifications_empty_list_message_en',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Сообщение об отсутствии оповещений, EN'),
        ),
        migrations.AddField(
            model_name='texts',
            name='notifications_empty_list_message_ru',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Сообщение об отсутствии оповещений, RU'),
        ),
        migrations.AddField(
            model_name='texts',
            name='notifications_list_message_en',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Сообщение списка оповещений, EN'),
        ),
        migrations.AddField(
            model_name='texts',
            name='notifications_list_message_ru',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Сообщение списка оповещений, RU'),
        ),
        migrations.AlterField(
            model_name='media',
            name='welcome_gif_en',
            field=main.models.preferences.GIF(blank=True, null=True, upload_to=main.models.preferences.MediaFile.get_path, validators=[main.models.preferences.MediaFile.validate_media], verbose_name='Приветственная GIF-ка, EN'),
        ),
        migrations.AlterField(
            model_name='media',
            name='welcome_gif_ru',
            field=main.models.preferences.GIF(blank=True, null=True, upload_to=main.models.preferences.MediaFile.get_path, validators=[main.models.preferences.MediaFile.validate_media], verbose_name='Приветственная GIF-ка, RU'),
        ),
        migrations.AlterField(
            model_name='media',
            name='welcome_video_en',
            field=main.models.preferences.Video(blank=True, null=True, upload_to=main.models.preferences.MediaFile.get_path, validators=[main.models.preferences.MediaFile.validate_media], verbose_name='Приветственное MP4 видео, EN'),
        ),
        migrations.AlterField(
            model_name='media',
            name='welcome_video_ru',
            field=main.models.preferences.Video(blank=True, null=True, upload_to=main.models.preferences.MediaFile.get_path, validators=[main.models.preferences.MediaFile.validate_media], verbose_name='Приветственное MP4 видео, RU'),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=main.models.models.Image(blank=True, null=True, upload_to=main.models.models.Image.get_path, validators=[main.models.models.Image.validate_image], verbose_name='Изображение снизу (до 1МБ)'),
        ),
    ]

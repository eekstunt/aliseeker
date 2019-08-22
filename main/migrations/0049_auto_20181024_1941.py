# Generated by Django 2.1 on 2018-10-24 19:41

from django.db import migrations
import main.models.models
import main.models.preferences


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_auto_20181024_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='texts',
            name='referral_program_balance_message_en',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Баланс реферальной программы, EN'),
        ),
        migrations.AddField(
            model_name='texts',
            name='referral_program_balance_message_ru',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Баланс реферальной программы, RU'),
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

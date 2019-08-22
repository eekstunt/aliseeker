# Generated by Django 2.1 on 2018-10-19 16:50

from django.db import migrations
import main.models.preferences


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20181019_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='feedback_button_label_en',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Кнопка обратной связи, EN'),
        ),
        migrations.AddField(
            model_name='settings',
            name='feedback_button_label_ru',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Кнопка обратной связи, RU'),
        ),
        migrations.AddField(
            model_name='settings',
            name='referral_program_button_label_en',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Кнопка реферальной программы, EN'),
        ),
        migrations.AddField(
            model_name='settings',
            name='referral_program_button_label_ru',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Кнопка реферальной программы, RU'),
        ),
        migrations.AddField(
            model_name='settings',
            name='seeker_button_label_en',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Кнопка поиска товара, EN'),
        ),
        migrations.AddField(
            model_name='settings',
            name='seeker_button_label_ru',
            field=main.models.preferences.BotMessage(default='-', max_length=4000, verbose_name='Кнопка поиска товара, RU'),
        ),
    ]

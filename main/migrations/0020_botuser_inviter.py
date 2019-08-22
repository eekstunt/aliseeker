# Generated by Django 2.1 on 2018-10-20 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_botuser_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='inviter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referrals', to='main.BotUser', verbose_name='Пригласитель'),
        ),
    ]

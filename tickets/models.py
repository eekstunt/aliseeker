import random
from string import ascii_lowercase
from datetime import datetime, timezone

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from tickets.bot import send_message_to_user

RANDOM_FILENAME_LENGTH = 8
MAX_IMAGE_SIZE_MB = 1


class Image(models.ImageField):
    max_size_mb = MAX_IMAGE_SIZE_MB

    def __init__(self, *args, **kwargs):
        kwargs['upload_to'] = self.get_path
        kwargs['blank'] = True
        kwargs['null'] = True
        kwargs['validators'] = [self.validate_image]

        return super().__init__(*args, **kwargs)

    def get_path(self, instance, filename, length=RANDOM_FILENAME_LENGTH):
        file_format = filename.split('.')[-1]

        filename = ''
        for index in range(length):
            filename += random.choice(ascii_lowercase)

        return f'{filename}.{file_format}'

    def validate_image(self, image):
        image_size_bytes = image.file.size
        max_size_bytes = self.max_size_mb * 1024 * 1024

        if image_size_bytes > max_size_bytes:
            raise ValidationError(f'Максимальный размер файла - {self.max_size_mb}МБ')


class TicketMessage(models.Model):
    created = models.DateTimeField(
        auto_now_add=True
    )

    dialogue = models.ForeignKey(
        to='TicketDialogue',
        related_name='messages',
        on_delete=models.CASCADE
    )

    html = models.TextField()


class TicketDialogue(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=settings.TICKETS_TO_USER,
        related_name='dialogue',
        on_delete=models.CASCADE
    )

    unread = models.BooleanField(
        blank=True,
        null=True,
        default=True
    )

    last_message_sender = models.CharField(
        verbose_name='Отправитель последнего сообщения',
        max_length=7,
        choices=[
            ('user', 'Пользователь'),
            ('support', 'Поддержка')
        ],
        default='user'
    )
    last_message_time = models.DateTimeField(
        verbose_name='Время последнего сообщения (часовой пояс UTC)',
        default=datetime.now(timezone.utc)
    )

    status = models.CharField(
        verbose_name='Статус',
        max_length=7,
        choices=[
            ('open', 'Открыт'),
            ('closed', 'Закрыт')
        ],
        default='open'
    )
    marked = models.BooleanField(
        verbose_name='Избранный',
        default=False
    )
    ignored = models.BooleanField(
        verbose_name='Игнор',
        default=False
    )

    form_message = models.TextField(
        verbose_name='Текст (форматированный)',
        max_length=4000,
        blank=True,
        null=True
    )
    form_button_title = models.CharField(
        verbose_name='Текст кнопки',
        max_length=50,
        blank=True,
        null=True
    )
    form_button_link = models.URLField(
        verbose_name='Ссылка кнопки',
        blank=True,
        null=True
    )
    form_image = Image('Изображение снизу (до 1 МБ)')

    def save(self, *args, **kwargs):
        adding = self._state.adding

        super().save(*args, **kwargs)

        if not adding:
            if(
                self.form_message or
                self.form_image
            ):
                send_message_to_user(
                    self.user, self,
                    self.form_message,
                    self.form_button_title,
                    self.form_button_link,
                    self.form_image
                )
                self.last_message_sender = 'support'
                self.last_message_time = datetime.now(timezone.utc)

            self.form_message = None
            self.form_button_title = None
            self.form_button_link = None
            self.form_image = None

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Диалог'
        verbose_name_plural = 'Диалоги'

    def __str__(self):
        return str(self.user)

import random
from string import ascii_lowercase
from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

__all__ = [
    'Money', 'BotUser',
    'Input', 'Output',
    'Click', 'Link', 'ShortLink', 'Search', 'Notification',
    'Post'
]

MAX_IMAGE_SIZE_MB = 1
RANDOM_FILENAME_LENGTH = 8


class Money(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 10
        kwargs['decimal_places'] = 2
        kwargs['default'] = 0

        return super().__init__(*args, **kwargs)


class BotUser(models.Model):
    user_id = models.BigIntegerField('ID',
        unique=True
    )

    username = models.CharField('Логин',
        max_length=256,
        unique=True,
        null=True
    )
    first_name = models.CharField('Имя',
        max_length=256,
        null=True
    )
    last_name = models.CharField('Фамилия',
        max_length=256,
        null=True
    )

    language = models.CharField('Язык',
        max_length=2,
        choices=[
            ('en', 'Английский'),
            ('ru', 'Русский')
        ],
        null=True
    )
    created = models.DateTimeField('Первый запуск бота (часовой пояс UTC)',
        auto_now_add=True
    )

    total_amount_of_searches = models.IntegerField('Общее количество поисков',
        default=0
    )
    total_amount_of_notifications = models.IntegerField('Общее количество отслеживаний',
        default=0
    )

    def now_amount_of_notifications(self):
        return self.notifications.filter(status='active').count()
    now_amount_of_notifications.short_description = 'Отслеживается сейчас'

    inviter = models.ForeignKey(verbose_name='Пригласитель',
        to='self',
        related_name='referrals',
        on_delete=models.SET_NULL,
        null=True
    )

    def amount_of_first_level_referrals(self):
        return self.referrals.count()
    amount_of_first_level_referrals.short_description = 'Количество приглашенных 1 уровня'

    def amount_of_second_level_referrals(self):
        amount = 0
        for referral in self.referrals.all():
            amount += referral.amount_of_first_level_referrals()
        return amount
    amount_of_second_level_referrals.short_description = 'Количество приглашенных 2 уровня'

    balance = Money('Баланс, USD')
    total_earned = Money('Всего заработано, USD')
    total_withdrawn = Money('Всего выведено, USD')

    last_action = models.CharField(
        max_length=64,
        default='created'
    )
    last_actions_times = models.CharField(
        max_length=256,
        default='0.0'
    )

    def __str__(self):
        return str(self.user_id)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Input(models.Model):
    created = models.DateTimeField('Дата создания (часовой пояс UTC)',
        auto_now_add=True
    )

    user = models.ForeignKey(verbose_name='Пользователь',
        to=BotUser,
        related_name='inputs',
        on_delete=models.CASCADE
    )

    amount = Money(verbose_name='Сумма, USD')

    order_number = models.CharField('Номер заказа на AliExpress',
        max_length=64
    )

    def __str__(self):
        time_isoformat = self.created.isoformat(sep=' ', timespec='seconds')
        time_isoformat = time_isoformat[:time_isoformat.index('+')]

        return f'Начисление {time_isoformat}'

    class Meta:
        verbose_name = 'Начисление'
        verbose_name_plural = 'Начисления'


class Output(models.Model):
    created = models.DateTimeField('Дата создания (часовой пояс UTC)',
        auto_now_add=True
    )

    user = models.ForeignKey(verbose_name='Пользователь',
        to=BotUser,
        related_name='outputs',
        on_delete=models.CASCADE
    )

    payment_system = models.CharField(verbose_name='Платежная система',
        max_length=64,
        choices=[
            (system[0], system[0])
            for system in settings.PAYMENT_SYSTEMS
        ]
    )

    amount = Money(verbose_name='Сумма, USD')

    history_id = models.BigIntegerField(verbose_name='ID транзакции в Payeer')

    def __str__(self):
        time_isoformat = self.created.isoformat(sep=' ', timespec='seconds')
        time_isoformat = time_isoformat[:time_isoformat.index('+')]

        return f'Выплата {time_isoformat}'

    class Meta:
        verbose_name = 'Выплата'
        verbose_name_plural = 'Выплаты'


class Click(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    button = models.CharField(max_length=64)


class Link(models.Model):
    offer_id = models.BigIntegerField()
    offer_url = models.URLField()
    offer_name = models.CharField(max_length=settings.MAX_OFFER_NAME_LENGTH)

    offer_price = models.FloatField()
    currency = models.CharField(max_length=3)

    def __str__(self):
        return str(self.offer_url)


class ShortLink(models.Model):
    salt = models.CharField(max_length=settings.SHORT_LINK_SALT_LENGTH)
    origin = models.URLField()


class Search(models.Model):
    created = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    created = models.DateTimeField('Дата создания (часовой пояс UTC)',
        auto_now_add=True
    )

    link = models.ForeignKey(verbose_name='Ссылка на AliExpress',
        to=Link,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(verbose_name='Пользователь',
        to=BotUser,
        related_name='notifications',
        on_delete=models.CASCADE
    )

    status = models.CharField(verbose_name='Статус',
        max_length=7,
        choices=[
            ('active', 'Отслеживается'),
            ('expired', 'Истекло')
        ],
        default='active'
    )

    def short_link(self):
        return str(self.link)[:50 - 3] + '...'

    def __str__(self):
        return self.short_link()

    class Meta:
        verbose_name = 'Оповещение'
        verbose_name_plural = 'Оповещения'


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


class Post(models.Model):
    created = models.DateTimeField('Дата создания (часовой пояс UTC)',
        auto_now_add=True
    )
    status = models.CharField('Статус',
        max_length=9,
        choices=[
            ('created', 'Создан'),
            ('postponed', 'Отложен'),
            ('queue', 'В очереди'),
            ('process', 'Рассылается'),
            ('done', 'Разослан')
        ],
        default='created'
    )

    text = models.TextField('Форматированный текст',
        max_length=4000
    )
    image = Image('Изображение снизу (до 1МБ)')
    button_title = models.CharField('Текст кнопки',
        max_length=50,
        blank=True,
        null=True
    )
    button_link = models.URLField('Ссылка кнопки',
        blank=True,
        null=True
    )

    segmentation_language = models.CharField('Язык',
        max_length=3,
        choices=[
            ('ru', 'Русский'),
            ('en', 'Английский'),
            ('all', 'Русский + Английский')
        ],
        default='all'
    )
    segmentation_referrals = models.CharField('Реферальная активность',
        max_length=7,
        choices=[
            ('without', 'Без рефералов'),
            ('with', 'С рефералами'),
            ('all', 'Без рефералов + С рефералами')
        ],
        default='all'
    )

    postpone = models.BooleanField(
        verbose_name='Отложить',
        default=False
    )
    postpone_time = models.DateTimeField(
        verbose_name='Время публикации (часовой пояс UTC)',
        default=datetime(2020, 1, 1)
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.postpone:
                self.status = 'postponed'
            else:
                self.status = 'queue'

        elif self.status == 'postponed' and not self.postpone:
            self.status = 'queue'

        if not self.button_title or not self.button_link:
            self.button_title = None
            self.button_link = None

        super().save(*args, **kwargs)

    amount_of_receivers = models.IntegerField('Количество пользователей, получивших пост',
        blank=True,
        null=True
    )

    def __str__(self):
        time_isoformat = self.created.isoformat(sep=' ', timespec='seconds')
        time_isoformat = time_isoformat[:time_isoformat.index('+')]

        return f'Пост {time_isoformat}'

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

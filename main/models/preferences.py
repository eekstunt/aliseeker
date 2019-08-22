import random
from string import ascii_lowercase

from django.db import models
from django.core.exceptions import ValidationError

from preferences.models import Preferences

__all__ = [
    'BotMessage', 'BotButtonLabel', 'Texts',
    'MediaFile', 'GIF', 'Video', 'Media',
    'Price', 'Percent', 'Numbers'
]

MAX_ANIMATION_SIZE_MB = 50
MAX_VIDEO_SIZE_MB = 50
RANDOM_FILENAME_LENGTH = 8


class BotMessage(models.TextField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 4000
        kwargs['default'] = '-'

        return super().__init__(*args, **kwargs)


class BotButtonLabel(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 50
        kwargs['default'] = '-'

        return super().__init__(*args, **kwargs)


class Texts(Preferences):
    language_choice_message = BotMessage('Сообщение выбора языка')
    language_choice_button_en_label = BotButtonLabel('Кнопка выбора EN языка')
    language_choice_button_ru_label = BotButtonLabel('Кнопка выбора RU языка')

    welcome_message_en = BotMessage('Приветственное сообщение, EN')
    welcome_message_ru = BotMessage('Приветственное сообщение, RU')
    seeker_button_label_en = BotButtonLabel('Кнопка поиска товара, EN')
    seeker_button_label_ru = BotButtonLabel('Кнопка поиска товара, RU')
    alert_list_button_label_en = BotButtonLabel('Кнопка оповещений, EN')
    alert_list_button_label_ru = BotButtonLabel('Кнопка оповещений, RU')
    feedback_button_label_en = BotButtonLabel('Кнопка обратной связи, EN')
    feedback_button_label_ru = BotButtonLabel('Кнопка обратной связи, RU')
    referral_program_button_label_en = BotButtonLabel('Кнопка реферальной программы, EN')
    referral_program_button_label_ru = BotButtonLabel('Кнопка реферальной программы, RU')

    seeker_link_message_en = BotMessage('Просьба прислать ссылку, EN')
    seeker_link_message_ru = BotMessage('Просьба прислать ссылку, RU')
    seeker_link_waiting_message_en = BotMessage('Сообщение об ожидании, EN')
    seeker_link_waiting_message_ru = BotMessage('Сообщение об ожидании, RU')
    seeker_link_wrong_message_en = BotMessage('Сообщение о неверной ссылке, EN')
    seeker_link_wrong_message_ru = BotMessage('Сообщение о неверной ссылке, RU')
    seeker_found_orders_message_en = BotMessage('Сообщение о найденных товарах, EN')
    seeker_found_orders_message_ru = BotMessage('Сообщение о найденных товарах, RU')
    seeker_notification_proposal_message_en = BotMessage('Предложение об отслеживании, EN')
    seeker_notification_proposal_message_ru = BotMessage('Предложение об отслеживании, RU')
    seeker_notification_proposal_button_label_en = BotButtonLabel('Кнопка предложения об отслеживании, EN')
    seeker_notification_proposal_button_label_ru = BotButtonLabel('Кнопка предложения об отслеживании, RU')
    seeker_no_similar_offers_message_en = BotMessage('Сообщение о том, что товаров не найдено, EN')
    seeker_no_similar_offers_message_ru = BotMessage('Сообщение о том, что товаров не найдено, RU')
    seeker_notification_done_message_en = BotMessage('Сообщение об отслеживании, EN')
    seeker_notification_done_message_ru = BotMessage('Сообщение об отслеживании, RU')
    seeker_notification_already_done_message_en = BotMessage('Сообщение о том, что товар уже отслеживается, EN')
    seeker_notification_already_done_message_ru = BotMessage('Сообщение о том, что товар уже отслеживается, RU')

    notifications_list_message_en = BotMessage('Сообщение списка отслеживания, EN')
    notifications_list_message_ru = BotMessage('Сообщение списка отслеживания, RU')
    notifications_empty_list_message_en = BotMessage('Сообщение о пустом списке отслеживания, EN')
    notifications_empty_list_message_ru = BotMessage('Сообщение о пустом списке отслеживания, RU')
    notifications_add_offer_message_en = BotButtonLabel('Кнопка добавления товара, EN')
    notifications_add_offer_message_ru = BotButtonLabel('Кнопка добавления товара, RU')
    notification_delete_button_label_en = BotButtonLabel('Кнопка удаления товара, EN')
    notification_delete_button_label_ru = BotButtonLabel('Кнопка удаления товара, RU')

    alert_changed_message_en = BotMessage('Сообщение об изменении цены, EN')
    alert_changed_message_ru = BotMessage('Сообщение об изменении цены, RU')
    alert_expired_message_en = BotMessage('Сообщение об истечении срока мониторинга, EN')
    alert_expired_message_ru = BotMessage('Сообщение об истечении срока мониторинга, RU')
    alert_proposal_message_en = BotMessage('Предложение о продолжении отслеживания, EN')
    alert_proposal_message_ru = BotMessage('Предложение о продолжении отслеживания, RU')
    alert_proposal_button_label_en = BotButtonLabel('Кнопка продолжения отслеживания, EN')
    alert_proposal_button_label_ru = BotButtonLabel('Кнопка продолжения отслеживания, RU')

    feedback_message_en = BotMessage('Сообщение обратной связи, EN')
    feedback_message_ru = BotMessage('Сообщение обратной связи, RU')
    feedback_accepted_message_en = BotMessage('Сообщение о принятом сообщении, EN')
    feedback_accepted_message_ru = BotMessage('Сообщение о принятом сообщении, RU')

    referral_program_message_en = BotMessage('Сообщение реферальной программы, EN')
    referral_program_message_ru = BotMessage('Сообщение реферальной программы, RU')
    referral_program_conditions_button_label_en = BotButtonLabel('Кнопка условий, EN')
    referral_program_conditions_button_label_ru = BotButtonLabel('Кнопка условий, RU')
    referral_program_balance_button_label_en = BotButtonLabel('Кнопка баланса, EN')
    referral_program_balance_button_label_ru = BotButtonLabel('Кнопка баланса, RU')
    referral_program_withdraw_button_label_en = BotButtonLabel('Кнопка вывода денег, EN')
    referral_program_withdraw_button_label_ru = BotButtonLabel('Кнопка вывода денег, RU')
    referral_program_rating_button_label_en = BotButtonLabel('Кнопка рейтинга, EN')
    referral_program_rating_button_label_ru = BotButtonLabel('Кнопка рейтинга, RU')
    referral_program_rating_week_button_label_en = BotButtonLabel('Кнопка рейтинга за неделю, EN')
    referral_program_rating_week_button_label_ru = BotButtonLabel('Кнопка рейтинга за неделю, RU')
    referral_program_rating_month_button_label_en = BotButtonLabel('Кнопка рейтинга за месяц, EN')
    referral_program_rating_month_button_label_ru = BotButtonLabel('Кнопка рейтинга за месяц, RU')
    referral_program_rating_all_time_button_label_en = BotButtonLabel('Кнопка рейтинга за все время, EN')
    referral_program_rating_all_time_button_label_ru = BotButtonLabel('Кнопка рейтинга за все время, RU')
    referral_program_invite_button_label_en = BotButtonLabel('Кнопка приглашения, EN')
    referral_program_invite_button_label_ru = BotButtonLabel('Кнопка приглашения, RU')
    referral_program_share_link_button_label_en = BotButtonLabel('Кнопка поделиться ссылкой, EN')
    referral_program_share_link_button_label_ru = BotButtonLabel('Кнопка поделиться ссылкой, RU')
    referral_program_get_referral_link_button_label_en = BotButtonLabel('Кнопка получения реферальной ссылки, EN')
    referral_program_get_referral_link_button_label_ru = BotButtonLabel('Кнопка получения реферальной ссылки, RU')
    referral_program_back_button_label_en = BotButtonLabel('Кнопка назад, EN')
    referral_program_back_button_label_ru = BotButtonLabel('Кнопка назад, RU')
    referral_program_conditions_button_label_en = BotButtonLabel('Кнопка условий реферальной программы, EN')
    referral_program_conditions_button_label_ru = BotButtonLabel('Кнопка условий реферальной программы, RU')
    referral_program_conditions_message_en = BotMessage('Условия реферальной программы, EN')
    referral_program_conditions_message_ru = BotMessage('Условия реферальной программы, RU')
    referral_program_balance_message_en = BotMessage('Баланс реферальной программы, EN')
    referral_program_balance_message_ru = BotMessage('Баланс реферальной программы, RU')
    referral_program_payment_system_message_en = BotMessage('Сообщение выбора платежной системы, EN')
    referral_program_payment_system_message_ru = BotMessage('Сообщение выбора платежной системы, RU')
    referral_program_account_number_message_en = BotMessage('Сообщение ввода номера кошелька, EN')
    referral_program_account_number_message_ru = BotMessage('Сообщение ввода номера кошелька, RU')
    referral_program_withdraw_waiting_message_en = BotMessage('Сообщение об ожидании вывода денег, EN')
    referral_program_withdraw_waiting_message_ru = BotMessage('Сообщение об ожидании вывода денег, RU')
    referral_program_withdraw_success_message_en = BotMessage('Сообщение об успешном выводе денег, EN')
    referral_program_withdraw_success_message_ru = BotMessage('Сообщение об успешном выводе денег, RU')
    referral_program_withdraw_fail_message_en = BotMessage('Сообщение о неуспешном выводе денег, EN')
    referral_program_withdraw_fail_message_ru = BotMessage('Сообщение о неуспешном выводе денег, RU')
    referral_program_min_withdrawal_amount_message_en = BotMessage('Сообщение о минимальной сумме для вывода, EN')
    referral_program_min_withdrawal_amount_message_ru = BotMessage('Сообщение о минимальной сумме для вывода, RU')
    referral_program_invitation_message_en = BotMessage('Приглашение, EN')
    referral_program_invitation_message_ru = BotMessage('Приглашение, RU')
    referral_program_invitation_button_label_en = BotButtonLabel('Кнопка приглашения, EN')
    referral_program_invitation_button_label_ru = BotButtonLabel('Кнопка приглашения, RU')

    unknown_message_message_en = BotMessage('Сообщение с инструкциями, EN')
    unknown_message_message_ru = BotMessage('Сообщение с инструкциями, RU')

    spam_protection_message_en = BotMessage('Сообщение о срабатывании защиты, EN')
    spam_protection_message_ru = BotMessage('Сообщение о срабатывании защиты, RU')

    def __str__(self):
        return 'Список текстов'

    class Meta:
        verbose_name = 'Список'
        verbose_name_plural = 'Тексты'


class MediaFile(models.FileField):
    file_format = 'media'
    max_size_mb = 0

    def __init__(self, *args, **kwargs):
        kwargs['upload_to'] = self.get_path
        kwargs['blank'] = True
        kwargs['null'] = True
        kwargs['validators'] = [self.validate_media]

        return super().__init__(*args, **kwargs)

    def get_path(self, instance, filename, length=RANDOM_FILENAME_LENGTH):
        filename = ''
        for index in range(length):
            filename += random.choice(ascii_lowercase)

        return f'{filename}.{self.file_format}'

    def validate_media(self, media):
        media_filename = media.file.name
        media_size_bytes = media.file.size
        max_size_bytes = self.max_size_mb * 1024 * 1024

        if media_size_bytes > max_size_bytes:
            raise ValidationError(f'Максимальный размер файла - {self.max_size_mb}МБ')

        if not media_filename.endswith(f'.{self.file_format}'):
            raise ValidationError(f'Поддерживается только .{self.file_format} формат')


class GIF(MediaFile):
    file_format = 'gif'
    max_size_mb = MAX_ANIMATION_SIZE_MB


class Video(MediaFile):
    file_format = 'mp4'
    max_size_mb = MAX_VIDEO_SIZE_MB


class Media(Preferences):
    welcome_gif_en = GIF('Приветственная GIF-ка, EN')
    welcome_gif_ru = GIF('Приветственная GIF-ка, RU')

    welcome_video_en = Video('Приветственное MP4 видео, EN')
    welcome_video_ru = Video('Приветственное MP4 видео, RU')

    def __str__(self):
        return 'Список медиа'

    class Meta:
        verbose_name = 'Список'
        verbose_name_plural = 'Медиа'


class Price(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 10
        kwargs['decimal_places'] = 2
        kwargs['default'] = 0

        return super().__init__(*args, **kwargs)


class Percent(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 5
        kwargs['decimal_places'] = 2
        kwargs['default'] = 0

        return super().__init__(*args, **kwargs)


class Numbers(Preferences):
    min_withdrawal_amount = Price('Минимальная сумма вывода, USD')

    referral_program_first_level_percent = Percent('Процент 1-го уровня реферальной программы, %')
    referral_program_second_level_percent = Percent('Процент 2-го уровня реферальной программы, %')

    min_price_delta_percent = Percent('Необходимая разница в цене для оповещения, %')
    tracking_days = models.IntegerField('Срок отслеживания товаров, дней',
        default=30
    )

    def __str__(self):
        return 'Список чисел'

    class Meta:
        verbose_name = 'Список'
        verbose_name_plural = 'Числа'

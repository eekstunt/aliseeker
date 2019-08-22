from decimal import Decimal
from datetime import datetime, timezone, timedelta

from django.db import models

from preferences.models import Preferences

from main.models import BotUser, Input, Output, Click, Search, Notification

__all__ = ['Stats']


class Stats(Preferences):
    def total_users(self):
        return BotUser.objects.count()
    total_users.short_description = 'Общее число'
    def total_users_en(self):
        return BotUser.objects.filter(language='en').count()
    total_users_en.short_description = 'Число англоязычных'
    def total_users_ru(self):
        return BotUser.objects.filter(language='ru').count()
    total_users_ru.short_description = 'Число русскоязычных'

    def searches_day(self):
        return self._searches(1)
    searches_day.short_description = 'Число поисков за 24 часа'
    def searches_month(self):
        return self._searches(30)
    searches_month.short_description = 'Число поисков за месяц'
    def searches_all_time(self):
        return self._searches(365 * 10)
    searches_all_time.short_description = 'Число поисков за все время'
    def _searches(self, delta_days):
        delta = timedelta(delta_days)
        from_time = datetime.now(timezone.utc) - delta
        return Search.objects.filter(created__gte=from_time).count()

    def total_monitoring_products(self):
        return Notification.objects.count()
    total_monitoring_products.short_description = 'Общее число товаров'

    def total_referrals(self):
        return BotUser.objects.exclude(inviter=None).count()
    total_referrals.short_description = 'Общее число приглашенных пользователей'
    def total_day_input(self):
        return self._total_input(1)
    total_day_input.short_description = 'Начислено за 24 часа, USD'
    def total_month_input(self):
        return self._total_input(30)
    total_month_input.short_description = 'Начислено за месяц, USD'
    def total_all_time_input(self):
        return self._total_input(365 * 10)
    total_all_time_input.short_description = 'Начислено за все время, USD'
    def total_day_output(self):
        return self._total_output(1)
    total_day_output.short_description = 'Выведено за 24 часа, USD'
    def total_month_output(self):
        return self._total_output(30)
    total_month_output.short_description = 'Выведено за месяц, USD'
    def total_all_time_output(self):
        return self._total_output(365 * 10)
    total_all_time_output.short_description = 'Выведено за все время, USD'
    def _total_input(self, delta_days):
        delta = timedelta(delta_days)
        from_time = datetime.now(timezone.utc) - delta
        total_input = Input.objects.filter(created__gte=from_time).aggregate(models.Sum('amount'))['amount__sum']
        total_input = Decimal(total_input or 0)
        return (f'{total_input:.2f}').replace('.', ',')
    def _total_output(self, delta_days):
        delta = timedelta(delta_days)
        from_time = datetime.now(timezone.utc) - delta
        total_output = Output.objects.filter(created__gte=from_time).aggregate(models.Sum('amount'))['amount__sum']
        total_output = Decimal(total_output or 0)
        return (f'{total_output:.2f}').replace('.', ',')

    def seeker_clicks_day(self):
        return self._clicks('seeker', 1)
    def seeker_clicks_month(self):
        return self._clicks('seeker', 30)
    def seeker_clicks_all_time(self):
        return self._clicks('seeker', 365 * 10)
    seeker_clicks_day.short_description = \
    seeker_clicks_month.short_description = \
    seeker_clicks_all_time.short_description = 'Поиск товара'
    def feedback_clicks_day(self):
        return self._clicks('feedback', 1)
    def feedback_clicks_month(self):
        return self._clicks('feedback', 30)
    def feedback_clicks_all_time(self):
        return self._clicks('feedback', 365 * 10)
    feedback_clicks_day.short_description = \
    feedback_clicks_month.short_description = \
    feedback_clicks_all_time.short_description = 'Обратная связь'
    def referral_program_clicks_day(self):
        return self._clicks('referral_program', 1)
    def referral_program_clicks_month(self):
        return self._clicks('referral_program', 30)
    def referral_program_clicks_all_time(self):
        return self._clicks('referral_program', 365 * 10)
    referral_program_clicks_day.short_description = \
    referral_program_clicks_month.short_description = \
    referral_program_clicks_all_time.short_description = 'Реферальная программа'
    def balance_clicks_day(self):
        return self._clicks('balance', 1)
    def balance_clicks_month(self):
        return self._clicks('balance', 30)
    def balance_clicks_all_time(self):
        return self._clicks('balance', 365 * 10)
    balance_clicks_day.short_description = \
    balance_clicks_month.short_description = \
    balance_clicks_all_time.short_description = 'Баланс'
    def rating_clicks_day(self):
        return self._clicks('rating', 1)
    def rating_clicks_month(self):
        return self._clicks('rating', 30)
    def rating_clicks_all_time(self):
        return self._clicks('rating', 365 * 10)
    rating_clicks_day.short_description = \
    rating_clicks_month.short_description = \
    rating_clicks_all_time.short_description = 'Рейтинг'
    def invite_friend_clicks_day(self):
        return self._clicks('invite_friend', 1)
    def invite_friend_clicks_month(self):
        return self._clicks('invite_friend', 30)
    def invite_friend_clicks_all_time(self):
        return self._clicks('invite_friend', 365 * 10)
    invite_friend_clicks_day.short_description = \
    invite_friend_clicks_month.short_description = \
    invite_friend_clicks_all_time.short_description = 'Пригласить друга'
    def _clicks(self, button, delta_days):
        delta = timedelta(delta_days)
        from_time = datetime.now(timezone.utc) - delta
        return Click.objects.filter(button=button, created__gte=from_time).count()

    def __str__(self):
        return 'Просмотр статистики'

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'

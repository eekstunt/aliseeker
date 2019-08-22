from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.html import format_html
from django.conf import settings

from preferences.admin import PreferencesAdmin

from main import models
from tickets.models import TicketDialogue
from tickets.admin import TicketDialogueAdmin

admin.site.site_header = f'Администрирование {settings.BOT_NAME}'
admin.site.site_title = f'Администрирование {settings.BOT_NAME}'
admin.site.site_url = ''

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Site)


class BotUserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Данные Telegram аккаунта', {'fields': [
            'user_id',
            'username',
            'first_name',
            'last_name'
        ]}),
        ('Данные аккаунта в боте', {'fields': [
            'created',
            'language'
        ]}),
        ('Активность', {'fields': [
            'total_amount_of_searches',
            'total_amount_of_notifications',
            'now_amount_of_notifications'
        ]}),
        ('Реферальная программа', {'fields': [
            'link_to_inviter',
            'amount_of_first_level_referrals',
            'amount_of_second_level_referrals',
            'balance',
            'total_earned',
            'total_withdrawn'
        ]})
    ]
    readonly_fields = [
        'user_id', 'username', 'first_name', 'last_name',
        'created',
        'total_amount_of_searches', 'total_amount_of_notifications', 'now_amount_of_notifications',
        'link_to_inviter', 'amount_of_first_level_referrals', 'amount_of_second_level_referrals',
        'total_earned', 'total_withdrawn'
    ]

    list_display = [
        'user_id', 'username', 'first_name', 'last_name',
        'created', 'language',
        'amount_of_first_level_referrals',
        'total_earned', 'total_withdrawn'
    ]
    list_per_page = 100

    search_fields = ['user_id', 'username', 'first_name', 'last_name']
    list_filter = ['language']

    def link_to_inviter(self, obj):
        link = reverse(
            'admin:main_botuser_change', args=[obj.inviter.pk]
        )
        return format_html(
            f'<a href="{link}" style="font-weight: bold">{obj.inviter}</a>'
        )
    link_to_inviter.short_description = 'Пригласитель'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class InputAdmin(admin.ModelAdmin):
    list_display = ['created', 'link_to_user', 'amount', 'order_number']
    list_display_links = None

    search_fields = ['user__user_id', 'amount', 'order_number']

    list_per_page = 100

    def link_to_user(self, obj):
        link = reverse(
            'admin:main_botuser_change', args=[obj.user.pk]
        )
        return format_html(
            f'<a href="{link}" style="font-weight: bold">{obj.user}</a>'
        )
    link_to_user.short_description = 'Пользователь'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OutputAdmin(admin.ModelAdmin):
    list_display = ['created', 'link_to_user', 'payment_system', 'amount', 'history_id']
    list_display_links = None

    list_per_page = 100

    search_fields = ['user__user_id', 'payment_system', 'amount', 'history_id']
    list_filter = ['payment_system']

    def link_to_user(self, obj):
        link = reverse(
            'admin:main_botuser_change', args=[obj.user.pk]
        )
        return format_html(
            f'<a href="{link}" style="font-weight: bold">{obj.user}</a>'
        )
    link_to_user.short_description = 'Пользователь'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['created', 'link_to_link', 'link_to_user']
    list_display_links = None
    list_per_page = 100

    search_fields = ['link__offer_url', 'user__user_id']

    def link_to_user(self, obj):
        link = reverse(
            'admin:main_botuser_change', args=[obj.user.pk]
        )
        return format_html(
            f'<a href="{link}" style="font-weight: bold">{obj.user}</a>'
        )
    link_to_user.short_description = 'Пользователь'

    def link_to_link(self, obj):
        return format_html(
            f'<a href="{obj.link}" target="_blank">{obj.short_link()}</a>'
        )
    link_to_link.short_description = 'Ссылка на AliExpress'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class PostAdmin(admin.ModelAdmin):
    change_form_template = 'admin/post_change_form.html'

    list_display = [
        'created', 'status', 'amount_of_receivers',
        'text', 'html_buttons', 'image',
        'segmentation_language', 'segmentation_referrals'
    ]
    list_display_links = ['created']

    search_fields = ['text', 'button_title', 'button_link']
    list_filter = ['status']

    list_per_page = 10

    def html_buttons(self, obj):
        if obj.button_title and obj.button_link:
            return format_html(
                f'<a href="{obj.button_link}" target="_blank">{obj.button_title}</a>'
            )
        else:
            return None
    html_buttons.short_description = 'Кнопка'

    def get_fieldsets(self, request, obj=None):
        base_fieldsets = [
            ('Сообщение', {'fields': [
                'text',
                'image',
                ('button_title', 'button_link')
            ]}),
            ('Сегментация рассылки', {'fields': [
                'segmentation_language',
                'segmentation_referrals'
            ]}),
            ('Откладывание поста', {'fields': [
                'postpone',
                'postpone_time'
            ]})
        ]

        if not obj:
            return base_fieldsets

        else:
            return [
                ('Общая информация', {'fields': [
                    'created',
                    'status'
                ] + (['amount_of_receivers'] if obj.status == 'done' else [])}),
            ] + base_fieldsets

    def get_readonly_fields(self, request, obj=None):
        return ['created', 'status', 'amount_of_receivers']

    def has_change_permission(self, request, obj=None):
        return (obj is None) or (obj.status in ['postponed'])

    def has_delete_permission(self, request, obj=None):
        return (obj is None) or (obj.status in ['postponed', 'queue', 'done'])

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False

        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False

        return super().change_view(request, object_id, form_url, extra_context)

    class Media:
        js = ('admin/js/post.js',)


class CustomPreferencesAdmin(PreferencesAdmin):
    exclude = ['sites']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False

        return super().change_view(request, object_id, form_url, extra_context)


class StatsAdmin(CustomPreferencesAdmin):
    change_form_template = 'admin/stats_change_form.html'

    fieldsets = [
        ('Пользователи', {'fields': [
            'total_users',
            'total_users_en',
            'total_users_ru'
        ]}),
        ('Поиск товаров', {'fields': [
            'searches_day',
            'searches_month',
            'searches_all_time'
        ]}),
        ('Мониторинг', {'fields': [
            'total_monitoring_products'
        ]}),
        ('Реферальная система', {'fields': [
            'total_referrals',
            ('total_day_input', 'total_day_output'),
            ('total_month_input', 'total_month_output'),
            ('total_all_time_input', 'total_all_time_output')
        ]}),
        ('Нажатия на кнопки за 24 часа', {'fields': [
            ('seeker_clicks_day', 'feedback_clicks_day', 'referral_program_clicks_day'),
            ('balance_clicks_day', 'rating_clicks_day', 'invite_friend_clicks_day')
        ]}),
        ('Нажатия на кнопки за месяц', {'fields': [
            ('seeker_clicks_month', 'feedback_clicks_month', 'referral_program_clicks_month'),
            ('balance_clicks_month', 'rating_clicks_month', 'invite_friend_clicks_month')
        ]}),
        ('Нажатия на кнопки за все время', {'fields': [
            ('seeker_clicks_all_time', 'feedback_clicks_all_time', 'referral_program_clicks_all_time'),
            ('balance_clicks_all_time', 'rating_clicks_all_time', 'invite_friend_clicks_all_time')
        ]})
    ]

    def has_change_permission(self, request, obj=None):
        return False


class TextsAdmin(CustomPreferencesAdmin):
    change_form_template = 'admin/texts_change_form.html'

    main_menu_buttons = [
        ('seeker_button_label_en', 'seeker_button_label_ru'),
        ('alert_list_button_label_en', 'alert_list_button_label_ru'),
        ('feedback_button_label_en', 'feedback_button_label_ru'),
        ('referral_program_button_label_en', 'referral_program_button_label_ru')
    ] if settings.BOT_ALERT_LIST else [
        ('seeker_button_label_en', 'seeker_button_label_ru'),
        ('feedback_button_label_en', 'feedback_button_label_ru'),
        ('referral_program_button_label_en', 'referral_program_button_label_ru')
    ]

    notifications = [
        ('Отслеживание', {'fields': [
            ('notifications_list_message_en', 'notifications_list_message_ru'),
            ('notifications_empty_list_message_en', 'notifications_empty_list_message_ru'),
            ('notifications_add_offer_message_en', 'notifications_add_offer_message_ru'),
            ('notification_delete_button_label_en', 'notification_delete_button_label_ru'),
            ('alert_changed_message_en', 'alert_changed_message_ru'),
            ('alert_expired_message_en', 'alert_expired_message_ru'),
            ('alert_proposal_message_en', 'alert_proposal_message_ru'),
            ('alert_proposal_button_label_en', 'alert_proposal_button_label_ru')
        ]})
    ] if settings.BOT_ALERT_LIST else [
        ('Отслеживание', {'fields': [
            ('alert_changed_message_en', 'alert_changed_message_ru'),
            ('alert_expired_message_en', 'alert_expired_message_ru'),
            ('alert_proposal_message_en', 'alert_proposal_message_ru'),
            ('alert_proposal_button_label_en', 'alert_proposal_button_label_ru')
        ]})
    ]

    fieldsets = [
        ('Выбор языка', {'fields': [
            'language_choice_message',
            ('language_choice_button_en_label', 'language_choice_button_ru_label')
        ]}),
        ('', {'fields': []}),
        ('Приветствие', {'fields': [
            ('welcome_message_en', 'welcome_message_ru')
        ]}),
        ('Главное меню', {'fields': main_menu_buttons}),
        ('', {'fields': []}),
        ('Поиск товаров', {'fields': [
            ('seeker_link_message_en', 'seeker_link_message_ru'),
            ('seeker_link_waiting_message_en', 'seeker_link_waiting_message_ru'),
            ('seeker_link_wrong_message_en', 'seeker_link_wrong_message_ru'),
            ('seeker_found_orders_message_en', 'seeker_found_orders_message_ru'),
            ('seeker_notification_proposal_message_en', 'seeker_notification_proposal_message_ru'),
            ('seeker_notification_proposal_button_label_en', 'seeker_notification_proposal_button_label_ru'),
            ('seeker_no_similar_offers_message_en', 'seeker_no_similar_offers_message_ru'),
            ('seeker_notification_done_message_en', 'seeker_notification_done_message_ru'),
            ('seeker_notification_already_done_message_en', 'seeker_notification_already_done_message_ru')
        ]}),
        *notifications,
        ('', {'fields': []}),
        ('Обратная связь', {'fields': [
            ('feedback_message_en', 'feedback_message_ru'),
            ('feedback_accepted_message_en', 'feedback_accepted_message_ru')
        ]}),
        ('', {'fields': []}),
        ('Реферальная программа', {'fields': [
            ('referral_program_message_en', 'referral_program_message_ru'),
            ('referral_program_conditions_button_label_en', 'referral_program_conditions_button_label_ru'),
            ('referral_program_balance_button_label_en', 'referral_program_balance_button_label_ru'),
            ('referral_program_withdraw_button_label_en', 'referral_program_withdraw_button_label_ru'),
            ('referral_program_rating_button_label_en', 'referral_program_rating_button_label_ru'),
            ('referral_program_rating_week_button_label_en', 'referral_program_rating_week_button_label_ru'),
            ('referral_program_rating_month_button_label_en', 'referral_program_rating_month_button_label_ru'),
            ('referral_program_rating_all_time_button_label_en', 'referral_program_rating_all_time_button_label_ru'),
            ('referral_program_invite_button_label_en', 'referral_program_invite_button_label_ru'),
            ('referral_program_share_link_button_label_en', 'referral_program_share_link_button_label_ru'),
            ('referral_program_get_referral_link_button_label_en', 'referral_program_get_referral_link_button_label_ru'),
            ('referral_program_back_button_label_en', 'referral_program_back_button_label_ru'),
            ('referral_program_conditions_message_en', 'referral_program_conditions_message_ru'),
            ('referral_program_balance_message_en', 'referral_program_balance_message_ru'),
            ('referral_program_payment_system_message_en', 'referral_program_payment_system_message_ru'),
            ('referral_program_account_number_message_en', 'referral_program_account_number_message_ru'),
            ('referral_program_withdraw_waiting_message_en', 'referral_program_withdraw_waiting_message_ru'),
            ('referral_program_withdraw_success_message_en', 'referral_program_withdraw_success_message_ru'),
            ('referral_program_withdraw_fail_message_en', 'referral_program_withdraw_fail_message_ru'),
            ('referral_program_min_withdrawal_amount_message_en', 'referral_program_min_withdrawal_amount_message_ru'),
            ('referral_program_invitation_message_en', 'referral_program_invitation_message_ru'),
            ('referral_program_invitation_button_label_en', 'referral_program_invitation_button_label_ru')
        ]}),
        ('', {'fields': []}),
        ('Неизвестное сообщение', {'fields': [
            ('unknown_message_message_en', 'unknown_message_message_ru')
        ]}),
        ('Защита от множественных нажатий', {'fields': [
            ('spam_protection_message_en', 'spam_protection_message_ru')
        ]})
    ]


class MediaAdmin(CustomPreferencesAdmin):
    change_form_template = 'admin/media_change_form.html'

    fieldsets = [
        ('Приветствие', {'fields': [
            ('welcome_gif_en', 'welcome_gif_ru'),
            ('welcome_video_en', 'welcome_video_ru')
        ]})
    ]


class NumbersAdmin(CustomPreferencesAdmin):
    fieldsets = [
        ('Оповещения', {'fields': [
            'min_price_delta_percent',
            'tracking_days'
        ]}),
        ('Реферальная программа', {'fields': [
            'min_withdrawal_amount',
            'referral_program_first_level_percent',
            'referral_program_second_level_percent'
        ]})
    ]


admin.site.register(models.BotUser, BotUserAdmin)
admin.site.register(models.Stats, StatsAdmin)

admin.site.register(models.Input, InputAdmin)
admin.site.register(models.Output, OutputAdmin)

admin.site.register(models.Notification, NotificationAdmin)

admin.site.register(models.Post, PostAdmin)

admin.site.register(TicketDialogue, TicketDialogueAdmin)

admin.site.register(models.Texts, TextsAdmin)
admin.site.register(models.Media, MediaAdmin)
admin.site.register(models.Numbers, NumbersAdmin)

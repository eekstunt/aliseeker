import telebot

from django.conf import settings

from main import data


def generate_language_choice_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.language_choice_button_en_label,
        callback_data='set_language_en'
    ))
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.language_choice_button_ru_label,
        callback_data='set_language_ru'
    ))

    return keyboard


def generate_main_menu_keyboard(language):
    seeker_button = telebot.types.KeyboardButton(
        data.seeker_button_label[language]
    )
    alert_list_button = telebot.types.KeyboardButton(
        data.alert_list_button_label[language]
    )
    feedback_button = telebot.types.KeyboardButton(
        data.feedback_button_label[language]
    )
    referral_program_button = telebot.types.KeyboardButton(
        data.referral_program_button_label[language]
    )

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if settings.BOT_ALERT_LIST:
        keyboard.row(
            seeker_button,
            alert_list_button
        )
        keyboard.row(
            feedback_button,
            referral_program_button
        )
    else:
        keyboard.row(
            seeker_button,
            feedback_button
        )
        keyboard.row(
            referral_program_button
        )

    return keyboard


def generate_notification_proposal_keyboard(language, link_index):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.seeker_notification_proposal_button_label[language],
        callback_data=f'set_notification_{link_index}'
    ))

    return keyboard


def generate_notifications_keyboard(language):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.notifications_add_offer_message[language],
        callback_data=f'add_notification'
    ))

    return keyboard


def generate_notification_keyboard(language, link, pk):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            data.notification_delete_button_label[language],
            callback_data=f'delete_notification_{pk}'
        ),
        telebot.types.InlineKeyboardButton(
            'AliExpress',
            url=link
        )
    )

    return keyboard


def generate_referral_program_keyboard(language, user_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            data.referral_program_conditions_button_label[language],
            callback_data='referral_program_conditions'
        ),
        telebot.types.InlineKeyboardButton(
            data.referral_program_balance_button_label[language],
            callback_data='referral_program_balance'
        )
    )
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_rating_button_label[language],
        callback_data='referral_program_rating'
    ))
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_invite_button_label[language],
        switch_inline_query=str(user_id)
    ))
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_get_referral_link_button_label[language],
        callback_data='get_referral_link'
    ))
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_back_button_label[language],
        callback_data='exit_referral_program'
    ))

    return keyboard


def generate_referral_program_conditions_keyboard(language):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_back_button_label[language],
        callback_data='back_to_referral_program'
    ))

    return keyboard


def generate_referral_program_balance_keyboard(language):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_withdraw_button_label[language],
        callback_data='withdraw'
    ))
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_back_button_label[language],
        callback_data='back_to_referral_program'
    ))

    return keyboard


def generate_payment_systems_keyboard(language):
    payment_systems = settings.PAYMENT_SYSTEMS

    keyboard = telebot.types.InlineKeyboardMarkup()

    for row_index in range((len(payment_systems) - 1) // 2 + 1):
        current_systems = payment_systems[row_index * 2:(row_index + 1) * 2]
        current_buttons = []

        for system in current_systems:
            current_buttons.append(telebot.types.InlineKeyboardButton(
                system[0],
                callback_data=f'payment_system_{system[1]}'
            ))

        keyboard.row(*current_buttons)

    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_back_button_label[language],
        callback_data='referral_program_balance'
    ))

    return keyboard


def generate_referral_program_rating_keyboard(language):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_rating_week_button_label[language],
        callback_data='referral_program_rating_period_week'
    ))
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_rating_month_button_label[language],
        callback_data='referral_program_rating_period_month'
    ))
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_rating_all_time_button_label[language],
        callback_data='referral_program_rating_period_alltime'
    ))
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_back_button_label[language],
        callback_data='back_to_referral_program'
    ))

    return keyboard


def generate_invite_friend_keyboard(language, bot_username, user_id):
    invite_link = f'https://t.me/{bot_username}?start={user_id}'

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.referral_program_invitation_button_label[language],
        url=invite_link
    ))

    return keyboard

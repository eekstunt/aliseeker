import re
import pprint
from time import sleep
from random import randint
from datetime import datetime, timezone, timedelta
from collections import Counter

import telebot

from django.conf import settings

from preferences import preferences

from main import models
from main import markup
from main import utils
from main import decorators
from main import api
from main import data
from tickets.bot import handle_message_from_user

bot = telebot.TeleBot(
    settings.TELEGRAM_BOT_TOKEN,
    threaded=settings.TELEBOT_THREADED
)

bot_username = bot.get_me().username


@bot.message_handler(commands=['start'])
@decorators.show_errors(bot)
@decorators.track_action('start')
def handle_start_command(message):
    if not utils.get_user(message):
        utils.create_user(message)

    bot.send_message(message.chat.id,
        text=data.language_choice_message,
        parse_mode='html',
        reply_markup=markup.generate_language_choice_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_language'))
@decorators.show_errors(bot)
@decorators.track_action('set_language')
def handle_language_choice(call):
    language = call.data[-2:]

    if not settings.BOT_ENGLISH_AVAILABLE and language == 'en':
        bot.send_message(call.message.chat.id,
            'English is not available!\nАнглийский язык недоступен!\n\nНеобходимо добавить английские тексты в админке.'
        )
        bot.answer_callback_query(call.id)
        return None

    user = utils.get_user(call)
    user.language = language
    user.save()

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id,
        text=data.welcome_message[language],
        parse_mode='html',
        reply_markup=markup.generate_main_menu_keyboard(language)
    )

    bot.answer_callback_query(call.id)

    welcome_gif = data.welcome_gif[language]
    if welcome_gif:
        welcome_gif_url = f'https://{settings.ALLOWED_HOSTS[0]}/media/{welcome_gif}'
        bot.send_animation(call.message.chat.id,
            animation=welcome_gif_url
        )
    welcome_video = data.welcome_video[language]
    if welcome_video:
        welcome_video_url = f'https://{settings.ALLOWED_HOSTS[0]}/media/{welcome_video}'
        bot.send_video(call.message.chat.id,
            video=welcome_video_url
        )


@bot.message_handler(func=lambda message: message.text in [
    data.seeker_button_label['en'],
    data.seeker_button_label['ru'],
])
@decorators.show_errors(bot)
@decorators.spam_protection(bot)
@decorators.track_action('seeker_button')
@decorators.track_click('seeker')
def handle_seeker_button(message):
    user = utils.get_user(message)
    language = user.language

    bot.send_message(message.chat.id,
        text=data.seeker_link_message[language],
        parse_mode='html',
        reply_markup=markup.generate_main_menu_keyboard(language)
    )


def handle_seeker_link(message):
    user = utils.get_user(message)
    language = user.language
    user.last_action = 'seeker_link_sent'
    user.save()

    waiting_message = bot.send_message(message.chat.id,
        text=data.seeker_link_waiting_message[language],
        parse_mode='html'
    )
    sleep(settings.SEEKER_LINK_WAITING_DELAY)

    try:
        link = re.search(f'http\S+', message.text).group()
        goods_api = api.GoodsAPI()
        offer_id = goods_api.get_offer_id(link)
        message.text = str(offer_id)

    except BaseException:
        bot.delete_message(message.chat.id, waiting_message.message_id)
        handle_seeker_link_wrong(message)

    else:
        bot.delete_message(message.chat.id, waiting_message.message_id)
        handle_seeker_link_correct(message)


@decorators.track_action('seeker_link_wrong')
def handle_seeker_link_wrong(message):
    user = utils.get_user(message)
    language = user.language

    bot.send_message(message.chat.id,
        text=data.seeker_link_wrong_message[language],
        parse_mode='html',
        reply_markup=markup.generate_main_menu_keyboard(language)
    )


def send_offer(message, base_offer, similar_offer, language, currency):
    goods_api = api.GoodsAPI()

    base_price = goods_api.get_offer_price_from_info(base_offer)
    price = goods_api.get_offer_price_from_info(similar_offer)
    price_delta = base_price - price
    price_str = f'{price:.2f}'
    price_delta_str = f'{price_delta:.2f}'

    title = utils.shorten_text(
        similar_offer['name'],
        max_length=settings.MAX_OFFER_NAME_LENGTH,
        ending='...'
    )
    picture = similar_offer['picture']
    link = utils.shorten_link(similar_offer['url'] + f'?click_id={message.chat.id}')

    currency_str = 'рублей' if currency == 'RUR' else 'USD'

    if language == 'en':
        text = (
            f'<b>{title}</b>\n\n' +
            f'Price: {price_str} {currency_str}\n\n' +
            f'<b>Cheaper by {price_delta_str} {currency_str}</b>\n\n' +
            f'<a href="{link}">View on AliExpress</a>'
        )
    else:
        text = (
            f'<b>{title}</b>\n\n' +
            f'Цена: {price_str} {currency_str}\n\n' +
            f'<b>Дешевле на {price_delta_str} {currency_str}</b>\n\n' +
            f'<a href="{link}">Посмотреть на AliExpress</a>'
        )

    if picture:
        bot.send_photo(message.chat.id,
            photo=picture,
            caption=text,
            parse_mode='html'
        )
    else:
        bot.send_message(message.chat.id,
            text=text,
            parse_mode='html',
            disable_web_page_preview=True
        )


@decorators.track_action('seeker_link_correct')
def handle_seeker_link_correct(message):
    user = utils.get_user(message)
    language = user.language
    currency = 'USD' if language == 'en' else 'RUR'
    user.total_amount_of_searches += 1
    user.save()
    search = models.Search()
    search.save()

    goods_api = api.GoodsAPI()

    base_offer_id = int(message.text)
    base_offer_info = goods_api.get_offer_info(base_offer_id,
        language='en',
        currency=currency
    )
    base_offer_name = base_offer_info['name']
    base_offer_price = goods_api.get_offer_price_from_info(base_offer_info)
    base_offer_link = base_offer_info['url']

    db_base_link = models.Link(
        offer_id=base_offer_id,
        offer_url=base_offer_link,
        offer_name=utils.shorten_text(base_offer_name, settings.MAX_OFFER_NAME_LENGTH, '...'),
        offer_price=base_offer_price,
        currency=currency
    )
    db_base_link.save()
    db_base_link_index = db_base_link.pk

    if currency == 'USD':
        min_price_usd = base_offer_price / 2
    else:
        temp_base_offer_info = goods_api.get_offer_info(base_offer_id,
            language='en',
            currency='USD'
        )
        temp_base_offer_price = goods_api.get_offer_price_from_info(temp_base_offer_info)
        min_price_usd = temp_base_offer_price / 2

    accuracy = ((len(base_offer_name) - 1) // 10 + 1) * 10
    similar_offers_info = []
    while not similar_offers_info and accuracy >= 30:
        similar_offers_info = goods_api.get_similar_offers_info(base_offer_info,
            accuracy,
            min_price_usd,
            language='en',
            currency=currency
        )
        similar_offers_info = [
            offer_info for offer_info in similar_offers_info
            if goods_api.get_offer_price_from_info(offer_info) < base_offer_price
        ]

        if accuracy >= 140:
            accuracy -= 10
        elif accuracy >= 50:
            accuracy -= 10
        else:
            accuracy -= 5

    if similar_offers_info:
        bot.send_message(message.chat.id,
            text=data.seeker_found_orders_message[language],
            parse_mode='html',
            reply_markup=markup.generate_main_menu_keyboard(language)
        )
        similar_offers_info.sort(key=lambda offer: goods_api.get_offer_price_from_info(offer))
        for similar_offer_info in similar_offers_info:
            send_offer(message,
                base_offer_info,
                similar_offer_info,
                language=language,
                currency=currency
            )
        bot.send_message(message.chat.id,
            text=data.seeker_notification_proposal_message[language],
            parse_mode='html',
            reply_markup=markup.generate_notification_proposal_keyboard(language, db_base_link_index)
        )

    else:
        bot.send_message(message.chat.id,
            text=data.seeker_no_similar_offers_message[language],
            parse_mode='html',
            reply_markup=markup.generate_main_menu_keyboard(language)
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_notification'))
@decorators.show_errors(bot)
@decorators.track_action('set_notification')
def handle_set_notification(call):
    user = utils.get_user(call)
    language = user.language

    link_index = int(call.data.split('_')[-1])
    link = models.Link.objects.get(pk=link_index)

    if not models.Notification.objects.filter(user=user, link__offer_id=link.offer_id):
        user.total_amount_of_notifications += 1
        user.save()

        notification = models.Notification(
            link=link, user=user
        )
        notification.save()

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=data.seeker_notification_done_message[language],
            parse_mode='html'
        )

    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=data.seeker_notification_already_done_message[language],
            parse_mode='html'
        )

    bot.answer_callback_query(call.id)


if settings.BOT_ALERT_LIST:
    @bot.message_handler(func=lambda message: message.text in [
        data.alert_list_button_label['en'],
        data.alert_list_button_label['ru'],
    ])
    @decorators.show_errors(bot)
    @decorators.spam_protection(bot)
    @decorators.track_action('alert_list_button')
    def handle_alert_list_button(message):
        user = utils.get_user(message)
        language = user.language

        click_id = int(user.user_id)

        notifications = user.notifications.all()

        for notification in notifications:
            link = notification.link

            bot.send_message(message.chat.id,
                text=f'<b>{link.offer_name}</b>',
                parse_mode='html',
                reply_markup=markup.generate_notification_keyboard(language,
                    utils.shorten_link(link.offer_url + f'?click_id={click_id}'),
                    notification.pk
                ),
                disable_web_page_preview=True
            )

        if notifications:
            bot.send_message(message.chat.id,
                text=data.notifications_list_message[language],
                parse_mode='html',
                reply_markup=markup.generate_notifications_keyboard(language)
            )
        else:
            bot.send_message(message.chat.id,
                text=data.notifications_empty_list_message[language],
                parse_mode='html',
                reply_markup=markup.generate_notifications_keyboard(language)
            )


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_notification'))
@decorators.show_errors(bot)
@decorators.track_action('add_notification')
def handle_add_notification(call):
    user = utils.get_user(call)
    language = user.language

    bot.send_message(call.message.chat.id,
        text=data.seeker_link_message[language],
        parse_mode='html',
        reply_markup=markup.generate_main_menu_keyboard(language)
    )

    bot.answer_callback_query(call.id)


@decorators.track_action('notification_link_wrong')
def handle_notification_link_wrong(message):
    user = utils.get_user(message)
    language = user.language

    bot.send_message(message.chat.id,
        text=data.seeker_link_wrong_message[language],
        parse_mode='html',
        reply_markup=markup.generate_main_menu_keyboard(language)
    )


@decorators.track_action('notification_link_correct')
def handle_notification_link_correct(message):
    user = utils.get_user(message)
    language = user.language
    currency = 'USD' if language == 'en' else 'RUR'

    goods_api = api.GoodsAPI()

    offer_id = int(message.text)
    offer_info = goods_api.get_offer_info(offer_id,
        language='en',
        currency=currency
    )
    offer_name = offer_info['name']
    offer_price = goods_api.get_offer_price_from_info(offer_info)
    offer_link = offer_info['url']

    link = models.Link(
        offer_id=offer_id,
        offer_url=offer_link,
        offer_name=utils.shorten_text(offer_name, settings.MAX_OFFER_NAME_LENGTH, '...'),
        offer_price=offer_price,
        currency=currency
    )
    link.save()

    if not models.Notification.objects.filter(user=user, link__offer_id=offer_id):
        user.total_amount_of_notifications += 1
        user.save()

        notification = models.Notification(
            link=link, user=user
        )
        notification.save()

        bot.send_message(message.chat.id,
            text=data.seeker_notification_done_message[language],
            parse_mode='html',
            reply_markup=markup.generate_main_menu_keyboard(language)
        )

    else:
        bot.send_message(message.chat.id,
            text=data.seeker_notification_already_done_message[language],
            parse_mode='html',
            reply_markup=markup.generate_main_menu_keyboard(language)
        )


def handle_notification_link(message):
    user = utils.get_user(message)
    language = user.language
    user.last_action = 'notification_link_sent'
    user.save()

    waiting_message = bot.send_message(message.chat.id,
        text=data.seeker_link_waiting_message[language],
        parse_mode='html'
    )
    sleep(settings.SEEKER_LINK_WAITING_DELAY)

    try:
        link = re.search(f'http\S+', message.text).group()
        goods_api = api.GoodsAPI()
        offer_id = goods_api.get_offer_id(link)
        message.text = str(offer_id)

    except BaseException as exception:
        # bot.send_message(message.chat.id, f'{type(exception).__name__}:\n\n{exception}')
        bot.delete_message(message.chat.id, waiting_message.message_id)
        handle_notification_link_wrong(message)

    else:
        bot.delete_message(message.chat.id, waiting_message.message_id)
        handle_notification_link_correct(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_notification'))
@decorators.show_errors(bot)
def handle_delete_notification(call):
    notification_pk = int(call.data.split('_')[-1])
    notification = models.Notification.objects.get(pk=notification_pk)

    notification.delete()

    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: message.text in [
    data.referral_program_button_label['en'],
    data.referral_program_button_label['ru'],
])
@decorators.show_errors(bot)
@decorators.spam_protection(bot)
@decorators.track_action('referral_program_button')
@decorators.track_click('referral_program')
def handle_referral_program_button(message):
    user = utils.get_user(message)
    language = user.language

    amount_of_first_level_referrals = user.amount_of_first_level_referrals()
    amount_of_second_level_referrals = user.amount_of_second_level_referrals()

    bot.send_message(message.chat.id,
        text=data.referral_program_message[language].format(
            amount_of_first_level_referrals=amount_of_first_level_referrals,
            amount_of_second_level_referrals=amount_of_second_level_referrals
        ),
        parse_mode='html',
        reply_markup=markup.generate_referral_program_keyboard(language, message.chat.id)
    )


@bot.callback_query_handler(func=lambda call: call.data == 'referral_program_conditions')
@decorators.show_errors(bot)
def handle_referral_program_conditions_button(call):
    user = utils.get_user(call)
    language = user.language

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
        text=data.referral_program_conditions_message[language],
        parse_mode='html',
        reply_markup=markup.generate_referral_program_conditions_keyboard(language)
    )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'referral_program_balance')
@decorators.show_errors(bot)
@decorators.track_click('balance')
def handle_referral_program_balance_button(call):
    user = utils.get_user(call)
    language = user.language

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
        text=data.referral_program_balance_message[language].format(
            balance=f'{user.balance:.2f}'
        ),
        parse_mode='html',
        reply_markup=markup.generate_referral_program_balance_keyboard(language)
    )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'withdraw')
@decorators.show_errors(bot)
def handle_withdraw_button(call):
    user = utils.get_user(call)
    language = user.language
    user_balance = user.balance
    min_amount = preferences.Numbers.min_withdrawal_amount

    if user_balance < min_amount:
        bot.send_message(call.message.chat.id,
            text=data.referral_program_min_withdrawal_amount_message[language].format(
                min_amount=f'{min_amount:.2f}'
            ),
            parse_mode='html',
            reply_markup=markup.generate_main_menu_keyboard(language)
        )

    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=data.referral_program_payment_system_message[language].format(
                balance=f'{user_balance:.2f}'
            ),
            parse_mode='html',
            reply_markup=markup.generate_payment_systems_keyboard(language)
        )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('payment_system'))
@decorators.show_errors(bot)
def handle_payment_system(call):
    user = utils.get_user(call)
    language = user.language
    user_balance = user.balance

    payment_system_id = int(call.data.split('_')[-1])

    user.last_action = f'choose_payment_system_{payment_system_id}'
    user.save()

    for payment_system in settings.PAYMENT_SYSTEMS:
        if payment_system[1] == payment_system_id:
            break

    bot.send_message(call.message.chat.id,
        text=data.referral_program_account_number_message[language].format(
            balance=f'{user_balance:.2f}',
            payment_system=payment_system[0],
            account=payment_system[2]
        ),
        parse_mode='html',
        reply_markup=markup.generate_main_menu_keyboard(language)
    )

    bot.answer_callback_query(call.id)


@decorators.track_action('payment')
def handle_account_number(message):
    user = utils.get_user(message)
    language = user.language
    user_balance = user.balance
    min_amount = preferences.Numbers.min_withdrawal_amount

    if user_balance < min_amount:
        bot.send_message(message.chat.id,
            text=data.referral_program_min_withdrawal_amount_message[language].format(
                min_amount=f'{min_amount:.2f}'
            ),
            parse_mode='html',
            reply_markup=markup.generate_main_menu_keyboard(language)
        )
        return None

    user.balance = 0
    user.save()

    account_number = message.text.split()[0]
    payment_system_id = int(user.last_action.split('_')[-1])
    for payment_system in settings.PAYMENT_SYSTEMS:
        if payment_system[1] == payment_system_id:
            break

    waiting_message = bot.send_message(message.chat.id,
        text=data.referral_program_withdraw_waiting_message[language],
        parse_mode='html'
    )
    sleep(settings.PAYMENT_DELAY)

    try:
        payeer_api = api.PayeerAPI()
        payeer_output = payeer_api.output(
            ps=payment_system_id,
            sum_in=user_balance,
            cur_in='USD',
            cur_out='RUB' if 'RU' in payment_system[0] else 'USD',
            to=account_number
        )
        if payeer_output['errors']:
            raise ValueError(payeer_output)

    except BaseException as exception:
        # bot.send_message(message.chat.id, f'{type(exception).__name__}:\n\n{exception}')

        user = utils.get_user(message)
        user.balance = user_balance
        user.save()

        result_message = data.referral_program_withdraw_fail_message
    else:
        output = models.Output(
            user=user,
            payment_system=payment_system[0],
            amount=user_balance,
            history_id=int(payeer_output['historyId'])
        )
        output.save()

        user = utils.get_user(message)
        user.total_withdrawn += user_balance
        user.save()

        result_message = data.referral_program_withdraw_success_message

    bot.delete_message(message.chat.id, waiting_message.message_id)
    bot.send_message(message.chat.id,
        text=result_message[language].format(
            account=account_number,
            balance=f'{user_balance:.2f}',
            payment_system=payment_system[0]
        ),
        parse_mode='html',
        reply_markup=markup.generate_main_menu_keyboard(language)
    )


@bot.callback_query_handler(func=lambda call: call.data == 'referral_program_rating')
@decorators.show_errors(bot)
@decorators.track_click('rating')
def handle_referral_program_rating_button(call):
    user = utils.get_user(call)
    language = user.language

    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
        reply_markup=markup.generate_referral_program_rating_keyboard(language)
    )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('referral_program_rating_period'))
@decorators.show_errors(bot)
def handle_referral_program_rating_period_button(call):
    user = utils.get_user(call)
    language = user.language

    period = call.data.split('_')[-1]

    title = data.referrals_program_rating_period_titles[period][language]

    if period == 'week':
        delta_days = 7
    elif period == 'month':
        delta_days = 30
    else:
        delta_days = 365 * 10
    from_time = datetime.now(timezone.utc) - timedelta(delta_days)
    newcomers = models.BotUser.objects.filter(created__gte=from_time).exclude(inviter=None)

    if not newcomers:
        if language == 'en':
            top_list_str = top_list_plain_str = 'No data for the selected period!'
        else:
            top_list_str = top_list_plain_str = 'Нет данных за выбранный период!'

    else:
        inviters_ids = [user.inviter_id for user in newcomers]
        inviters_top_ids = Counter(inviters_ids).most_common(settings.REFERRAL_PROGRAM_RATING_SIZE)

        top_list_str = ''
        top_list_plain_str = ''
        for position, (pk, amount) in enumerate(inviters_top_ids, 1):
            inviter = models.BotUser.objects.get(pk=pk)
            inviter_title = inviter.first_name
            if inviter.last_name:
                inviter_title += ' ' + inviter.last_name
            top_list_str += f'{position}. {inviter_title}: <b>{amount}</b>\n'
            top_list_plain_str += f'{position}. {inviter_title}: {amount}\n'
        top_list_str = top_list_str[:-1]
        top_list_plain_str = top_list_plain_str[:-1]

    text = f'{title}:\n\n{top_list_str}'
    plain_text = f'{title}:\n\n{top_list_plain_str}'

    if call.message.text != plain_text:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=text,
            parse_mode='html',
            reply_markup=markup.generate_referral_program_rating_keyboard(language)
        )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_referral_program')
@decorators.show_errors(bot)
def handle_exit_referral_program_balance(call):
    user = utils.get_user(call)
    language = user.language

    amount_of_first_level_referrals = user.amount_of_first_level_referrals()
    amount_of_second_level_referrals = user.amount_of_second_level_referrals()

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
        text=data.referral_program_message[language].format(
            amount_of_first_level_referrals=amount_of_first_level_referrals,
            amount_of_second_level_referrals=amount_of_second_level_referrals
        ),
        parse_mode='html',
        reply_markup=markup.generate_referral_program_keyboard(language, call.message.chat.id)
    )

    bot.answer_callback_query(call.id)


@bot.inline_handler(func=lambda query: True)
@decorators.show_errors(bot)
@decorators.track_click('invite_friend')
def handle_referral_inline_invite(query):
    user = utils.get_user(query)
    user_id = user.user_id
    language = user.language

    result = telebot.types.InlineQueryResultArticle(id=randint(0, 2 ** 32 - 1),
        title=data.referral_program_share_link_button_label[language],
        input_message_content=telebot.types.InputTextMessageContent(
            message_text=data.referral_program_invitation_message[language],
            parse_mode='html'
        ),
        reply_markup=markup.generate_invite_friend_keyboard(language, bot_username, user_id)
    )

    bot.answer_inline_query(inline_query_id=query.id,
        is_personal=True,
        cache_time=0,
        next_offset='',

        results=[result]
    )


@bot.callback_query_handler(func=lambda call: call.data == 'get_referral_link')
@decorators.show_errors(bot)
@decorators.track_action('get_referral_link')
def handle_get_referral_link(call):
    user = utils.get_user(call)

    referral_link = f'https://t.me/{bot_username}?start={user.user_id}'
    bot.send_message(call.message.chat.id,
        text=referral_link
    )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'exit_referral_program')
@decorators.show_errors(bot)
def handle_exit_referral_program(call):
    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: message.text in [
    data.feedback_button_label['en'],
    data.feedback_button_label['ru'],
])
@decorators.show_errors(bot)
@decorators.spam_protection(bot)
@decorators.track_action('feedback_button')
@decorators.track_click('feedback')
def handle_feedback_button(message):
    user = utils.get_user(message)
    language = user.language

    bot.send_message(message.chat.id,
        text=data.feedback_message[language],
        parse_mode='html',
        reply_markup=markup.generate_main_menu_keyboard(language)
    )


@decorators.show_errors(bot)
@decorators.track_action('unknown')
def handle_unknown(message):
    user = utils.get_user(message)
    language = user.language

    bot.reply_to(message,
        text=data.unknown_message_message[language],
        parse_mode='html',
        reply_markup=markup.generate_main_menu_keyboard(language)
    )


@bot.message_handler(content_types=['text'])
@decorators.show_errors(bot)
def handle_text_message(message):
    user = utils.get_user(message)
    language = user.language
    last_action = user.last_action

    if last_action in ['seeker_button', 'seeker_link_wrong']:
        handle_seeker_link(message)

    elif last_action in ['add_notification', 'notification_link_wrong']:
        handle_notification_link(message)

    elif last_action == 'feedback_button':
        handle_message_from_user(message, user,
            data.feedback_accepted_message[language]
        )

    elif last_action.startswith('choose_payment_system'):
        handle_account_number(message)

    else:
        handle_unknown(message)


@bot.message_handler(content_types=['photo'])
@decorators.show_errors(bot)
def handle_photo_message(message):
    user = utils.get_user(message)
    language = user.language
    last_action = user.last_action

    if last_action == 'feedback_button':
        handle_message_from_user(message, user,
            data.feedback_accepted_message[language]
        )

    else:
        handle_unknown(message)

import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliseeker.settings")
django.setup()

from time import sleep
from datetime import datetime, timezone, timedelta

import telebot

from preferences import preferences

from main import utils
from main import models
from main import data
from main import markup
from main.bot import bot
from main.api import GoodsAPI

DELAY = 1


def send_expired_offer(offer, user_id, language):
    link = offer.link
    text = data.alert_expired_message[language].format(
        offer_name=link.offer_name,
        offer_link=utils.shorten_link(link.offer_url + f'?click_id={user_id}')
    )

    bot.send_message(user_id,
        text=text,
        parse_mode='html',
        reply_markup=markup.generate_main_menu_keyboard(language),
        disable_web_page_preview=True
    )

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.alert_proposal_button_label[language],
        callback_data=f'set_notification_{link.pk}'
    ))
    bot.send_message(user_id,
        text=data.alert_proposal_message[language],
        parse_mode='html',
        reply_markup=keyboard
    )


def send_priced_offer(offer, user_id, language):
    link = offer.link
    text = data.alert_changed_message[language].format(
        offer_name=link.offer_name,
        offer_link=utils.shorten_link(link.offer_url + f'?click_id={user_id}')
    )

    bot.send_message(user_id,
        text=text,
        parse_mode='html',
        reply_markup=markup.generate_main_menu_keyboard(language),
        disable_web_page_preview=True
    )

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(
        data.alert_proposal_button_label[language],
        callback_data=f'set_notification_{link.pk}'
    ))
    bot.send_message(user_id,
        text=data.alert_proposal_message[language],
        parse_mode='html',
        reply_markup=keyboard
    )


def process_offer(offer, min_delta_price, max_days):
    user = offer.user

    from_time_expired = datetime.now(timezone.utc) - timedelta(max_days)
    if offer.created <= from_time_expired:
        send_expired_offer(offer, user.user_id, user.language)
        offer.delete()
        return None

    link = offer.link

    offer_id = link.offer_id
    old_price = link.offer_price
    currency = link.currency

    goods_api = GoodsAPI()
    new_offer_info = goods_api.get_offer_info(offer_id, language='en', currency=currency)
    new_price = goods_api.get_offer_price_from_info(new_offer_info)

    if (1 - new_price / old_price) * 100 >= min_delta_price:
        send_priced_offer(offer, user.user_id, user.language)
        offer.delete()
        link = offer.link
        link.offer_price = new_price
        link.save()
        return None


def process_offers():
    offers = list(models.Notification.objects.all())

    min_delta_price = float(preferences.Numbers.min_price_delta_percent)
    max_days = float(preferences.Numbers.tracking_days)

    for offer in offers:
        print(f'process {offer}')
        try:
            process_offer(offer, min_delta_price, max_days)
        except BaseException as error:
            print(f'{type(error)}:\n{error}')


def main():
    while True:
        try:
            process_offers()
        except BaseException as error:
            print(f'{type(error)}:\n{error}')

        sleep(DELAY)


if __name__ == '__main__':
    main()

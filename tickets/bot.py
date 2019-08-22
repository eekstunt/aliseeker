import os
import random
from html import escape
from datetime import datetime, timezone
from string import ascii_lowercase
from importlib import import_module

import telebot
import requests

from django.conf import settings

from tickets import models

RANDOM_FILENAME_LENGTH = 8


def generate_random_filename(length=RANDOM_FILENAME_LENGTH):
    filename = ''
    for index in range(length):
        filename += random.choice(ascii_lowercase)

    return filename


def get_link_to_photo(bot, message):
    telegram_photo = message.photo[-1]
    telegram_file = bot.get_file(telegram_photo.file_id)

    photo_url = f'https://api.telegram.org/file/bot{settings.TICKETS_BOT_TOKEN}/{telegram_file.file_path}'

    photo_filename = generate_random_filename()
    photo_filename += '.' + telegram_file.file_path.split('.')[-1]

    photo_path = os.path.join(settings.MEDIA_ROOT, photo_filename)
    with open(photo_path, 'wb') as photo_file:
        response = requests.get(photo_url)
        photo_file.write(response.content)

    link_to_photo = f'https://{settings.ALLOWED_HOSTS[0]}/media/{photo_filename}'

    return link_to_photo


def handle_message_from_user(message, user, accepted_message):
    bot = import_module(settings.TICKETS_MODULE_WITH_TELEBOT).bot

    if not user.dialogue.count():
        dialogue = models.TicketDialogue(user=user)
        dialogue.save()
    else:
        dialogue = models.TicketDialogue.objects.get(user=user)

    message_html = '<div class="dialogue-message user-message">'
    message_time = datetime.now().isoformat(sep=' ', timespec='seconds')
    message_html += f'<div class="dialogue-message-time">{message_time}</div>'
    if message.text:
        message_text = escape(message.text)
        message_html += f'<div class="dialogue-message-text">{message_text}</div>'
    elif message.photo:
        if message.caption:
            message_caption = escape(message.caption)
            message_html += f'<div class="dialogue-message-text">{message_caption}</div>'
        link_to_photo = get_link_to_photo(bot, message)
        message_html += f'<a class="dialogue-image" href="{link_to_photo}"><img src="{link_to_photo}" /></a>'
    message_html += '</div>'

    ticket_message = models.TicketMessage(
        dialogue=dialogue,
        html=message_html
    )
    ticket_message.save()

    dialogue.last_message_sender = 'user'
    dialogue.last_message_time = datetime.now(timezone.utc)
    dialogue.unread = True
    dialogue.save()

    bot.reply_to(message,
        text=accepted_message,
        parse_mode='html'
    )


def send_message_to_user(user, dialogue, text, button_title, button_link, image):
    bot = import_module(settings.TICKETS_MODULE_WITH_TELEBOT).bot

    message_html = '<div class="dialogue-message support-message">'
    message_time = datetime.now().isoformat(sep=' ', timespec='seconds')
    message_html += f'<div class="dialogue-message-time">{message_time}</div>'

    if text:
        if button_title and button_link:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row(telebot.types.InlineKeyboardButton(
                text=button_title,
                url=button_link
            ))
        else:
            markup = None

        try:
            text = text.format(user_first_name=user.first_name)
        except BaseException:
            pass

        title = f'<b>{settings.TICKETS_SUPPORT_TITLE}:</b>\n\n'
        telegram_message = title + text
        if image:
            image_link = f'https://{settings.ALLOWED_HOSTS[0]}/media/{image}'
            telegram_message = f'<a href="{image_link}">&#8204;</a>' + telegram_message
        try:
            bot.send_message(user.user_id,
                text=telegram_message,
                parse_mode='html',
                reply_markup=markup
            )
        except BaseException:
            pass

        message_html += f'<div class="dialogue-message-text">{text}</div>'
        if image:
            message_html += f'<a class="dialogue-image" href="{image_link}"><img src="{image_link}" /></a>\n'
        if button_title and button_link:
            message_html += f'<a class="dialogue-button" href="{button_link}" target="_blank">- {button_title} -</a>\n'

    elif image:
        image_link = f'https://{settings.ALLOWED_HOSTS[0]}/media/{image}'
        try:
            bot.send_photo(user.user_id,
                photo=image_link,
                caption=f'<b>{settings.TICKETS_SUPPORT_TITLE}</b>',
                parse_mode='html'
            )
        except BaseException:
            pass

        message_html += f'<a class="dialogue-image" href="{image_link}"><img src="{image_link}" /></a>'

    message_html += '</div>'

    message = models.TicketMessage(
        dialogue=dialogue,
        html=message_html
    )
    message.save()

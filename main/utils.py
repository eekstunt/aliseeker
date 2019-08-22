import random
from string import ascii_lowercase

import telebot

from django.core import exceptions
from django.conf import settings

from main.models import BotUser, ShortLink


def get_message_from_data(data):
    if isinstance(data, telebot.types.CallbackQuery):
        message = data.message
    else:
        message = data

    return message


def create_user(message):
    blocks = message.text.split()
    if len(blocks) > 1:
        inviter_id = int(blocks[-1])
        inviter = BotUser.objects.get(user_id=inviter_id)
    else:
        inviter = None

    user = BotUser(
        user_id=message.chat.id,
        username=message.chat.username,
        first_name=message.chat.first_name,
        last_name=message.chat.last_name,

        inviter=inviter
    )
    user.save()

    return user


def get_user(data):
    if isinstance(data, telebot.types.InlineQuery):
        chat_id = data.from_user.id
    else:
        message = get_message_from_data(data)
        chat_id = message.chat.id

    try:
        user = BotUser.objects.get(user_id=chat_id)
    except exceptions.ObjectDoesNotExist:
        user = None

    return user


def shorten_text(text, max_length, ending=''):
    max_length -= len(ending)
    words = text.split()

    short_text = words[0]

    for word in words[1:]:
        if len(short_text) + len(word) + 1 > max_length:
            short_text += ending
            break
        else:
            short_text += ' ' + word

    return short_text


def shorten_link(long_link):
    salt = ''
    for char_index in range(settings.SHORT_LINK_SALT_LENGTH):
        salt += random.choice(ascii_lowercase)

    short_link_db = ShortLink(origin=long_link, salt=salt)
    short_link_db.save()

    short_link = f'https://{settings.ALLOWED_HOSTS[0]}/{salt}'

    return short_link


def _apihelper_send_animation(token, chat_id, animation):
    method_url = 'sendAnimation'

    payload = {
        'chat_id': chat_id,
        'animation': animation
    }

    return telebot.apihelper._make_request(token,
        method_url, params=payload, method='post'
    )


def _apihelper_send_video(token, chat_id, video):
    method_url = 'sendAnimation'

    payload = {
        'chat_id': chat_id,
        'video': video
    }

    return telebot.apihelper._make_request(token,
        method_url, params=payload, method='post'
    )


telebot.apihelper.send_animation = _apihelper_send_animation
telebot.apihelper.send_video = _apihelper_send_video


def _telebot_send_animation(self, chat_id, animation):
    return telebot.types.Message.de_json(telebot.apihelper.send_animation(
        self.token, chat_id, animation
    ))


def _telebot_send_video(self, chat_id, video):
    return telebot.types.Message.de_json(telebot.apihelper.send_animation(
        self.token, chat_id, video
    ))


telebot.TeleBot.send_animation = _telebot_send_animation
telebot.TeleBot.send_video = _telebot_send_video

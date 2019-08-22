import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliseeker.settings")
django.setup()

from time import sleep
from datetime import datetime, timezone

import telebot

from django.conf import settings

from main import models
from main.bot import bot

DELAY = 1


def process_statuses():
    now = datetime.now(timezone.utc)

    expired_posts = models.Post.objects.filter(
        status='postponed', postpone_time__lte=now
    )

    for post in expired_posts:
        print(f'queue {post.created}')
        try:
            post.status = 'queue'
            post.save()
        except BaseException as error:
            print(f'{type(error)}:\n{error}')


def send_post_to_user(post, user):
    text = post.text
    if post.image:
        image_url = f'https://{settings.ALLOWED_HOSTS[0]}/media/{post.image}'
        text = f'<a href="{image_url}">&#8204;</a>' + text

    if post.button_title and post.button_link:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(
            text=post.button_title,
            url=post.button_link
        ))
    else:
        keyboard = None

    bot.send_message(user.user_id,
        text=text,
        parse_mode='html',
        reply_markup=keyboard
    )


def process_post(post):
    print(f'post {post.created}')
    post.status = 'process'
    post.save()

    users = list(models.BotUser.objects.all())

    receivers = []

    for user in users:
        user_language = [user.language, 'all']
        if user.amount_of_first_level_referrals():
            user_referrals = ['with', 'all']
        else:
            user_referrals = ['without', 'all']

        post_language = post.segmentation_language
        post_referrals = post.segmentation_referrals

        if post_language in user_language and post_referrals in user_referrals:
            receivers.append(user)

    amount_of_receivers = 0

    for user in receivers:
        print(f'receiver {user.username}')
        try:
            send_post_to_user(post, user)
        except BaseException as error:
            print(f'{type(error)}:\n{error}')
        else:
            amount_of_receivers += 1
    print(f'total {amount_of_receivers}')

    post.status = 'done'
    post.amount_of_receivers = amount_of_receivers
    post.save()


def main():
    while True:
        try:
            process_statuses()
        except BaseException as error:
            print(f'{type(error)}:\n{error}')

        try:
            post = models.Post.objects.filter(status='queue').order_by('created').first()
            if post:
                process_post(post)
        except BaseException as error:
            print(f'{type(error)}:\n{error}')

        sleep(DELAY)


if __name__ == '__main__':
    main()

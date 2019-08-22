from decimal import Decimal

import telebot

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from preferences import preferences

from main.bot import bot
from main.models import ShortLink, BotUser, Input


@require_POST
@csrf_exempt
def handle_telegram_update(request):
    update_json_string = request.body.decode()
    update = telebot.types.Update.de_json(update_json_string)

    bot.process_new_updates([update])

    return HttpResponse()


def handle_short_link(request, salt):
    try:
        short_link = ShortLink.objects.get(salt=salt)
        origin = short_link.origin

        return redirect(origin)

    except BaseException:
        return HttpResponseNotFound()


def handle_epn_order(request, click_id, order_number, amount_cents):
    click_id = int(click_id)
    order_number = str(order_number)
    amount_cents = int(float(amount_cents))

    user = BotUser.objects.get(user_id=click_id)

    if user.inviter:
        first_inviter = user.inviter
    else:
        first_inviter = None
    if first_inviter and first_inviter.inviter:
        second_inviter = first_inviter.inviter
    else:
        second_inviter = None

    if first_inviter:
        amount = (Decimal(amount_cents) / 100) * (Decimal(preferences.Numbers.referral_program_first_level_percent) / 100)

        first_inviter.balance += amount
        first_inviter.total_earned += amount
        first_inviter.save()

        db_input = Input(
            user=first_inviter,
            amount=amount,
            order_number=order_number
        )
        db_input.save()

    if second_inviter:
        amount = (Decimal(amount_cents) / 100) * (Decimal(preferences.Numbers.referral_program_second_level_percent) / 100)

        second_inviter.balance += amount
        second_inviter.total_earned += amount
        second_inviter.save()

        db_input = Input(
            user=second_inviter,
            amount=amount,
            order_number=order_number
        )
        db_input.save()

    return HttpResponse()

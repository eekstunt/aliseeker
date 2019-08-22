from time import time

from django.conf import settings

from main import utils
from main import models
from main import data

SPAM_PROTECTION_AMOUNT = 5
SPAM_PROTECTION_DELTA = 6


def _send_error(bot, data_, exception):
    message = utils.get_message_from_data(data_)

    bot.send_message(message.chat.id,
        text=f'{type(exception).__name__}:\n\n{exception}'
    )


def show_errors(bot):
    def installer(function):
        nonlocal bot

        def wrapper(data_):
            nonlocal function

            try:
                result = function(data_)

            except BaseException as exception:
                if settings.BOT_SHOW_ERRORS:
                    _send_error(bot, data_, exception)
                return None

            else:
                return result

        return wrapper

    return installer


def _last_actions_times(user, max_amount_of_messages):
    now = time()

    last_actions_times = [
        float(action) for action in user.last_actions_times.split()
    ]
    last_actions_times.append(now)
    last_actions_times = last_actions_times[-max_amount_of_messages:]

    user.last_actions_times = ' '.join([
        str(action) for action in last_actions_times
    ])
    user.save()

    return last_actions_times


def spam_protection(bot,
    max_amount_of_messages=SPAM_PROTECTION_AMOUNT, min_delta=SPAM_PROTECTION_DELTA
):
    def installer(function):
        nonlocal bot
        nonlocal max_amount_of_messages, min_delta

        def wrapper(data_):
            nonlocal function

            message = utils.get_message_from_data(data_)

            user = utils.get_user(message)
            language = user.language

            last_actions_times = _last_actions_times(user, max_amount_of_messages)

            if len(last_actions_times) == max_amount_of_messages:
                delta = last_actions_times[-1] - last_actions_times[0]
            else:
                delta = float('inf')

            if delta < min_delta:
                bot.send_message(message.chat.id,
                    text=data.spam_protection_message[language],
                    parse_mode='html'
                )
                return None
            else:
                return function(data_)

        return wrapper

    return installer


def track_action(action):
    def installer(function):
        nonlocal action

        def wrapper(data_):
            nonlocal function

            result = function(data_)

            user = utils.get_user(data_)
            user.last_action = action
            user.save()

            return result

        return wrapper

    return installer


def track_click(button):
    def installer(function):
        nonlocal button

        def wrapper(data_):
            nonlocal function

            result = function(data_)

            click = models.Click(button=button)
            click.save()

            return result

        return wrapper

    return installer

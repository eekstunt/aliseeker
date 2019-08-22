from django import template

from tickets import models

register = template.Library()


@register.simple_tag
def unread_messages():
    amount = models.TicketDialogue.objects.filter(unread=True, ignored=False).count()

    if 11 <= amount <= 20:
        caption = 'непрочитанных диалогов'
    elif (amount % 10) == 1:
        caption = 'непрочитанный диалог'
    elif (amount % 10) <= 4:
        caption = 'непрочитанных диалога'
    else:
        caption = 'непрочитанных диалогов'

    if not amount:
        html = ''
    else:
        html = '<div style="display: inline-block; padding: 8px 5px; line-height: normal; color: white; background: #d76d5b;">'
        html += f'В поддержке <b>{amount}</b> {caption}!'
        html += '</div>'

    return html

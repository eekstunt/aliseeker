from django.contrib import admin
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.urls import reverse
from django.conf import settings


class TicketDialogueIgnoredFilter(admin.SimpleListFilter):
    title = 'Игнор'
    parameter_name = 'ignored'

    def lookups(self, request, model_admin):
        return (
            ('all', 'Все'),
            ('ignored', 'Да')
        )

    def queryset(self, request, queryset):
        ignored = request.GET.get('ignored')

        if ignored == 'all':
            return queryset.all()
        elif ignored == 'ignored':
            return queryset.filter(ignored=True)
        else:
            return queryset.filter(ignored=False)

    def choices(self, cl):
        yield {
            'selected': self.value() is None,
            'query_string': cl.get_query_string({}, [self.parameter_name]),
            'display': 'Нет'
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title
            }


class TicketDialogueAdmin(admin.ModelAdmin):
    change_form_template = 'admin/ticket_change_form.html'

    list_display = ['user', 'user_first_name', 'user_last_name', 'last_message_sender', 'read', 'last_message_time', 'status', 'marked', 'ignored']
    list_editable = ['status', 'marked', 'ignored']

    search_fields = ['user__user_id', 'user__username', 'user__first_name', 'user__last_name']
    list_filter = ['status', 'marked', TicketDialogueIgnoredFilter]

    ordering = ('-last_message_time',)
    list_per_page = 15

    def get_fieldsets(self, request, obj=None):
        if obj is not None and obj.unread:
            obj.unread = False
            obj.save()
        fieldsets = [
            ('Пользователь', {'fields': [
                'link_to_user'
            ]}),
            ('Диалог', {'fields': [
                'dialogue_html'
            ]}),
            ('Состояния', {'fields': [
                'status', 'marked', 'ignored'
            ]}),
            ('Новое сообщение', {'fields': [
                'form_message',
                ('form_button_title', 'form_button_link'),
                'form_image'
            ]})
        ]
        return fieldsets
    readonly_fields = [
        'link_to_user',
        'dialogue_html'
    ]

    def link_to_user(self, obj):
        link = reverse(
            f'admin:{settings.TICKETS_TO_USER_URL_REVERSE}_change', args=[obj.user.pk]
        )
        return format_html(
            f'<a href="{link}" style="font-weight: bold">{obj.user}</a>'
        )
    link_to_user.short_description = 'Пользователь'

    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = 'Имя'

    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = 'Фамилия'

    def dialogue_html(self, obj):
        html = ''
        for message in obj.messages.order_by('created'):
            html += message.html + '\n'
        return format_html(html)

    def read(self, obj):
        return None if obj.last_message_sender == 'support' else not obj.unread
    read.short_description = 'Прочитано'
    read.boolean = True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False

        return super().change_view(request, object_id, form_url, extra_context)

    def has_add_permission(self, request, *args, **kwargs):
        return False

    def has_delete_permission(self, request, *args, **kwargs):
        return False

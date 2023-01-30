NOTIFY_EVENT_INVITE_TO_COMPANY = 4200

GARPIX_COMPANY_NOTIFY_EVENTS = {
    NOTIFY_EVENT_INVITE_TO_COMPANY: {
        'title': 'invite to company',
        'context_description': "<ul>"
                               "    <li>{{ invite_confirmation_link }} - Ссылка-приглашение в компанию</li>"
                               "    <li>{{ company_title }} - Название компании</li>"
                               "    <li>{{ invite }} - Объект инвайта в компанию</li>"
                               "</ul>",
    }
}

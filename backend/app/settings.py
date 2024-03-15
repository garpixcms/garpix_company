from garpixcms.settings import *  # noqa
from garpix_company.settings import *  # noqa

INSTALLED_APPS = [
    'tabbed_admin',
    'modeltranslation',
    'polymorphic_tree',
    'polymorphic',
    'mptt',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'ckeditor',
    'ckeditor_uploader',
    'rest_framework',
    'django.contrib.sites',
    'solo',
    'fcm_django',
    'corsheaders',
    'rest_framework.authtoken',
    'oauth2_provider',
    'social_django',
    # garpixcms
    'garpix_utils',
    'eqator',
    'garpix_admin_lock',
    'garpix_page',
    'garpix_user',
    'garpix_menu',
    'garpix_notify',
    'garpix_package',
    'garpix_auth',
    'drf_spectacular',
    'garpixcms',
    # website
    'garpix_company',
    'user',
    'app'
]

MIGRATION_MODULES.update({  # noqa:F405
    'fcm_django': 'app.migrations.fcm_django',
    'garpix_company': 'app.migrations.garpix_company'
})

NOTIFY_EVENTS.update(GARPIX_COMPANY_NOTIFY_EVENTS)

CHOICES_NOTIFY_EVENT = [(k, v['title']) for k, v in NOTIFY_EVENTS.items()]

GARPIX_COMPANY_MODEL = 'app.Company'

GARPIX_COMPANY_ROLE_MODEL = 'app.UserCompanyRole'

GARPIX_USER_COMPANY_MODEL = 'garpix_company.UserCompany'

GARPIX_COMPANY_CREATE_AND_INVITE_SERIALIZER = 'app.serializers.invite.CustomInviteCompanySerializer'
GARPIX_COMPANY_USER_SERIALIZER = 'app.serializers.user.UserSerializer'
GARPIX_COMPANY_ROLE_SERIALIZER = 'garpix_company.serializers.role.GarpixCompanyRoleSerializer'

GARPIX_COMPANY_INVITE_NOT_USERS = True

SITE_URL = '127.0.0.1:8000'

ISO_LOGS_PRODUCT = 'garpix_company'
IB_ISO_LOGS_NAME = 'garpix_company_ib'
SYSTEM_ISO_LOGS_NAME = 'garpix_company_system'

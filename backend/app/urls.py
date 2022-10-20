from garpixcms.urls import *  # noqa

from rest_framework import routers
from django.urls import path, include

router = routers.DefaultRouter()

urlpatterns = [
    # garpix_company
    path('', include(('garpix_company.urls', 'company'), namespace='garpix_company'))
] + urlpatterns

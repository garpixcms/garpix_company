from django.conf import settings
from django.urls import path, include
from rest_framework_nested import routers
from . import views

app_name = 'garpix_company'

API_URL = getattr(settings, 'API_URL', 'api')

router = routers.SimpleRouter()

urlpatterns = []

router.register('company_invite', views.InviteToCompanyViewSet, basename='company_invite')

router.register('company', views.CompanyViewSet, basename='api_company')

company_user_router = routers.NestedDefaultRouter(router, 'company', lookup='company')
company_user_router.register('user', views.UserCompanyViewSet, basename='api_company_user')

urlpatterns += [
    path(f'{API_URL}/', include(router.urls)),
    path(f'{API_URL}/', include(company_user_router.urls)),
]

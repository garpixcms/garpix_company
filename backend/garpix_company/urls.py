from django.conf import settings
from django.urls import path, include
from rest_framework_nested import routers
from . import views

app_name = 'garpix_company'

API_URL = getattr(settings, 'API_URL', 'api')

router = routers.SimpleRouter()

urlpatterns = []

router.register(f'{API_URL}/company_invite', views.InviteToCompanyViewSet, basename='company_invite')

router.register(f'{API_URL}/company', views.CompanyViewSet, basename='api_company')

company_user_router = routers.NestedDefaultRouter(router, f'{API_URL}/company', lookup='company')
company_user_router.register(r'user', views.UserCompanyViewSet, basename='api_company_user')

urlpatterns += [
    path(r'', include(router.urls)),
    path(r'', include(company_user_router.urls)),
]

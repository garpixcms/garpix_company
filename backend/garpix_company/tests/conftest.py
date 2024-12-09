"""
Модуль для определения общих фикстур pytest.
"""

import uuid
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken
from rest_framework.test import APIClient

from garpix_company.models.company import get_company_model
from garpix_company.models.user_company import get_user_company_model
from garpix_company.models.user_role import get_company_role_model

User = get_user_model()
UserCompanyRole = get_company_role_model()
UserCompany = get_user_company_model()
Company = get_company_model()


@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        return User.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def create_role(db):
    def make_role(title, role_type):
        return UserCompanyRole.objects.create(title=title, role_type=role_type)

    return make_role


@pytest.fixture
def setup(create_user, create_role):
    admin_role = create_role(title="admin", role_type=UserCompanyRole.ROLE_TYPE.ADMIN)
    owner_role = create_role(title="owner", role_type=UserCompanyRole.ROLE_TYPE.OWNER)
    employee_role = create_role(title="employee", role_type=UserCompanyRole.ROLE_TYPE.EMPLOYEE)

    admin_user = create_user(username='adminuser', password='password123', is_staff=True)
    owner_user = create_user(username='owneruser', password='password123', is_staff=True)
    employee_user = create_user(username='employeeuser', password='password123', is_staff=True)
    regular_user = create_user(username='regularuser', password='password123')
    invited_user = create_user(username='inviteduser', email='invited@example.com', password='password123')
    other_user = create_user(username='otheruser', email='other@example.com', password='password123')

    company = Company.objects.create(title='Company 1', full_title='Full Company 1')

    UserCompany.objects.create(user=owner_user, company=company, role=owner_role)
    UserCompany.objects.create(user=admin_user, company=company, role=admin_role)
    UserCompany.objects.create(user=employee_user, company=company, role=employee_role)

    company.participants.set([owner_user, employee_user, admin_user])

    return {
        'owner_role': owner_role,
        'admin_role': admin_role,
        'employee_role': employee_role,
        'owner_user': owner_user,
        'admin_user': admin_user,
        'employee_user': employee_user,
        'regular_user': regular_user,
        'invited_user': invited_user,
        'other_user': other_user,
        'company': company,
    }


@pytest.fixture
def get_authorized_client(db):
    def make_client(user):
        client = APIClient()
        application = Application.objects.create(
            name="Test Application",
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            user=user
        )
        access_token = AccessToken.objects.create(
            user=user,
            scope='read write',
            expires=timezone.now() + timedelta(days=1),
            token=str(uuid.uuid4()),
            application=application
        )
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token.token}')
        return client

    return make_client


@pytest.fixture
def admin_client(setup, get_authorized_client):
    return get_authorized_client(setup['admin_user'])


@pytest.fixture
def owner_client(setup, get_authorized_client):
    return get_authorized_client(setup['owner_user'])


@pytest.fixture
def employee_client(setup, get_authorized_client):
    return get_authorized_client(setup['employee_user'])


@pytest.fixture
def regular_client(setup, get_authorized_client):
    return get_authorized_client(setup['regular_user'])


@pytest.fixture
def invited_client(setup, get_authorized_client):
    return get_authorized_client(setup['invited_user'])


@pytest.fixture
def other_client(setup, get_authorized_client):
    return get_authorized_client(setup['other_user'])

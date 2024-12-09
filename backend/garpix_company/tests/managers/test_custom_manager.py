import pytest

from app.models import Company, UserCompanyRole
from garpix_company.helpers import COMPANY_STATUS_ENUM, CHOICES_INVITE_STATUS_ENUM
from garpix_company.models import InviteToCompany


@pytest.mark.django_db
def test_active_companies_manager():
    active_company = Company.objects.create(
        title='Active Company',
        status=COMPANY_STATUS_ENUM.ACTIVE
    )
    deleted_company = Company.objects.create(
        title='Deleted Company',
        status=COMPANY_STATUS_ENUM.DELETED
    )

    active_companies = Company.active_objects.all()

    assert active_company in active_companies
    assert deleted_company not in active_companies


@pytest.mark.django_db
def test_created_invites_manager():
    company = Company.objects.create(title='Company')

    employee_role = UserCompanyRole.objects.create(
        title="employee",
        role_type=UserCompanyRole.ROLE_TYPE.EMPLOYEE
    )

    created_invite = InviteToCompany.objects.create(
        company=company,
        status=CHOICES_INVITE_STATUS_ENUM.CREATED,
        email="created_test@garpix.com",
        role=employee_role
    )
    accepted_invite = InviteToCompany.objects.create(
        company=company,
        status=CHOICES_INVITE_STATUS_ENUM.ACCEPTED,
        email="accepted_test@garpix.com",
        role=employee_role
    )

    created_invites = InviteToCompany.created_objects.all()

    assert created_invite in created_invites
    assert accepted_invite not in created_invites

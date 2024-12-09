import pytest
from django.urls import reverse
from rest_framework import status

from garpix_company.models import InviteToCompany
from garpix_company.models.user_company import UserCompany


@pytest.mark.django_db
class TestInviteToCompanyViewSet:

    def test_invite_retrieve_by_receiver(self, setup, invited_client):
        company = setup['company']
        employee_role = setup['employee_role']
        invited_user = setup['invited_user']

        invite = InviteToCompany.objects.create(
            company=company,
            email=invited_user.email,
            role=employee_role,
            user=invited_user
        )

        url = reverse('garpix_company:company_invite-detail', args=[invite.id])
        response = invited_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['email'] == invited_user.email

    def test_invite_retrieve_by_other_user(self, setup, other_client):
        company = setup['company']
        employee_role = setup['employee_role']
        invited_user = setup['invited_user']

        invite = InviteToCompany.objects.create(
            company=company,
            email=invited_user.email,
            role=employee_role,
            user=invited_user
        )

        url = reverse('garpix_company:company_invite-detail', args=[invite.id])
        response = other_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN, "Другие пользователи не могут получить детали приглашения"

    def test_invite_accept_by_receiver(self, setup, invited_client):
        company = setup['company']
        employee_role = setup['employee_role']
        invited_user = setup['invited_user']

        invite = InviteToCompany.objects.create(
            company=company,
            email=invited_user.email,
            role=employee_role,
            user=invited_user
        )

        url = reverse('garpix_company:company_invite-accept', args=[invite.id])
        response = invited_client.post(url)
        assert response.status_code == status.HTTP_200_OK

        expected_data = {
            'email': invited_user.email,
            'role': employee_role.id,
            'user': invited_user.id
        }
        assert response.data == expected_data, "Ответ не соответствует ожидаемым данным"

        invite.refresh_from_db()
        assert invite.status == InviteToCompany.CHOICES_INVITE_STATUS.ACCEPTED
        assert UserCompany.objects.filter(user=invited_user, company=company).exists()

        url = reverse('garpix_company:company_invite-accept', args=[invite.id])
        response = invited_client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND, "Нельзя принять заявку без статуса 'CREATED'"

    def test_invite_accept_by_other_user(self, setup, other_client):
        company = setup['company']
        employee_role = setup['employee_role']
        invited_user = setup['invited_user']

        invite = InviteToCompany.objects.create(
            company=company,
            email=invited_user.email,
            role=employee_role,
            user=invited_user
        )

        url = reverse('garpix_company:company_invite-accept', args=[invite.id])
        response = other_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invite_decline_by_receiver(self, setup, invited_client):
        company = setup['company']
        employee_role = setup['employee_role']
        invited_user = setup['invited_user']

        invite = InviteToCompany.objects.create(
            company=company,
            email=invited_user.email,
            role=employee_role,
            user=invited_user
        )

        url = reverse('garpix_company:company_invite-decline', args=[invite.id])
        response = invited_client.post(url)
        assert response.status_code == status.HTTP_200_OK

        expected_data = {
            'email': invited_user.email,
            'role': employee_role.id,
            'user': invited_user.id
        }
        assert response.data == expected_data, "Ответ не соответствует ожидаемым данным"

        invite.refresh_from_db()
        assert invite.status == InviteToCompany.CHOICES_INVITE_STATUS.DECLINED
        assert not UserCompany.objects.filter(user=invited_user, company=company).exists()

    def test_invite_decline_by_other_user(self, setup, other_client):
        company = setup['company']
        employee_role = setup['employee_role']
        invited_user = setup['invited_user']

        invite = InviteToCompany.objects.create(
            company=company,
            email=invited_user.email,
            role=employee_role,
            user=invited_user
        )

        url = reverse('garpix_company:company_invite-decline', args=[invite.id])
        response = other_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

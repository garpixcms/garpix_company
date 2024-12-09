import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from garpix_company.models import InviteToCompany
from garpix_company.models.company import get_company_model
from garpix_company.models.user_company import get_user_company_model
from garpix_company.models.user_role import get_company_role_model
from garpix_company.tests.conftest import regular_client

User = get_user_model()
UserCompanyRole = get_company_role_model()
UserCompany = get_user_company_model()
Company = get_company_model()


@pytest.mark.django_db
class TestCompanyViewSet:

    def test_company_list_as_admin(self, setup, admin_client):
        url = reverse('garpix_company:api_company-list')
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'Company 1' in [company['title'] for company in response.json()]

    def test_company_list_as_regular_user(self, setup, regular_client):
        url = reverse('garpix_company:api_company-list')
        response = regular_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_company_retrieve_as_member(self, setup, employee_client):
        company = setup['company']
        url = reverse('garpix_company:api_company-detail', args=[company.id])
        response = employee_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_company_retrieve_as_non_member(self, setup, regular_client):
        company = setup['company']
        url = reverse('garpix_company:api_company-detail', args=[company.id])
        response = regular_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_company_create(self, setup, regular_client):
        data = {
            'title': 'New Company',
            'full_title': 'New Company Full'
        }

        url = reverse('garpix_company:api_company-list')
        response = regular_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Company.objects.filter(title='New Company').exists()
        assert (user_company := UserCompany.objects.get(user=setup['regular_user'], company=response.json()["id"]))
        assert user_company.role.role_type == "owner", "Пользователь, создавший компанию, должен стать владельцем"

    def test_company_update_as_owner(self, setup, owner_client):
        company = setup["company"]
        data = {
            'title': 'Updated Company'
        }
        url = reverse('garpix_company:api_company-detail', args=[company.id])
        response = owner_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['title'] == 'Updated Company'

    def test_company_update_as_non_owner(self, setup, employee_client):
        company = setup['company']
        data = {
            'title': 'Updated Company'
        }
        url = reverse('garpix_company:api_company-detail', args=[company.id])
        response = employee_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_company_delete_as_owner(self, setup, owner_client):
        company = setup['company']
        queryset = Company.active_objects.filter(id=company.id)
        assert queryset.exists(), 'Ожидается существование активной компании до выполнения теста'

        url = reverse('garpix_company:api_company-detail', args=[company.id])
        response = owner_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not queryset.exists()

    def test_company_change_owner(self, setup, owner_client):
        company = setup['company']
        employee_user = setup['employee_user']
        owner_user = setup['owner_user']
        data = {
            'new_owner': employee_user.id,
            'stay_in_company': True
        }

        url = reverse('garpix_company:api_company-change-owner', args=[company.id])
        response = owner_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'status' in data
        assert data['status'] == 'Владелец успешно изменен'

        assert UserCompany.objects.filter(user=employee_user, company=company,
                                          role__role_type='owner').exists()

        assert not UserCompany.objects.filter(user=owner_user, company=company,
                                              role__role_type='owner').exists()

    @pytest.mark.django_db
    def test_change_owner_blocked_user(self, setup, owner_client):
        company = setup['company']
        employee_user = setup['employee_user']

        user_company = UserCompany.objects.get(user=employee_user, company=company)
        user_company.is_blocked = True
        user_company.save()

        url = reverse('garpix_company:api_company-change-owner', args=[company.id])
        data = {'new_owner': employee_user.id, 'stay_in_company': True}

        response = owner_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            "Заблокированный пользователь не может быть назначен владельцем компании"
        )

    @pytest.mark.django_db
    def test_change_owner_existing_owner(self, setup, owner_client):
        company = setup['company']
        owner_user = setup['owner_user']

        url = reverse('garpix_company:api_company-change-owner', args=[company.id])
        data = {'new_owner': owner_user.id, 'stay_in_company': True}

        response = owner_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            "Пользователь с указанным id уже является владельцем компании"
        )

    @pytest.mark.django_db
    def test_change_owner_non_employee(self, setup, owner_client):
        company = setup['company']
        regular_user = setup['regular_user']

        url = reverse('garpix_company:api_company-change-owner', args=[company.id])
        data = {'new_owner': regular_user.id, 'stay_in_company': True}

        response = owner_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            "Только сотрудник компании может быть назначен владельцем"
        )

    def test_company_invite_user(self, setup, admin_client):
        company = setup['company']
        admin_role = setup['admin_role']
        invited_user = setup['invited_user']

        data = {
            'user': invited_user.id,
            'role': admin_role.id
        }

        url = reverse('garpix_company:api_company-invite', args=[company.id])
        response = admin_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        expected_data = data | {'email': invited_user.email}
        assert data == expected_data, "Ответ не соответствует ожидаемым данным"

    def test_company_employee_invite_(self, setup, admin_client):
        company = setup['company']
        admin_role = setup['admin_role']
        employee_user = setup['employee_user']
        url = reverse('garpix_company:api_company-invite', args=[company.id])

        data = {
            'user': employee_user.id,
            'role': admin_role.id
        }
        response = admin_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST, 'Нельзя отправить приглашение для сотрудника компании'

    @override_settings(
        GARPIX_COMPANY_INVITE_NOT_USERS=True
    )
    def test_company_not_users_invite_on(self, setup, admin_client):
        company = setup['company']
        admin_role = setup['admin_role']
        url = reverse('garpix_company:api_company-invite', args=[company.id])

        data = {
            'role': admin_role.id,
            'email': 'not_registered@garpix.com'
        }

        response = admin_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED, (
            f"Ожидался статус {status.HTTP_201_CREATED}, но получен {response.status_code}"
        )

    @override_settings(
        GARPIX_COMPANY_INVITE_NOT_USERS=False
    )
    def test_company_not_users_invite_off(self, setup, admin_client):
        company = setup['company']
        admin_role = setup['admin_role']
        url = reverse('garpix_company:api_company-invite', args=[company.id])

        data = {
            'role': admin_role.id,
            'email': 'not_registered@garpix.com'
        }

        response = admin_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f"Ожидался статус {status.HTTP_400_BAD_REQUEST}, но получен {response.status_code}"
        )

    @pytest.mark.django_db
    def test_create_and_invite_success(self, setup, owner_client):
        company = setup['company']
        employee_role = setup['employee_role']

        url = reverse('garpix_company:api_company-create-and-invite', args=[company.id])

        data = {
            'email': 'new_user@example.com',
            'role': employee_role.id,
            'username': 'new_user'
        }

        response = owner_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED, f"Ожидаемый статус: 201, полученный: {response.status_code}"

        response_data = response.json()
        expected_data = {
            'email': 'new_user@example.com',
            'role': employee_role.id
        }
        assert response_data == expected_data, "Ответ не соответствует ожидаемым данным"

        user = User.objects.filter(email='new_user@example.com').first()
        assert user is not None, "Пользователь не был создан"
        assert user.username == 'new_user', f"Ожидаемое имя пользователя: 'new_user', полученное: '{user.username}'"

        invite = InviteToCompany.objects.filter(email='new_user@example.com', company=company).first()
        assert invite is not None, "Инвайт не был создан"
        assert invite.role == employee_role, "Роль в инвайте не соответствует ожидаемой"
        assert invite.status == InviteToCompany.CHOICES_INVITE_STATUS.CREATED, "Статус инвайта не соответствует ожидаемому"

    def test_company_invite_user_as_non_admin(self, setup, employee_client):
        company = setup['company']
        employee_role = setup['employee_role']
        invited_user = setup['invited_user']

        data = {
            'user': invited_user.id,
            'role': employee_role.id
        }

        url = reverse('garpix_company:api_company-invite', args=[company.id])
        response = employee_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invites_list(self, setup, admin_client):
        company = setup['company']
        employee_role = setup['employee_role']
        admin_role = setup['admin_role']

        user1_email = "user1@garpix.com"
        user2_email = "user2@garpix.com"

        # Создание инвайтов
        status_created = InviteToCompany.CHOICES_INVITE_STATUS.CREATED
        InviteToCompany.objects.create(
            email=user1_email,
            company=company,
            role=employee_role,
            status=status_created
        )
        InviteToCompany.objects.create(
            email=user2_email,
            company=company,
            role=admin_role,
            status=InviteToCompany.CHOICES_INVITE_STATUS.ACCEPTED
        )

        url = reverse('garpix_company:api_company-invites', args=[company.id])

        # Фильтрация по статусу
        response = admin_client.get(url, {"status": status_created})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 1, f"Ожидается 1 инвайт, получено: {len(response_data)}"
        assert response_data[0]['email'] == user1_email, "Email инвайта не соответствует ожидаемому"
        assert response_data[0]['status'] == status_created, "Статус инвайта не соответствует ожидаемому"

        # Фильтрация по роли
        response = admin_client.get(url, {"role": employee_role.id})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 1, f"Ожидается 1 инвайт, получено: {len(response_data)}"
        assert response_data[0]['email'] == user1_email, "Email инвайта не соответствует ожидаемому"
        assert response_data[0]['role']['id'] == employee_role.id, "Роль инвайта не соответствует ожидаемой"

        # Фильтрация по отсутствующему статусу
        response = admin_client.get(url, {"status": "non_existing_status"})
        assert response.status_code == status.HTTP_200_OK, "Ожидается успешный статус 200"
        assert len(response.json()) == 0, "Ожидается пустой список для несуществующего статуса"

        # Фильтрация по отсутствующей роли
        response = admin_client.get(url, {"role": 99999})  # Несуществующая роль
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert 'role' in response_data, "Ожидается сообщение об ошибке для отсутствующей роли"

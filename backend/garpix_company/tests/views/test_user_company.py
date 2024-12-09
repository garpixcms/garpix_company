import pytest
from django.urls import reverse
from rest_framework import status
from garpix_company.models.user_company import UserCompany


@pytest.mark.django_db
class TestUserCompanyViewSet:

    def test_list_users_as_staff(self, setup, admin_client, employee_client):
        company = setup['company']
        url = reverse('garpix_company:api_company_user-list', kwargs={'company_pk': company.id})

        # Проверка для администратора
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK, "Администратор компании должен иметь доступ к списку пользователей"
        data = response.json()
        assert len(data) == 3, "В компании должно быть 3 пользователя"

        # Проверка для сотрудника
        response = employee_client.get(url)
        assert response.status_code == status.HTTP_200_OK, "Сотрудник компании может получить список пользователей компании"

    def test_retrieve_user_as_admin(self, setup, admin_client):
        company = setup['company']
        employee_user = setup['employee_user']
        user_company = UserCompany.objects.get(user=employee_user, company=company)

        url = reverse(
            'garpix_company:api_company_user-detail',
            kwargs={'company_pk': company.id, 'pk': user_company.id}
        )
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json().get('user', {}).get('id') == employee_user.id

    def test_block_user_as_admin(self, setup, admin_client):
        company = setup['company']
        user_company = UserCompany.objects.get(user=setup['employee_user'], company=company)

        url = reverse(
            'garpix_company:api_company_user-block',
            kwargs={'company_pk': company.id, 'pk': user_company.id}
        )
        response = admin_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'status': 'success'}, "Ответ не соответствует ожидаемым данным"

        user_company.refresh_from_db()
        assert user_company.is_blocked, "Пользователь должен быть заблокирован"

    def test_block_owner(self, setup, admin_client):
        company = setup['company']
        owner_user = setup['owner_user']
        user_company = UserCompany.objects.get(user=owner_user, company=company)

        url = reverse(
            'garpix_company:api_company_user-block',
            kwargs={'company_pk': company.id, 'pk': user_company.id}
        )
        response = admin_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'non_field_error' in data
        assert data['non_field_error'][0] == 'Нельзя заблокировать владельца компании'

    def test_unblock_user_as_admin(self, setup, admin_client):
        company = setup['company']
        user_company = UserCompany.objects.get(user=setup['employee_user'], company=company)
        user_company.is_blocked = True
        user_company.save()

        url = reverse(
            'garpix_company:api_company_user-unblock',
            kwargs={'company_pk': company.id, 'pk': user_company.id}
        )
        response = admin_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'status': 'success'}, "Ответ не соответствует ожидаемым данным"

        user_company.refresh_from_db()
        assert not user_company.is_blocked, "Пользователь должен быть разблокирован"

    def test_change_role_as_admin(self, setup, admin_client):
        company = setup['company']
        user_company = UserCompany.objects.get(user=setup['employee_user'], company=company)
        new_role = setup['admin_role']

        url = reverse(
            'garpix_company:api_company_user-change-role',
            kwargs={'company_pk': company.id, 'pk': user_company.id}
        )
        data = {'role': new_role.id}
        response = admin_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'status': 'success'}, "Ответ не соответствует ожидаемым данным"

        user_company.refresh_from_db()
        assert user_company.role == new_role, "Роль пользователя должна быть изменена"

    def test_change_role_to_owner(self, setup, admin_client):
        company = setup['company']
        user_company = UserCompany.objects.get(user=setup['employee_user'], company=company)
        owner_role = setup['owner_role']

        url = reverse(
            'garpix_company:api_company_user-change-role',
            kwargs={'company_pk': company.id, 'pk': user_company.id}
        )
        data = {'role': owner_role.id}
        response = admin_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_error' in response.json()

    def test_delete_user_as_admin(self, setup, admin_client):
        company = setup['company']
        user_company = UserCompany.objects.get(user=setup['employee_user'], company=company)

        url = reverse(
            'garpix_company:api_company_user-detail',
            kwargs={'company_pk': company.id, 'pk': user_company.id}
        )
        response = admin_client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert not UserCompany.objects.filter(
            id=user_company.id).exists(), "Пользователь должен быть удален из компании"

    def test_delete_owner(self, setup, admin_client):
        company = setup['company']
        user_company = UserCompany.objects.get(user=setup['owner_user'], company=company)

        url = reverse(
            'garpix_company:api_company_user-detail',
            kwargs={'company_pk': company.id, 'pk': user_company.id}
        )
        response = admin_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'non_field_error' in data
        assert data['non_field_error'][0] == 'Нельзя удалить владельца компании'

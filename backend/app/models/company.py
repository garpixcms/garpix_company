from garpix_company.models import AbstractCompany, UserCompany


class Company(AbstractCompany):

    @classmethod
    def check_user_companies_limit(cls, user):
        return UserCompany.objects.filter(user=user).count() < 1

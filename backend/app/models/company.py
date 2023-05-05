from garpix_company.models import AbstractCompany, get_user_company_model
UserCompany = get_user_company_model()


class Company(AbstractCompany):

    @classmethod
    def check_user_companies_limit(cls, user):
        return UserCompany.objects.filter(user=user).count() < 10

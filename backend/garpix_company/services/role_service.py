from garpix_company.models.user_role import get_company_role_model


class UserCompanyRoleService():

    def __init__(self):
        self.CompanyRoleModel = get_company_role_model()

    def get_owner_role(self):
        return self.CompanyRoleModel.objects.filter(role_type=self.CompanyRoleModel.ROLE_TYPE.OWNER).first()

    def get_employee_role(self):
        return self.CompanyRoleModel.objects.filter(role_type=self.CompanyRoleModel.ROLE_TYPE.EMPLOYEE).first()

    def get_admin_role(self):
        return self.CompanyRoleModel.objects.filter(role_type=self.CompanyRoleModel.ROLE_TYPE.ADMIN).first()

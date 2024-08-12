from django.contrib import admin
from django.forms import BaseInlineFormSet, ValidationError
from django.utils.translation import gettext as _
from garpix_company.models import get_user_company_model, get_company_role_model


UserCompany = get_user_company_model()
UserCompanyRole = get_company_role_model()


class UserCompanyInlineFormset(BaseInlineFormSet):
    def clean(self) -> None:
        super().clean()

        self._validate_has_one_owner()

    def _validate_has_one_owner(self) -> None:
        owners = set()

        for form in self.forms:
            if form.cleaned_data['role'].role_type == UserCompanyRole.ROLE_TYPE.OWNER:
                owners.add(form.cleaned_data['user'])

        if len(owners) != 1:
            raise ValidationError(_('В компании должен быть 1 владелец.'))


class UserCompanyInline(admin.TabularInline):
    model = UserCompany
    extra = 0
    raw_id_fields = ['user']
    formset = UserCompanyInlineFormset


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    readonly_fields = ('created_at', )
    inlines = (UserCompanyInline,)

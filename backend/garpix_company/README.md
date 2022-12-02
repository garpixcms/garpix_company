# Garpix Company

Company module for Django/DRF projects.


## Quickstart

Install with pip:

```bash
pip install garpix_company
```

Add the `garpix_company` to your `INSTALLED_APPS`:

```python
# settings.py

# ...
INSTALLED_APPS = [
    # ...
    'garpix_company',
]
```

and to migration modules:

```python
# settings.py

# ...
MIGRATION_MODULES = {
    'garpix_company': 'app.migrations.garpix_company',
}
```

Add to `urls.py`:

```python

# ...
urlpatterns = [
    # ...
    # garpix_user
    path('', include(('garpix_company.urls', 'garpix_company'), namespace='garpix_company')),

]
```

Add Company model to your project using abstract `AbstractCompany` from the model:
```python
from garpix_company.models import AbstractCompany


class Company(AbstractCompany):
    pass

```

Add `GARPIX_COMPANY_MODEL` to `settings.py`:

```python
# settings.py

GARPIX_COMPANY_MODEL = 'app.Company'

```

Use `CompanyAdmin` as base in your admin panel:
```python
from django.contrib import admin

from app.models import Company
from garpix_company.admin import CompanyAdmin


@admin.register(Company)
class CompanyAdmin(CompanyAdmin):
    pass

```

## Invite and create user

You can add fields to `company_invite/create_and_invite` endpoint.  

To do it override `CreateAndInviteToCompanySerializer` by adding field and add it to `settings`:

```python
# settings.py

GARPIX_COMPANY_CREATE_AND_INVITE_SERIALIZER = 'app.serializers.CustomInviteCompanySerializer'

```

```python
# app.serializers.py

from rest_framework import serializers

from garpix_company.serializers import CreateAndInviteToCompanySerializer


class CustomInviteCompanySerializer(CreateAndInviteToCompanySerializer):
    username = serializers.CharField(write_only=True)

    class Meta(CreateAndInviteToCompanySerializer.Meta):
        fields = CreateAndInviteToCompanySerializer.Meta.fields + ('username',)


```

## Permissions

If you need to add custom permissions on company endpoints, you can override `action_permissions` class method of `Company` model:

```python
from garpix_company.models import AbstractCompany
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from garpix_company.permissions import CompanyAdminOnly, CompanyOwnerOnly

class Company(AbstractCompany):

    @classmethod
    def action_permissions(cls):
        return {'create': [IsAuthenticated],
                'retrieve': [AllowAny],
                'list': [AllowAny],
                'update': [IsAdminUser | CompanyAdminOnly],
                'partial_update': [IsAdminUser | CompanyAdminOnly],
                'destroy': [IsAdminUser | CompanyAdminOnly],
                'change_owner': [IsAdminUser | CompanyOwnerOnly]}
```

See `garpix_company/tests/test_company.py` for examples.

# Changelog

Смотри [CHANGELOG.md](CHANGELOG.md).

# Contributing

Смотри [CONTRIBUTING.md](CONTRIBUTING.md).

# License

[MIT](LICENSE)

---

Developed by Garpix / [https://garpix.com](https://garpix.com)
### 2.7.0 (04.05.2023)

- `GARPIX_USER_COMPANY_MODEL` setting added
- `role` and `stay_in_company` fields added to `change_owner` endpoint

### 2.6.1 (27.04.2023)

- Invite user bug fixed

### 2.6.0 (14.02.2023)

- Decline previous invites for the invite to same person

### 2.5.0 (10.02.2023)

- `is_admin` field removed from `company` views
- GET `company` and `company/{id}/` endpoints permissions changed
- Added a check to see if the user is blocked when changing the owner
- Added check whether the user to whom the invite is sent is already company user

### 2.4.1 (06.02.2023)

- Updated `django-filter` minimum version to 21.1

### 2.4.0 (06.02.2023)

- `accept` and `decline` invite endpoints fixed
- `change` owner now works by `UserCompany` instance id
- Invite permissions fixed

### 2.3.0 (06.02.2023)

- Added `is_blocked` filter to `company/{id}/user` endpoint

### 2.2.0 (02.02.2023)

- Set `blank=True` to field `user` of `InviteToCompany` model
- Pagination added to `invites` endpoint

### 2.1.1 (02.02.2023)

- `CompanyOwnerOnly` and `CompanyAdminOnly` permissions bug fixed

### 2.1.0 (30.01.2023)

- `lookup_field` updated to `id` in  invite view.

### 2.0.0 (26.01.2023)

- Fields `owner` from `Company`, `is_admin` from `UserCompany` and `Invite` models deprecated
- `change_role` endpoint added
- `status` filter added to `invites` list endpoint
- All permissions are in views now
- `user` field added to invite functionality

### 1.2.0 (19.01.2023)

- Fixed bug with `CompanyAdminOnly` permission classes
- `GARPIX_COMPANY_ROLE_SERIALIZER` setting added (see `Readme.md`)

### 1.1.0 (19.01.2023)

- Fixed bug with permissions
- `role` field added to `InviteToCompany`
- Searching added to GET `company/{pk}/user/` endpoint
- `company/{pk}/invites/` endpoint added.
- `GARPIX_COMPANY_USER_SERIALIZER` setting added (see `Readme.md`)

### 1.0.1 (13.01.2023)

- Fixed bug with company creation endpoint

### 1.0.0 (26.12.2022)

- Release to pypi.org

### 1.0.0-rc5 (26.12.2022)

- Admin panel changes

### 1.0.0-rc4 (08.12.2022)

- `destroy` action added to `UerCompany` view.
- `AbstractUserCompanyRole` model added (see `Readme.md`).
- `check_user_companies_limit` class method added to `Company` model.

### 1.0.0-rc3 (02.12.2022)

- `owner` field added to `Company` model.

### 1.0.0-rc2 (25.10.2022)

- Invite and create user endpoint added (see `Readme.md`);

### 1.0.0-rc1 (21.10.2022)

- Release on pypi.org.

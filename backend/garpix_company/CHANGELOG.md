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

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

See `garpix_vacancy/tests/test_company.py` for examples.

# Changelog

Смотри [CHANGELOG.md](CHANGELOG.md).

# Contributing

Смотри [CONTRIBUTING.md](CONTRIBUTING.md).

# License

[MIT](LICENSE)

---

Developed by Garpix / [https://garpix.com](https://garpix.com)
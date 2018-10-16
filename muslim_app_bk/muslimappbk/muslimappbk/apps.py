from django.contrib.admin.apps import AdminConfig


class MuslimAppConfig(AdminConfig):
    default_site = 'muslimappbk.admin.MuslimAppAdminSite'

from django.contrib.admin import AdminSite

# Register your models here.
class MuslimAppAdminSite(AdminSite):
    site_header = 'Muslim App administration'
    site_title = 'Muslim App'
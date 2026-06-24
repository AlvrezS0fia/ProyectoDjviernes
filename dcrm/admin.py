from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    site_header = 'ANGELOW'
    site_title = 'Panel de Administración'
    index_title = 'Bienvenido'
    site_url = '/'

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

custom_admin_site = CustomAdminSite(name='custom_admin')
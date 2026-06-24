from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'direccion_corta', 'fecha_registro')
    list_filter = ('fecha_registro',)
    search_fields = ('nombre', 'email', 'telefono', 'direccion')
    ordering = ('-fecha_registro',)
    list_per_page = 25

    fieldsets = (
        ('Información personal', {
            'fields': ('nombre', 'email', 'telefono', 'direccion'),
            'description': 'Datos de contacto del cliente registrado.'
        }),
        ('Datos del sistema', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',),
            'description': 'Información generada automáticamente.'
        }),
    )
    readonly_fields = ('fecha_registro',)
    date_hierarchy = 'fecha_registro'

    actions = ['exportar_csv', 'marcar_sin_telefono']

    def direccion_corta(self, obj):
        if not obj.direccion:
            return '—'
        return obj.direccion[:60] + ('…' if len(obj.direccion) > 60 else '')
    direccion_corta.short_description = 'Dirección'
    direccion_corta.admin_order_field = 'direccion'

    def exportar_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="clientes.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Nombre', 'Email', 'Teléfono', 'Dirección', 'Fecha registro'])
        for c in queryset:
            writer.writerow([c.id, c.nombre, c.email, c.telefono, c.direccion, c.fecha_registro])
        return response
    exportar_csv.short_description = "Exportar seleccionados a CSV"

    def marcar_sin_telefono(self, request, queryset):
        count = queryset.filter(telefono__isnull=True).update(telefono='')
        self.message_user(request, f"{count} cliente(s) sin teléfono detectados.")
    marcar_sin_telefono.short_description = "Marcar seleccionados sin teléfono"
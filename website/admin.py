from django.contrib import admin
from .models import Record


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_completo', 'email', 'phone_number', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'city')
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Información personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number'),
            'description': 'Nombre completo y datos de contacto del usuario.'
        }),
        ('Ubicación', {
            'fields': ('address', 'city', 'state', 'zip_code'),
            'description': 'Dirección y datos de localización.'
        }),
        ('Datos del sistema', {
            'fields': ('created_at',),
            'classes': ('collapse',),
            'description': 'Fecha de registro del usuario. Generada automáticamente.'
        }),
    )
    readonly_fields = ('created_at',)

    actions = ['exportar_registros_csv', 'marcar_sin_ciudad']

    def nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    nombre_completo.short_description = 'Nombre completo'
    nombre_completo.admin_order_field = 'last_name'

    def exportar_registros_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="registros.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Nombre', 'Apellido', 'Email', 'Teléfono', 'Dirección', 'Ciudad', 'Estado', 'Código Postal', 'Fecha Registro'])
        for r in queryset:
            writer.writerow([r.id, r.first_name, r.last_name, r.email, r.phone_number, r.address, r.city, r.state, r.zip_code, r.created_at])
        return response
    exportar_registros_csv.short_description = "📥 Exportar registros a CSV"

    def marcar_sin_ciudad(self, request, queryset):
        count = queryset.filter(city__isnull=True).count()
        self.message_user(request, f"{count} registro(s) sin ciudad detectados.", level='warning')
    marcar_sin_ciudad.short_description = "⚠️ Ver registros sin ciudad"
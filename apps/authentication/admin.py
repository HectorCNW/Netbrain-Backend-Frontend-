from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "nombre", "rol", "activo", "fecha_creacion"]
    list_filter = ["rol", "activo"]
    search_fields = ["email", "nombre"]
    ordering = ["-fecha_creacion"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Info", {"fields": ("nombre", "rol", "activo")}),
        ("Permisos", {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "nombre", "rol", "password1", "password2")}),
    )

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class KararsizimUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "created_at")
    readonly_fields = ("created_at",)
    fieldsets = UserAdmin.fieldsets + (
        ("Ek bilgiler", {"fields": ("created_at",)}),
    )

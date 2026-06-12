# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Кастомный админ-класс для модели User."""

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        "id",
        "email",
        "name",
        "surname",
        "phone",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = ("email", "name", "surname", "phone")

    list_filter = ("is_active", "is_staff", "is_superuser")

    ordering = ("-id",)

    list_per_page = 25

    list_editable = ("is_active", "is_staff")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Личная информация"), {"fields": ("name", "surname", "avatar", "phone", "github_url", "about")}),
        (_("Права доступа"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Избранное"), {"fields": ("favorites",), "classes": ("collapse",)}),
        (_("Важные даты"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "surname", "phone", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ("last_login", "date_joined")

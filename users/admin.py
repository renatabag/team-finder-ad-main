from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User
from .validators import validate_github_url


class CustomUserChangeForm(UserChangeForm):
    """Кастомная форма для изменения пользователя в админке."""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


class CustomUserCreationForm(UserCreationForm):
    """Кастомная форма для создания пользователя в админке."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Кастомный админ-класс для модели User с поддержкой всех полей."""

    # Формы для создания и редактирования
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # Поля отображаемые в списке пользователей
    list_display = ("email", "name", "surname", "phone", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "name", "surname", "phone")
    ordering = ("email",)

    # Настройка полей для редактирования (форма редактирования)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {
            "fields": (
                "name",
                "surname",
                "avatar",
                "phone",
                "github_url",
                "about",
            )
        }),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Favorites"), {"fields": ("favorites",)}),
    )

    # Настройка полей для создания нового пользователя
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # Поля только для чтения
    readonly_fields = ("last_login", "date_joined")

    def get_fieldsets(self, request, obj=None):
        """Динамически изменяем fieldsets для разных ситуаций."""
        fieldsets = super().get_fieldsets(request, obj)

        if not obj:
            # Для создания нового пользователя убираем лишние поля
            return fieldsets

        # Для существующего пользователя показываем все поля
        return fieldsets
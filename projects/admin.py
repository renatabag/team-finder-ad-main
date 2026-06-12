from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Админ-класс для модели Project."""

    # Поля для отображения в списке
    list_display = (
        "id",
        "name",
        "owner",
        "status",
        "participants_count",
        "created_at",
        "github_url",
    )

    # Поля для поиска
    search_fields = (
        "name",
        "description",
        "owner__email",
        "owner__name",
        "owner__surname",
        "github_url",
    )

    # Фильтры
    list_filter = (
        "status",
        "created_at",
        "owner",
    )

    # Сортировка по умолчанию
    ordering = ("-created_at",)

    # Количество объектов на странице
    list_per_page = 25

    # Поля, которые можно редактировать прямо в списке
    list_editable = ("status",)

    # Поля только для чтения
    readonly_fields = ("created_at", "participants_list")

    # Фильтр по дате с иерархией
    date_hierarchy = "created_at"

    # Группировка полей в форме редактирования
    fieldsets = (
        (None, {"fields": ("name", "description")}),
        (
            _("Детали проекта"),
            {
                "fields": (
                    "owner",
                    "status",
                    "github_url",
                    "participants",
                )
            },
        ),
        (
            _("Информация"),
            {
                "fields": ("created_at", "participants_list"),
                "classes": ("collapse",),
            },
        ),
    )

    # Фильтр по владельцу с поиском
    autocomplete_fields = ("owner", "participants")

    # Оптимизация запросов
    list_select_related = ("owner",)

    def get_queryset(self, request):
        """Оптимизация запросов с аннотацией количества участников."""
        return super().get_queryset(request).annotate(participants_count=Count("participants"))

    def participants_count(self, obj):
        """Отображение количества участников."""
        return obj.participants_count

    participants_count.short_description = "Участников"
    participants_count.admin_order_field = "participants_count"

    def participants_list(self, obj):
        """Отображение списка участников для админки."""
        participants = obj.participants.all()[:10]
        if not participants:
            return "Нет участников"
        return ", ".join([f"{p.name} {p.surname}" for p in participants])

    participants_list.short_description = "Список участников"

    # Действия для нескольких объектов
    actions = ["make_closed", "make_open"]

    @admin.action(description="Закрыть выбранные проекты")
    def make_closed(self, request, queryset):
        """Массовое закрытие проектов."""
        updated = queryset.update(status=Project.STATUS_CLOSED)
        self.message_user(request, f"Закрыто проектов: {updated}")

    @admin.action(description="Открыть выбранные проекты")
    def make_open(self, request, queryset):
        """Массовое открытие проектов."""
        updated = queryset.update(status=Project.STATUS_OPEN)
        self.message_user(request, f"Открыто проектов: {updated}")

    # Сохранение с дополнительной логикой
    def save_model(self, request, obj, form, change):
        """Дополнительная логика при сохранении через админку."""
        if not change:  # Если создаётся новый проект
            obj.owner = request.user
        super().save_model(request, obj, form, change)

from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.constants import (
    PROJECTS_PER_PAGE,  # Константа должна быть в core/constants.py
)
from utils import paginate_queryset

from .forms import ProjectForm
from .models import Project


def project_list_view(request):
    """Список всех проектов с оптимизацией запросов."""
    # Оптимизация: добавляем количество участников (один дополнительный запрос)
    queryset = (
        Project.objects.select_related("owner")  # Загружаем владельца (JOIN, 1 запрос)
        .prefetch_related("participants")  # Предзагружаем участников (1 запрос)
        .annotate(participants_count=Count("participants"))  # Добавляем аннотацию с количеством
        .order_by("-created_at")
    )

    page_obj = paginate_queryset(request, queryset, PROJECTS_PER_PAGE)

    return render(
        request,
        "projects/project_list.html",
        {"projects": page_obj},
    )


def project_detail_view(request, project_id):
    """Детальная страница проекта с оптимизацией."""
    # Оптимизация: загружаем всё необходимое за 2-3 запроса
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        id=project_id,
    )

    return render(
        request,
        "projects/project-details.html",
        {"project": project},
    )


@login_required
def create_project_view(request):
    """Создание нового проекта."""
    form = ProjectForm(request.POST or None)

    if form.is_valid():
        project_obj = form.save(commit=False)
        project_obj.owner = request.user
        project_obj.save()
        project_obj.participants.add(request.user)
        return redirect("projects:detail", project_id=project_obj.id)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def edit_project_view(request, project_id):
    """Редактирование проекта."""
    project_obj = get_object_or_404(Project, id=project_id)

    if project_obj.owner != request.user:
        return redirect("projects:detail", project_id=project_obj.id)

    form = ProjectForm(request.POST or None, instance=project_obj)

    if form.is_valid():
        updated_project = form.save()
        return redirect("projects:detail", project_id=updated_project.id)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": True,
        },
    )


@require_POST
@login_required
def toggle_participation_view(request, project_id):
    """Участие/отказ от участия в проекте."""
    project_obj = get_object_or_404(Project, id=project_id)
    user = request.user

    already_joined = project_obj.participants.filter(id=user.id).exists()

    if already_joined:
        project_obj.participants.remove(user)
    else:
        project_obj.participants.add(user)

    return JsonResponse(
        {
            "status": "ok",
            "participant": not already_joined,
        },
        status=HTTPStatus.OK,
    )


@require_POST
@login_required
def complete_project_view(request, project_id):
    """Завершение проекта (только для владельца)."""
    project_obj = get_object_or_404(Project, id=project_id)

    if project_obj.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Только владелец может завершить проект"},
            status=HTTPStatus.FORBIDDEN,
        )

    if project_obj.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "Проект уже завершён"},
            status=HTTPStatus.BAD_REQUEST,
        )

    project_obj.status = Project.STATUS_CLOSED
    project_obj.save(update_fields=["status"])

    return JsonResponse(
        {
            "status": "ok",
            "project_status": Project.STATUS_CLOSED,
        },
        status=HTTPStatus.OK,
    )


@require_POST
@login_required
def toggle_favorite_view(request, project_id):
    """Добавление/удаление проекта в избранное."""
    project_obj = get_object_or_404(Project, id=project_id)
    user = request.user

    in_favorites = user.favorites.filter(id=project_obj.id).exists()

    if in_favorites:
        user.favorites.remove(project_obj)
    else:
        user.favorites.add(project_obj)

    return JsonResponse(
        {
            "status": "ok",
            "favorited": not in_favorites,
        },
        status=HTTPStatus.OK,
    )


@login_required
def favorite_projects_view(request):
    """Список избранных проектов пользователя с оптимизацией."""
    queryset = (
        request.user.favorites.select_related("owner")
        .prefetch_related("participants")
        .annotate(participants_count=Count("participants"))
        .order_by("-created_at")
    )

    page_obj = paginate_queryset(request, queryset, PROJECTS_PER_PAGE)

    return render(
        request,
        "projects/favorite_projects.html",
        {"projects": page_obj},
    )

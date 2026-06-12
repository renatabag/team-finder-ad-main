from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone  # ← ДОБАВИТЬ ЭТОТ ИМПОРТ

from core.constants import (
    USER_ABOUT_MAX_LEN,
    USER_NAME_MAX_LEN,
    USER_PHONE_MAX_LEN,
    USER_SURNAME_MAX_LEN,
)
from utils import build_avatar_file

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LEN)
    surname = models.CharField(max_length=USER_SURNAME_MAX_LEN)
    avatar = models.ImageField(upload_to="users/avatars/", blank=True)
    phone = models.CharField(max_length=USER_PHONE_MAX_LEN, unique=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=USER_ABOUT_MAX_LEN, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)  # ← ДОБАВИТЬ ЭТУ СТРОКУ
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = build_avatar_file(self.name, self.email)  # ← здесь
        super().save(*args, **kwargs)

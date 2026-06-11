from urllib.parse import urlparse
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from projects.models import Project


class ProjectForm(forms.ModelForm):
    STATUS_DISPLAY_CHOICES = [
        (Project.STATUS_OPEN, "Открыт"),
        (Project.STATUS_CLOSED, "Закрыт"),
    ]

    status = forms.ChoiceField(label="Статус", choices=STATUS_DISPLAY_CHOICES)

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название",
            "description": "Описание",
            "github_url": "Ссылка на GitHub",
        }

    def clean_github_url(self):
        """Валидация, что ссылка ведёт на GitHub."""
        github_url = self.cleaned_data.get("github_url")

        # Если поле пустое (blank=True), пропускаем валидацию
        if not github_url:
            return github_url

        # Базовая валидация URL (проверка формата)
        url_validator = URLValidator()
        try:
            url_validator(github_url)
        except ValidationError:
            raise ValidationError("Введите корректный URL адрес.")

        # Проверка, что домен принадлежит GitHub
        allowed_domains = [
            "github.com",
            "www.github.com",
            "raw.githubusercontent.com",
            "gist.github.com",
            "api.github.com",
        ]

        parsed_url = urlparse(github_url)
        domain = parsed_url.netloc.lower()

        domain = domain.split(":")[0]

        if not any(
            domain == allowed or domain.endswith(f".{allowed}")
            for allowed in allowed_domains
        ):
            raise ValidationError(
                "Ссылка должна вести на GitHub (github.com, "
                "raw.githubusercontent.com, gist.github.com или api.github.com)")

        path = parsed_url.path.strip("/")
        if not path:
            raise ValidationError(
                "Укажите полную ссылку на репозиторий, "
                "например: https://github.com/username/repo"
            )

        return github_url

from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_github_url(value):
    """Валидация URL на принадлежность к GitHub."""
    if not value:
        return value

    parsed_url = urlparse(value)
    domain = parsed_url.netloc.lower()

    valid_domain = domain in {"github.com", "www.github.com"}
    valid_scheme = parsed_url.scheme in {"http", "https"}

    if not valid_scheme or not valid_domain:
        raise ValidationError("Укажите ссылку на github.com")

    return value

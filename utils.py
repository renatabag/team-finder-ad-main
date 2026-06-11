import hashlib
import re
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont

# Константы для телефонов
PHONE_PATTERN = re.compile(r"^(8\d{10}|\+7\d{10})$")

# Константы для аватаров
AVATAR_SIZE = 128
AVATAR_TEXT_COLOR = "white"
AVATAR_FONT_SIZE = 72
AVATAR_FONT_NAME = "DejaVuSans-Bold.ttf"
DEFAULT_AVATAR_LETTER = "U"

# Цвета для фона аватара
COLOR_GREEN = "#6B8E73"
COLOR_BLUE = "#7C90A0"
COLOR_BROWN = "#8D7B68"
COLOR_PURPLE = "#7F6A93"
COLOR_TEAL = "#5F8A8B"
COLOR_BEIGE = "#8A7E66"

AVATAR_COLORS = [
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_BROWN,
    COLOR_PURPLE,
    COLOR_TEAL,
    COLOR_BEIGE,
]


def paginate_queryset(request, queryset, per_page):
    """Пагинация queryset."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def normalize_phone_number(raw_phone: str) -> str:
    """Нормализация номера телефона к формату +7XXXXXXXXXX."""
    value = (raw_phone or "").strip()
    return f"+7{value[-10:]}"


def pick_avatar_background(seed: str) -> str:
    """Выбор цвета фона для аватара на основе seed-строки."""
    source = (seed or "user").encode("utf-8")
    color_index = int(hashlib.md5(source).hexdigest(), 16) % len(AVATAR_COLORS)
    return AVATAR_COLORS[color_index]


def get_avatar_font(font_size: int = AVATAR_FONT_SIZE):
    """
    Получение шрифта для аватара.

    Для pillow==11.3.0 параметр size поддерживается напрямую.
    """
    try:
        return ImageFont.truetype(AVATAR_FONT_NAME, font_size)
    except (OSError, IOError):
        # Если шрифт не найден, используем стандартный с нужным размером
        return ImageFont.load_default(size=font_size)


def build_avatar_file(
        name: str,
        email: str,
        size: int = AVATAR_SIZE) -> ContentFile:
    """
    Генерация avatar-файла на основе имени и email.

    Args:
        name: Имя пользователя
        email: Email пользователя
        size: Размер аватара в пикселях (по умолчанию AVATAR_SIZE)

    Returns:
        ContentFile: Сгенерированный файл аватара
    """
    bg_color = pick_avatar_background(email or name)

    avatar_image = Image.new("RGB", (size, size), bg_color)
    canvas = ImageDraw.Draw(avatar_image)

    first_letter = (name[:1] if name else DEFAULT_AVATAR_LETTER).upper()

    font = get_avatar_font(AVATAR_FONT_SIZE)

    # Центрируем текст (для pillow==11.3.0 используем textbbox)
    bbox = canvas.textbbox((0, 0), first_letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_x = (size - text_width) / 2
    text_y = (size - text_height) / 2

    canvas.text((text_x, text_y), first_letter,
                fill=AVATAR_TEXT_COLOR, font=font)

    binary_stream = BytesIO()
    avatar_image.save(binary_stream, format="PNG")

    # Создаём безопасное имя файла
    safe_email = email.replace("@", "_").replace(".", "_")
    file_name = f"avatar_{safe_email}.png"

    return ContentFile(binary_stream.getvalue(), name=file_name)


def build_avatar_custom_size(name: str, email: str, size: int) -> ContentFile:
    """
    Генерация аватара с кастомным размером.

    Args:
        name: Имя пользователя
        email: Email пользователя
        size: Размер аватара в пикселях

    Returns:
        ContentFile: Сгенерированный файл аватара
    """
    return build_avatar_file(name, email, size)

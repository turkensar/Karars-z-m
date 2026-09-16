from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

RESERVED_USERNAMES = {"admin", "kararsizim", "destek", "yonetim", "root", "api"}

username_validator = RegexValidator(
    regex=r"^[a-z0-9_.]+$",
    message="Kullanıcı adı sadece küçük harf, rakam, alt çizgi ve nokta içerebilir.",
)


class User(AbstractUser):
    username = models.CharField(
        max_length=24,
        unique=True,
        validators=[username_validator],
        help_text="3-24 karakter, sadece küçük harf, rakam, _ ve . içerebilir.",
    )
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def normalize_username(cls, username):
        username = super().normalize_username(username)
        return username.lower() if username else username

    def clean(self):
        super().clean()
        if len(self.username) < 3:
            raise ValidationError({"username": "Kullanıcı adı en az 3 karakter olmalı."})
        if self.username.startswith(".") or self.username.endswith("."):
            raise ValidationError({"username": "Kullanıcı adı nokta ile başlayamaz veya bitemez."})
        if self.username in RESERVED_USERNAMES:
            raise ValidationError({"username": "Bu kullanıcı adı kullanılamaz."})

    def save(self, *args, **kwargs):
        self.username = self.normalize_username(self.username)
        super().save(*args, **kwargs)

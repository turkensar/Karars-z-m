import uuid

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models

from .constants import CATEGORY_CHOICES


class Poll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="polls"
    )
    question = models.CharField(max_length=160, validators=[MinLengthValidator(10)])
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, null=True, blank=True
    )
    total_votes = models.PositiveIntegerField(default=0, editable=False)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.question


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=60)
    position = models.PositiveSmallIntegerField()
    vote_count = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]
        unique_together = ("poll", "position")

    def __str__(self):
        return self.text


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    voter_key = models.CharField(max_length=64, db_index=True, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["poll", "user"],
                condition=models.Q(user__isnull=False),
                name="unique_vote_per_user_per_poll",
            ),
            models.UniqueConstraint(
                fields=["poll", "voter_key"],
                condition=models.Q(user__isnull=True),
                name="unique_vote_per_anon_per_poll",
            ),
        ]

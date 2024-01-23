from django.db import models
from django.core.validators import RegexValidator


class Group(models.Model):
    code_name_validator = RegexValidator(
        regex=r"^[a-zA-Z0-9\-_\.]{1,100}$",
        message="Code Name must be a valid Unicode string with length < 100",
    )
    TYPE_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
        ("custom", "Custom"),
    ]
    name = models.CharField(max_length=255)
    code_name = models.CharField(
        unique=True,
        max_length=255,
        validators=[code_name_validator],
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="public")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def subscription_count(self):
        return self.subscription_set.filter(status="subscribe").count()

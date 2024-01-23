from django.db import models
from channels.db import database_sync_to_async
from django.utils import timezone


class User(models.Model):
    user_id = models.CharField(max_length=255)
    user_notification_id = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    user_agent = models.CharField(max_length=500)
    read_notifications = models.ManyToManyField(
        "Notification", through="UserReadNotification", null=True, blank=True
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Notification User"
        verbose_name_plural = "Notification Users"

    def __str__(self):
        return self.user_notification_id

    @classmethod
    @database_sync_to_async
    def create_user(cls, channel_name, user_notification_id, headers):
        user_agent = None
        for name, value in headers:
            if name == b"user-agent":
                user_agent = value.decode("utf-8")
                break
        return cls.objects.create(
            user_id=channel_name,
            user_notification_id=user_notification_id,
            user_agent=user_agent,
        )

    @classmethod
    @database_sync_to_async
    def get_user(cls, user_notification_id):
        return cls.objects.filter(
            user_notification_id=user_notification_id, status=True
        ).last()

    @classmethod
    @database_sync_to_async
    def delete_user(cls, user_channel_name):
        return cls.objects.filter(user_id=user_channel_name).update(
            status=False, left_at=timezone.now()
        )


class UserReadNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey("Notification", on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "notification"]

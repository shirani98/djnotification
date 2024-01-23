from django.db import models
from channels.db import database_sync_to_async
from django.utils import timezone
from .group import Group
from .user import User


class Subscription(models.Model):
    EVENT_CHOICES = [
        ("subscribe", "Subscribe"),
        ("unsubscribe", "UnSubscribe"),
        ("left", "Left"),
    ]
    user = models.ForeignKey("notification.User", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=EVENT_CHOICES, default="subscribe")
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.group} - {self.status}"

    @classmethod
    @database_sync_to_async
    def create_subscription(cls, channel_name, group_name):
        try:
            user = User.objects.get(user_id=channel_name)
            group = Group.objects.get(code_name=group_name)
            if cls.objects.filter(user=user, group=group, status="subscribe").exists():
                return False
            cls.objects.create(user=user, group=group)
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    @database_sync_to_async
    def left_user_groups(cls, channel_name):
        return Subscription.objects.filter(
            user__user_id=channel_name, status="subscribe"
        ).update(status="left", left_at=timezone.now())

    @classmethod
    @database_sync_to_async
    def unsubscribe_user_group(cls, channel_name, group_name):
        try:
            group = Group.objects.get(code_name=group_name)
            updated_groups = cls.objects.filter(
                user__user_id=channel_name, group=group, status="subscribe"
            ).update(status="unsubscribe", left_at=timezone.now())
            if updated_groups > 0:
                return True
            return False
        except Exception as e:
            print(e)
            return False

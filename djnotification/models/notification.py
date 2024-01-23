from django.db import models
from channels.db import database_sync_to_async
from .group import Group
from .subscription import Subscription
from django.apps import apps
from datetime import datetime
from djnotification.tasks import send_notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone


class Notification(models.Model):
    TYPE_CHOICES = [
        ("card", "Card"),
        ("modal", "Modal"),
        ("image_only", "Image Only"),
        ("top_banner", "Top Banner"),
    ]
    message_layout = models.CharField(
        max_length=15, choices=TYPE_CHOICES, default="card"
    )
    user_id = models.CharField(max_length=255, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    message_title = models.CharField(max_length=255)
    body = models.CharField(max_length=255, null=True, blank=True)
    image = models.URLField(max_length=200, null=True, blank=True)
    portrait_image = models.URLField(max_length=200, null=True, blank=True)
    landscape_image = models.URLField(max_length=200, null=True, blank=True)
    extra_data = models.JSONField(null=True, blank=True)
    time_to_send = models.DateTimeField(null=True, blank=True)
    background_color = models.CharField(max_length=7, blank=True, null=True)
    text_color = models.CharField(max_length=7, blank=True, null=True)
    action = models.URLField(max_length=200, null=True, blank=True)
    button_text = models.CharField(max_length=255, null=True, blank=True)
    button_text_color = models.CharField(max_length=7, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(
        default=timezone.datetime.max, blank=True, null=True
    )
    sent_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        if self.group:
            return f"{self.group} - {self.created_at}"
        return f"{self.user_id} - {self.created_at}"

    @classmethod
    def create_notification(cls, notification_data):
        group_name = str
        if notification_data.get("group"):
            group_name = notification_data.get("group")

        if notification_data.get("user_id"):
            group_name = f"private_{notification_data['user_id']}"

        if notification_data.get("time_to_send"):
            notification_data["time_to_send"] = datetime.utcfromtimestamp(
                notification_data.get("time_to_send")
            )
        if group_name.startswith("private"):
            notification_data["user_id"] = group_name[8:]
            notification_obj = cls.objects.create(**notification_data)
        else:
            group = Group.objects.get(code_name=notification_data["group"])
            notification_data["group"] = group
            notification_obj = cls.objects.create(**notification_data)
            notification_data["group"] = group.code_name
        return notification_obj, notification_data, group_name

    @classmethod
    @database_sync_to_async
    def read_message(cls, user_channel_name, notification_id):
        try:
            User_Model = apps.get_model(app_label="notification", model_name="User")
            user = User_Model.objects.filter(
                user_id=user_channel_name, status=True
            ).last()
            notification = cls.objects.get(id=notification_id)
            if (
                notification.user_id is not None
                and user.user_notification_id != notification.user_id
            ):
                return False

            if (
                notification.group is not None
                and not Subscription.objects.filter(
                    user=user, group=notification.group, status="subscribe"
                ).exists()
            ):
                return False
            user.read_notifications.add(notification)
            user.save()
            return True

        except Exception:
            return False

    def send_notification(self, specific_group_name=None, update_sent_time=True):
        if self.group:
            group_name = self.group.code_name
            notification_data = {
                "id": self.id,
                "message_layout": self.message_layout,
                "group": group_name,
                "message_title": self.message_title,
                "body": self.body,
                "image": self.image,
                "extra_data": self.extra_data,
                "portrait_image": self.portrait_image,
                "landscape_image": self.landscape_image,
                "background_color": self.background_color,
                "text_color": self.text_color,
                "action": self.action,
                "button_text": self.button_text,
                "button_text_color": self.button_text_color,
            }

        elif self.user_id:
            group_name = f"private_{self.user_id}"
            notification_data = {
                "id": self.id,
                "message_layout": self.message_layout,
                "user_id": self.user_id,
                "message_title": self.message_title,
                "body": self.body,
                "image": self.image,
                "extra_data": self.extra_data,
                "portrait_image": self.portrait_image,
                "landscape_image": self.landscape_image,
                "background_color": self.background_color,
                "text_color": self.text_color,
                "action": self.action,
                "button_text": self.button_text,
                "button_text_color": self.button_text_color,
            }
        if specific_group_name:
            group_name = specific_group_name
        if self.time_to_send:
            send_notification.apply_async(
                args=[group_name, notification_data],
                eta=self.time_to_send,
            )
        else:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                group_name,
                {"type": "notification_message", "message": notification_data},
            )
        if update_sent_time:
            self.sent_at = timezone.now()
            self.save()

    @classmethod
    @database_sync_to_async
    def send_lost_notifications(cls, user_id, group_name):
        try:
            if group_name.startswith("private_"):
                User_Model = apps.get_model(app_label="notification", model_name="User")
                pv_notifications = Notification.objects.none()
                general_notifications = Notification.objects.none()
                try:
                    user_left_time = (
                        User_Model.objects.filter(
                            user_notification_id=user_id, status=False
                        )
                        .last()
                        .left_at
                    )
                    user_enter_time = (
                        User_Model.objects.filter(
                            user_notification_id=user_id, status=True
                        )
                        .last()
                        .joined_at
                    )
                    pv_notifications = Notification.objects.filter(
                        sent_at__gt=user_left_time,
                        sent_at__lt=user_enter_time,
                        expired_at__gt=timezone.now(),
                        user_id=user_id,
                    )
                except Exception:
                    pass
                try:
                    general_group = Group.objects.get_or_create(
                        name="General", code_name="general"
                    )
                    general_notifications = Notification.objects.filter(
                        sent_at__gt=user_left_time,
                        sent_at__lt=user_enter_time,
                        expired_at__gt=timezone.now(),
                        group=general_group[0],
                    )
                except Exception:
                    pass
                notifications = pv_notifications | general_notifications
            else:
                groups_left_time = (
                    Subscription.objects.filter(
                        user__user_notification_id=user_id,
                        group__code_name=group_name,
                        status__in=["unsubscribe", "left"],
                    )
                    .last()
                    .left_at
                )
                groups_enter_time = (
                    Subscription.objects.filter(
                        user__user_notification_id=user_id,
                        group__code_name=group_name,
                        status="subscribe",
                    )
                    .last()
                    .joined_at
                )
                notifications = Notification.objects.filter(
                    sent_at__gt=groups_left_time,
                    sent_at__lt=groups_enter_time,
                    expired_at__gt=timezone.now(),
                    group__code_name=group_name,
                )

            for notification in notifications:
                notification.send_notification(
                    f"private_{user_id}", update_sent_time=False
                )
            return True
        except Exception as e:
            print(e)
            return False

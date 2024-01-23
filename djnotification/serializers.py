from rest_framework import serializers
from djnotification.models import Group


class BaseNotification(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    message_layout = serializers.CharField(max_length=30)
    group = serializers.CharField(max_length=255, required=False)
    user_id = serializers.CharField(max_length=255, required=False)
    extra_data = serializers.JSONField(required=False)

    def validate(self, data):
        group = data.get("group")
        user_id = data.get("user_id")

        if not group and not user_id:
            raise serializers.ValidationError(
                "Either 'group' or 'user_id' should be provided."
            )

        if group and user_id:
            raise serializers.ValidationError(
                "Provide just one of 'group' or 'user_id' item."
            )

        if group and not Group.objects.filter(code_name=group).exists():
            raise serializers.ValidationError(f"Group '{group}' does not exist.")

        return data


class NotificationSerializer(BaseNotification):
    body = serializers.CharField(max_length=255, required=False)
    image = serializers.URLField(max_length=200, required=False)
    portrait_image = serializers.URLField(max_length=200, required=False)
    landscape_image = serializers.URLField(max_length=200, required=False)
    background_color = serializers.CharField(max_length=7, required=False)
    text_color = serializers.CharField(max_length=7, required=False)
    action = serializers.URLField(max_length=200, required=False)
    button_text = serializers.CharField(max_length=255, required=False)
    button_text_color = serializers.CharField(max_length=7, required=False)
    created_at = serializers.DateTimeField(read_only=True)


class CardNotificationSerializer(BaseNotification):
    background_color = serializers.CharField(max_length=7)
    text_color = serializers.CharField(max_length=7)
    message_title = serializers.CharField(max_length=255)
    body = serializers.CharField(max_length=255, required=False)
    portrait_image = serializers.URLField(max_length=200)
    landscape_image = serializers.URLField(max_length=200)
    button_text = serializers.CharField(max_length=255)
    button_text_color = serializers.CharField(max_length=7)
    time_to_send = serializers.IntegerField(required=False)


class ImageOnlyNotificationSerializer(BaseNotification):
    image = serializers.URLField(max_length=200)
    action = serializers.URLField(max_length=200, required=False)
    time_to_send = serializers.IntegerField(required=False)


class ModalNotificationSerializer(BaseNotification):
    background_color = serializers.CharField(max_length=7)
    text_color = serializers.CharField(max_length=7)
    message_title = serializers.CharField(max_length=255)
    body = serializers.CharField(max_length=255, required=False)
    image = serializers.URLField(max_length=200, required=False)
    button_text = serializers.CharField(max_length=255, required=False)
    time_to_send = serializers.IntegerField(required=False)


class TopBannerNotificationSerializer(BaseNotification):
    background_color = serializers.CharField(max_length=7)
    text_color = serializers.CharField(max_length=7)
    message_title = serializers.CharField(max_length=255)
    body = serializers.CharField(max_length=255, required=False)
    image = serializers.URLField(max_length=200, required=False)
    action = serializers.CharField(max_length=255, required=False)
    time_to_send = serializers.IntegerField(required=False)

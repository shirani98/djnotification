from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@shared_task
def send_notification(group_name, notification_data):
    if notification_data.get("time_to_send"):
        notification_data.pop("time_to_send")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {"type": "notification_message", "message": notification_data},
    )

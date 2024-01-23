from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from djnotification.models import Subscription, Notification, User


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_notification_id = self.scope["url_route"]["kwargs"]["user_id"]
        await self.channel_layer.group_add(
            f"private_{self.user_notification_id}", self.channel_name
        )
        await self.channel_layer.group_add("general", self.channel_name)
        self.groups = ["general", f"private_{self.user_notification_id}"]
        await User.create_user(
            self.channel_name, self.user_notification_id, self.scope["headers"]
        )
        await Notification.send_lost_notifications(
            self.user_notification_id, f"private_{self.user_notification_id}"
        )
        await self.accept()

    async def disconnect(self, close_code=None):
        if self.channel_layer:
            await User.delete_user(self.channel_name)
            await Subscription.left_user_groups(self.channel_name)
            for group_name in self.groups:
                await self.channel_layer.group_discard(group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        notification_type = text_data_json["action"]

        if notification_type.startswith("subscribe_") and self.channel_layer:
            group_name = notification_type[10:]

            status = await Subscription.create_subscription(
                self.channel_name, group_name
            )
            await Notification.send_lost_notifications(
                self.user_notification_id, group_name
            )
            if status is True:
                await self.channel_layer.group_add(group_name, self.channel_name)
                self.groups.append(group_name)
            await self.status_response(status)

        elif notification_type.startswith("unsubscribe_") and self.channel_layer:
            group_name = notification_type[12:]
            status = await Subscription.unsubscribe_user_group(
                self.channel_name, group_name
            )
            if status is True:
                await self.channel_layer.group_discard(group_name, self.channel_name)
                self.groups.remove(group_name)
            await self.status_response(status)

        elif notification_type == "read_notification" and self.channel_layer:
            status = await Notification.read_message(
                self.channel_name, text_data_json["notification_id"]
            )
            await self.status_response(status)

    async def notification_message(self, event):
        await self.send(json.dumps({"type": "notification", "data": event["message"]}))

    async def status_response(self, status):
        if status == True:
            await self.send(json.dumps({"type": "notification", "status": True}))
        else:
            await self.send(json.dumps({"type": "notification", "status": False}))

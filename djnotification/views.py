from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    NotificationSerializer,
    CardNotificationSerializer,
    ImageOnlyNotificationSerializer,
    ModalNotificationSerializer,
    TopBannerNotificationSerializer,
)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from djnotification.models import Notification, Subscription, User
from django.db.models import Q
from djnotification.tasks import send_notification
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone


class NotificationPagination(PageNumberPagination):
    page_size = 10


class NotificationAPIView(APIView):
    pagination_class = NotificationPagination

    def get_serializer_class(self, data):
        if data.get("message_layout") == "card":
            return CardNotificationSerializer
        elif data.get("message_layout") == "image_only":
            return ImageOnlyNotificationSerializer
        elif data.get("message_layout") == "modal":
            return ModalNotificationSerializer
        elif data.get("message_layout") == "top_banner":
            return TopBannerNotificationSerializer
        else:
            return Response(
                {"error": "message_layout not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request):
        serializer_class = self.get_serializer_class(data=request.data)
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        notif, data, group_name = Notification.create_notification(
            serializer.validated_data
        )
        data["notification_id"] = notif.id
        channel_layer = get_channel_layer()
        if notif.time_to_send:
            send_notification.apply_async(
                args=[group_name, data], eta=notif.time_to_send
            )
        else:
            async_to_sync(channel_layer.group_send)(
                group_name, {"type": "notification_message", "message": data}
            )
        notif.sent_at = timezone.now()
        notif.save()
        return Response(
            {"message": "Notification sent successfully", "id": notif.id},
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        try:
            user_notification_id = request.query_params.get("id")
            if user_notification_id:
                user_id = User.objects.filter(
                    user_notification_id=user_notification_id, status=True
                ).values("id")
                user_group = Subscription.objects.filter(
                    user__id__in=user_id, status="subscribe"
                ).values_list("group")

                notifications = Notification.objects.filter(
                    Q(group__in=user_group) | Q(user_id=user_notification_id)
                )
            else:
                notifications = Notification.objects.all()
            paginator = NotificationPagination()
            result_page = paginator.paginate_queryset(notifications, request)
            serializer = NotificationSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception:
            return Response(
                {"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND
            )

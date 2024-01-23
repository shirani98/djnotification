from django.contrib import admin
from .models import Subscription, Group, Notification, User, UserReadNotification
from django.core.exceptions import ValidationError
from django import forms


class SubscriptionAdmin(admin.ModelAdmin):
    readonly_fields = ("joined_at", "left_at")
    list_display = ("user", "group", "status", "joined_at")


admin.site.register(Subscription, SubscriptionAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "code_name", "created_at", "subscription_count"]

    def clean(self):
        code_name = self.code_name

        if (
            not code_name.isascii()
            or len(code_name) >= 100
            or not code_name.isprintable()
        ):
            raise ValidationError(
                "Group name must be a valid unicode string with length < 100 containing only ASCII alphanumerics, hyphens, underscores, or periods."
            )

        return code_name


admin.site.register(Group, GroupAdmin)


class ReadNotificationSection(admin.TabularInline):
    model = UserReadNotification
    extra = 1


class UserAdmin(admin.ModelAdmin):
    list_display = ["user_notification_id", "status", "joined_at", "left_at"]
    inlines = (ReadNotificationSection,)


admin.site.register(User, UserAdmin)


class NotificationAdminForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        user_id = cleaned_data.get("user_id")
        group = cleaned_data.get("group")

        if user_id and group:
            self.add_error("user_id", "Cannot specify both user_id and group.")
            self.add_error("group", "Cannot specify both user_id and group.")


class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm
    list_display = [
        "id",
        "message_layout",
        "group",
        "user_id",
        "message_title",
        "sent_at",
    ]
    actions = ["send_notification"]

    def send_notification(self, request, queryset):
        for notification in queryset:
            notification.send_notification()
        self.message_user(request, f"Notifications sent for {queryset.count()} items.")

    send_notification.short_description = "Send notification to selected items"


admin.site.register(Notification, NotificationAdmin)

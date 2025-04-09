import uuid

from django.conf import settings
from django.db import models


class Call(models.Model):
    VIDEO = "video"
    VOICE = "voice"
    CALL_TYPE_CHOICES = [
        (VIDEO, "Video"),
        (VOICE, "Voice"),
    ]
    PENDING = "pending"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    CALL_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ONGOING, "Ongoing"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    def generate_channel_id():
        return uuid.uuid4().hex[:8]

    channel_id = models.CharField(
        max_length=8, default=generate_channel_id, editable=False, unique=True
    )
    call_type = models.CharField(max_length=5, choices=CALL_TYPE_CHOICES, default=VIDEO)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default="ongoing")
    status = models.CharField(
        max_length=20, choices=CALL_STATUS_CHOICES, default=PENDING
    )

    def __str__(self):
        return f"Call {self.call_id} ({self.call_type})"


class CallUser(models.Model):
    HOST = "host"
    AUDIENCE = "audience"
    ROLE_CHOICES = [
        (HOST, "Host"),
        (AUDIENCE, "Audience"),
    ]

    call = models.ForeignKey(Call, related_name="users", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="calls", on_delete=models.CASCADE
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=AUDIENCE)

    def __str__(self):
        return f"User {self.user.username} in Call {self.call.call_id} as {self.role}"


class MediaControl(models.Model):
    call = models.ForeignKey(
        Call, related_name="media_controls", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="media_controls",
        on_delete=models.CASCADE,
    )
    is_muted = models.BooleanField(default=False)
    is_camera_off = models.BooleanField(default=False)

    def __str__(self):
        return f"MediaControl for User {self.user.username} in Call {self.call.call_id}"


class ScreenShare(models.Model):
    call = models.ForeignKey(
        Call, related_name="screen_shares", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="screen_shares", on_delete=models.CASCADE
    )
    is_sharing = models.BooleanField(default=False)

    def __str__(self):
        return f"ScreenShare by User {self.user.username} in Call {self.call.call_id}"


class Message(models.Model):
    call = models.ForeignKey(Call, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="sent_messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in Call {self.call.call_id} at {self.timestamp}"


class AgoraToken(models.Model):
    call = models.ForeignKey(Call, related_name="tokens", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="tokens", on_delete=models.CASCADE
    )
    token = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField()  # Expiry time for the token validity

    def __str__(self):
        return f"Token for User {self.user.username} in Call {self.call.call_id}"

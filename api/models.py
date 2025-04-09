import uuid
from django.db import models
from django.conf import settings
from datetime import datetime
import time
import os
import hmac
import hashlib
import base64
import requests

AGORA_APP_ID = os.getenv("AGORA_APP_ID")
AGORA_APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE")
AGORA_REST_API_URL = "https://api.agora.io/v1/apps/{}/token".format(AGORA_APP_ID)


class Call(models.Model):
    VIDEO = "video"
    VOICE = "voice"
    CALL_TYPE_CHOICES = [
        (VIDEO, "Video"),
        (VOICE, "Voice"),
    ]

    call_id = models.UUIDField(
        default=uuid.uuid4.hex[:8], editable=False, unique=True
    )  # Generate UUID for call_id
    call_type = models.CharField(max_length=5, choices=CALL_TYPE_CHOICES, default=VIDEO)
    channel_id = models.CharField(max_length=100)  # Agora channel ID for the call
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default="ongoing")

    def __str__(self):
        return f"Call {self.call_id} ({self.call_type})"


class CallUser(models.Model):
    call = models.ForeignKey(Call, related_name="users", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="calls", on_delete=models.CASCADE
    )
    role = models.CharField(
        max_length=50, choices=[("host", "Host"), ("audience", "Audience")]
    )

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


def generate_agora_token(
    channel_name, user_id, role, expiry_duration=31104000
):  # 52 weeks = 31,104,000 seconds
    """
    Generate Agora token using Agora REST API.
    Args:
        channel_name: The name of the Agora channel.
        user_id: The user ID for whom the token is generated.
        role: Role of the user ('host' or 'audience').
        expiry_duration: Expiry duration in seconds (default is 52 weeks).
    Returns:
        str: The generated Agora token.
    """
    # Set the expiration timestamp
    expiration_timestamp = int(time.time() + expiry_duration)

    # Set the token parameters
    token_params = {
        "channelName": channel_name,
        "userAccount": user_id,
        "role": role,
        "expireAt": expiration_timestamp,
    }

    # Sign the token request with HMAC-SHA256
    secret = AGORA_APP_CERTIFICATE
    data = f"{channel_name}{user_id}{role}{expiration_timestamp}"
    signature = hmac.new(
        secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
    ).digest()
    token = base64.b64encode(signature).decode("utf-8")

    # Send the request to Agora's API
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    response = requests.post(AGORA_REST_API_URL, json=token_params, headers=headers)

    if response.status_code == 200:
        # Return the token from the response
        return response.json().get("token")
    else:
        raise Exception(
            f"Failed to generate token: {response.status_code}, {response.text}"
        )

    def is_expired(self):
        """
        Checks if the token has expired.
        Returns:
            True if expired, False otherwise.
        """
        return datetime.now() > self.expiry_time

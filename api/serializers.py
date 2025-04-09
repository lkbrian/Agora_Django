from rest_framework import serializers
from .models import Call, CallUser, MediaControl, ScreenShare, Message, AgoraToken
from django.contrib.auth import get_user_model


# Serializer for the Call model
class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = [
            "call_id",
            "call_type",
            "channel_id",
            "start_time",
            "end_time",
            "status",
        ]


# Serializer for the CallUser model
class CallUserSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=get_user_model().objects.all()
    )

    class Meta:
        model = CallUser
        fields = ["call", "user", "role"]


# Serializer for the MediaControl model
class MediaControlSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=get_user_model().objects.all()
    )

    class Meta:
        model = MediaControl
        fields = ["call", "user", "is_muted", "is_camera_off"]


# Serializer for the ScreenShare model
class ScreenShareSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=get_user_model().objects.all()
    )

    class Meta:
        model = ScreenShare
        fields = ["call", "user", "is_sharing"]


# Serializer for the Message model
class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(
        slug_field="username", queryset=get_user_model().objects.all()
    )

    class Meta:
        model = Message
        fields = ["call", "sender", "content", "timestamp"]


# Serializer for the AgoraToken model
class AgoraTokenSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=get_user_model().objects.all()
    )
    call = serializers.PrimaryKeyRelatedField(queryset=Call.objects.all())

    class Meta:
        model = AgoraToken
        fields = ["call", "user", "token", "generated_at", "expiry_time"]

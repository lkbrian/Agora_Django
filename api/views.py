from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from .models import Call, CallUser, AgoraToken
from .utils import (
    generate_agora_token,
)


class RegisterUserView(generics.CreateAPIView):
    def post(self, request):
        data = request.data
        try:
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            if not username or not email or not password:
                return Response(
                    {"error": "Username, email, and password are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if the user already exists
            User = get_user_model()
            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "User with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create a new user
            user = User.objects.create(
                username=username, email=email, password=make_password(password)
            )

            return Response(
                {"message": "User created successfully."},
                status=status.HTTP_201_CREATED,
                user=user,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    def post(self, request):
        data = request.data
        try:
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return Response(
                    {"error": "Email and password are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            User = get_user_model()
            user = User.objects.filter(email=email).first()

            if not user or not check_password(password, user.password):
                return Response(
                    {"error": "Invalid credentials."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": "Login successful."}, user=user, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Call Creation View (Initiate Call)
class CreateCallView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            call_type = request.data.get("call_type", "video")

            call = Call.objects.create(
                call_type=call_type,
                status=Call.PENDING,
            )

            # Associate the user as the host
            CallUser.objects.create(call=call, user=user, role=CallUser.HOST)

            return Response(
                {
                    "message": "Call created successfully.",
                    "channel_id": call.channel_id,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RtcTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            uid = int(request.data.get("uid"))
            channel_id = request.data.get("channel_id")
            role = request.data.get("role")

            if role not in ["host", "audience"]:
                return Response(
                    {"error": "Invalid role, must be 'host' or 'audience'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                call = Call.objects.get(channel_id=channel_id)
            except Call.DoesNotExist:
                return Response(
                    {"error": "Call with the provided channel_id does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                call_user = CallUser.objects.get(call=call, user=request.user)
                print(call_user)
            except CallUser.DoesNotExist:
                return Response(
                    {"error": "User is not part of this call."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Generate the Agora token
            token = generate_agora_token(uid, channel_id, role)

            # Calculate the expiry time (for example, 1 hour from now)
            expiry_time = datetime.utcnow()

            # Store the token in the AgoraToken model
            AgoraToken.objects.create(
                call=call, user=request.user, token=token, expiry_time=expiry_time
            )

            return Response({"token": token, "code": 200}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class JoinCallView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            channel_id = request.data.get("channel_id")
            role = request.data.get("role")

            if role not in ["host", "audience"]:
                return Response(
                    {"error": "Invalid role, must be 'host' or 'audience'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                call = Call.objects.get(channel_id=channel_id)
            except Call.DoesNotExist:
                return Response(
                    {"error": "Call with the provided channel_id does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                call_user = CallUser.objects.get(call=call, user=user)
                print(call_user)
            except CallUser.DoesNotExist:
                if role == "host":
                    CallUser.objects.create(call=call, user=user, role=CallUser.HOST)
                else:
                    CallUser.objects.create(
                        call=call, user=user, role=CallUser.AUDIENCE
                    )

            uid = user.id
            token = generate_agora_token(uid, channel_id, role)

            AgoraToken.objects.create(call=call, user=user, token=token)

            return Response({"token": token, "code": 200}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgoraTokenListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            tokens = AgoraToken.objects.filter(user=request.user)
            token_data = [
                {
                    "call_id": token.call.channel_id,
                    "token": token.token,
                    "generated_at": token.generated_at,
                    "expiry_time": token.expiry_time,
                }
                for token in tokens
            ]
            return Response({"tokens": token_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

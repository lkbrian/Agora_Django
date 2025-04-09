from django.urls import path
from .views import (
    RegisterUserView,
    LoginUserView,
    CreateCallView,
    RtcTokenView,
    AgoraTokenListView,
    JoinCallView,
)

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("create-call/", CreateCallView.as_view(), name="create-call"),
    path("generate-token/", RtcTokenView.as_view(), name="generate-token"),
    path("get-tokens/", AgoraTokenListView.as_view(), name="get-tokens"),
    path(
        "join-call/", JoinCallView.as_view(), name="join-call"
    ),  # Add this line for the Join Call view
]

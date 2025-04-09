from django.contrib import admin
from api.models import AgoraToken, Call, CallUser, MediaControl, Message, ScreenShare

admin.site.register(Call)
admin.site.register(CallUser)
admin.site.register(Message)
admin.site.register(AgoraToken)
admin.site.register(MediaControl)
admin.site.register(ScreenShare)

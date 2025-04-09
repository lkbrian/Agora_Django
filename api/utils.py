import os
from datetime import datetime, timedelta
from agora_token_builder import RtcTokenBuilder

AGORA_APP_ID = os.getenv("AGORA_APP_ID")
AGORA_APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE")


def generate_agora_token(uid, channel_name, role):
    """
    Generates an Agora token for a given user (`uid`) and channel (`channel_name`)
    with a specified role (`host` or `audience`).
    """
    role_enum = 1 if role == "host" else 2
    expiration_time = datetime.utcnow() + timedelta(
        weeks=52
    )  # Token expiry in 52 weeks
    expire_timestamp = int(expiration_time.timestamp())

    token = RtcTokenBuilder.build_token_with_uid(
        AGORA_APP_ID,
        AGORA_APP_CERTIFICATE,
        channel_name,
        uid,
        role_enum,
        expire_timestamp,
    )

    return token

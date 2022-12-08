from base64 import b64encode
from collections import OrderedDict
from hashlib import sha256
from hmac import HMAC
from urllib.parse import urlencode

from app.SberCatClient import SberCatClient
from app.config import settings


def sign_params(user_id: str) -> str:
    """Check VK Apps signature"""
    query = {
        "vk_user_id": user_id,
        "vk_app_id": "51443865",
        "vk_is_app_user": "1",
        "vk_are_notifications_enabled": "0",
        "vk_language": "ru",
        "vk_access_token_settings": "",
        "vk_platform": "mobile_web",
    }
    vk_subset = OrderedDict(sorted(x for x in query.items() if x[0][:3] == "vk_"))
    hash_code = b64encode(
        HMAC(settings.sbercat_secret.encode(), urlencode(vk_subset, doseq=True).encode(), sha256).digest()
        )
    sign = hash_code.decode('utf-8')[:-1].replace('+', '-').replace('/', '_')
    return sign


async def cats_to_website_repr(client: SberCatClient) -> dict:
    return {}

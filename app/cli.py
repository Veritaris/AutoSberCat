import asyncio

from app.SberCatClient import SberCatClient
from app.config import settings

if __name__ == "__main__":
    client = SberCatClient(token=settings.sbercat_app_token, user_id=settings.user_id)
    asyncio.run(client.renew_all_cats())

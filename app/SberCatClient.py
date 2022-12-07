import asyncio
import httpx
import requests

from app.config import settings
from dataclasses import dataclass


@dataclass
class act:
    url: str
    method: str = "GET"


# {"to":"personal","amount":2}
# {"to":"business","amount":2}

class SberCatClient:
    __app_endpoint: str = settings.sbercat_app_endpoint
    __known_endpoints = {
        "fetch_coins": act("game/take_coins", "POST"),
        "fetch": act("game/take_coins", "POST"),
        "charge_for_coins": act("game/charge", "POST"),
        "transfer_to_personal": act("user/transfer_coins", "POST"),
        "charge": act("game/charge", "POST"),
        "get_work_info": act("game/get"),
        "get_employee_info": act("staff/info"),
    }
    worker_id: int
    current_action: str = ""
    method: str = "POST"
    token: str
    asynchronous: bool = True

    def __init__(self, token: str, worker_id: int = None):
        self.worker_id = 0
        self.token = token

    def __getattr__(self, item):
        if not (action := self.__known_endpoints.get(item)):
            raise AttributeError(f"Unknown action {item}")

        self.current_action = action.url
        self.method = action.method

        print(f"item: {item}, action: {action}, method: {self.method}")

        if self.asynchronous:
            return self.__make_async_action

        return self.__make_sync_action

    def renew_all_cats_sync(self):
        self.set_sync()
        info: dict = self.get_work_info()
        employees = info["data"]["locations"][0]["employees"]
        employee_ids = [emp["type"] for emp in employees]

        for emp_id in employee_ids:
            self.worker_id = emp_id
            for i in range(5):
                result = self.fetch_coins()
                if result.get("status") == "ok" or result.get("code") == "employee_is_working":
                    break

                result = self.charge_for_coins()
                if result.get("status") == "ok" or result.get("code") == "employee_already_charged":
                    break

    async def renew_all_cats(self):
        info: dict = await self.get_work_info()
        employees = info["data"]["locations"][0]["employees"]
        employee_ids = [emp["type"] for emp in employees]

        for emp_id in employee_ids:
            self.worker_id = emp_id
            for i in range(5):
                result = await self.fetch_coins()
                if result.get("status") == "ok" or result.get("code") == "employee_is_working":
                    break

                result = await self.charge_for_coins()
                if result.get("status") == "ok" or result.get("code") == "employee_already_charged":
                    break

    def set_async(self):
        self.asynchronous = True

    def set_sync(self):
        self.asynchronous = False

    def __make_sync_action(self) -> dict:
        data = {
            "employee_type": f"{self.worker_id}"
        }
        session = requests.session()
        session.headers.update(
            {
                "Authorization": f"Bearer {self.token}"
            }
        )
        response = session.request(
            method=self.method,
            url=self.__app_endpoint.format(action=self.current_action),
            data=data
        )

        if response.status_code >= 400:
            print(f"Something went wrong! Error:\n{response.text}")
            try:
                return response.json()
            except Exception:
                return {"error": "yes"}

        print(f"Successfully fired action {self.current_action}! \nResponse: {response.text}")
        try:
            return response.json()
        except Exception:
            return {"error": "yes"}

    async def __make_async_action(self):
        data = {
            "employee_type": f"{self.worker_id}"
        }

        async with httpx.AsyncClient() as http_client:
            http_client.headers.update(
                {
                    "Authorization": f"Bearer {self.token}"
                }
            )
            response = await http_client.request(
                method=self.method,
                url=self.__app_endpoint.format(action=self.current_action),
                data=data
            )

            if response.status_code >= 400:
                print(f"Something went wrong! Error:\n{response.text}")
                try:
                    return response.json()
                except Exception:
                    return {"error": "yes"}

            print(f"Successfully fired action {self.current_action}! \nResponse: {response.text}")
            try:
                return response.json()
            except Exception:
                return {"error": "yes"}

    async def get_new_employee_info(self):
        pass


if __name__ == "__main__":
    client = SberCatClient(token=settings.sbercat_app_token)
    asyncio.run(client.renew_all_cats())

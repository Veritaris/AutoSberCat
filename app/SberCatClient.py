from dataclasses import dataclass
from typing import Optional

import httpx
from httpx import Response as AsyncResponse
from requests import Response as SyncResponse
from requests import Session

from app.config import settings
from app.i18n import i18n
from app.models import Employee, OfficeData


@dataclass
class point:
    url: str
    method: str = "GET"


class SberCatClient:
    __app_base_url: str = settings.sbercat_app_endpoint
    __known_endpoints = {
        "fetch_coins": point("game/take_coins", "POST"),
        "fetch": point("game/take_coins", "POST"),
        "charge_for_coins": point("game/charge", "POST"),
        "charge": point("game/charge", "POST"),
        "transfer_money": point("user/transfer_coins", "POST"),
        "get_work_info": point("game/get"),
        "get_new_employee_info": point("staff/info"),
    }
    __duration_boosters = {
        "coffee_point": 20,
        "plant": 10,
    }
    __money_boosters = {
        "coffee_point": 10,
        "plant": 5,
    }
    __action_type = {
        "cat": ("game/take_coins", "game/charge"),
        "money": ("user/transfer_coins",)
    }

    worker_id: int
    current_action: str = ""
    method: str = "POST"
    token: str
    asynchronous: bool = True

    def __init__(self, token: str):
        self.worker_id = 0
        self.token = token

    def __getattr__(self, item):
        if not (action := self.__known_endpoints.get(item)):
            raise AttributeError(f"Unknown action {item}")

        self.current_action = action.url
        self.method = action.method

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
        self.set_async()
        office_info: OfficeData = OfficeData(**(await self.get_work_info()).get("data"))
        locations = office_info.locations

        employee_ids = [
            emp.type
            for loc in office_info.locations
            for emp in loc.employees
        ]

        boosters = locations[0].permanent_boosters
        max_duration = 120
        max_money = 60

        for booster in boosters:
            max_duration += self.__duration_boosters.get(booster.type, 0)
            max_money += self.__money_boosters.get(booster.type, 0)

        for emp_id in employee_ids:
            self.worker_id = emp_id
            for i in range(5):
                result = await self.fetch_coins()
                if result.get("code") == "employee_is_working":
                    break
                if result.get("status") == "ok":
                    print(i18n("cat.coins_fetch", id=emp_id, amount=max_money))

                result = await self.charge_for_coins()
                if result.get("code") == "employee_already_charged":
                    break
                if result.get("status") == "ok":
                    print(i18n("cat.will_work_for", id=emp_id, duration=max_duration))

        if settings.do_money_autotransfer:
            await self.transfer_coins()

    def set_async(self):
        self.asynchronous = True

    def set_sync(self):
        self.asynchronous = False

    def __make_sync_action(self) -> dict:
        data = {
            "employee_type": f"{self.worker_id}"
        }

        with Session() as session:
            session.headers.update(
                {
                    "Authorization": f"Bearer {self.token}"
                }
            )
            response = session.request(
                method=self.method,
                url=self.__app_base_url.format(action=self.current_action),
                data=data
            )

        return self.process_response(response)

    async def __make_async_action(self) -> dict:
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
                url=self.__app_base_url.format(action=self.current_action),
                data=data
            )

        return self.process_response(response)

    def process_response(self, response: SyncResponse | AsyncResponse, *args, **kwargs) -> dict:
        if response.status_code >= 400:
            try:
                data = response.json()

                match (code := data.get("code")):
                    case "employee_is_working":
                        message = i18n("cat.already_working", id=self.worker_id)
                    case "employee_not_charged":
                        message = i18n("cat.not_charged", id=self.worker_id)
                    case "not_enough_money":
                        message = i18n("money.not_enough")
                    case _:
                        print(data)
                        print(f"{response.url}, {response.headers}")
                        message = i18n("unknown_error")

                print(message)
                return data
            except Exception:
                return {"error": "yes"}

        try:
            data = response.json()
        except Exception:
            return {"error": "yes"}

        cat = Employee(**data.get("employee"))
        if cat is not None and self.current_action == "game/charge":
            duration = cat.active_minutes_left
            cat_id = cat.type
            print(i18n("cat.will_work_for", id=cat_id, duration=duration))

        return data

    async def transfer_coins(self, to: str = "personal", amount: Optional[int] = None):
        if to == "personal":
            office_info: OfficeData = OfficeData(**(await self.get_work_info()).get("data"))
            money = office_info.business_coins
            money_to_pay = sum(
                [
                    emp.salary
                    for loc in office_info.locations
                    for emp in loc.employees
                    if emp.salary is not None
                ]
            )
            amount = money - money_to_pay
            if amount <= 0:
                print(i18n("money.not_enough_to_payday", payday=money_to_pay, money=money))
                return

        data = {
            "to": to,
            "amount": amount
        }

        async with httpx.AsyncClient() as http_client:
            http_client.headers.update(
                {
                    "Authorization": f"Bearer {self.token}"
                }
            )
            action = self.__known_endpoints.get("transfer_money")
            response = await http_client.request(
                method=action.method,
                url=self.__app_base_url.format(action=action.url),
                data=data
            )

        return self.process_response(response)

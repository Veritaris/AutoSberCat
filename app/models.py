from pydantic.main import BaseModel
from typing import Any, List, Optional


class SessionData(BaseModel):
    sbercat_token: str


class Employee(BaseModel):
    active_minutes_left: int
    max_daily_profit: int
    type: int = 0
    active_period: int
    can_take_coins: bool
    count_taps: int
    minutes_until_salary_payment: Optional[int] = 0
    profit: int
    workplace_id: Optional[int]
    salary: Optional[int] = 0


class Booster(BaseModel):
    type: str
    limit_exceeded: Any
    next_booster_price: Optional[int]


class Workplace(BaseModel):
    employee_type: int
    id: int


class Location(BaseModel):
    type: str
    employees: List[Employee]
    permanent_boosters: List[Booster]
    workplaces: List[Workplace]


class User(BaseModel):
    photo_100: str
    id: int | str
    total_coins: int
    last_name: str
    first_name: str


class OfficeData(BaseModel):
    business_coins: int
    pizza_available: bool
    locations: List[Location]
    temporary_boosters: List


class Rating(BaseModel):
    status: str
    data: List[User]
    current_user: User

    def get_current_user_rating(self):
        return self.get_rating(self.current_user.id)

    def get_rating(self, uid: int | str):
        return next((index for (index, user) in enumerate(self.data) if user.id == uid), None)

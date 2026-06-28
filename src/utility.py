from dataclasses import dataclass
from enum import Enum
from os import getenv
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(override=True)


class Test(BaseModel):
    test: str


class ProductItem(BaseModel):
    name: str
    quantity: int
    amount: int
    price: str


class Payment(BaseModel):
    sys: Optional[str] = None
    systranid: Optional[str] = None
    orderid: Optional[str] = None
    products: List[ProductItem]
    amount: Optional[str] = None


class FormData(BaseModel):
    Email: str
    Name: str
    Phone: Optional[str] = None
    input: Optional[str] = None
    Checkbox: Optional[str] = None
    Checkbox_2: Optional[str] = None
    Checkbox_3: Optional[str] = None
    payment: Payment
    formid: Optional[str] = None
    formname: Optional[str] = None


@dataclass
class ProcessUser:
    Email: str
    Name: str
    Course: str


class ProdamusAPIUtility(Enum):
    """Класс для организации работы с API XL prodamus

    Справочный центр по API: `https://app.xl.ru/api/public`
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{getenv("PRODAMUS_TOKEN")}",
    }
    scenarios = {"Тест": "KSuVSIeCr0OPXaOa9_P2aQ"}

    # post запросы
    create_user = "https://api.xl.ru/api/v1/crm/lead"
    scenario_run = "https://api.xl.ru/api/v1/scenario/run"
    get_users = "https://api.xl.ru/api/v1/crm/lead/table"

    # get запросы
    get_user = "https://api.xl.ru/api/v1/crm/lead/"  # {id}


@dataclass
class Course:
    tilda_name: str
    XL_name: str
    course_id: int


class Courses(Enum):
    """Класс для организации работы с курсами"""

    MINI = Course(tilda_name="Тариф Мини", XL_name="Пилочный для тебя", course_id=1)
    OPTIMUM = Course(
        tilda_name="Тариф Оптимум", XL_name="Пилочный для тебя", course_id=2
    )
    PREMIUM = Course(
        tilda_name="Тариф Премиум", XL_name="Пилочный для тебя", course_id=2
    )
    UPGRADE = Course(
        tilda_name="Пилочный для тебя 2.0", XL_name="Пилочный для тебя", course_id=2
    )
    POKRYTIE_LAKOM = Course(
        tilda_name="Видеоуроки по покрытию лаком", XL_name="Покрытие лаком", course_id=3
    )
    YXOD_ZA_RUKAMI = Course(
        tilda_name="Большой гайд по уходу за руками",
        XL_name="Уход за руками",
        course_id=4,
    )

    @classmethod
    def all_unique_names(cls) -> List[str]:
        all_names = []
        for member in cls:
            course = member.value
            if isinstance(course, Course):
                all_names.append(course.tilda_name)
                all_names.append(course.XL_name)
        return list(dict.fromkeys(all_names))
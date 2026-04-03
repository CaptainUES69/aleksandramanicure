from dataclasses import dataclass
from enum import Enum
from os import getenv
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(override=True)


class GoogleUser(Enum):
    Login = getenv("LOGIN")
    Password = getenv("PASSWORD")


class FileTemplates(Enum):
    main_dir = Path("./src/templates")
    text = Path(f"{main_dir}/greatings.txt")


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
class Course:
    title: str
    chat_id: list[str]


class CourseList(Enum):
    MINI = Course(title="Тариф Мини", chat_id="-1001926986163")
    UPGRADE = Course(title="Пилочный для тебя 2.0", chat_id="-1002193144744")
    OPTIMUM = Course(title="Тариф Оптимум", chat_id="-1002193144744")
    PREMIUM = Course(title="Тариф Премиум", chat_id="-1002193144744")
    VIDEO = Course(title="Видеоуроки по покрытию лаком", chat_id="-1002485625661")
    GUIDE = Course(title="Большой гайд по уходу за руками", chat_id="-1002487896138")

    @classmethod
    def chat_id_by_title(cls, title: str) -> str | None:
        if not hasattr(cls, "_title_to_chat"):
            cls._title_to_chat = {
                member.value.title: member.value.chat_id for member in cls
            }
        return cls._title_to_chat.get(title)


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
        "Authorization": getenv("PRODAMUS_TOKEN"),
    }

    create_user = "https://api.xl.ru/api/v1/crm/lead"
    scenario_run = "https://api.xl.ru/api/v1/scenario/run"
    scenarios = {
        'Тест': 'KSuVSIeCr0OPXaOa9_P2aQ'
    }

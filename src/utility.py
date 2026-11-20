"""Модели данных, настройки API и справочник курсов.

Содержит:
    * pydantic-модели входящего вебхука от Tilda (`FormData`, `Test` и т.д.);
    * `ProcessUser` - упрощённые данные покупателя для внутренней обработки;
    * `ProdamusAPIUtility` - адреса и заголовки API XL (Prodamus XL);
    * `Courses` - соответствие названий тарифов на Tilda курсам на платформе XL.
"""

from dataclasses import dataclass
from enum import Enum
from os import getenv
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel

# Загружаем переменные из файла .env (нужен PRODAMUS_TOKEN).
# override=True - значения из .env перекрывают переменные окружения.
load_dotenv(override=True)


# ---------------------------------------------------------------------------
# Модели входящего запроса (вебхук Tilda)
# ---------------------------------------------------------------------------


class Test(BaseModel):
    """Тестовый запрос `{"test": "..."}` (Tilda шлёт его при проверке вебхука)."""

    test: str


class ProductItem(BaseModel):
    """Один товар в заказе."""

    name: str  # Название товара (совпадает с `Course.tilda_name`)
    quantity: int
    amount: int
    price: str


class Payment(BaseModel):
    """Информация об оплате из формы Tilda."""

    sys: Optional[str] = None  # Платёжная система
    systranid: Optional[str] = None  # ID транзакции в платёжной системе
    orderid: Optional[str] = None  # ID заказа
    products: List[ProductItem]  # Список купленных товаров
    amount: Optional[str] = None  # Общая сумма заказа


class FormData(BaseModel):
    """Полное тело вебхука о покупке (поля формы Tilda).

    Обязательны только `Email`, `Name` и `payment`, остальное опционально.
    """

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
    """Минимальные данные покупателя, которые нужны для выдачи доступа."""

    Email: str
    Name: str
    Course: str  # Название купленного товара на Tilda


# ---------------------------------------------------------------------------
# Настройки API XL
# ---------------------------------------------------------------------------


class ProdamusAPIUtility(Enum):
    """Класс для организации работы с API XL prodamus

    Справочный центр по API: `https://app.xl.ru/api/public`

    Значения доступны через `.value`, например
    `ProdamusAPIUtility.create_user.value`.
    """

    # Заголовки для всех запросов. Токен берётся из .env (PRODAMUS_TOKEN).
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{getenv("PRODAMUS_TOKEN")}",
    }
    # ID сценариев (автоворонок) в XL по их названию.
    # Сценарий выдаёт пользователю доступ к курсу.
    scenarios = {"Тест": "KSuVSIeCr0OPXaOa9_P2aQ"}

    # post запросы
    create_user = "https://api.xl.ru/api/v1/crm/lead"  # создать контакт
    scenario_run = "https://api.xl.ru/api/v1/scenario/run"  # запустить сценарий
    get_users = "https://api.xl.ru/api/v1/crm/lead/table"  # поиск контактов по фильтру

    # get запросы
    get_user = "https://api.xl.ru/api/v1/crm/lead/"  # {id} - данные контакта по id


# ---------------------------------------------------------------------------
# Справочник курсов
# ---------------------------------------------------------------------------


@dataclass
class Course:
    """Описание курса.

    Attributes:
        tilda_name: Название товара на сайте Tilda (приходит в вебхуке).
        XL_name: Название курса (библиотеки) на платформе XL.
        course_id: Внутренний номер курса.
    """

    tilda_name: str
    XL_name: str
    course_id: int


class Courses(Enum):
    """Класс для организации работы с курсами

    Несколько тарифов Tilda могут вести в один и тот же курс XL
    (например, Мини / Оптимум / Премиум -> "Пилочный для тебя").
    `UPGRADE` - это доплата за повышение тарифа: она доступна только тем,
    у кого курс "Пилочный для тебя" уже есть в библиотеке.
    """

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
    GEL_LAK = Course(
        tilda_name="Видеоуроки по покрытию гель-лаком.", XL_name="Покрытие гель-лаком", course_id=5
    )
    LAK_OPTIMUM = Course(
        tilda_name="Покрытие гель-лаком + Пилочный", XL_name="Покрытие гель-лаком + Пилочный", course_id=5
    )


    @classmethod
    def all_unique_names(cls) -> List[str]:
        """Возвращает все известные названия курсов (и Tilda, и XL) без повторов.

        Используется в `Methods._fetch_user_library_name`, чтобы из библиотеки
        пользователя оставить только "наши" курсы. Порядок сохраняется.
        """
        all_names = []
        for member in cls:
            course = member.value
            if isinstance(course, Course):
                all_names.append(course.tilda_name)
                all_names.append(course.XL_name)
        # dict.fromkeys убирает дубликаты, сохраняя порядок
        return list(dict.fromkeys(all_names))

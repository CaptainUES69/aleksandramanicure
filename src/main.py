"""Точка входа: веб-сервер (FastAPI), принимающий вебхук с сайта на Tilda.

Как это работает в целом:
    1. Клиент оплачивает тариф/курс на сайте (форма Tilda + оплата).
    2. Tilda отправляет POST-запрос с данными формы на `/this/is/buy`.
    3. Сервер сразу отвечает "200 OK" (чтобы Tilda не ждала), а выдачу доступа
       к курсу выполняет в фоне (`Methods.process_user`), обращаясь к API
       платформы XL (Prodamus XL).
"""

import uvicorn
from fastapi import BackgroundTasks, FastAPI, status
from fastapi.responses import JSONResponse

from .conf import CustomLogger, Logger
from .methods import Methods
from .utility import FormData, ProcessUser, Test

app = FastAPI()

# Один общий экземпляр класса с логикой работы с API XL
methods = Methods()

# Логгер веб-сервера, пишет в ./logs/webserver.log
logger: Logger = CustomLogger("webserver")._logger


@app.post("/this/is/buy")
async def process_buy(data: FormData | Test, bg: BackgroundTasks):
    """Обрабатывает вебхук Tilda о новой покупке.

    Принимает одно из двух тел запроса:
        * `Test`     - тестовый запрос `{"test": "..."}`. Tilda отправляет такой
                       при проверке вебхука в настройках формы. Просто отвечаем OK.
        * `FormData` - реальная покупка (email, имя, состав заказа и т.д.).

    Для реальной покупки берём email, имя и название первого товара из заказа
    (оно совпадает с `tilda_name` в `Courses`) и ставим фоновую задачу
    `Methods.process_user`, которая создаёт пользователя / выдаёт доступ.

    Args:
        data: Тело запроса (`FormData` или `Test`).
        bg: Менеджер фоновых задач FastAPI.

    Returns:
        JSONResponse: Всегда 200 и `{"status": "OK", ...}`. Результат выдачи
        доступа в ответ не попадает, его нужно смотреть в логах (`logs/methods.log`).
    """
    # Логируем всё, что пришло, чтобы можно было разобраться при проблемах
    logger.info(data)

    # Тестовый запрос от Tilda - ничего не обрабатываем
    if isinstance(data, Test):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "OK", "message": "Test successful"},
        )

    # Из данных формы собираем только то, что нужно для обработки.
    # Берётся первый товар в заказе: считается, что в корзине один курс.
    user = ProcessUser(
        Email=data.Email, Name=data.Name, Course=data.payment.products[0].name
    )

    # Выдача доступа идёт в фоне, после того как ответ уже отправлен
    bg.add_task(methods.process_user, user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "OK", "message": "Data transited"},
    )


if __name__ == "__main__":
    # Запуск: `python -m src.main` (см. CMD в Dockerfile).
    # host 0.0.0.0 нужен, чтобы сервер был доступен снаружи контейнера.
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("Server stopped by user")

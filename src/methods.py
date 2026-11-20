"""Логика работы с API XL (Prodamus XL): поиск/создание контакта и выдача доступа.

Главный метод - `Methods.process_user`. Остальные методы (с `_` в начале)
внутренние и вызываются только из него.
"""

from requests import get, post

from .conf import CustomLogger, Logger
from .utility import Courses, ProcessUser, ProdamusAPIUtility


class Methods:
    """Набор методов для обработки покупки и взаимодействия с API XL."""

    # Логгер класса, пишет в ./logs/methods.log
    _logger: Logger = CustomLogger("methods")._logger

    # Внутренние методы

    def __init__(self):
        pass

    def _create_user(self, data: ProcessUser) -> str:
        """Создаёт нового контакта (лида) в CRM XL.

        Args:
            data: Данные покупателя (используются email и имя).

        Returns:
            str: ID созданного контакта. `None`, если создать не удалось
            (ошибка API или исключение, причина пишется в лог).
        """
        try:
            response = post(
                url=ProdamusAPIUtility.create_user.value,
                headers=ProdamusAPIUtility.headers.value,
                json={"email": data.Email, "firstName": data.Name},
            )
            # В ответе XL полезные данные лежат в поле "body" (здесь - ID контакта)
            body = response.json().get("body")
            if response.status_code == 200 and body is not None:
                self._logger.info(f"Inner - User: {data.Email} created")
                return body

            else:
                self._logger.warning(
                    f"Inner - User doesn`t created because of: {response.status_code}, {response.reason}\n{response.text}"
                )
                return

        except Exception as e:
            self._logger.error(
                f"Error while creating user: {data.Email} {data.Course}, {e.with_traceback(e.__traceback__)}"
            )
            return

    def _scenario_run(self, data: ProcessUser, user_id: str) -> str:
        """Запускает в XL сценарий для контакта (выдача доступа к курсу).

        В сценарий передаются данные контакта и название купленного курса
        (`data.course`), по которому сценарий решает, что выдать.

        Args:
            data: Данные покупателя.
            user_id: ID контакта в XL.

        Returns:
            str: Тело ответа XL при успешном запуске. `None`, если ответ
            пустой или произошла ошибка (причина пишется в лог).
        """
        try:
            response = post(
                url=ProdamusAPIUtility.scenario_run.value,
                headers=ProdamusAPIUtility.headers.value,
                json={
                    "scenarioId": ProdamusAPIUtility.scenarios.value.get("Тест"),
                    "contactId": str(user_id),
                    "contactData": {
                        "email": str(data.Email),
                        "firstName": str(data.Name),
                    },
                    "data": {"course": str(data.Course)},
                },
            )
            body = response.json().get("body")
            if not body:
                self._logger.error("Inner - Empty body while run scenario")
                return
            return body

        except Exception as e:
            self._logger.error(
                f"Error while run scenario for user: {data.Email} {data.Course}, {e.with_traceback(e.__traceback__)}"
            )
            return

    def _fetch_user_id_by_email(self, email: setattr) -> list[dict[str, str]]:
        """Ищет контакт в XL по email.

        Args:
            email: Email покупателя.

        Returns:
            ID найденного контакта (берётся первый из найденных).
            `None`, если контакт не найден или произошла ошибка.
            (Аннотация типа в сигнатуре неточная, фактически возвращается ID.)
        """
        try:
            response = post(
                url=ProdamusAPIUtility.get_users.value,
                headers=ProdamusAPIUtility.headers.value,
                json={"filter": {"email": email}},
            )
            # Список найденных контактов лежит в body -> items
            body = response.json().get("body").get("items")
            if response.status_code == 200 and len(body) > 0:
                self._logger.info(f"Inner - User found: {email}")
                return body[0].get("id")

            else:
                self._logger.warning(f"Inner - User not found: {email}")
                return

        except Exception as e:
            self._logger.error(
                f"Error while fetching user id by email: {email}, {e.with_traceback(e.__traceback__)}"
            )
            return

    def _fetch_user_library_name(self, id: str) -> list[str]:
        """Получает список курсов, которые уже есть в библиотеке пользователя.

        Запрашивает у XL доступы контакта и оставляет только те курсы,
        названия которых известны в `Courses` (чужие/прочие игнорируются).
        Дубликаты убираются.

        Args:
            id: ID контакта в XL.

        Returns:
            list[str]: Названия курсов пользователя. Пустой список при ошибке.
        """
        try:
            response = get(
                url=f"{ProdamusAPIUtility.get_user.value}{id}",
                headers=ProdamusAPIUtility.headers.value,
                # GraphQL-подобный список полей: нужны только названия библиотек (курсов)
                params={
                    "fields": "{id email studentCourseAccesses{libraryAccess{library{name}}}}"
                },
            )

            response.json()["body"]["studentCourseAccesses"]
            courses_list = []
            for item in response.json()["body"]["studentCourseAccesses"]:
                course = item["libraryAccess"]["library"]["name"]
                if course not in courses_list and course in Courses.all_unique_names():
                    courses_list.append(course)
            return courses_list

        except Exception as e:
            self._logger.error(
                f"Error while fetching user library name: {id}, {e.with_traceback(e.__traceback__)}"
            )
            return []

    # Обработка данных пользователя

    def process_user(self, data: ProcessUser):
        """Основной сценарий обработки покупки (вызывается из main.py в фоне).

        Алгоритм:
            1. Ищем контакт в XL по email.
            2. Контакта нет:
                * если куплен `UPGRADE` ("Пилочный для тебя 2.0") - ничего не делаем,
                  так как улучшение возможно только при наличии предыдущего курса;
                * иначе создаём контакт и запускаем сценарий выдачи курса.
            3. Контакт уже есть:
                * куплен любой курс, кроме `UPGRADE` - запускаем сценарий;
                * куплен `UPGRADE` - запускаем сценарий только если в библиотеке
                  пользователя уже есть курс "Пилочный для тебя".

        Метод ничего не возвращает: результат (успех, пропуск, ошибка)
        записывается в лог `logs/methods.log`.

        Args:
            data: Данные покупателя (email, имя, название купленного курса).
        """
        try:
            # Шаг 1. Ищем пользователя в XL
            user_id = self._fetch_user_id_by_email(data.Email)

            # Шаг 2. Новый пользователь
            if user_id is None:
                # Апгрейд без предыдущего курса не выдаём
                if data.Course == Courses.UPGRADE.value.tilda_name:
                    self._logger.info(
                        f"User: {data.Email} with Course: {data.Course}, doesn`t have previous course in library, scenario not run"
                    )
                    return
                user_id = self._create_user(data)
                scenario = self._scenario_run(data, user_id)
                if scenario:
                    self._logger.info(
                        f"User: {data.Email} with Course: {data.Course}, processed correct"
                    )
                    return

            # Шаг 3. Существующий пользователь: смотрим, какие курсы у него уже есть
            user_courses = self._fetch_user_library_name(user_id)

            # Обычная покупка (не апгрейд) - просто выдаём курс
            if data.Course != Courses.UPGRADE.value.tilda_name:
                scenario = self._scenario_run(data, user_id)
                if scenario:
                    self._logger.info(
                        f"User: {data.Email} with Course: {data.Course}, processed correct"
                    )
                    return

            # Апгрейд - выдаём, только если базовый курс уже есть в библиотеке
            self._logger.info(f"{user_courses}")
            if Courses.UPGRADE.value.XL_name in user_courses:
                scenario = self._scenario_run(data, user_id)
                if scenario:
                    self._logger.info(
                        f"User: {data.Email} with Course: {data.Course}, processed correct"
                    )
                    return
                
        except Exception as e:
            self._logger.error(
                f"Error while processing user: {data.Email} {data.Course}, {e.with_traceback(e.__traceback__)}"
            )

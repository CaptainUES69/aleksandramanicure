from requests import post, get

from .conf import CustomLogger, Logger
from .utility import ProcessUser, ProdamusAPIUtility, Courses


class Methods:
    _logger: Logger = CustomLogger("methods")._logger

    # Внутренние методы

    def __init__(self):
        pass

    def _create_user(self, data: ProcessUser) -> str:
        response = post(
            url=ProdamusAPIUtility.create_user.value,
            headers=ProdamusAPIUtility.headers.value,
            json={"email": data.Email, "firstName": data.Name},
        )
        body = response.json().get("body")
        if response.status_code == 200 and body is not None:
            self._logger.info(f"Inner - User: {data.Email} created")
            return body

        else:
            self._logger.warning(
                f"Inner - User doesn`t created because of: {response.status_code}, {response.reason}\n{response.text}"
            )
            return

    def _scenario_run(self, data: ProcessUser, user_id: str) -> str:
        response = post(
            url=ProdamusAPIUtility.scenario_run.value,
            headers=ProdamusAPIUtility.headers.value,
            json={
                "scenarioId": ProdamusAPIUtility.scenarios.value.get("Тест"),
                "contactId": str(user_id),
                "contactData": {"email": str(data.Email), "firstName": str(data.Name)},
                "data": {"course": str(data.Course)},
            },
        )
        body = response.json().get("body")
        if not body:
            self._logger.error("Inner - Empty body while run scenario")
            return
        return body

    def _fetch_user_id_by_email(self, email: setattr) -> list[dict[str, str]]:
        response = post(
            url=ProdamusAPIUtility.get_users.value,
            headers=ProdamusAPIUtility.headers.value,
            json={"filter": {"email": email}},
        )
        body = response.json().get("body").get("items")
        if response.status_code == 200 and body is not None:
            self._logger.info(f"Inner - User found: {email}")
            return body[0].get("id")

        else:
            self._logger.warning(f"Inner - User not found: {email}")
            return

    def _fetch_user_library_name(self, id: str) -> list[str]:
        response = get(
            url=f"{ProdamusAPIUtility.get_user.value}{id}",
            headers=ProdamusAPIUtility.headers.value,
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

    # Обработка данных пользователя

    def process_user(self, data: ProcessUser):
        try:
            user_id = self._fetch_user_id_by_email(data.Email)
            if user_id is None:
                user_id = self._create_user(data)
                scenario = self._scenario_run(data, user_id)
                if scenario:
                    self._logger.info(
                        f"User: {data.Email} with Course: {data.Course}, processed correct"
                    )
                    return

            user_courses = self._fetch_user_library_name(user_id)
            if data.Course != Courses.UPGRADE.value.tilda_name:
                scenario = self._scenario_run(data, user_id)
                if scenario:
                    self._logger.info(
                        f"User: {data.Email} with Course: {data.Course}, processed correct"
                    )
                    return

            self._logger.info(f'{user_courses}')
            if Courses.UPGRADE.value.XL_name in user_courses:
                scenario = self._scenario_run(data, user_id)
                if scenario:
                    self._logger.info(
                        f"User: {data.Email} with Course: {data.Course}, processed correct"
                    )
                    return
        
            self._logger.info(f"User: {data.Email} with Course: {data.Course}, doesn`t have course in library, scenario not run")
            return

        except Exception as e:
            self._logger.error(f"Error while processing user: {data.Email} {data.Course}, {e.with_traceback()}")

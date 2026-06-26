from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import getenv
from pathlib import Path
from smtplib import SMTP

import aiofiles
from aiogram import Bot
from aiogram.types import ChatInviteLink
from dotenv import load_dotenv
from jinja2 import Template
from requests import post

from .conf import CustomLogger, Logger
from .utility import (CourseList, FileTemplates, GoogleUser, ProcessUser,
                      ProdamusAPIUtility)


class Methods:
    _bot: Bot
    _logger: Logger = CustomLogger("methods")._logger

    # Внутренние методы

    def __init__(self):
        load_dotenv(override=True)
        self._bot = Bot(token=getenv("LINK_TOKEN"))
        pass

    async def _create_link_async(self, chat_id: str | int) -> str | None:
        try:
            link_data: ChatInviteLink = await self._bot.create_chat_invite_link(
                chat_id=chat_id, member_limit=1
            )
            return link_data.invite_link

        except Exception as e:
            self._logger.error(
                f"Exception type: {e.__class__.__name__}, while creating invite link to {chat_id}"
            )
            return

    def _create_user_XL(self, data: ProcessUser) -> str:
        response = post(
            url=ProdamusAPIUtility.create_user.value,
            headers=ProdamusAPIUtility.headers.value,
            json={"email": data.Email, "firstName": data.Name},
        )
        body = response.json().get("body")
        if response.status_code == 200 and body is not None:
            self._logger.info(f"User: {data.Email} created")
            return body

        elif response.status_code == 400 and any(
            "emailAlreadyExists" == error.get("type")
            for error in response.json().get("errors")
        ):
            self._logger.info(f"User: {data.Email} already exist")
            return

        else:
            self._logger.warning(
                f"User doesn`t created because of: {response.status_code}, {response.reason}\n{response.text}"
            )
            return

    def _scenario_run(self, data: ProcessUser, user_id: str) -> str:
        response = post(
            url=ProdamusAPIUtility.scenario_run.value,
            headers=ProdamusAPIUtility.headers.value,
            json={
                "scenarioId": ProdamusAPIUtility.scenarios.value.get("Тест"),
                "contactId": user_id,
                "contactData": {"email": data.Email, "firstName": data.Name},
                "data": {"course": data.Course},
            },
        )
        body = response.json().get("body")
        if not body:
            self._logger.error("Empty body while run scenario")
            return
        return body

    # Обработка данных пользователя

    async def process_user_Telegram(self, data: ProcessUser):
        chat_id: str = CourseList.chat_id_by_title(data.Course)
        if not chat_id:
            self._logger.error(
                f"Course {data.Course} doesn`t response correctly, check admin rights, and chat_id in CourseList"
            )
            return
        invite_link = await self._create_link_async(chat_id)

        self.send_email(data.Email, invite_link, data.Name, data.Course)
        return invite_link

    def process_user_XL(self, data: ProcessUser):
        user_id = self._create_user_XL(data)
        if not user_id:
            return

        scenario = self._scenario_run(data, user_id)
        if scenario:
            self._logger.info(
                f"User: {data.Email} with Course: {data.Course}, processed correct"
            )

    def send_email(self, recipient_email: str, link: str, name: str, course_name: str):
        try:
            smtp_server = SMTP("smtp.gmail.com", 587)
            msg = MIMEMultipart()
            smtp_server.starttls()
            smtp_server.login(GoogleUser.Login.value, GoogleUser.Password.value)

            msg["From"] = GoogleUser.Login.value
            msg["To"] = recipient_email
            msg["Subject"] = (
                f"Приветствуем на курсе «Пилочный для тебя», {course_name} от Александры Воропаевой✨"
            )

            with open(FileTemplates.text.value, "r", encoding="utf-8") as file:
                template_text = file.read()
                template: Template = Template(template_text)
                mes = template.render({"name": name, "link": link})

            msg.attach(MIMEText(mes, "plain"))
            smtp_server.sendmail(
                GoogleUser.Login.value, recipient_email, msg.as_string()
            )

        finally:
            smtp_server.quit()

    async def write_file(self, filepath_input: str, content: str) -> bool:
        filepath = Path(filepath_input)
        self._logger.info(f"Start changing: {filepath}")
        async with aiofiles.open(filepath, mode="w", encoding="utf-8") as f:
            try:
                await f.write(content)
                self._logger.info(f"File {filepath.name} changed")
                return True

            except Exception as e:
                self._logger.critical(
                    f"Exception with type: {type(e).__name__}", exc_info=True
                )
                return False

    async def read_file(self, filepath: Path) -> str:
        async with aiofiles.open(filepath, mode="r", encoding="utf-8") as f:
            try:
                content = await f.read()
                return content

            except Exception as e:
                self._logger.critical(
                    f"Exception with type: {type(e).__name__}", exc_info=True
                )

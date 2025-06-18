from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import  HTTPException, Request, Response
from jinja2 import Template
from aiogram import Bot
from urllib.parse import unquote
from src.models import Purchase

import smtplib, re, json

from dotenv import load_dotenv 
from os import getenv
from src.models import logger

load_dotenv()

async def parse_data(parsed_data: dict[str, list[str]]):
    try:
        logger.info("Receiving data...")
        if "test=test" in parsed_data:
            return Response(status_code = 200)
        
        else:
            logger.info("Parsing data...")
            data_dict = {key: unquote(value[0]) for key, value in parsed_data.items()}
            data_dict["payment"] = json.loads(data_dict["payment"])
            form_data = Purchase(**data_dict)
            logger.info(f"Data succefull parsed...")

        return form_data
    
    except Exception as e:
        logger.error(f"{type(e).__name__} while parcing data...", exc_info = True)
        raise HTTPException(status_code=500, detail=f"Internal server error.")

async def send_mail(recipient_email: str, link: str, name: str, course: str):
    try:
        logger.info("Creating Email template.")
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.starttls()
        smtp_server.login(getenv("ELOGIN"), getenv("EPASSWORD"))
        c = re.sub(r'[1234567890.=]', '', course.replace('[', '').replace(']', ''))
        link_list = link.split(" | ")

        msg = MIMEMultipart()
        msg["From"] = getenv("ELOGIN")
        msg["To"] = recipient_email
        msg["Subject"] = f"Приветствуем на курсе «Пилочный для тебя», {c} от Александры Воропаевой✨"
        
        logger.info("Insert text into Email.")
        if (getenv("SECOND_NAME") in course) or (getenv("THIRD_NAME") in course) or (getenv("UPDATE_NAME") in course):
            with open("src/Templates/two_links.txt", "r", encoding="utf-8") as file:
                template_text = file.read()
            link
            template = Template(template_text)
            mes = template.render({'name': name, 'channel': link_list[0], 'chat': link_list[1]})
        
        else:
            with open("src/Templates/one_link.txt", "r", encoding="utf-8") as file:
                template_text = file.read()
            template = Template(template_text)
            mes = template.render({'name': name, 'channel': link})
        logger.info("Template create correctly.")

    except Exception as e:
        logger.error(f"{type(e).__name__} while creating Email template:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error.")
    
    else:
        try:
            msg.attach(MIMEText(mes, "plain"))
            smtp_server.sendmail(getenv("ELOGIN"), recipient_email, msg.as_string())
            logger.info("Sending Email.")
        except Exception as e:
            logger.error(f"{type(e).__name__} while sending mail", exc_info=True)
        else:
            logger.info("Mail send correctly")
    
    finally:
        smtp_server.quit()
        logger.info("SMTP server closing.")

async def create_link(course: str, courses: dict):
    async with Bot(token = getenv("TOKEN")) as bot:
        try:
            for name in courses:
                if name in course:
                    config = courses[name]
                    channel_link = await bot.create_chat_invite_link(
                        chat_id=config["channel"],
                        member_limit=1
                        )
                    
                    if config["chat"]:
                        chat_link = await bot.create_chat_invite_link(
                            chat_id=config["chat"],
                            member_limit=1
                            )
                        logger.info("Links create correctly.")
                        return f"{channel_link.invite_link} | {chat_link.invite_link}"

                    logger.info("Link create correctly.")
                    return channel_link.invite_link
                
            logger.error(f"Course don`t exist:", exc_info=True)
            raise HTTPException(status_code=404, detail="Course name not found")
        
        except TypeError as e:
            logger.error(f"Type error:", exc_info=True)
            raise HTTPException(status_code=500)
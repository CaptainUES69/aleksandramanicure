from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, EmailStr
from email.mime.text import MIMEText
from fastapi import  HTTPException
from dotenv import load_dotenv 
from jinja2 import Template
from aiogram import Bot
from os import getenv

import smtplib, re, logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
load_dotenv()

class PaymentData(BaseModel):
    sys: str
    systranid: str
    orderid: str
    products: list[str]
    amount: str

class Purchase(BaseModel):
    Email: EmailStr
    Name: str
    Phone: str
    input: str
    Checkbox: str
    Checkbox_2: str
    Checkbox_3: str
    payment: PaymentData
    formid: str
    formname: str

coursesList = {
    getenv("FIRST_NAME"): {
        "channel": getenv('FIRST_CHANNEL'),
        "chat": None
    },
    getenv("UPDATE_NAME"): {
        "channel": getenv('PREMIUM_CHANNEL'),
        "chat": getenv('PREMIUM_CHAT')
    },
    getenv("SECOND_NAME"): {
        "channel": getenv('PREMIUM_CHANNEL'),
        "chat": getenv('PREMIUM_CHAT')
    },
    getenv("THIRD_NAME"): {
        "channel": getenv('PREMIUM_CHANNEL'),
        "chat": getenv('PREMIUM_CHAT')
    },
    getenv("FOUR_NAME"): {
        "channel": getenv('FOUR_CHANNEL'),
        "chat": None
    },
    getenv("FIVE_NAME"): {
        "channel": getenv('FIVE_CHANNEL'),
        "chat": None
    }
}


async def SendMail(recipient_email: str, link: str, name: str, course: str):
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
            with open("Templates/two_links.txt", "r", encoding="utf-8") as file:
                template_text = file.read()
            link
            template = Template(template_text)
            mes = template.render({'name': name, 'channel': link_list[0], 'chat': link_list[1]})
        
        else:
            with open("Templates/one_link.txt", "r", encoding="utf-8") as file:
                template_text = file.read()
            template = Template(template_text)
            mes = template.render({'name': name, 'channel': link})
        logger.info("Template create correctly.")

    except Exception:
        logger.error(f"Error while creating Email template:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error.")
    
    else:
        try:
            msg.attach(MIMEText(mes, "plain"))
            smtp_server.sendmail(getenv("ELOGIN"), recipient_email, msg.as_string())
            logger.info("Sending Email.")
        except Exception as e:
            logger.error("Error while sending mail", exc_info=True)
        else:
            logger.info("Mail send correctly")
    
    finally:
        smtp_server.quit()
        logger.info("SMTP server closing.")

async def Create_link(course: str):
    async with Bot(token = getenv("TOKEN")) as bot:
        try:
            for name in coursesList:
                if name in course:
                    config = coursesList[name]
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
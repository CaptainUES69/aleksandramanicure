from fastapi import FastAPI, Request, HTTPException, Response
from contextlib import asynccontextmanager
import uvicorn

from src.functions import sendMail, createLink, parseData
from src.models import coursesList

from dotenv import load_dotenv 
from os import getenv

from src.models import logger
from datetime import datetime
import traceback, requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Open")
    load_dotenv()
    yield 
    print("Close")

app = FastAPI(lifespan = lifespan)

@app.post("/this/is/buy", tags=["Сашины курсы"], summary="Прием вебхука")
async def receiveData(request: Request):
    try:
        form_data = await parseData(request)
        link = await createLink(str(form_data.payment.products), coursesList)
        await sendMail(form_data.Email, link, form_data.Name, str(form_data.payment.products))
    
    except HTTPException as e:
        send_telegram_message(e)
        raise HTTPException(status_code = e.status_code)
    
    except Exception as e:
        logger.error(f"Untitled error:", exc_info=True)
        send_telegram_message(e)
        HTTPException(status_code = 500, detail=f"Internal server error.")
        
    else:
        logger.info(f"Data succefull received: {form_data.Email} {form_data.payment.products}")
        return Response(status_code = 200)

def send_telegram_message(e: Exception):
    logger.critical("Exception(s) catched sending to Telegram...")
    try:
        error_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = (
                "🔴 <b>Произошла ошибка!</b>\n\n"
                f"<b>Тип ошибки:</b> <code>{type(e).__name__}</code>\n"
                f"<b>Время:</b> <code>{error_time}</code>\n"
                f"<b>Где произошла:</b> <code>{__file__}</code>\n\n"
                "<b>Traceback:</b>\n"
                f"<pre>{traceback.format_exc()}</pre>")
        
        url = f"https://api.telegram.org/bot{getenv("TOKEN")}/sendMessage"
        payload = {
            "chat_id": getenv("TECH_SUPPORT_ID"),
            "text": message,
            "parse_mode": "HTML"}

        response = requests.post(url, json = payload)
        return response.json()
    
    except Exception as e:
        print(f"Ошибка при отправке в Telegram: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "src.webserver:app", host="127.0.0.1", port=8000)
        # ssl_keyfile="/etc/letsencrypt/live/aleksandramanicureserver.ru/privkey.pem", 
        # ssl_certfile="/etc/letsencrypt/live/aleksandramanicureserver.ru/cert.pem")

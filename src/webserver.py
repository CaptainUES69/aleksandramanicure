from fastapi import FastAPI, Request, HTTPException, Response
from contextlib import asynccontextmanager
from urllib.parse import parse_qs
import uvicorn

from src.functions import send_mail, create_link, parse_data
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
async def receive_data(request: Request):
    try:

        raw_data = await request.body()
        logger.info(raw_data.decode("utf-8"))
        parsed_data = parse_qs(raw_data.decode("utf-8"))
        logger.info(parsed_data)
        if "test" in parsed_data:
            return Response(status_code = 200)
        
        else:
            form_data = await parse_data(parsed_data)
            logger.info(f"Data succefull received: {form_data.Email} {form_data.payment.products}")
            link = await create_link(str(form_data.payment.products))
            await send_mail(form_data.Email, link, form_data.Name, str(form_data.payment.products))
    
    except HTTPException as e:
        send_telegram_message(e)
        raise HTTPException(status_code = e.status_code)
    
    except Exception as e:
        logger.error(f"Untitled error:", exc_info=True)
        send_telegram_message(e)
        HTTPException(status_code = 500, detail=f"Internal server error.")
        
    else:
        return Response(status_code = 200)

@app.get("/test")
async def test():
    return "hello"

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
        
        url = f"https://api.telegram.org/bot{getenv('TECHTOKEN')}/sendMessage"
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
        "src.webserver:app", host="127.0.0.1", port=5000)

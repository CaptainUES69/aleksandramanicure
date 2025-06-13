from fastapi import FastAPI, Request, HTTPException, Response
from contextlib import asynccontextmanager
from urllib.parse import unquote, parse_qs
from dotenv import load_dotenv 
from functions import logger, SendMail, Create_link, Purchase
from os import getenv
from datetime import datetime

import uvicorn, json, requests, traceback


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Open")
    load_dotenv()
    yield 
    print("Close")

app = FastAPI(lifespan = lifespan)


@app.post("/this/is/buy", tags=["Сашины курсы"], summary="Прием вебхука")
async def Receive_data(request: Request):
    try:
        logger.info("Receiving data...")
        raw_data = await request.body()
        parsed_data = parse_qs(raw_data.decode("utf-8"))
        if "test" in parsed_data:
            return Response(status_code = 200)
        else:
            logger.info("Parsing data...")
            data_dict = {key: unquote(value[0]) for key, value in parsed_data.items()}
            data_dict["payment"] = json.loads(data_dict["payment"])
            form_data = Purchase(**data_dict)
            logger.info(f"Data succefull parsed: {form_data.Email} {form_data.payment.products}")

        link = await Create_link(str(form_data.payment.products))
        await SendMail(form_data.Email, link, form_data.Name, str(form_data.payment.products))
    
    except HTTPException as e:
        send_telegram_message(e)
        raise HTTPException(status_code=e.status_code)
    
    except Exception as e:
        logger.error(f"Untitled error:", exc_info=True)
        HTTPException(status_code=500, detail=f"Internal server error.")

        send_telegram_message(e)

    else:
        logger.info(f"Data succefull received: {form_data.Email} {form_data.payment.products}")

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
        "webserver:app", host="127.0.0.1", port=8000,
        ssl_keyfile="/etc/letsencrypt/live/aleksandramanicureserver.ru/privkey.pem", 
        ssl_certfile="/etc/letsencrypt/live/aleksandramanicureserver.ru/cert.pem")

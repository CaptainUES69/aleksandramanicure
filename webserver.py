from fastapi import FastAPI, Request, HTTPException, Response
from contextlib import asynccontextmanager
from urllib.parse import unquote, parse_qs
from dotenv import load_dotenv 
from functions import logger, SendMail, Create_link, Purchase

import uvicorn, json


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Open")
    load_dotenv()
    yield 
    print("Close")

app = FastAPI(lifespan = lifespan)


@app.post("/this/is/buy", tags=["Сашины курсы"], summary="Прием вебхука")
async def Receive_data(request: Request):
    logger.info("Receiving and parsing data...")
    raw_data = await request.body()
    parsed_data = parse_qs(raw_data.decode("utf-8"))
    if "test" in parsed_data:
        return Response(status_code = 200)
    else:
        data_dict = {key: unquote(value[0]) for key, value in parsed_data.items()}
        data_dict["payment"] = json.loads(data_dict["payment"])
        form_data = Purchase(**data_dict)
        logger.info(f"Data succefull parsed: {form_data.Email} {form_data.payment.products}")

    try:
        link = await Create_link(str(form_data.payment.products))
        await SendMail(form_data.Email, link, form_data.Name, str(form_data.payment.products))
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code)

    except Exception as e:
        logger.error(f"Untitled error:", exc_info=True)
        HTTPException(status_code=500, detail=f"Internal server error.")
    
    else:
        logger.info(f"Data succefull received: {form_data.Email} {form_data.payment.products}")


if __name__ == "__main__":
    uvicorn.run("webserver:app", host="127.0.0.1", port=8000,
        ssl_keyfile="/etc/letsencrypt/live/aleksandramanicureserver.ru/privkey.pem", 
        ssl_certfile="/etc/letsencrypt/live/aleksandramanicureserver.ru/cert.pem")

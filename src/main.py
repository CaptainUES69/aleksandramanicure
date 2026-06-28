import uvicorn
from fastapi import BackgroundTasks, FastAPI, status
from fastapi.responses import JSONResponse

from .conf import CustomLogger, Logger
from .methods import Methods
from .utility import FormData, ProcessUser, Test

app = FastAPI()
methods = Methods()
logger: Logger = CustomLogger("webserver")._logger


@app.post("/this/is/buy")
async def process_buy(data: FormData | Test, bg: BackgroundTasks):
    logger.info(data)
    if isinstance(data, Test):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "OK", "message": "Test successful"},
        )

    user = ProcessUser(
        Email=data.Email, Name=data.Name, Course=data.payment.products[0].name
    )
    bg.add_task(methods.process_user, user)        

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "OK", "message": "Data transited"},
    )


if __name__ == "__main__":
    try:
        port = int(input("Input port for instance of webserver:\n"))
        uvicorn.run("src.main:app", host="127.0.0.1", port=port)

    except KeyboardInterrupt:
        print("Webserver Close")

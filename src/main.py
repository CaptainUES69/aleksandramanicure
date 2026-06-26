import uvicorn
from fastapi import BackgroundTasks, FastAPI, status
from fastapi.responses import JSONResponse

from .conf import CustomLogger, Logger
from .db_orm import TableManager
from .methods import Methods
from .utility import CourseList, FormData, ProcessUser, Test

app = FastAPI()
methods = Methods()
logger: Logger = CustomLogger("webserver")._logger
db = TableManager()


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
    bg.add_task(db.create_user, data)
    if user.Course == CourseList.UPGRADE.value.title:
        db_user = db.get_user(data.Email)
        if db_user != None:
            bg.add_task(methods.process_user_XL, user)
            # bg.add_task(methods.process_user_Telegram, user)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "OK", "message": "Data successfuly transited"},
            )
        
        logger.critical(f"{user.Email} {user.Course} doesn`t have original course")
        
    # bg.add_task(methods.process_user_Telegram, user)
    bg.add_task(methods.process_user_XL, user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "OK", "message": "Data successfuly transited"},
    )


if __name__ == "__main__":
    try:
        port = int(input("Input port for instance of webserver:\n"))
        uvicorn.run("src.main:app", host="127.0.0.1", port=port)

    except KeyboardInterrupt:
        print("Webserver Close")

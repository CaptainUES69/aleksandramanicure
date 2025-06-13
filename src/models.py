from pydantic import BaseModel, EmailStr
from os import getenv
from dotenv import load_dotenv 

import logging

load_dotenv



logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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
        "chat": None},

    getenv("UPDATE_NAME"): {
        "channel": getenv('PREMIUM_CHANNEL'),
        "chat": getenv('PREMIUM_CHAT')},

    getenv("SECOND_NAME"): {
        "channel": getenv('PREMIUM_CHANNEL'),
        "chat": getenv('PREMIUM_CHAT')},

    getenv("THIRD_NAME"): {
        "channel": getenv('PREMIUM_CHANNEL'),
        "chat": getenv('PREMIUM_CHAT')},

    getenv("FOUR_NAME"): {
        "channel": getenv('FOUR_CHANNEL'),
        "chat": None},

    getenv("FIVE_NAME"): {
        "channel": getenv('FIVE_CHANNEL'),
        "chat": None}}
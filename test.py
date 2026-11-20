from requests import post, get



response = post(
    url="https://aleksandramanicureserver.ru/this/is/buy",
    # url = "http://localhost:8000/this/is/buy",
    json={
        "Email": "forapexlegends1348@gmail.com",
        "Name": "Ксения",
        "Phone": "+375256691580",
        "input": None,
        "Checkbox": "yes",
        "Checkbox_2": "yes",
        "Checkbox_3": "yes",
        "payment": {
            "sys": "custom.payform",
            "systranid": "0",
            "orderid": "2034678436",
            "products": [
                {
                    "name": "Видеоуроки по покрытию лаком",
                    "quantity": 1,
                    "amount": 7900,
                    "price": "7900"
                }
            ],
            "amount": "7900"
        },
        "formid": "form1816933531",
        "formname": "Cart"
    },
    proxies={
        'http': None,
        'https': None,
    }
)
print(response.status_code)
print(response.text)
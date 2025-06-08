import requests

post_data = [
    "test=test"
    ,"Email=forapexlegends1348%40gmail.com&Name=%D0%90%D0%BD%D0%B0%D1%81%D1%82%D0%B0%D1%81%D0%B8%D1%8F&Phone=%2B79381071777&input=%40kargina_nastasya&Checkbox=yes&Checkbox_2=yes&Checkbox_3=yes&payment=%7B%22sys%22%3A%22custom.payform%22%2C%22systranid%22%3A%220%22%2C%22orderid%22%3A%221673094520%22%2C%22products%22%3A%5B%22%D0%92%D0%B8%D0%B4%D0%B5%D0%BE%D1%83%D1%80%D0%BE%D0%BA%D0%B8+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BA%D1%80%D1%8B%D1%82%D0%B8%D1%8E+%D0%BB%D0%B0%D0%BA%D0%BE%D0%BC.%3D3000%22%5D%2C%22amount%22%3A%223000%22%7D&formid=form777641779&formname=Cart"
    ,"Email=forapexlegends1348%40gmail.com&Name=%D0%9B%D1%8E%D0%B4%D0%BC%D0%B8%D0%BB%D0%B0&Phone=79055730759&input=Ltenit&Checkbox=yes&Checkbox_2=yes&Checkbox_3=yes&payment=%7B%22sys%22%3A%22custom.payform%22%2C%22systranid%22%3A%220%22%2C%22orderid%22%3A%222126831316%22%2C%22products%22%3A%5B%22%D0%9F%D0%B8%D0%BB%D0%BE%D1%87%D0%BD%D1%8B%D0%B9+%D0%B4%D0%BB%D1%8F+%D1%82%D0%B5%D0%B1%D1%8F+2.0%3D2400%22%5D%2C%22amount%22%3A%222400%22%7D&formid=form777641779&formname=Cart"
    ,"Email=forapexlegends1348%40bk.ru&Name=%D0%A0%D1%8F%D0%B1%D1%83%D1%85%D0%B8%D0%BD%D0%B0+%D0%90%D0%BD%D0%B0%D1%81%D1%82%D0%B0%D1%81%D0%B8%D1%8F+%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%BD%D0%B0+%D0%A0%D1%8F%D0%B1%D1%83%D1%85%D0%B8%D0%BD%D0%B0&Phone=89127394495&input=%2B79127394495&Checkbox=yes&Checkbox_2=yes&Checkbox_3=yes&payment=%7B%22sys%22%3A%22custom.payform%22%2C%22systranid%22%3A%220%22%2C%22orderid%22%3A%221198726844%22%2C%22products%22%3A%5B%22%D0%A2%D0%B0%D1%80%D0%B8%D1%84+%D0%9C%D0%B8%D0%BD%D0%B8%3D5900%22%5D%2C%22amount%22%3A%225900%22%7D&formid=form777641779&formname=Cart"
    ,"Email=forapexlegends1348%40gmail.com&Name=%D0%9E%D0%B2%D1%81%D1%8F%D0%BD%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2%D0%B0+%D0%9E%D0%BA%D1%81%D0%B0%D0%BD%D0%B0&Phone=%2B79268678910&input=%40kladovka_beauty&Checkbox=yes&Checkbox_2=yes&Checkbox_3=yes&payment=%7B%22sys%22%3A%22custom.payform%22%2C%22systranid%22%3A%220%22%2C%22orderid%22%3A%221868223462%22%2C%22products%22%3A%5B%22%D0%A2%D0%B0%D1%80%D0%B8%D1%84+%D0%9E%D0%BF%D1%82%D0%B8%D0%BC%D1%83%D0%BC%3D7900%22%5D%2C%22amount%22%3A%227900%22%7D&formid=form777641779&formname=Cart"
    ,"Email=Voropaevaa1979%40mail.ru&Name=%D0%9E%D0%B2%D1%81%D1%8F%D0%BD%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2%D0%B0+%D0%9E%D0%BA%D1%81%D0%B0%D0%BD%D0%B0&Phone=%2B79268678910&input=%40kladovka_beauty&Checkbox=yes&Checkbox_2=yes&Checkbox_3=yes&payment=%7B%22sys%22%3A%22custom.payform%22%2C%22systranid%22%3A%220%22%2C%22orderid%22%3A%221868223462%22%2C%22products%22%3A%5B%22%D0%A2%D0%B0%D1%80%D0%B8%D1%84+%D0%9E%D0%BF%D1%82%D0%B8%D0%BC%D1%83%D0%BC%3D7900%22%5D%2C%22amount%22%3A%227900%22%7D&formid=form777641779&formname=Cart"    
]

url_data = [
    "http://127.0.0.1:8000/this/is/buy",
    "https://aleksandramanicureserver.ru/this/is/buy",
    "https://aleksandramanicureserver.requestcatcher.com/test"
]

header = {
    'tuna-skip-browser-warning': ''
}

requests.post(url=url_data[0], data = post_data[1])
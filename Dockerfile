FROM python:3.11.9-slim
# Установка python

WORKDIR /app 
# Рабочая директория

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt
# Копирование и установка зависимостей

COPY . .
# Копирование всех файлов

ENV PYTHONPATH=/

CMD ["python", "-m", "src.webserver"]
# Запуск экземпляра
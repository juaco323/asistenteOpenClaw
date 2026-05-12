FROM python:3.12-slim

WORKDIR /app

COPY integrations/telegram-bot/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY integrations/telegram-bot /app

CMD ["python", "-m", "app.main"]

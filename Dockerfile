FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN PLAYWRIGHT_BROWSERS_PATH=/tmp/browsers python -m playwright install chromium --with-deps

ENV PLAYWRIGHT_BROWSERS_PATH=/tmp/browsers

COPY . .

EXPOSE 8000

CMD gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --access-logfile -

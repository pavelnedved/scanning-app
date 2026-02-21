FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY scanning_app/ scanning_app/

ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=8080
ENV FLASK_DEBUG=false

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]

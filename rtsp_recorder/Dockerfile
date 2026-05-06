FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update
RUN apt install -y libxcb1 libgl1 libglib2.0-0

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app
COPY .env /app/
COPY ./*.py /app/

CMD ["python", "main.py"]

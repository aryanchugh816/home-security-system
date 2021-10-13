FROM python:3.7-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY . .
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--reload"]
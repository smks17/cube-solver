FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt .
RUN pip install --quiet -r requirements.txt

COPY . .

CMD ["python", "main.py"]

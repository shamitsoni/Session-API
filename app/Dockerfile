FROM python:3.12-alpine

WORKDIR /app

COPY app.py requirements.txt ./

RUN pip install -r requirements.txt

RUN apk add curl

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
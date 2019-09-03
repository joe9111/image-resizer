FROM python:3.6-alpine
WORKDIR /code
ENV FLASK_APP kafka_consumer/consumer.py
ENV FLASK_RUN_HOST 0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev
COPY requirements.txt requirements.txt
RUN apk --update add \
    build-base \
    jpeg-dev \
    zlib-dev
RUN pip install -r requirements.txt
COPY . .
# CMD ["flask", "run", "--host", "0.0.0.0"]
CMD ["python3", "kafka_consumer/consumer.py"]
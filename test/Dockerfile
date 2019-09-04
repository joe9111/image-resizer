FROM python:3.6-alpine
WORKDIR /code
ENV FLASK_APP kafka_producer/app.py
ENV FLASK_RUN_HOST 0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev
COPY requirements.txt requirements.txt
RUN apk --update add \
    build-base \
    jpeg-dev \
    zlib-dev
RUN pip install -r requirements.txt
COPY . .
# COPY test/ .
# COPY kafka_producer/ .
# COPY kafka_producer .
# COPY test .

# ADD test/ .
# RUN ls /code
# CMD ["python3", "-m", "pytest"]
ENTRYPOINT [ "sh" ]
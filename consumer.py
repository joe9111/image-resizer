from flask import Flask, Response
from kafka import KafkaConsumer
import logging

logger = logging.getLogger('ftpuploader')
# connect to Kafka server and pass the topic we want to consume
consumer = KafkaConsumer('my-topic', group_id='view',
                         bootstrap_servers=['kafka:9092'], api_version=(0, 10, 0))


# Continuously listen to the connection and print messages as recieved
app = Flask(__name__)


@app.route('/')
def index():
    # return a multipart response
    logger.warning('Sending to kafka!')
    return Response(kafkastream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def kafkastream():
    logger.warning('Sending to kafka!')
    for msg in consumer:
        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + msg.value + b'\r\n\r\n')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

import eventlet
eventlet.monkey_patch()

import sys
import json
import requests

from kafka import KafkaConsumer
from concurrent.futures import ThreadPoolExecutor

def process_message(data):
    message = data.get('data', "Empty data!")
    sid = data.get('sid', "")
    message = message[::-1]
    print('answering:' + message)
    response = requests.post('http://localhost:5011/send', json={'message':'Brain said: '+message,'sid':sid})
    print('response.status_code:' + str(response.status_code))
    sys.stdout.flush()

def main(args=None):
    # To consume latest messages and auto-commit offsets
    consumer = KafkaConsumer('to_bot',
                            bootstrap_servers=['localhost:9092'],
                            value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    executor = ThreadPoolExecutor(max_workers=2)
    for message in consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                            message.offset, message.key,
                                            message.value))
        executor.submit(process_message, message.value)

if __name__ == "__main__":
    main()
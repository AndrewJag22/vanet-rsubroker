import time
import paho.mqtt.client as paho
import hashlib, ssl, requests, pickle, json, threading, logging
import pandas as pd
import concurrent.futures

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s', filename='/var/log/mqttsubscriber.log')

# Connection parameters
broker = "192.168.0.112"
port = 8883
root_ca = "/etc/certs/ca.crt"
client_crt = "/etc/certs/broker.crt"
private_key = "/etc/certs/broker.key"
topic = "vanet/messages"

# Method called when a new message has been received from broker
def on_message(client, userdata, message):
    # Creates a new thread for each message received
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(message_to_blockchain, message)
        return_value = future.result()
        logging.info(return_value)

# Method for uploading to the blockchain
def message_to_blockchain(message):
    start_time = time.time()
    logging.info("Received message")
    try:
        df = pickle.loads(message.payload)
        payload = json.dumps({"MessageBody": df.set_index('Element')['Value'].to_dict()})
        headers = {'content-type': 'application/json'}
        response = requests.post('http://localhost:5000/new_transaction',
                               data=payload, headers=headers)
        logging.info("Time taken to process message to blockchain " + time.time()-start_time)
        if "Success" in response:
            return "Successfully added transaction to blockchain"
        else:
            return response
    except:
        return "There was a problem"
    finally:
        return "Thread is closed"
   



client= paho.Client()  
client.on_message=on_message
client.mid_value=None
client.tls_set(ca_certs=root_ca,
            certfile=client_crt,
            keyfile=private_key,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers=None)

print("Connecting to broker",broker)
client.connect(broker, port)

print("Subscribing to", topic)
client.subscribe(topic)

# Keeps the client alive
client.loop_forever()


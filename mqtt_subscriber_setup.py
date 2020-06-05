import time, sys
import paho.mqtt.client as paho
import hashlib, ssl, requests, pickle, argparse, json, threading, logging
import pandas as pd
import concurrent.futures

# For creating logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s', filename='/var/log/mqttsubscriber.log')
logger = logging.getLogger(__name__)

# Connection parameters
with open ("/etc/mqtt/ip_address", "r") as ip_address:
    broker = ip_address.readline().rstrip('\n')
port = 8883
root_ca = "/etc/mqtt/ca.crt"
client_crt = "/etc/mqtt/" + broker + ".crt"
private_key = "/etc/mqtt/" + broker + ".key"
topic = "vanet/messages"

# Method called when a new message has been received from broker
def on_message(client, userdata, message):
    # Creates a new thread for each message received
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(message_to_blockchain, message)
        return_value = future.result()
        print(return_value)
        if return_value[0] != 'No response':
            logging.info('Post status: ' + return_value[0].status_code.__str__() + ', Time taken to add transaction: ' + return_value[2].__str__())
        else:
            logging.info('Post status: ' + return_value[0] + ', Errors: ' + return_value[1].__str__())

# Method for uploading to the blockchain
def message_to_blockchain(message):
    start_time = time.time()
    error = 'None'
    response = 'No response'
    end_time = ''
    try:
        df = pickle.loads(message.payload)
        payload = json.dumps({'MessageBody': df.set_index('Element')['Value'].to_dict()})
        headers = {'content-type': 'application/json'}
        response = requests.post('http://localhost:5000/new_transaction',
                               data=payload, headers=headers)
        end_time = time.time() - start_time
    except:
        error = sys.exc_info()[1]
    finally:
        return [response, error, end_time]
   



client = paho.Client()  
client.on_message=on_message
client.mid_value=None
client.tls_set(ca_certs=root_ca,
            certfile=client_crt,
            keyfile=private_key,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers=None)

client.enable_logger(logger)

client.username_pw_set('blockchainclient',password='blockchain')

print("Connecting to broker",broker)
client.connect(broker, port)

print("Subscribing to", topic)
client.subscribe(topic)

# Keeps the client alive
client.loop_forever()


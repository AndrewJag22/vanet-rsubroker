# Generates private key used for blockchain
python3 private_key_generator.py

# Creates the broker's key and csr for mqtt connection
./broker_csr_key_gen.sh

# Sends the created crs to the CA for certification
./mqttbrokerca.sh

# Creates cron jobs to perform mqtt subscriber setup and run the blockchain whenever the server is put on
crontab -l > current_cron
cat >> current_cron << EOF
@reboot /etc/mosquitto/./broker_server.exp
@reboot /etc/blockchain/./sub_script.exp
@reboot python3 /etc/blockchain/rsu_blockchain.py
EOF
crontab < current_cron
rm -f current_cron

# Creates copies of mqtt broker and subscriber and, blockchain executable files
cp broker_server.exp /etc/mosquitto/./broker_server.exp
cp sub_script.exp /etc/blockchain/sub_script.exp
cp mqtt_subscriber_setup.py /etc/blockchain/mqtt_subscriber_setup.py
cp rsu_blockchain.py /etc/blockchain/rsu_blockchain.py

# Starts up the mqtt broker and subscriber and, blockchain
/etc/mosquitto/./broker_server.exp 
/etc/blockchain/./sub_script.exp
python3 /etc/blockchain/rsu_blockchain.py

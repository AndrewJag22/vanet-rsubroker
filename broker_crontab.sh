BLOCKCHAINDIR=/etc/blockchain

if test -e "$BLOCKCHAINDIR"; then
    echo "/etc/blockchain directory already exists"
else
    mkdir "$BLOCKCHAINDIR"
    echo "Created /etc/blockchain directory"
fi

# Installing dependencies
apt-get install -y python3-flask python3-pandas
sudo -H pip3 install paho-mqtt

# Generates private key used for blockchain
python3 private_key_generator.py

# Creates the broker's key and csr for mqtt connection
./broker_csr_key_gen.sh

# Sends the created crs to the CA for certification
./mqttbrokerca.sh

# Creates copies of mqtt broker and subscriber and, blockchain executable files
cp broker.exp /etc/mosquitto/broker.exp
cp sub_script.exp /etc/blockchain/sub_script.exp
cp mqtt_subscriber_setup.py /etc/blockchain/mqtt_subscriber_setup.py
cp rsu_blockchain.py /etc/blockchain/rsu_blockchain.py
cp broker_csr_key_gen.sh /etc/certs/broker_csr_key_gen.sh
cp mqttbrokerca.sh /etc/certs/mqttbrokerca.sh

# Adds executable attribute to scripts
chmod +x broker_csr_key_gen.sh
chmod +x mqttbrokerca.sh
chmod +x /etc/mosquitto/broker.exp
chmod +x /etc/blockchain/sub_script.exp

# Copies services to /lib/systemd/system folder
cp rsu_blockchain.service /lib/systemd/system/rsu_blockchain.service
cp sub_script.service /lib/systemd/system/sub_script.service
cp broker.service /lib/systemd/system/broker.service

# Creates cron jobs to perform mqtt broker and subscriber setup and run the blockchain whenever the server is put on
crontab -l > current_cron
cat >> current_cron << EOF
@reboot systemctl start sub_script.service
@reboot systemctl start rsu_blockchain.service
@reboot systemctl start broker.service
EOF
crontab < current_cron
rm -f current_cron

# Starts up the mqtt broker and subscriber and, blockchain services
systemctl daemon-reload

systemctl enable sub_script.service
systemctl start sub_script.service

systemctl enable rsu_blockchain.service
systemctl start rsu_blockchain.service

systemctl enable broker.service
systemctl start broker.service

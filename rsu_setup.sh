BLOCKCHAINDIR=/etc/blockchain
CERTDIR=/etc/mqtt
RSUIP=$1
CASERVERIP=$2

if test -e "$BLOCKCHAINDIR"; then
    echo "/etc/blockchain directory already exists"
else
    mkdir "$BLOCKCHAINDIR"
    echo "Created /etc/blockchain directory"
fi

if test -e "$CERTDIR"; then
    echo "/etc/mqtt directory already exists"
else
    mkdir "$CERTDIR"
    echo "Created /etc/mqtt directory"
fi

# Creates file containing RSU IP address
echo "$RSUIP" > /etc/mqtt/ip_address

# Installing dependencies
apt-get install -y mosquitto python3-flask python3-pandas python3-ecdsa sshpass python3-pip expect
sudo -H pip3 install paho-mqtt

# Creates copies of mqtt broker and subscriber and, blockchain executable files
cp broker.exp /etc/mosquitto/broker.exp
cp sub_script.exp /etc/mqtt/sub_script.exp
cp mqtt_subscriber_setup.py /etc/mqtt/mqtt_subscriber_setup.py
cp rsu_blockchain.py /etc/blockchain/rsu_blockchain.py
cp rsu_csr_key_gen.sh /etc/mqtt/rsu_csr_key_gen.sh
cp mqttrsuca.sh /etc/mqtt/mqttrsuca.sh

# Adds executable attribute to scripts
chmod +x rsu_csr_key_gen.sh
chmod +x mqttrsuca.sh
chmod +x /etc/mqtt/rsu_csr_key_gen.sh
chmod +x /etc/mqtt/mqttrsuca.sh
chmod +x /etc/mosquitto/broker.exp
chmod +x /etc/mqtt/sub_script.exp

# Generates private key used for blockchain
python3 private_key_generator.py

# Creates the rsu's key and csr for mqtt connection
./rsu_csr_key_gen.sh $RSUIP

# Sends the created crs to the CA for certification
./mqttrsuca.sh $RSUIP $CASERVERIP

# Copies services to /lib/systemd/system folder
cp rsu_blockchain.service /lib/systemd/system/rsu_blockchain.service
cp sub_script.service /lib/systemd/system/sub_script.service
cp broker.service /lib/systemd/system/broker.service

# Mosquitto broker configuration
echo -e "\nallow_anonymous false\n\nacl_file /etc/mosquitto/aclfile\n\nport 8883\n\n#ssl settings\ncafile /etc/mqtt/ca.crt\nkeyfile /etc/mqtt/$RSUIP.key\ncertfile /etc/mqtt/$RSUIP.crt\ntls_version tlsv1.2\n\nrequire_certificate true\nuse_identity_as_username true" >> /etc/mosquitto/mosquitto.conf
echo -e "#General rule to allow publishing\npattern write vanet/messages\n\n#Only for broker to subscribe to that topic\nuser $RSUIP\ntopic readwrite vanet/messages" > /etc/mosquitto/aclfile

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

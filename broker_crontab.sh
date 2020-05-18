# Generates private key used for blockchain
python3 private_keygenerator.py

# Creates the broker's key and csr for mqtt connection
./broker_csr_key_gen.sh

# Sends the created crs to the CA for certification
./mqttbrokerca.sh

# Creates cron jobs to perform mqtt subscriber setup and run the blockchain whenever the server is put on
crontab -l > current_cron
cat >> current_cron << EOF
@reboot python3 mqtt_subscriber_setup.py
@reboot python3 rsu_blockchain.py
EOF
crontab < current_cron
rm -f current_cron
# vanet-rsubroker

This is the setup for the Road Side Units that will act as their own brokers for vehicles to connect to and publish messages to. Th RSU also subscribes to the topic to receive the messages sent by vehicles.

In the **broker_csr_key_gen.sh** file, the password as well as subjectinfo details should be changed accordingly. The Common Name field in subjectinfo (CN) must match the name of broker that would be connected to. In testing, this can be the IP address of the broker.

In the **mqttbrokerca.sh** file, the CAserverIP field will need an input. Before connecting to the CA server, it is necessary to do a manual ssh connection **as root** to verify the ssh host using the ECDSA key fingerprint and add to the CA server to known-hosts.

In the **mqtt_subscriber_setup.py** file, the  broker field will need the Common Name for the broker and the **sub_script.exp** file should also have the password changed.

It should be noted that the SSL connection required by MQTT is only supported by Python 3.6.x and lower.

On downloading and after making the above changes, the broker_setup.sh file should be run as root using command:

    sudo bash ./broker_setup.sh

The created file **/etc/mosquitto/aclfile** should have the broker ID changed and the broker service should be restarted using:
    systemctl restart broker.service
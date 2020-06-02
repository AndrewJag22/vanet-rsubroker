# vanet-rsubroker

This is the setup for the Road Side Units that will act as their own brokers for vehicles to connect to and publish messages to. Th RSU also subscribes to the topic to receive the messages sent by vehicles.

Input the IP address of the machine to the **RSUIP** fields within the following files: **rsu_csr_key_gen.sh**, **mqttrsuca.sh**, **rsu_setup.sh**.

In the **rsu_csr_key_gen.sh** file, the password as well as subjectinfo details should be changed accordingly.

In the **mqttrsuca.sh** file, the CASERVERIP field will need the IP address of the machine hosting CA Server. Before connecting to the CA server, it is necessary to do a manual ssh connection **as root** to verify the ssh host using the ECDSA key fingerprint and add to the CA server to known-hosts.

In the **mqtt_subscriber_setup.py** file, the  broker field will need the Common Name for the broker (IP address of the machine) and the **sub_script.exp** file should also have the password changed.

It should be noted that the SSL connection required by MQTT is only supported by Python 3.6.x and lower.

On downloading and after making the above changes, the rsu_setup.sh file should be run as root using command:

    sudo bash ./rsu_setup.sh

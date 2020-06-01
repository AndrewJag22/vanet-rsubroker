# vanet-rsubroker

This is the setup for the Road Side Units that will act as their own brokers for vehicles to connect to and publish messages to. Th RSU also subscribes to the topic to receive the messages sent by vehicles.

In the **broker_csr_key_gen.sh** file, the password as well as subjectinfo details should be changed accordingly. The Common Name field in subjectinfo (CN) must match the name of broker that would be connected to. In testing, this can be the IP address of the broker.

In the **mqttbrokerca.sh** file, the CAserverIP field will need an input

The sub_script.exp file should also have the password changed.

It should be noted that the SSL connection required by MQTT is only supported by Python 3.6.x and lower.

On downloading, the broker_setup.sh file should be run as root using command:

    sudo bash ./broker_setup.sh
# vanet-rsubroker

This is the setup for the Road Side Units that will act as their own brokers for vehicles to connect to and publish messages to. Th RSU also subscribes to the topic to receive the messages sent by vehicles.

In the **broker_csr_key_gen.sh"" file, the password as well as subjectinfo details should be changed accordingly

It should be noted that the SSL connection required by MQTT is only supported by Python 3.6.x and lower
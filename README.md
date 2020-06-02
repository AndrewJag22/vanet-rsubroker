# vanet-rsubroker

This is the setup for the Road Side Units that will act as their own brokers for vehicles to connect to and publish messages to. Th RSU also subscribes to the topic to receive the messages sent by vehicles.

In the **rsu_csr_key_gen.sh** file, the password as well as subjectinfo details should be changed accordingly. The **sub_script.exp** file should also have the password changed to match.

Before connecting to the CA server, it is necessary to do a manual ssh connection **as root** to verify the ssh host using the ECDSA key fingerprint and add the CA server to known-hosts using the command below:
    $ sudo sftp vanetclients@[IP address of CA Server]

It should be noted that the SSL connection required by MQTT is only supported by Python 3.6.x and lower.

On downloading and after making the above changes, the rsu_setup.sh file should be run as root using command:

    $ sudo bash ./rsu_setup.sh <IP Address of host machine> <IP address of CA Server>

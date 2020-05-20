export SSHPASS=vanetclients # Password to connect to sftp client profile of certification authority
cd /etc/certs
echo "Sending CSR to CA server"
# Connects to the sftp client for certification at username@ca_server_name to submit csr
sshpass -e sftp -oBatchMode=no -b - vanetclients@192.168.0.98 << !
   cd incoming_requests
   put broker.csr
   bye
!
echo "Receiving CA and client certificates"
sleep 1
# Connects to the sftp client for certification at username@ca_server_name to collect CA certificate and user certificate
sshpass -e sftp -oBatchMode=no -b - vanetclients@192.168.0.98 << !
   get ca.crt
   cd outgoing_certificates
   get broker.crt
   rm broker.crt
   bye
!
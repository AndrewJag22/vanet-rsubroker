export SSHPASS=vanetclients # Password to connect to sftp client profile of certification authority

RSUIP=$1
CASERVERIP=$2

cd /etc/mqtt
echo "Sending CSR to CA server"

# Connects to the sftp client for certification at username@ca_server_name to submit csr
sshpass -e sftp -oBatchMode=no -b - vanetclients@$CASERVERIP << !
   cd incoming_requests
   put $RSUIP.csr
   bye
!

echo "Receiving CA and client certificates"
sleep 1

# Connects to the sftp client for certification at username@ca_server_name to collect CA certificate and user certificate
sshpass -e sftp -oBatchMode=no -b - vanetclients@$CASERVERIP << !
   get ca.crt
   cd outgoing_certificates
   get $RSUIP.crt
   rm $RSUIP.crt
   bye
!
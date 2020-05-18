export SSHPASS=vanetclients
cd /etc/certs
echo "Sending CSR to CA server"
sshpass -e sftp -oBatchMode=no -b - vanetclients@192.168.0.98 << !
   cd incoming_requests
   put broker.csr
   bye
!
echo "Receiving CA and client certificates"
sleep 1
sshpass -e sftp -oBatchMode=no -b - vanetclients@192.168.0.98 << !
   get ca.crt
   cd outgoing_certificates
   get broker.crt
   rm broker.crt
   bye
!
export SSHPASS=vanetclients
cd /etc/certs
echo "Yup"
sshpass -e sftp -oBatchMode=no -b - vanetclients@192.168.0.98 << !
   cd incoming_requests
   put broker.csr
   bye
!
echo "Done"
sleep 2
sshpass -e sftp -oBatchMode=no -b - vanetclients@192.168.0.98 << !
   cd outgoing_certificates
   get ca.crt
   get broker.crt
   rm broker.crt
   bye
!
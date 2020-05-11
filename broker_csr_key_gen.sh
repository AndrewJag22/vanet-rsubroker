SUBINFO=/etc/certs/subjectinfo
PASSFILE=/etc/certs/passwordfile

while IFS="," read -r f1 f2 f3 f4 f5 f6
do
    CO="$f1"
    ST="$f2"
    LO="$f3"
    OR="$f4"
    OU="$f5"
    CN="$f6"

    echo "$CO $ST $LO $OR $OU $CN"
done < "$SUBINFO"

CERTDIR=/etc/certs
FILE=/etc/certs/broker.key
FILE2=/etc/certs/broker.csr

if test -f "$CERTDIR"; then
    continue
else
    sudo mkdir "$CERTDIR"
fi

if test -f "$FILE"; then
    echo "PEM file exists"
    echo "**********Replacing file**********"
    sudo rm "$FILE"
    sudo rm "$FILE2"
    sudo openssl genrsa -des3 -out "$FILE" -passout file:$PASSFILE 2048
    sudo openssl req -out "$FILE2" -key "$FILE" -passin file:$PASSFILE -subj "/C=$CO/ST=$ST/L=$LO/O=$OR/OU=$OU/CN=$CN" -new
else
    echo "PEM file does not exist"
    sudo openssl genrsa -des3 -out "$FILE" -passout file:$PASSFILE 2048
    sudo openssl req -out "$FILE2" -key "$FILE" -passin file:$PASSFILE -subj "/C=$CO/ST=$ST/L=$LO/O=$OR/OU=$OU/CN=$CN" -new
fi

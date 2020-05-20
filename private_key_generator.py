import ecdsa
from hashlib import sha256

filename = "/etc/blockchain/blockchain_private_key"
my_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha256)

fd = open(filename, "w+")
fd.write(my_key.to_string().hex())

fd.close()


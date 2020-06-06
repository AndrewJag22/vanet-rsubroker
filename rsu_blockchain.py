from flask import Flask, request
import hashlib, json, time, ecdsa, requests, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s', filename='/var/log/blockchain.log')

# Extracts Private and Public keys for blockchain use
filename = '/etc/blockchain/blockchain_private_key'
fd = open(filename, 'r')
private_key = ecdsa.SigningKey.from_string(bytes.fromhex(fd.read()), curve=ecdsa.SECP256k1)
pub_key = private_key.get_verifying_key()

class Transaction:
    def __init__(self, transaction):
        self.data = transaction['MessageBody']
        self.timestamp = transaction['timestamp']
        

class Block:
    def __init__(self, timestamp, transactions, public_key, previous_hash = ''):
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.block_creator_public_key = public_key 
    
    # Create hash of data block
    def calculate_hash(self):
        self.block_hash = hashlib.sha256((self.timestamp.__str__() + json.dumps(self.transactions) + self.previous_hash).encode('utf-8')).hexdigest()

    def add_hash_and_signature(self, block_hash, block_signature):
        self.block_hash = block_hash
        self.block_signature = block_signature

    def sign_block(self, signing_key):
        # Compares value of verifying key generated to that of the public key
        if signing_key.get_verifying_key().to_string().hex() != self.block_creator_public_key:
            raise Exception('You cannot create block for another node')
        else:
            # Signs the block to be added to the chain
            self.block_signature = signing_key.sign(bytes(self.block_hash, 'utf-8')).hex()

    def is_block_valid(self, last_block):

        # Compares the previous_hash value of the new block to the hash of the last block in the chain
        if self.previous_hash != last_block.block_hash:
            return False

        # Checks the presence of the signature value in the block
        if len(self.block_signature) == 0 or not self.block_signature:
            return False

        # Verifies the signature of the block hash    
        return pub_key.verify(bytes.fromhex(self.block_signature), bytes(self.block_hash, 'utf-8'))



class Blockchain:
    def __init__(self):
        self.pending_transactions = []
        self.chain = [self.create_genesis_block()]
    
    # Create Genesis block for blockchain
    def create_genesis_block(self):
        genesis_block = Block(time.time(), '', pub_key.to_string().hex())
        genesis_block.calculate_hash()
        genesis_block.sign_block(private_key)
        return genesis_block

    # Add transactions to a pending transactions list and when the number of pending transactions get to 5, a new block is created
    def add_transactions(self, transaction):
        trans = Transaction(transaction)
        self.pending_transactions.append(trans.__dict__)
        logging.info('New transaction added')

        if(len(self.pending_transactions) == 5):
            consensus()
            new_block = Block(time.time(), self.pending_transactions, pub_key.to_string().hex(), self.get_last_block().block_hash)
            new_block.calculate_hash()
            new_block.sign_block(private_key)
            self.add_block_to_chain(new_block, True)
            self.pending_transactions = []
    
    # Appends new block to the chain
    def add_block_to_chain(self, block, announce=False):
        last_block = self.get_last_block()

        if not block.is_block_valid(last_block):
            logging.info('Block cannot be added because it is invalid')
            return False
        self.chain.append(block)

        # Checks if the new block is being created by the node
        if announce:
            announce_new_block(block)

        logging.info('New Block added to Blockchain')
        return True

    # Gets the last block present in the blockchain
    def get_last_block(self):
        return self.chain[-1]

    # Checks validity of blockchain
    def check_chain_validity(self, chain):
        for block in chain:
            if not block.is_block_valid():
                return False
        return True


app = Flask(__name__)

# Initialize a blockchain object.
blockchain = Blockchain()

# Contains the host addresses of other participating members of the network
peers = []

# Endpoint for adding new transactions which is referenced in the subscribe file
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    transaction_data = request.get_json()

    transaction_data['timestamp'] = time.time()
    blockchain.add_transactions(transaction_data)

    return 'Success', 201

# Endpoint for requesting blockchain
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    logging.info('Sending chain dump')
    return json.dumps({'length': len(chain_data), 'chain': chain_data})

# Endpoint to add new peers to the network
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    # The host address to the peer node 
    node_address = request.get_json()['node_address']
    registration_status = request.get_json()['registration_status']
    if not node_address:
        return 'Invalid data', 400

    # Add the node to the peer list
    if not node_address in peers:
        peers.append(node_address)
        logging.info(node_address + ' has been added to peers')
     
    # Checks if node has been registered with another node
    if registration_status == 'True':
        return 'Peer has been registered by another'

    # Return the blockchain to the newly registered node so that it can sync
    data_dump = get_chain()
    data = json.loads(data_dump)
    data['peers'] = peers
    return json.dumps(data)

# Enpoint to unregister node from peers list
@app.route('/unregister_node', methods=['POST'])
def unregister_peer():
    node_addresses = request.get_json()['node_addresses']
    if not node_addresses:
        return "Invalid data", 400
    
    for node_address in node_addresses:
        if node_address not in peers:
            print(node_address + ' not in peers list')
            return node_address + ' not in peers list'
        else:
            peers.remove(node_address)
            headers = {'Content-Type': "application/json"}

            for peer in peers:
                response = requests.post(peer + "unregister_node", data=request.get_json(), headers=headers)
                logging.info(response.url + " " + response.content + " " + response.status_code)
        
            return 'Successfully unregistered ' + node_address, 200

# Endpoint to resgister node with existing node
@app.route('/register_with', methods=['POST'])
def register_with_existing_node():

    # Gets node address of existing node from post request
    node_address = request.get_json()['node_address']
    if not node_address:
        return 'Invalid data', 400

    logging.info('Registering with ' + node_address)

    data = {'node_address': request.host_url,
            'registration_status': 'False'}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(node_address + 'register_node',
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers

        # Checks if node has been added to peers
        if not node_address in peers:
            peers.append(node_address)
            logging.info(node_address + ' has been added to peers')
        
        # Creates blockchain from acquired chain dump
        chain_dump = response.json()['chain']
        create_chain_from_dump(chain_dump)

        # Adds peers from existing node's peers
        for peer in response.json()['peers']:
            if peer in peers or peer == request.url_root:
              continue  

            peers.append(peer)

        # Registers node with other peers in the network
        data = {'node_address': request.host_url,
                'registration_status': 'True'}
        headers = {'Content-Type': 'application/json'}

        for peer in peers:
            if peer != node_address:
                response = requests.post(peer + 'register_node',
                                data=json.dumps(data), headers=headers)

        return 'Registration successful', 200
    else:
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    blockchain.chain.clear()
    for index, block_data in enumerate(chain_dump):
        block = Block(block_data['timestamp'],
                      block_data['transactions'],
                      block_data['block_creator_public_key'],
                      block_data['previous_hash'],
                      )

        block.add_hash_and_signature(block_data['block_hash'], block_data['block_signature'])
        if index > 0:
            added = blockchain.add_block_to_chain(block)
            if not added:
                raise Exception('The chain dump is tampered!!')
        else:
            blockchain.chain.append(block)

# Endpoint for adding a new block to the chain
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()['block']
    block = Block(block_data['timestamp'],
                      block_data['transactions'],
                      block_data['block_creator_public_key'],
                      block_data['previous_hash'],
                      )
    block.add_hash_and_signature(block_data['block_hash'], block_data['block_signature'])
    added = blockchain.add_block_to_chain(block)

    if not added:
        return 'The block was discarded by the node', 400

    return 'Block added to the chain', 201

# Announces new block that has been created
def announce_new_block(block):
    block_data = {'block': block.__dict__}
    headers = {'Content-Type': 'application/json'}
    for peer in peers:
        url = '{}add_block'.format(peer)
        requests.post(url, data=json.dumps(block_data), headers=headers)

# Checks to see the longest chain the network
def consensus():
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for peer in peers:
        response = requests.get('{}chain'.format(peer))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain

# Flask app settings
if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=5000)
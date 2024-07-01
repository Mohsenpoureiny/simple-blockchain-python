from time import time
import json
import hashlib 
import requests
from urllib.parse import urlparse


class Block:
    def __init__(self, index, timestamp, trxs, nounce , previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.trxs = trxs
        self.nounce = nounce
        self.previous_hash = previous_hash

    def __hash__(self):
        ''' hash a block '''
        return Block.hashblock(self.__str__().encode())

    @staticmethod
    def hashblock(phase):
        return hashlib.sha256(hashlib.sha256(phase).hexdigest().encode()).hexdigest()
    
    def is_valid(self):
        '''checks if this proof is fine or not '''
        DL = 3
        return self.__hash__().startswith(DL * '0')
    
    def __str__(self):
        return json.dumps(self.__dict__(),sort_keys=True)
    
    def __dict__(self):
        _block = {
            "index": self.index,
            "timestamp": self.timestamp,
            "trxs": self.trxs,
            "nounce": self.nounce,
            "previous_hash": self.previous_hash
        }
        return _block

class Blockchain:
    ''' defines a block chain on one machine '''
    def __init__(self):

        self.chain = []

        self.mempool = []

        genesis_block = Block(index=0,timestamp=time(),trxs=[],nounce=0,previous_hash=0)

        self.chain.append(genesis_block)

        self.nodes = set()

    def __chain__(self):
        _chain = []
        for b in self.chain:
            _chain.append(b.__dict__())
        return _chain
    
    def new_block(self, block ):
        ''' create a new block '''
        if(block.is_valid()):
            
            for tri in block.trxs:
                for trmem,i in self.mempool:
                    if tri["headers"]["hash"] == trmem["headers"]["hash"]:
                        del self.mempool[i]
            
            self.chain.append(block)

            return block
    


    def new_trx(self,ts,transactions=[],):
        ''' add a new trx to the mempool '''
        trx = {
            "headers": {
                "hash": "0"
            },
            "body":{
                "timestamp": ts,
                "transactions":transactions,
            }
        }
        trx["headers"]["hash"] = hashlib.sha512(json.dumps(trx["body"], sort_keys=True).encode()).hexdigest()
        for _trx in self.mempool:
            if _trx["headers"]["hash"] == trx["headers"]["hash"]:
                return trx
        self.mempool.append(trx)

        return trx



    def register_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def valid_chain(self,chain):
        """ check if the chain is valid """
        last_block=chain[0]
        current_index =0 
        while current_index < len(chain):
            block = chain[current_index]

            current_index = 1

            if block.previous_hash != Block.hashblock(last_block):
                return False
            if not self.valid_proof(last_block.nounce, block.nounce):
                return False
            
            last_block = block
            current_index += 1
    
        return True
    
    def resolve_conflicts(self):
        """ checks All nodes and select the best """

        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f"http://{node}/chain")
            if response.status_code ==200:
                length = response.json()["length"]
                chain = response.json()["chain"]
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        
        if new_chain:
            self.chain = new_chain
            return True
        
        return False
    
    def inform_trx_nodes(self,trx):
        """ inform nodes to new transaction """

        neighbours = self.nodes

        for node in neighbours:
            try:
                requests.post(f"http://{node}/transaction",json={
                    "timestamp":trx["timestamp"],
                    "transactions":trx["transactions"],
                })
            except:
                pass

    @property
    def last_block(self):
        ''' return last block '''
        return self.chain[-1]
    


    def proof_of_work(self, last_proof):
        ''' shows that the work is done '''
        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof



from flask import Flask, jsonify, request
from uuid import uuid4
import sys
from bc import Blockchain, Block
import json
from time import time

app = Flask(__name__)

node_id = str(uuid4())

blockchain = Blockchain()

@app.route('/mine', methods=["POST"])
def mine():
    '''this will mine a block and add it to the chain'''
    values = request.get_json()
    block = Block(
        index=len(blockchain.chain), 
        trxs=values['trxs'],
        timestamp=values['timestamp'],
        nounce=values['nounce'],
        previous_hash=blockchain.chain[-1].__hash__(),
    )
    if block.is_valid():
        block = blockchain.new_block(block)
        res = {
            "message": "block created",
            'index': block.index,
            'trxs': block.trxs,
            'nounce': block.nounce,
            'previous_hash': block.previous_hash,
        }
        return jsonify(res),200
    else:
        res = {
            "message": "block is invalid",
        }
        return jsonify(res),401

@app.route('/mempool')
def mempool():
    ''''''
    res = {
            "mempool": blockchain.mempool,
            'mempool_size': len(blockchain.mempool),
    }
    return jsonify(res),200


@app.route('/transaction', methods=['POST'])
def new_trx():
    ''' will add a new trx '''
    values = request.get_json()
    _trx = blockchain.new_trx(
        values['timestamp'] if "timestamp" in values else time(),
        values['transactions'],
    )
    blockchain.inform_trx_nodes(_trx["body"])
    res = {
        'message': "recived",
        "mempool": blockchain.mempool
    }
    return jsonify(res)


@app.route('/chain')
def full_chain():
    blockchain.resolve_conflicts()
    res = {
        'chain': blockchain.__chain__(),
        'length': len(blockchain.chain)
    }
    return jsonify(res)


@app.route('/nodes/register', methods=["POST"])
def register_node():
    values = request.get_json()

    nodes = values.get('nodes')

    for node in nodes:
        blockchain.register_node(node)
    blockchain.resolve_conflicts()
    res = {
        "message": "nodes added",
        "total_nodes": list(blockchain.nodes)
    }
    return jsonify(res)


@app.route('/consensus', methods=["POST"])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        res = {
            "message": 'replaced',
            'chain': blockchain.chain
        }
    else:
        res = {
                "message": 'Im the Best',
                'chain': blockchain.chain
        }
    
    return jsonify(res)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=sys.argv[1])
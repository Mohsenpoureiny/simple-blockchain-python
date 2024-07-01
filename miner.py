import requests
import json
from time import sleep
from bc import *
import os

nodeurl = os.environ.get("NODE_URL")
mempool = []

def update_mempool():
    global mempool
    mempool = json.loads(requests.get(nodeurl+"/mempool").content)["mempool"]




while True:
    update_mempool()
    if len(mempool) > 0:
        last_block = json.loads(
            requests.get(nodeurl+"/chain").content
                                )["chain"][-1]
        previous_hash = Block.hashblock(json.dumps(last_block,sort_keys=True).encode())
        block = Block(index=last_block["index"]+1,timestamp=time(), trxs=mempool,nounce=1,previous_hash=previous_hash)
        
        while block.is_valid() == False:
            block.nounce+=1.

        res = requests.post(nodeurl+"/mine",json={
            "timestamp":block.timestamp,
            "trxs": block.trxs,
            "nounce":block.nounce
        },)
        if res.status_code == 200:
            print(f"Block #{block.index} mined with nounce {block.nounce}")
        else:
            print(res.content)

    else:
        print("mempool is empty!")
        sleep(5)
        continue
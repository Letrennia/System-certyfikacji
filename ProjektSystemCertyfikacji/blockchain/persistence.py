# persistence.py
import json
from pathlib import Path
from .core import SimpleBlockchain, Block, SupplyChainSubchain

BLOCKCHAIN_FILE = Path("blockchain_data.json")
SUBCHAINS_FILE = Path("subchains_data.json")


def save_blockchain(blockchain: SimpleBlockchain):
    """Zapis prostego blockchaina do pliku JSON."""
    with BLOCKCHAIN_FILE.open("w", encoding="utf-8") as f:
        json.dump(blockchain.get_chain(), f, indent=4, ensure_ascii=False)
    
    # Zapis podłańcuchów
    subchains_data = {}
    for batch_id, subchain in blockchain.subchains.items():
        subchains_data[batch_id] = {
            "batch_id": subchain.batch_id,
            "certificate_id": subchain.certificate_id,
            "producer_id": subchain.producer_id,
            "chain": subchain.get_chain()
        }
    
    with SUBCHAINS_FILE.open("w", encoding="utf-8") as f:
        json.dump(subchains_data, f, indent=4, ensure_ascii=False)


def load_blockchain() -> SimpleBlockchain:
    """Wczytanie blockchaina z JSON jeżeli istnieje."""
    blockchain = SimpleBlockchain()

    if not BLOCKCHAIN_FILE.exists():
        return blockchain

    with BLOCKCHAIN_FILE.open("r", encoding="utf-8") as f:
        chain_data = json.load(f)

    blockchain.chain = []
    for block_data in chain_data:
        block = Block(
            index=block_data["index"],
            timestamp=block_data["timestamp"],
            data=block_data["data"],
            previous_hash=block_data["previous_hash"]
        )
        blockchain.chain.append(block)
    
    # Wczytanie podłańcuchów
    if SUBCHAINS_FILE.exists():
        with SUBCHAINS_FILE.open("r", encoding="utf-8") as f:
            subchains_data = json.load(f)
        
        for batch_id, subchain_data in subchains_data.items():
            subchain = SupplyChainSubchain(
                subchain_data["batch_id"],
                subchain_data["certificate_id"],
                subchain_data["producer_id"]
            )
            # Wczytanie bloków podłańcucha
            subchain.chain = []
            for block_data in subchain_data["chain"]:
                block = Block(
                    index=block_data["index"],
                    timestamp=block_data["timestamp"],
                    data=block_data["data"],
                    previous_hash=block_data["previous_hash"]
                )
                subchain.chain.append(block)
            
            blockchain.subchains[batch_id] = subchain

    return blockchain

# persistence.py
import json
from pathlib import Path
from .core import SimpleBlockchain, Block

BLOCKCHAIN_FILE = Path("blockchain_data.json")


def save_blockchain(blockchain: SimpleBlockchain):
    """Zapis prostego blockchaina do pliku JSON."""
    with BLOCKCHAIN_FILE.open("w", encoding="utf-8") as f:
        json.dump(blockchain.get_chain(), f, indent=4, ensure_ascii=False)


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

    return blockchain

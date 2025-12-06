import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any


class Block:

    def __init__(self, index: int, timestamp: str, data: Dict[str, Any], previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class SimpleBlockchain:

    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, datetime.now().isoformat(), {"message": "Genesis Block"}, "0")
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: Dict[str, Any]) -> Block:
        previous_block = self.get_latest_block()
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now().isoformat(),
            data=data,
            previous_hash=previous_block.hash
        )
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def get_chain(self) -> List[Dict]:
        return [block.to_dict() for block in self.chain]

    def register_certificate(self, certificate_id: str, certificate_data: Dict) -> str:
        data = {
            "type": "certificate_registration",
            "certificate_id": certificate_id,
            "certificate_number": certificate_data.get("certificate_number"),
            "holder_entity_id": certificate_data.get("holder_entity_id"),
            "valid_from": str(certificate_data.get("valid_from")),
            "valid_to": str(certificate_data.get("valid_to")),
            "certificate_type": certificate_data.get("certificate_type"),
            "authority_id": certificate_data.get("authority_id")
        }
        block = self.add_block(data)
        return block.hash

    def register_batch(self, batch_id: int, batch_data: Dict) -> str:
        data = {
            "type": "batch_registration",
            "batch_id": batch_id,
            "certificate_id": batch_data.get("certificate_id"),
            "name": batch_data.get("name"),
            "category": batch_data.get("category"),
            "production_date": str(batch_data.get("production_date")),
            "producer_id": batch_data.get("producer_id"),
            "amount": batch_data.get("amount"),
            "unit": batch_data.get("unit")
        }
        block = self.add_block(data)
        return block.hash

    def register_transfer(self, batch_id: int, from_entity: int, to_entity: int) -> str:
        data = {
            "type": "batch_transfer",
            "batch_id": batch_id,
            "from_entity_id": from_entity,
            "to_entity_id": to_entity,
            "transfer_date": datetime.now().isoformat()
        }
        block = self.add_block(data)
        return block.hash

    def verify_certificate(self, certificate_id: str) -> bool:
        for block in self.chain:
            if block.data.get("type") == "certificate_registration":
                if block.data.get("certificate_id") == certificate_id:
                    return True
        return False

    def get_batch_history(self, batch_id: int) -> List[Dict]:
        history = []
        for block in self.chain:
            if block.data.get("batch_id") == batch_id:
                history.append(block.to_dict())
        return history

    def get_certificate_batches(self, certificate_id: str) -> List[Dict]:
        batches = []
        for block in self.chain:
            if (block.data.get("type") == "batch_registration" and
                block.data.get("certificate_id") == certificate_id):
                batches.append(block.to_dict())
        return batches


_blockchain_instance = None


def get_blockchain() -> SimpleBlockchain:
    global _blockchain_instance
    if _blockchain_instance is None:
        _blockchain_instance = SimpleBlockchain()
    return _blockchain_instance
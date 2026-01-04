import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


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


class SupplyChainSubchain:
    """
    Podłańcuch blockchain dla śledzenia łańcucha dostaw (Track & Trace).
    Każdy podłańcuch jest przypisany do konkretnej partii produktu.
    """
    
    SUPPLY_CHAIN_STAGES = {
        'producer': 'Producent',
        'processor': 'Przetwórca',
        'distributor': 'Dystrybutor',
        'retailer': 'Sklep'
    }
    
    def __init__(self, batch_id: int, certificate_id: int, producer_id: int):
        self.batch_id = batch_id
        self.certificate_id = certificate_id
        self.producer_id = producer_id
        self.chain: List[Block] = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        genesis_data = {
            "type": "supply_chain_genesis",
            "batch_id": self.batch_id,
            "certificate_id": self.certificate_id,
            "producer_id": self.producer_id,
            "message": "Supply Chain Genesis Block"
        }
        genesis_block = Block(0, datetime.now().isoformat(), genesis_data, "0")
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
        # Zapis podłańcucha jest obsługiwany przez główny blockchain
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
    
    def register_production(self, 
                           harvest_date: Optional[str] = None,
                           production_date: str = None,
                           storage_conditions: str = None,
                           location: str = None,
                           additional_data: Dict = None) -> str:
        """Rejestracja etapu produkcji/zboru"""
        data = {
            "type": "production",
            "stage": "producer",
            "batch_id": self.batch_id,
            "certificate_id": self.certificate_id,
            "producer_id": self.producer_id,
            "harvest_date": harvest_date,
            "production_date": production_date,
            "storage_conditions": storage_conditions,
            "location": location,
            "timestamp": datetime.now().isoformat()
        }
        if additional_data:
            data.update(additional_data)
        
        block = self.add_block(data)
        return block.hash
    
    def register_processing(self,
                            processor_id: int,
                            processing_date: str,
                            storage_conditions: str,
                            transport_temperature: float,
                            location: str,
                            from_entity_id: int,
                            additional_data: Dict = None) -> str:
        """Rejestracja etapu przetwarzania"""
        data = {
            "type": "processing",
            "stage": "processor",
            "batch_id": self.batch_id,
            "certificate_id": self.certificate_id,
            "processor_id": processor_id,
            "processing_date": processing_date,
            "storage_conditions": storage_conditions,
            "transport_temperature": transport_temperature,
            "location": location,
            "from_entity_id": from_entity_id,
            "timestamp": datetime.now().isoformat()
        }
        if additional_data:
            data.update(additional_data)
        
        block = self.add_block(data)
        return block.hash
    
    def register_distribution(self,
                              distributor_id: int,
                              distribution_date: str,
                              storage_conditions: str,
                              transport_temperature: float,
                              location: str,
                              from_entity_id: int,
                              additional_data: Dict = None) -> str:
        """Rejestracja etapu dystrybucji"""
        data = {
            "type": "distribution",
            "stage": "distributor",
            "batch_id": self.batch_id,
            "certificate_id": self.certificate_id,
            "distributor_id": distributor_id,
            "distribution_date": distribution_date,
            "storage_conditions": storage_conditions,
            "transport_temperature": transport_temperature,
            "location": location,
            "from_entity_id": from_entity_id,
            "timestamp": datetime.now().isoformat()
        }
        if additional_data:
            data.update(additional_data)
        
        block = self.add_block(data)
        return block.hash
    
    def register_retail(self,
                       retailer_id: int,
                       retail_date: str,
                       storage_conditions: str,
                       location: str,
                       from_entity_id: int,
                       additional_data: Dict = None) -> str:
        """Rejestracja etapu sprzedaży detalicznej"""
        data = {
            "type": "retail",
            "stage": "retailer",
            "batch_id": self.batch_id,
            "certificate_id": self.certificate_id,
            "retailer_id": retailer_id,
            "retail_date": retail_date,
            "storage_conditions": storage_conditions,
            "location": location,
            "from_entity_id": from_entity_id,
            "timestamp": datetime.now().isoformat()
        }
        if additional_data:
            data.update(additional_data)
        
        block = self.add_block(data)
        return block.hash
    
    def get_full_history(self) -> List[Dict]:
        """Pobranie pełnej historii produktu 'od pola do stołu'"""
        return [block.to_dict() for block in self.chain]
    
    def get_chain(self) -> List[Dict]:
        return [block.to_dict() for block in self.chain]
    
    def get_supply_chain_map_data(self, geocode: bool = True) -> Dict:
        """
        Przygotowanie danych łańcucha dostaw w formacie odpowiednim do wyświetlenia na mapie.
        Zwraca strukturę z punktami (waypoints) i trasami między nimi.
        
        Args:
            geocode: Czy geokodować adresy na współrzędne geograficzne (domyślnie True)
        """
        waypoints = []
        routes = []
        
        stage_order = {
            'producer': 1,
            'processor': 2,
            'distributor': 3,
            'retailer': 4
        }
        
        stage_labels = {
            'producer': 'Producent',
            'processor': 'Przetwórca',
            'distributor': 'Dystrybutor',
            'retailer': 'Sklep'
        }
        
        # Filtrowanie tylko bloków reprezentujących etapy łańcucha dostaw (pomijamy genesis)
        supply_chain_blocks = [
            block for block in self.chain 
            if block.data.get('type') in ['production', 'processing', 'distribution', 'retail']
        ]
        
        for block in supply_chain_blocks:
            block_data = block.data
            stage_type = block_data.get('stage', 'unknown')
            stage_label = stage_labels.get(stage_type, stage_type)
            
            # Przygotowanie punktu na mapie
            waypoint = {
                "id": block.index,
                "order": stage_order.get(stage_type, 99),
                "stage": stage_type,
                "stage_label": stage_label,
                "location": block_data.get('location', 'Unknown'),
                "timestamp": block.timestamp,
                "date": block_data.get('production_date') or 
                       block_data.get('processing_date') or 
                       block_data.get('distribution_date') or 
                       block_data.get('retail_date') or 
                       block.timestamp,
                "block_hash": block.hash,
                "details": {
                    "storage_conditions": block_data.get('storage_conditions'),
                    "transport_temperature": block_data.get('transport_temperature'),
                    "harvest_date": block_data.get('harvest_date'),
                    "from_entity_id": block_data.get('from_entity_id'),
                }
            }
            
            # Dodanie informacji o uczestniku w zależności od typu etapu
            if stage_type == 'producer':
                waypoint["entity_id"] = block_data.get('producer_id')
                waypoint["entity_type"] = "producer"
            elif stage_type == 'processor':
                waypoint["entity_id"] = block_data.get('processor_id')
                waypoint["entity_type"] = "processor"
            elif stage_type == 'distributor':
                waypoint["entity_id"] = block_data.get('distributor_id')
                waypoint["entity_type"] = "distributor"
            elif stage_type == 'retailer':
                waypoint["entity_id"] = block_data.get('retailer_id')
                waypoint["entity_type"] = "retailer"
            
            # Dodanie dodatkowych danych jeśli istnieją
            if block_data.get('additional_data'):
                waypoint["details"].update(block_data.get('additional_data', {}))
            
            waypoints.append(waypoint)
        
        # Sortowanie waypoints według kolejności
        waypoints.sort(key=lambda x: (x["order"], x["timestamp"]))
        
        # Geokodowanie adresów na współrzędne geograficzne (jeśli włączone)
        if geocode:
            try:
                from .geocoding import geocode_address
                import time
                
                for waypoint in waypoints:
                    location_address = waypoint.get("location")
                    if location_address and location_address != 'Unknown':
                        geocoded = geocode_address(location_address, delay=1.0)
                        if geocoded:
                            waypoint["coordinates"] = {
                                "latitude": geocoded.get("latitude"),
                                "longitude": geocoded.get("longitude"),
                                "display_name": geocoded.get("display_name", location_address)
                            }
                        else:
                            waypoint["coordinates"] = None
                        # Opóźnienie między requestami (Nominatim rate limit)
                        time.sleep(1.0)
                    else:
                        waypoint["coordinates"] = None
            except Exception as e:
                # Jeśli geokodowanie się nie powiodło, kontynuuj bez współrzędnych
                print(f"Warning: Geocoding failed: {e}")
                for waypoint in waypoints:
                    waypoint["coordinates"] = None
        
        # Tworzenie tras między punktami (po sortowaniu)
        for idx in range(1, len(waypoints)):
            previous_waypoint = waypoints[idx - 1]
            current_waypoint = waypoints[idx]
            route = {
                "from": {
                    "id": previous_waypoint["id"],
                    "location": previous_waypoint["location"],
                    "stage": previous_waypoint["stage"],
                    "stage_label": previous_waypoint["stage_label"],
                    "coordinates": previous_waypoint.get("coordinates")
                },
                "to": {
                    "id": current_waypoint["id"],
                    "location": current_waypoint["location"],
                    "stage": current_waypoint["stage"],
                    "stage_label": current_waypoint["stage_label"],
                    "coordinates": current_waypoint.get("coordinates")
                },
                "transport_info": {
                    "temperature": current_waypoint["details"].get("transport_temperature"),
                    "timestamp": current_waypoint["timestamp"],
                    "date": current_waypoint["date"]
                }
            }
            routes.append(route)
        
        return {
            "batch_id": self.batch_id,
            "certificate_id": self.certificate_id,
            "producer_id": self.producer_id,
            "waypoints": waypoints,
            "routes": routes,
            "total_stages": len(waypoints),
            "journey_summary": {
                "start_location": waypoints[0]["location"] if waypoints else None,
                "end_location": waypoints[-1]["location"] if waypoints else None,
                "start_date": waypoints[0]["date"] if waypoints else None,
                "end_date": waypoints[-1]["date"] if waypoints else None,
                "stages_completed": len(waypoints)
            }
        }
    
    def to_dict(self) -> Dict:
        return {
            "batch_id": self.batch_id,
            "certificate_id": self.certificate_id,
            "producer_id": self.producer_id,
            "chain_length": len(self.chain),
            "is_valid": self.is_chain_valid(),
            "chain": self.get_chain()
        }


class SimpleBlockchain:

    def __init__(self):
        self.chain: List[Block] = []
        self.subchains: Dict[str, SupplyChainSubchain] = {}  # batch_id -> SupplyChainSubchain
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
        # Automatyczne zapisanie po dodaniu bloku
        self._save()
        return new_block
    
    def _save(self):
        """Wewnętrzna metoda zapisu blockchaina"""
        try:
            from .persistence import save_blockchain as persist_save
            persist_save(self)
        except Exception:
            # Ignorowanie błędów zapisu w trybie produkcyjnym
            pass

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
        
        # Tworzenie podłańcucha dla partii produktu
        certificate_id = batch_data.get("certificate_id")
        producer_id = batch_data.get("producer_id")
        if certificate_id and producer_id:
            subchain = SupplyChainSubchain(batch_id, certificate_id, producer_id)
            self.subchains[str(batch_id)] = subchain
            
            # Rejestracja adresu podłańcucha w głównym łańcuchu
            subchain_address_data = {
                "type": "subchain_creation",
                "batch_id": batch_id,
                "certificate_id": certificate_id,
                "subchain_address": subchain.get_latest_block().hash,
                "producer_id": producer_id
            }
            self.add_block(subchain_address_data)
        
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
    
    def get_subchain(self, batch_id: int) -> Optional[SupplyChainSubchain]:
        """Pobranie podłańcucha dla danej partii"""
        return self.subchains.get(str(batch_id))
    
    def create_subchain(self, batch_id: int, certificate_id: int, producer_id: int) -> SupplyChainSubchain:
        """Utworzenie nowego podłańcucha dla partii produktu"""
        subchain = SupplyChainSubchain(batch_id, certificate_id, producer_id)
        self.subchains[str(batch_id)] = subchain
        
        # Rejestracja adresu podłańcucha w głównym łańcuchu
        subchain_address_data = {
            "type": "subchain_creation",
            "batch_id": batch_id,
            "certificate_id": certificate_id,
            "subchain_address": subchain.get_latest_block().hash,
            "producer_id": producer_id
        }
        self.add_block(subchain_address_data)
        self._save()  # Zapis po utworzeniu podłańcucha
        
        return subchain
    
    def get_subchain_address(self, batch_id: int) -> Optional[str]:
        """Pobranie adresu podłańcucha z głównego łańcucha"""
        for block in self.chain:
            if (block.data.get("type") == "subchain_creation" and
                block.data.get("batch_id") == batch_id):
                return block.data.get("subchain_address")
        return None
    
    def get_all_subchains(self) -> Dict[str, Dict]:
        """Pobranie wszystkich podłańcuchów"""
        return {batch_id: subchain.to_dict() for batch_id, subchain in self.subchains.items()}
    
    def get_batch_supply_chain_history(self, batch_id: int) -> Optional[List[Dict]]:
        """Pobranie pełnej historii łańcucha dostaw dla partii (od pola do stołu)"""
        subchain = self.get_subchain(batch_id)
        if subchain:
            return subchain.get_full_history()
        return None
    
    def get_batch_supply_chain_map_data(self, batch_id: int) -> Optional[Dict]:
        """Pobranie danych łańcucha dostaw w formacie mapy dla partii"""
        subchain = self.get_subchain(batch_id)
        if subchain:
            return subchain.get_supply_chain_map_data()
        return None


_blockchain_instance = None


def get_blockchain() -> SimpleBlockchain:
    global _blockchain_instance
    if _blockchain_instance is None:
        # Wczytanie blockchaina z pliku jeśli istnieje
        try:
            from .persistence import load_blockchain
            _blockchain_instance = load_blockchain()
        except Exception:
            # Jeśli wczytanie się nie powiodło, utworzenie nowego
            _blockchain_instance = SimpleBlockchain()
    return _blockchain_instance


def save_blockchain():
    """Zapis blockchaina do pliku"""
    global _blockchain_instance
    if _blockchain_instance is not None:
        try:
            from .persistence import save_blockchain as persist_save
            persist_save(_blockchain_instance)
        except Exception as e:
            # Logowanie błędu, ale nie przerywanie działania
            print(f"Error saving blockchain: {e}")
"""
Moduł geokodowania adresów na współrzędne geograficzne.
Wykorzystuje darmowe API Nominatim (OpenStreetMap).
"""
import time
import urllib.parse
import urllib.request
import json
from typing import Optional, Dict


def geocode_address(address: str, delay: float = 1.0) -> Optional[Dict]:
    """
    Geokodowanie adresu używając Nominatim (OpenStreetMap) - darmowe API bez klucza.
    
    Args:
        address: Adres do geokodowania (np. "Warszawa, Polska")
        delay: Opóźnienie między requestami (Nominatim wymaga max 1 request/sekundę)
    
    Returns:
        Dict z kluczami: 'latitude', 'longitude', 'display_name', 'address' lub None
    """
    if not address or address == 'Unknown':
        return None
    
    try:
        # URL encode adresu
        encoded_address = urllib.parse.quote(address)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1"
        
        # Nominatim wymaga User-Agent
        headers = {
            'User-Agent': 'SupplyChainTracking/1.0 (contact@example.com)'
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            
            if data and len(data) > 0:
                result = data[0]
                return {
                    'latitude': float(result.get('lat', 0)),
                    'longitude': float(result.get('lon', 0)),
                    'display_name': result.get('display_name', address),
                    'address': address,
                    'provider': 'nominatim'
                }
        
        # Opóźnienie przed następnym requestem (Nominatim rate limit)
        time.sleep(delay)
        return None
        
    except Exception as e:
        print(f"Error geocoding address '{address}': {e}")
        return None


def batch_geocode_addresses(addresses: list, delay: float = 1.0) -> Dict[str, Optional[Dict]]:
    """
    Geokodowanie wielu adresów naraz z odpowiednim opóźnieniem.
    
    Args:
        addresses: Lista adresów do geokodowania
        delay: Opóźnienie między requestami (Nominatim rate limit: 1 request/sekundę)
    
    Returns:
        Dict: {address: geocoding_result}
    """
    results = {}
    
    for address in addresses:
        if address and address != 'Unknown':
            result = geocode_address(address, delay=delay)
            results[address] = result
            
            # Opóźnienie dla Nominatim (rate limiting)
            if delay > 0:
                time.sleep(delay)
        else:
            results[address] = None
    
    return results

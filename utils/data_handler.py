from typing import List, Dict
import json
import os
import hashlib
from .remote_storage import (
    remote_available,
    get_all_wishlists_remote,
    save_wishlists_index_remote,
    load_wishlist_remote,
    save_wishlist_remote,
)

DATA_DIR = 'data'

def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)

def get_wishlist_filename(wishlist_id: str) -> str:
    """Get filename for a specific wishlist"""
    return os.path.join(DATA_DIR, f"wishlist_{wishlist_id}.json")

def get_all_wishlists() -> List[Dict]:
    """Load all available wishlists (id and name only)"""
    if remote_available():
        return get_all_wishlists_remote()
    ensure_data_dir()
    index_file = os.path.join(DATA_DIR, 'wishlists_index.json')
    if os.path.exists(index_file):
        try:
            with open(index_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except:
            pass
    return []

def save_wishlists_index(wishlists: List[Dict]) -> None:
    """Save wishlists index"""
    if remote_available():
        return save_wishlists_index_remote(wishlists)
    ensure_data_dir()
    index_file = os.path.join(DATA_DIR, 'wishlists_index.json')
    with open(index_file, 'w', encoding='utf-8') as file:
        json.dump(wishlists, file, indent=4, ensure_ascii=False)

def create_wishlist(name: str, password: str) -> str:
    """Create a new wishlist and return its ID"""
    import hashlib
    
    # Generate unique ID from name and timestamp
    wishlist_id = hashlib.md5(f"{name}{os.urandom(8).hex()}".encode()).hexdigest()[:12]
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Create wishlist data
    wishlist_data = {
        "id": wishlist_id,
        "name": name,
        "password_hash": password_hash,
        "items": []
    }
    
    # Save wishlist file (use remote if available)
    if remote_available():
        save_wishlist_remote(wishlist_id, wishlist_data)
    else:
        ensure_data_dir()
        filename = get_wishlist_filename(wishlist_id)
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(wishlist_data, file, indent=4, ensure_ascii=False)
    
    # Update index
    wishlists = get_all_wishlists()
    wishlists.append({"id": wishlist_id, "name": name})
    save_wishlists_index(wishlists)
    
    return wishlist_id

def load_wishlist(wishlist_id: str) -> Dict:
    """Load a specific wishlist"""
    if remote_available():
        return load_wishlist_remote(wishlist_id)
    ensure_data_dir()
    filename = get_wishlist_filename(wishlist_id)
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except:
            pass
    return None

def save_wishlist(wishlist_id: str, data: Dict) -> None:
    """Save a specific wishlist"""
    if remote_available():
        return save_wishlist_remote(wishlist_id, data)
    ensure_data_dir()
    filename = get_wishlist_filename(wishlist_id)
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def verify_wishlist_password(wishlist_id: str, password: str) -> bool:
    """Verify password for a wishlist"""
    wishlist = load_wishlist(wishlist_id)
    if not wishlist:
        return False
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return wishlist.get('password_hash') == password_hash


def delete_wishlist(wishlist_id: str) -> bool:
    """Delete a wishlist by ID. Returns True if successful."""
    from .remote_storage import delete_wishlist_remote
    
    # Remove from index
    wishlists = get_all_wishlists()
    wishlists = [w for w in wishlists if w.get('id') != wishlist_id]
    save_wishlists_index(wishlists)
    
    # Delete the wishlist file
    if remote_available():
        delete_wishlist_remote(wishlist_id)
    else:
        filename = get_wishlist_filename(wishlist_id)
        if os.path.exists(filename):
            os.remove(filename)
    
    return True


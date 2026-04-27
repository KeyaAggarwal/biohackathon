import hashlib
import hmac
import json
import time

class BlackBoxChain:
    """
    Cryptographic Logging System for the SynthShield Device.
    Maintains an immutable, tamper-evident chain of synthesis and screening events.
    """
    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key
        self.chain = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Initialize the chain with a genesis block."""
        genesis_event = {"action": "genesis_block", "system": "SynthShield_v1"}
        # Use 64 zeros as the previous hash for the genesis block
        prev_hash = "0" * 64
        genesis_hash = self._calculate_hash(genesis_event, prev_hash)
        
        self.chain.append({
            "event": genesis_event,
            "hash": genesis_hash,
            "prev_hash": prev_hash
        })

    def _calculate_hash(self, event: dict, prev_hash: str) -> str:
        """
        Calculates the HMAC-SHA256 hash binding the event data with the previous block's hash.
        """
        # Deterministic serialization of the event dictionary
        event_string = json.dumps(event, sort_keys=True)
        
        # Bind event data with previous hash
        payload = f"{event_string}|{prev_hash}".encode('utf-8')
        
        # Generate HMAC using the hardware root of trust (secret key)
        return hmac.new(self.secret_key, payload, hashlib.sha256).hexdigest()

    def log_event(self, event: dict) -> str:
        """Log a new event into the cryptographic chain."""
        prev_hash = self.chain[-1]["hash"]
        
        # Add a timestamp if one isn't provided to ensure uniqueness
        if "timestamp" not in event:
            event["timestamp"] = str(time.time())
            
        new_hash = self._calculate_hash(event, prev_hash)
        
        block = {
            "event": event,
            "hash": new_hash,
            "prev_hash": prev_hash
        }
        self.chain.append(block)
        return new_hash

    def verify_chain(self) -> bool:
        """Verify the integrity of the entire chain to detect tampering."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            prev_block = self.chain[i-1]
            
            # 1. Check if the stored previous hash matches the actual hash of the previous block
            if current_block["prev_hash"] != prev_block["hash"]:
                return False
            
            # 2. Re-calculate the hash of the current block to ensure event data wasn't modified
            recalculated_hash = self._calculate_hash(current_block["event"], current_block["prev_hash"])
            if recalculated_hash != current_block["hash"]:
                return False
                
        return True

    def get_merkle_root(self) -> str:
        """
        Calculate the Merkle Root for all block hashes in the chain.
        Useful for periodic anchoring to an external ledger or ZK-Proof generation.
        """
        if not self.chain:
            return None
            
        # Start with the leaves (the hashes of our blocks)
        hashes = [block["hash"] for block in self.chain]
        
        # Build the tree bottom-up
        while len(hashes) > 1:
            # If odd number of leaves, duplicate the last one
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
            
            next_level = []
            for i in range(0, len(hashes), 2):
                combined = f"{hashes[i]}{hashes[i+1]}".encode('utf-8')
                next_level.append(hashlib.sha256(combined).hexdigest())
            
            hashes = next_level
            
        return hashes[0]
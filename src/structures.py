# ==============================================================================
# File: structures.py
# Module 2 of the Valorium X Simulator
# This module defines the core data structures of the blockchain:
# Transaction and Block, conceptually integrating the Quadrit system.
# Architect: Sylver Blade
# ==============================================================================

import time
import json
from quadrits import hash_data, string_to_quadrits, quadrits_to_string, Quadrit
from typing import List, Dict, Any

class Transaction:
    """
    Represents a single transaction. In a real implementation, all its
    data would be encoded into Quadrits.
    """
    def __init__(self, sender: str, recipient: str, amount: float, data: str = ''):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        # We simulate the data field being a string that gets converted to quadrits
        self.quadrit_data_payload = string_to_quadrits(data)
        self.timestamp = time.time()
        self.signature = None

    def get_payload_as_string(self) -> str:
        """Helper to get the quadrit data back as a string for display."""
        try:
            return quadrits_to_string(self.quadrit_data_payload)
        except ValueError:
            return "[Invalid Quadrit Payload]"

    def to_dict(self) -> Dict[str, Any]:
        """Returns the transaction data as a dictionary for hashing and signing."""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "quadrit_data_payload": [q.name for q in self.quadrit_data_payload], # Represent quadrits by names (A,T,C,G)
            "timestamp": self.timestamp
        }
        
    def calculate_hash(self) -> str:
        """Calculates the hash of the transaction."""
        tx_string = json.dumps(self.to_dict(), sort_keys=True)
        return hash_data(tx_string)

    def sign_transaction(self, signing_key):
        """Signs the transaction."""
        # Cryptographic signing logic (e.g., EdDSA) will be implemented here.
        # This proves the sender authorized the transaction.
        self.signature = "simulated_signature_of_" + self.calculate_hash()

    def is_valid(self) -> bool:
        """Validates the transaction's basic integrity."""
        # In a real system, we'd verify the signature here.
        # We also add a basic check for non-negative amounts.
        return self.sender and self.recipient and self.amount > 0

class Block:
    """Represents a single block in the First Helix."""
    def __init__(self, timestamp: float, transactions: List[Transaction], previous_hash: str):
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0 # Will be used later for CIP complexity simulation
        self.block_hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculates the hash of the entire block."""
        block_header_string = json.dumps({
            "timestamp": self.timestamp,
            # In a real implementation, this would be a Merkle Root.
            # For this simulator, we hash the list of transaction hashes.
            "transactions": [tx.calculate_hash() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hash_data(block_header_string)

    def mine_block(self, difficulty: int):
        """
        Placeholder for the complex consensus mechanism (CIP).
        For now, this simulates a simple Proof-of-Work to ensure blocks are not created instantly.
        """
        target = "0" * difficulty
        while self.block_hash[:difficulty] != target:
            self.nonce += 1
            self.block_hash = self.calculate_hash()
        print(f"    [WORK] Block Mined (CIP Simulated): {self.block_hash[:10]}...")

# --- Test Script ---
if __name__ == "__main__":
    print("--- Testing the Valorium X Structures Module ---")
    
    # 1. Create test transactions
    print("\n1. Creating test transactions...")
    tx1 = Transaction(sender="VQX_ΣA7C3_AXON", recipient="VQX_ΦB9F1_AXON", amount=100, data="Test Data 1")
    tx2 = Transaction(sender="VQX_ΦB9F1_AXON", recipient="VQX_ΣA7C3_AXON", amount=25, data="Response")
    print("  - Transaction 1 created.")
    print("  - Transaction 2 created.")
    
    # 2. Check transaction hashing
    print(f"\n2. Hash for Transaction 1: {tx1.calculate_hash()[:16]}...")
    
    # 3. Create a Genesis Block
    print("\n3. Creating Genesis Block...")
    genesis_block = Block(time.time(), [], "0")
    print(f"  - Genesis Block Hash: {genesis_block.block_hash[:16]}...")

    # 4. Create a new Block
    print("\n4. Creating a new block with transactions...")
    block1 = Block(time.time(), [tx1, tx2], genesis_block.block_hash)
    print(f"  - New Block Hash: {block1.block_hash[:16]}...")
    
    # 5. Simulate "mining" (CIP calculation)
    print("\n5. Simulating CIP calculation (mining)...")
    difficulty = 2 # A low difficulty for quick testing
    block1.mine_block(difficulty)
    print("  - Mining complete.")
    
    print("\n✅ SUCCESS: Block and Transaction structures are operational.")

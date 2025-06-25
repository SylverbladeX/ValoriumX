# ==============================================================================
# File: blockchain.py
# Module 3 of the Valorium X Simulator
# Version: 2.0
# Last Updated: 2025-06-20
#
# This module defines the Blockchain class, which manages the chain of blocks,
# state (balances), pending transactions, and validation logic.
# Architect: Sylver Blade
# ==============================================================================

import time
from structures import Block, Transaction
from typing import List, Dict

class Blockchain:
    """
    Manages the chain of blocks, state, pending transactions, and validation.
    """
    def __init__(self, difficulty: int = 2):
        # The chain starts with the Genesis Block
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = difficulty # Placeholder for PoW/CIP complexity
        # Pending transactions, our future "RNA Buffer Zone"
        self.pending_transactions: List[Transaction] = []
        self.mining_reward = 100 # A fixed reward for mining a new block
        # State Management for account balances
        self.balances: Dict[str, float] = {}

    def create_genesis_block(self) -> Block:
        """Creates the very first block in the chain (Block 0)."""
        # In a real implementation, this block would contain foundational information.
        return Block(timestamp=time.time(), transactions=[], previous_hash="0")

    @property
    def last_block(self) -> Block:
        """Returns the latest block in the chain."""
        return self.chain[-1]
    
    def get_balance_of_address(self, address: str) -> float:
        """Gets the current balance of a given address."""
        return self.balances.get(address, 0)

    def add_transaction(self, transaction: Transaction):
        """
        Adds a new transaction to the pending list after thorough validation.
        """
        if not transaction.sender or not transaction.recipient:
            raise ValueError("Transaction must include sender and recipient.")
        
        if not transaction.is_valid():
            raise ValueError("Cannot add invalid transaction.")

        # Validate sender's balance (unless it's a reward from the network)
        if transaction.sender != "Network Reward":
            sender_balance = self.get_balance_of_address(transaction.sender)
            if sender_balance < transaction.amount:
                raise ValueError("Insufficient funds.")
            
        self.pending_transactions.append(transaction)
        print(f"  [INFO] Transaction from {transaction.sender[:12]}... to {transaction.recipient[:12]}... for {transaction.amount} $VQXAI added to buffer.")


    def mine_pending_transactions(self, mining_reward_address: str):
        """
        Creates a new block with all pending transactions and adds it to the chain.
        This function would be triggered by a Validator Node in the real network.
        """
        # In a real system, the selection of transactions would be more complex.
        
        # Create the reward transaction for the miner/validator
        reward_tx = Transaction(sender="Network Reward", recipient=mining_reward_address, amount=self.mining_reward)
        self.pending_transactions.append(reward_tx)

        # Create the new block
        new_block = Block(
            timestamp=time.time(), 
            transactions=self.pending_transactions, 
            previous_hash=self.last_block.block_hash
        )
        
        # This simulates the work of Neural Nodes calculating the CIP
        new_block.mine_block(self.difficulty)
        
        print(f"  [SUCCESS] Block {len(self.chain)} successfully mined!")
        self.chain.append(new_block)
        
        # Update balances based on the transactions in the mined block
        for tx in self.pending_transactions:
            if tx.sender != "Network Reward": # Don't deduct from the network
                self.balances[tx.sender] -= tx.amount
            
            self.balances[tx.recipient] = self.get_balance_of_address(tx.recipient) + tx.amount

        # Reset pending transactions
        self.pending_transactions = []

    def is_chain_valid(self) -> bool:
        """
        Verifies the integrity of the entire blockchain by ensuring
        all blocks are correctly linked and hashed.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # 1. Check if the hash of the block is still correct
            if current_block.block_hash != current_block.calculate_hash():
                print(f"  [ERROR] Invalid hash for Block {i}: {current_block.block_hash}")
                return False
            
            # 2. Check if the block points correctly to the previous block's hash
            if current_block.previous_hash != previous_block.block_hash:
                print(f"  [ERROR] Invalid chain link between Block {i-1} and {i}.")
                return False
        return True

# --- Test Script ---
if __name__ == "__main__":
    print("--- Testing the Valorium X Blockchain Module ---")

    # 1. Initialize the blockchain
    valorium_chain = Blockchain(difficulty=2)
    print("\n1. Valorium X Blockchain initialized...")

    # 2. Set initial balances
    valorium_chain.balances["VQX_ΣA7C3_AXON"] = 500
    valorium_chain.balances["VQX_ΦB9F1_AXON"] = 200
    print("\n2. Initial balances set for test wallets.")

    # 3. Add transactions
    print("\n3. Adding transactions to the 'RNA Buffer'...")
    try:
        valorium_chain.add_transaction(Transaction(sender="VQX_ΣA7C3_AXON", recipient="VQX_ΦB9F1_AXON", amount=100))
        valorium_chain.add_transaction(Transaction(sender="VQX_ΦB9F1_AXON", recipient="VQX_ΨC2D4_AXON", amount=50))
    except ValueError as e:
        print(f"  [ERROR] {e}")

    # 4. Mine a block
    print("\n4. Mining a new block...")
    valorium_chain.mine_pending_transactions(mining_reward_address="SylverBlade_Wallet")

    # 5. Check balances
    print("\n5. Checking balances after mining:")
    print(f"  - Balance of VQX_ΣA7C3_AXON: {valorium_chain.get_balance_of_address('VQX_ΣA7C3_AXON')}")
    print(f"  - Balance of VQX_ΦB9F1_AXON: {valorium_chain.get_balance_of_address('VQX_ΦB9F1_AXON')}")
    print(f"  - Balance of VQX_ΨC2D4_AXON: {valorium_chain.get_balance_of_address('VQX_ΨC2D4_AXON')}")
    print(f"  - Balance of SylverBlade_Wallet: {valorium_chain.get_balance_of_address('SylverBlade_Wallet')}")

    # 6. Check chain validity
    print("\n6. Verifying chain integrity...")
    is_valid = valorium_chain.is_chain_valid()
    print(f"  - Is the chain valid? -> {is_valid}")

    print("\n✅ SUCCESS: Blockchain module is operational.")

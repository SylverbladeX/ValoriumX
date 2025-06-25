# ==============================================================================
# Valorium X: Python Simulator v6 - Resilience Test
# Architect: Sylver Blade, Assisted by Gemini
#
# This single-file script simulates a more robust version of the Valorium X
# network, incorporating multi-node consensus, malicious node simulation,
# and dynamic proposer selection.
# ==============================================================================

import hashlib
import json
import math
import random
import time
from enum import Enum
from typing import List, Dict, Any, Union

# ==============================================================================
# SECTION 1: QUADRITS CORE
# Description: Defines the core information unit of Valorium X.
# ==============================================================================

class Quadrit(Enum):
    A = 0; T = 1; C = 2; G = 3

def hash_data(data: Union[str, bytes]) -> str:
    """Utility function to hash data using the SHA-512 algorithm."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha512(data).hexdigest()

# ==============================================================================
# SECTION 2: DATA STRUCTURES
# Description: Defines the core data structures for Valorium X.
# ==============================================================================

class Transaction:
    """Represents a single transaction."""
    def __init__(self, sender: str, recipient: str, amount: float):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()
    
    def to_dict(self):
        return self.__dict__

    def calculate_hash(self) -> str:
        tx_string = json.dumps(self.to_dict(), sort_keys=True)
        return hash_data(tx_string)

class RnaTemplate:
    """Represents the lightweight 'messenger' created by a Validator Node."""
    def __init__(self, transactions: List[Transaction], proposer_address: str):
        self.proposer_address = proposer_address
        self.transaction_hashes = [tx.calculate_hash() for tx in transactions]
        self.timestamp = time.time()
        self.template_hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        data_string = json.dumps({"proposer": self.proposer_address, "tx_hashes": self.transaction_hashes, "timestamp": self.timestamp}, sort_keys=True)
        return hash_data(data_string)

class CipProof:
    """Represents the CORE proof, which should be identical for all honest nodes."""
    def __init__(self, rna_template_hash: str, coherence_anchors_hash: str):
        self.rna_template_hash = rna_template_hash
        self.coherence_anchors_hash = coherence_anchors_hash
        self.proof_hash = hash_data(self.rna_template_hash + self.coherence_anchors_hash)

class CipAttestation:
    """Represents a Neural Node's signature on a specific CIP Proof. This is the 'vote'."""
    def __init__(self, cip_proof: CipProof, node_address: str):
        self.proof_hash = cip_proof.proof_hash
        self.node_address = node_address
        self.signature = hash_data(cip_proof.proof_hash + node_address)

class Block:
    """Represents a final, validated block in the First Helix."""
    def __init__(self, timestamp: float, transactions: List[Transaction], previous_hash: str, rna_template_hash: str, block_number: int):
        self.block_number = block_number
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.rna_template_hash = rna_template_hash
        self.winning_cip_proof: CipProof = None 
        self.attestations: List[CipAttestation] = [] 
        self.block_hash = None

    def calculate_hash(self) -> str:
        """Calculates the hash of the entire block."""
        block_data = {
            "block_number": self.block_number,
            "timestamp": self.timestamp,
            "transactions": [tx.calculate_hash() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "rna_template_hash": self.rna_template_hash,
            "winning_cip_proof": self.winning_cip_proof.__dict__ if self.winning_cip_proof else None,
            "attestations": sorted([att.__dict__ for att in self.attestations], key=lambda x: x['node_address'])
        }
        return hash_data(json.dumps(block_data, sort_keys=True))

# ==============================================================================
# SECTION 3: NETWORK NODES
# Description: Defines the specialized actors in the network.
# ==============================================================================

class ValidatorNode:
    """Represents a node responsible for proposing RNA templates."""
    def __init__(self, address: str):
        self.address = address

    def create_rna_template(self, transactions: list):
        """'Transcribes' transactions into a lightweight RNA Template."""
        print(f"  [Validator {self.address}] Transcribing {len(transactions)} transactions...")
        return RnaTemplate(transactions, self.address)

class NeuralNode:
    """Represents a node providing 'useful computation' for the Second Helix."""
    def __init__(self, address: str, is_honest: bool = True):
        self.address = address
        self.is_honest = is_honest # Simulates node honesty

    def attest_to_cip(self, cip_proof: CipProof):
        """ 'Signs' or 'votes' for a given CIP proof. """
        time.sleep(0.02 + random.random() * 0.05) # Simulate variable computation time
        
        if self.is_honest:
            # Honest nodes attest to the correct proof
            print(f"    - HONEST attestation for proof {cip_proof.proof_hash[:8]}... from {self.address}")
            return CipAttestation(cip_proof, self.address)
        else:
            # A malicious node creates an attestation for a FAKE proof
            print(f"      [!] MALICIOUS NODE {self.address} is creating a FAKE proof!")
            fake_proof = CipProof("fake_rna_hash", hash_data("fake_anchors"))
            return CipAttestation(fake_proof, self.address)

# ==============================================================================
# SECTION 4: BLOCKCHAIN ORCHESTRATOR
# Description: Orchestrates the corrected distributed consensus workflow.
# ==============================================================================

class Blockchain:
    """Manages the chain and the multi-node consensus process."""
    def __init__(self, validator_nodes: List[ValidatorNode], neural_nodes: List[NeuralNode]):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.pending_transactions: List[Transaction] = []
        self.validator_nodes = validator_nodes
        self.neural_nodes = neural_nodes
        self.balances: Dict[str, float] = {}
        self.mining_reward = 100
        self.cip_consensus_threshold = math.floor(len(self.neural_nodes) * 2 / 3) + 1
        self.current_proposer_index = 0

    def create_genesis_block(self) -> Block:
        """Creates the very first block."""
        genesis_rna = RnaTemplate([], "genesis_proposer")
        genesis_block = Block(time.time(), [], "0", genesis_rna.template_hash, 0)
        genesis_block.winning_cip_proof = CipProof(genesis_rna.template_hash, hash_data("genesis_anchors"))
        genesis_block.attestations.append(CipAttestation(genesis_block.winning_cip_proof, "genesis_calculator"))
        genesis_block.block_hash = genesis_block.calculate_hash()
        return genesis_block
        
    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction):
        sender_balance = self.balances.get(transaction.sender, 0)
        if transaction.sender != "Network Reward" and sender_balance < transaction.amount:
            print(f"  [!] Transaction from {transaction.sender} failed: Insufficient funds.")
            return
        self.pending_transactions.append(transaction)
        print(f"  - Transaction from {transaction.sender} to {transaction.recipient} for {transaction.amount} VQXAI added to buffer.")

    def get_coherence_anchors(self) -> Dict[str, Any]:
        return { "total_supply_in_wallets": sum(self.balances.values()), "last_block_hash": self.last_block.block_hash }

    def process_block_creation_cycle(self):
        """Simulates one full cycle of block creation with multi-node consensus."""
        if not self.pending_transactions:
            print("\n[Network] No pending transactions to process.")
            return

        # Dynamic Proposer Selection (Round-Robin)
        proposer_node = self.validator_nodes[self.current_proposer_index]
        self.current_proposer_index = (self.current_proposer_index + 1) % len(self.validator_nodes)
        
        valid_txs = list(self.pending_transactions)
        self.pending_transactions = []
        
        rna_template = proposer_node.create_rna_template(valid_txs)
        print(f"\n[Cycle Start] Validator {proposer_node.address} created RNA Template {rna_template.template_hash[:8]}...")
        
        print("  [Network] Calculating core CIP Proof and broadcasting for attestation...")
        anchors_hash = hash_data(json.dumps(self.get_coherence_anchors(), sort_keys=True))
        core_cip_proof = CipProof(rna_template.template_hash, anchors_hash)
        
        attestations = [node.attest_to_cip(core_cip_proof) for node in self.neural_nodes]

        print(f"  [Network] Checking for consensus on proof {core_cip_proof.proof_hash[:8]}... (Threshold: {self.cip_consensus_threshold} attestations)")
        
        valid_attestations = [att for att in attestations if att.proof_hash == core_cip_proof.proof_hash]
        
        if len(valid_attestations) < self.cip_consensus_threshold:
            print(f"[FAILURE] CIP Consensus failed. Only {len(valid_attestations)} valid attestations received. Block creation aborted.")
            return

        print(f"  [Network] Consensus reached with {len(valid_attestations)} valid attestations!")
        
        print(f"  [Validator {proposer_node.address}] Assembling final block...")
        new_block = Block(
            timestamp=time.time(),
            transactions=valid_txs,
            previous_hash=self.last_block.block_hash,
            rna_template_hash=rna_template.template_hash,
            block_number=len(self.chain)
        )
        new_block.winning_cip_proof = core_cip_proof
        new_block.attestations = valid_attestations
        new_block.block_hash = new_block.calculate_hash()
        
        self.chain.append(new_block)
        
        self.update_balances(valid_txs, proposer_node.address, [att.node_address for att in valid_attestations])
        print(f"[SUCCESS] Block {new_block.block_number} 'welded' to the First Helix!")

    def update_balances(self, transactions: List[Transaction], proposer_address: str, contributing_neural_nodes: List[str]):
        """Updates balances and distributes rewards."""
        for tx in transactions:
             self.balances[tx.sender] = self.balances.get(tx.sender, 0) - tx.amount
             self.balances[tx.recipient] = self.balances.get(tx.recipient, 0) + tx.amount
        
        proposer_reward = self.mining_reward * 0.2
        neural_node_pool_reward = self.mining_reward * 0.8
        
        self.balances[proposer_address] = self.balances.get(proposer_address, 0) + proposer_reward
        if contributing_neural_nodes:
            reward_per_node = neural_node_pool_reward / len(contributing_neural_nodes)
            for address in contributing_neural_nodes:
                self.balances[address] = self.balances.get(address, 0) + reward_per_node

# ==============================================================================
# SECTION 5: MAIN SIMULATION SCRIPT
# Description: Main script to run the resilience test.
# ==============================================================================

if __name__ == '__main__':
    print("--- VALORIUM X SIMULATOR V6: RESILIENCE TEST ---")

    # 1. Initialize network actors, now with multiple validators and a malicious node
    print("\n[Step 1] Initializing Network Nodes...")
    validator_nodes = [ValidatorNode(f"Validator-{i+1:02}") for i in range(3)]
    # Node 5 is malicious and will vote incorrectly
    neural_nodes = [NeuralNode(f"NeuralNode-{i+1:02}", is_honest=(i != 4)) for i in range(5)]
    print(f"  - {len(validator_nodes)} Validator Nodes created.")
    print(f"  - {len(neural_nodes)} Neural Nodes created (Note: {neural_nodes[4].address} is malicious).")

    # 2. Initialize the blockchain
    valorium_chain = Blockchain(validator_nodes, neural_nodes)
    print("Valorium X Blockchain initialized.")

    # 3. Distribute initial funds
    valorium_chain.balances["Alice"] = 1000
    valorium_chain.balances["Bob"] = 500
    print("\n[Step 2] Distributing initial funds...")

    # 4. Run several block creation cycles to see the proposer rotation and consensus in action
    for i in range(4):
        print(f"\n===== CYCLE {i+1} =====")
        # Add some random transactions
        sender = random.choice(["Alice", "Bob"])
        recipient = random.choice(["Charlie", "David", "Eve"])
        amount = random.randint(10, 50)
        print(f"[Network] New pending transaction from {sender} to {recipient} for {amount} VQXAI.")
        valorium_chain.add_transaction(Transaction(sender, recipient, amount))
        
        # Add another transaction
        sender2 = random.choice(["Alice", "Bob", "Charlie"])
        if valorium_chain.balances.get(sender2, 0) > 100: # Ensure sender has some funds
            amount2 = random.randint(20, 60)
            print(f"[Network] New pending transaction from {sender2} to {recipient} for {amount2} VQXAI.")
            valorium_chain.add_transaction(Transaction(sender2, recipient, amount2))

        valorium_chain.process_block_creation_cycle()

    print("\n--- FINAL STATE ---")
    print(f"Blockchain Length: {len(valorium_chain.chain)} blocks")
    print("Final Account Balances:")
    for address, balance in sorted(valorium_chain.balances.items()):
        print(f"  - {address}: {balance:.2f} VQXAI")
# ==============================================================================
# Valorium X: Python Simulator v7.2 - The Final Audit
# Architect: Sylver Blade, Assisted by Gemini
#
# This version provides enhanced logging and a deterministic main loop
# to ensure the simulation's behavior is clear, predictable, and robust.
# It validates the Stencil, Reputation, and Slashing mechanisms.
# ==============================================================================

import hashlib
import json
import math
import random
import time
from enum import Enum
from typing import List, Dict, Any, Union

# ==============================================================================
# SECTION 1: GLOBAL UTILITY FUNCTIONS & CORE DATA
# ==============================================================================

def hash_data(data: Union[str, bytes, dict]) -> str:
    """Utility function to hash data using the SHA-512 algorithm."""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha512(data).hexdigest()

# ==============================================================================
# SECTION 2: CORE DATA STRUCTURES
# ==============================================================================

class Transaction:
    """Represents a single transaction."""
    def __init__(self, sender: str, recipient: str, amount: float):
        self.sender, self.recipient, self.amount, self.timestamp = sender, recipient, amount, time.time()
    def calculate_hash(self) -> str: return hash_data(self.__dict__)

class RnaTemplate:
    """Represents the lightweight 'messenger' created by a Validator Node."""
    def __init__(self, transactions: List[Transaction], proposer_address: str):
        self.proposer_address = proposer_address
        self.transactions = transactions
        self.transaction_hashes = [tx.calculate_hash() for tx in transactions]
        self.timestamp = time.time()
        self.template_hash = hash_data({"proposer": self.proposer_address, "tx_hashes": self.transaction_hashes, "timestamp": self.timestamp})

class CipProof:
    """Represents the CORE proof, which should be identical for all honest nodes."""
    def __init__(self, rna_template_hash: str, coherence_anchors_hash: str):
        self.rna_template_hash, self.coherence_anchors_hash = rna_template_hash, coherence_anchors_hash
        self.proof_hash = hash_data(self.rna_template_hash + self.coherence_anchors_hash)

class CipAttestation:
    """Represents a Neural Node's signature on a specific CIP Proof. This is the 'vote'."""
    def __init__(self, cip_proof: CipProof, node_address: str):
        self.proof_hash, self.node_address = cip_proof.proof_hash, node_address
        self.signature = hash_data(cip_proof.proof_hash + node_address)

class Block:
    """Represents a final, validated block in the First Helix."""
    def __init__(self, block_number: int, timestamp: float, transactions: List[Transaction], previous_hash: str, rna_template_hash: str):
        self.block_number, self.timestamp, self.transactions, self.previous_hash = block_number, timestamp, transactions, previous_hash
        self.rna_template_hash = rna_template_hash
        self.winning_cip_proof: CipProof = None 
        self.attestations: List[CipAttestation] = [] 
        self.block_hash = None
    
    def calculate_hash(self) -> str:
        block_data = {
            "block_number": self.block_number, "timestamp": self.timestamp, 
            "transactions": [tx.calculate_hash() for tx in self.transactions],
            "previous_hash": self.previous_hash, "rna_template_hash": self.rna_template_hash,
            "winning_cip_proof": self.winning_cip_proof.__dict__ if self.winning_cip_proof else None,
            "attestations": sorted([att.__dict__ for att in self.attestations], key=lambda x: x['node_address'])
        }
        return hash_data(block_data)

# ==============================================================================
# SECTION 3: NETWORK NODES
# ==============================================================================

class Node:
    """Base class for all network participants, now with software integrity."""
    def __init__(self, address: str, software_version: str):
        self.address = address
        self.stake = 1000.0 # Initial stake
        self.reputation = 1.0 # Reputation score from 0.0 to 1.0
        self.software_version = software_version
        self.software_hash = hash_data(f"ValoriumX Node Software {software_version}")

class ValidatorNode(Node):
    """Proposes RNA templates."""
    def create_rna_template(self, transactions: list) -> RnaTemplate:
        print(f"  [Validator {self.address}] Transcribing {len(transactions)} transactions...")
        return RnaTemplate(transactions, self.address)

class NeuralNode(Node):
    """Provides 'useful computation' and attests to CIPs."""
    def __init__(self, address: str, software_version: str, is_honest: bool = True):
        super().__init__(address, software_version)
        self.is_honest = is_honest

    def attest_to_cip(self, cip_proof: CipProof) -> CipAttestation:
        time.sleep(0.01) # Simulate computation time
        if self.is_honest:
            return CipAttestation(cip_proof, self.address)
        else:
            print(f"      [!] MALICIOUS NODE {self.address} is creating a FAKE proof!")
            fake_proof = CipProof("fake_rna_hash", hash_data("fake_anchors"))
            return CipAttestation(fake_proof, self.address)

# ==============================================================================
# SECTION 4: THE STENCIL
# ==============================================================================

class Stencil:
    """Represents the official registry of compliant software hashes."""
    def __init__(self):
        self.versions = {}

    def register_version(self, version: str, software_name: str):
        software_hash = hash_data(software_name)
        self.versions[version] = software_hash
        print(f"[Stencil] Official software version '{version}' registered with hash {software_hash[:8]}...")

    def is_compliant(self, node: Node) -> bool:
        """Checks if a node's software hash matches the official stencil."""
        official_hash = self.versions.get(node.software_version)
        if official_hash and node.software_hash == official_hash:
            return True
        print(f"    [STENCIL] Compliance check FAILED for {node.address}. Software version '{node.software_version}' is not recognized.")
        return False

# ==============================================================================
# SECTION 5: BLOCKCHAIN ORCHESTRATOR
# ==============================================================================

class Blockchain:
    def __init__(self, validator_nodes: List[ValidatorNode], neural_nodes: List[NeuralNode], stencil: Stencil):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.pending_transactions: List[Transaction] = []
        self.validator_nodes = validator_nodes
        self.neural_nodes = neural_nodes
        self.stencil = stencil
        self.balances: Dict[str, float] = {}
        self.mining_reward = 100
        self.current_proposer_index = 0
        self.treasury_address = "ValoriumX_Treasury"
        self.reputation_threshold = 0.5
        self.slashing_penalty = 50.0

    def create_genesis_block(self) -> Block:
        """Creates the very first block in the chain."""
        genesis_rna = RnaTemplate([], "genesis_proposer")
        genesis_block = Block(0, time.time(), [], "0", genesis_rna.template_hash)
        genesis_cip_proof = CipProof(genesis_rna.template_hash, hash_data("genesis_anchors"))
        genesis_block.winning_cip_proof = genesis_cip_proof
        genesis_block.attestations.append(CipAttestation(genesis_cip_proof, "genesis_calculator"))
        genesis_block.block_hash = genesis_block.calculate_hash()
        return genesis_block
        
    @property
    def last_block(self) -> Block: return self.chain[-1]
    
    def add_transaction(self, tx: Transaction):
        if tx.sender != "Network Reward" and self.balances.get(tx.sender, 0) < tx.amount:
            print(f"  [!] Transaction from {tx.sender} for {tx.amount} VQXAI rejected: Insufficient funds.")
            return False
        self.pending_transactions.append(tx)
        print(f"  - Transaction from {tx.sender} to {tx.recipient} for {tx.amount} VQXAI added to buffer.")
        return True

    def get_coherence_anchors(self) -> Dict[str, Any]: 
        return { "total_supply": sum(self.balances.values()), "last_block_hash": self.last_block.block_hash }

    def process_block_creation_cycle(self):
        """Simulates one full cycle of block creation with the immune system."""
        if not self.pending_transactions:
            print("\n[Network] No pending transactions to process.")
            return

        proposer_node = self.validator_nodes[self.current_proposer_index]
        self.current_proposer_index = (self.current_proposer_index + 1) % len(self.validator_nodes)
        
        print(f"\n===== CYCLE {len(self.chain)} | Proposer: {proposer_node.address} =====")
        
        if not self.stencil.is_compliant(proposer_node):
            print(f"  [IMMUNE SYSTEM] Proposer {proposer_node.address} is not compliant. Slashing and skipping cycle.")
            self.slash_node(proposer_node)
            self.pending_transactions = []
            return

        transactions_for_block = list(self.pending_transactions)
        rna_template = proposer_node.create_rna_template(transactions_for_block)
        print(f"  [RNA] RNA Template {rna_template.template_hash[:8]}... created.")
        self.pending_transactions = []
        
        participating_nodes = [n for n in self.neural_nodes if self.stencil.is_compliant(n) and n.reputation >= self.reputation_threshold]
        if not participating_nodes:
            print("  [FAILURE] No reputable and compliant Neural Nodes available.")
            return
            
        print(f"  [Network] {len(participating_nodes)} compliant & reputable nodes participating in consensus.")
        core_cip_proof = CipProof(rna_template.template_hash, hash_data(self.get_coherence_anchors()))
        attestations = [node.attest_to_cip(core_cip_proof) for node in participating_nodes]

        cip_consensus_threshold = math.floor(len(participating_nodes) * 2 / 3) + 1
        print(f"  [Consensus] Checking for consensus on proof {core_cip_proof.proof_hash[:8]}... (Threshold: {cip_consensus_threshold} attestations)")
        
        proof_counts = {}; [proof_counts.update({att.proof_hash: proof_counts.get(att.proof_hash, 0) + 1}) for att in attestations]
        
        # Identify malicious nodes who participated but didn't submit the winning proof
        winning_proof_hash = None
        if core_cip_proof.proof_hash in proof_counts and proof_counts[core_cip_proof.proof_hash] >= cip_consensus_threshold:
            winning_proof_hash = core_cip_proof.proof_hash
            print(f"  [Consensus] Consensus reached with {proof_counts[winning_proof_hash]} valid attestations!")
            for node in participating_nodes:
                node_attestation = next((att for att in attestations if att.node_address == node.address), None)
                if node_attestation and node_attestation.proof_hash != winning_proof_hash:
                    self.slash_node(node)
        else:
            print(f"  [FAILURE] CIP Consensus failed. Block creation aborted.")
            # Punish all participants for failing to reach consensus on a valid proof
            for node in participating_nodes:
                self.slash_node(node)
            return

        print(f"  [Assembly] Validator {proposer_node.address} assembling final block...")
        new_block = Block(len(self.chain), time.time(), transactions_for_block, self.last_block.block_hash, rna_template.template_hash)
        new_block.winning_cip_proof = core_cip_proof
        new_block.attestations = [att for att in attestations if att.proof_hash == winning_proof_hash]
        new_block.block_hash = new_block.calculate_hash()
        
        self.chain.append(new_block)
        
        self.update_balances_and_rewards(proposer_node, [att.node_address for att in new_block.attestations], transactions_for_block)
        print(f"  [SUCCESS] Block {new_block.block_number} 'welded' to the First Helix!")

    def slash_node(self, node: Node):
        slash_amount = min(node.stake, self.slashing_penalty)
        if slash_amount > 0:
            node.stake -= slash_amount
            node.reputation = max(0, node.reputation - 0.25)
            self.balances[self.treasury_address] = self.balances.get(self.treasury_address, 0) + slash_amount
            print(f"    [IMMUNE SYSTEM] Node {node.address} slashed! Stake reduced by {slash_amount:.2f}. New reputation: {node.reputation:.2f}")

    def update_balances_and_rewards(self, proposer_node: ValidatorNode, contributing_nodes: List[str], transactions: List[Transaction]):
        print("  [Balances] Updating account balances...")
        for tx in transactions:
            self.balances[tx.sender] = self.balances.get(tx.sender, 0) - tx.amount
            self.balances[tx.recipient] = self.balances.get(tx.recipient, 0) + tx.amount

        proposer_reward = self.mining_reward * 0.2
        neural_node_pool_reward = self.mining_reward * 0.8
        
        self.balances[proposer_node.address] = self.balances.get(proposer_node.address, 0) + proposer_reward
        if contributing_nodes:
            reward_per_node = neural_node_pool_reward / len(contributing_nodes)
            for address in contributing_nodes:
                self.balances[address] = self.balances.get(address, 0) + reward_per_node
                # Reward honest nodes with a small reputation boost
                all_nodes = self.validator_nodes + self.neural_nodes
                node = next((n for n in all_nodes if n.address == address), None)
                if node: node.reputation = min(1.0, node.reputation + 0.02)
        print("  [Balances] Rewards distributed.")

# ==============================================================================
# SECTION 6: MAIN SIMULATION SCRIPT
# ==============================================================================

if __name__ == '__main__':
    print("--- VALORIUM X SIMULATOR V7.2: FINAL AUDIT ---")

    # 1. Create the Stencil and register the official software version
    stencil = Stencil()
    stencil.register_version("v1.0", "ValoriumX Node Software v1.0")

    # 2. Initialize network actors
    print("\n[Step 1] Initializing Network Nodes...")
    validator_nodes = [ValidatorNode(f"Validator-{i+1:02}", "v1.0") for i in range(3)]
    neural_nodes = [
        NeuralNode("NeuralNode-01", "v1.0", is_honest=True),
        NeuralNode("NeuralNode-02", "v1.0", is_honest=True),
        NeuralNode("NeuralNode-03", "v1.0", is_honest=True),
        NeuralNode("NeuralNode-04", "v1.0", is_honest=False), # Malicious but compliant
        NeuralNode("NeuralNode-05", "v1.1-beta") # Non-compliant software
    ]
    print(f"  - {len(neural_nodes)} Neural Nodes created (Note: {neural_nodes[3].address} is malicious, {neural_nodes[4].address} is non-compliant).")

    # 3. Initialize the blockchain and initial funds
    valorium_chain = Blockchain(validator_nodes, neural_nodes, stencil)
    print("\n[Step 2] Valorium X Blockchain initialized with Stencil.")
    
    # Initialize stakes and balances for all nodes and users
    all_nodes = validator_nodes + neural_nodes
    for node in all_nodes:
        valorium_chain.balances[node.address] = node.stake
    valorium_chain.balances["Alice"] = 1000
    valorium_chain.balances["Bob"] = 500
    print("Initial funds and stakes distributed.")
    
    # 4. Run several block creation cycles
    for i in range(4):
        # Create a new transaction for this cycle
        sender = random.choice(["Alice", "Bob"])
        recipient = "Charlie"
        amount = random.randint(20, 70)
        print(f"\n[Network] Preparing transaction from {sender} to {recipient} for {amount} VQXAI.")
        valorium_chain.add_transaction(Transaction(sender, recipient, amount))
        
        valorium_chain.process_block_creation_cycle()

        print("\n  --- Node Status Report ---")
        for node in all_nodes:
            print(f"    - {node.address}: Reputation = {node.reputation:.2f}, Stake = {node.stake:.2f}")

    print("\n--- FINAL STATE ---")
    print(f"Blockchain Length: {len(valorium_chain.chain)} blocks")
    print("Final Account Balances:")
    for address, balance in sorted(valorium_chain.balances.items()):
        print(f"  - {address}: {balance:.2f} VQXAI")

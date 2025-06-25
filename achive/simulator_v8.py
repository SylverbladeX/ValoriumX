# ==============================================================================
# Valorium X: Python Simulator v8.2 - Hyperdrive Ready
# Architect: Sylver Blade, Assisted by Gemini
#
# This is the definitive, stable, single-file version of the simulator.
# It includes a fully functional Immune System with Stencil, Reputation,
# and Slashing, along with robust error handling and clear logging.
# ==============================================================================

import hashlib
import json
import math
import random
import time
import logging
from enum import Enum
from typing import List, Dict, Any, Union

# ==============================================================================
# SECTION 0: LOGGING SETUP
# ==============================================================================

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] - %(message)s', datefmt='%H:%M:%S')

# ==============================================================================
# SECTION 1: GLOBAL UTILITY FUNCTIONS
# ==============================================================================

def hash_data(data: Union[str, bytes, dict]) -> str:
    """Utility function to hash data using the SHA-512 algorithm."""
    if isinstance(data, dict):
        # Ensure consistent hashing for dictionaries
        data = json.dumps(data, sort_keys=True)
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha512(data).hexdigest()

# ==============================================================================
# SECTION 2: CORE DATA STRUCTURES
# ==============================================================================

class Transaction:
    """Represents a single transaction."""
    def __init__(self, sender: str, recipient: str, amount: float, timestamp: float = None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp or time.time()
    
    def to_dict(self):
        """Serializes the transaction to a dictionary."""
        return self.__dict__

    def calculate_hash(self) -> str: 
        """Calculates the unique hash of the transaction."""
        return hash_data(self.to_dict())

class RnaTemplate:
    """Represents the lightweight 'messenger' created by a Validator Node."""
    def __init__(self, transactions: List[Transaction], proposer_address: str):
        self.proposer_address = proposer_address
        self.transactions = transactions
        self.transaction_hashes = [tx.calculate_hash() for tx in self.transactions]
        self.timestamp = time.time()
        self.template_hash = hash_data({"proposer": self.proposer_address, "tx_hashes": self.transaction_hashes, "timestamp": self.timestamp})

class CipProof:
    """Represents the CORE proof, which should be identical for all honest nodes."""
    def __init__(self, rna_template_hash: str, coherence_anchors_hash: str):
        self.rna_template_hash = rna_template_hash
        self.coherence_anchors_hash = coherence_anchors_hash
        self.proof_hash = hash_data(self.rna_template_hash + self.coherence_anchors_hash)

class CipAttestation:
    """Represents a Neural Node's signature on a specific CIP Proof."""
    def __init__(self, cip_proof: CipProof, node_address: str):
        self.proof_hash = cip_proof.proof_hash
        self.node_address = node_address
        self.signature = hash_data(cip_proof.proof_hash + node_address)

class Block:
    """Represents a final, validated block in the First Helix."""
    def __init__(self, block_number: int, timestamp: float, transactions: List[Transaction], previous_hash: str, rna_template_hash: str):
        self.block_number = block_number
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.rna_template_hash = rna_template_hash
        self.winning_cip_proof: CipProof = None 
        self.attestations: List[CipAttestation] = [] 
        self.block_hash = None
    
    def to_dict(self):
        """Serializes the block to a dictionary."""
        return {
            "block_number": self.block_number,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "rna_template_hash": self.rna_template_hash,
            "winning_cip_proof": self.winning_cip_proof.__dict__ if self.winning_cip_proof else None,
            "attestations": [att.__dict__ for att in self.attestations],
            "block_hash": self.block_hash
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a Block instance from a dictionary (e.g., from a JSON file)."""
        transactions = [Transaction(**tx_data) for tx_data in data['transactions']]
        rna_hash = data.get('rna_template_hash', '')
        block_num = data.get('block_number', 0)
        block = cls(block_num, data['timestamp'], transactions, data['previous_hash'], rna_hash)
        
        if data.get('winning_cip_proof'):
            block.winning_cip_proof = CipProof(**data['winning_cip_proof'])
        
        if data.get('attestations') and block.winning_cip_proof:
            for att_data in data['attestations']:
                block.attestations.append(CipAttestation(block.winning_cip_proof, att_data['node_address']))

        block.block_hash = data.get('block_hash')
        return block

    def calculate_hash(self) -> str:
        """Calculates the hash of the entire block, ensuring consistency."""
        block_data = self.to_dict()
        block_data.pop('block_hash', None) # Ensure hash is not part of the data being hashed
        block_data['attestations'] = sorted(block_data.get('attestations', []), key=lambda x: x['node_address'])
        return hash_data(block_data)
        
# ==============================================================================
# SECTION 3: NETWORK NODES
# ==============================================================================
class Node:
    """Base class for all network participants, with software integrity."""
    def __init__(self, address: str, software_version: str):
        self.address, self.stake, self.reputation = address, 1000.0, 1.0
        self.software_version, self.software_hash = software_version, hash_data(f"ValoriumX Node Software {software_version}")

class ValidatorNode(Node):
    """Proposes RNA templates."""
    def create_rna_template(self, txs: list) -> RnaTemplate:
        logging.info(f"Validator {self.address}: Transcribing {len(txs)} transactions...")
        return RnaTemplate(txs, self.address)

class NeuralNode(Node):
    """Provides 'useful computation' and attests to CIPs."""
    def __init__(self, address: str, software_version: str, is_honest: bool = True):
        super().__init__(address, software_version)
        self.is_honest = is_honest

    def attest_to_cip(self, cip_proof: CipProof) -> CipAttestation:
        time.sleep(0.01)
        if self.is_honest:
            return CipAttestation(cip_proof, self.address)
        else:
            logging.warning(f"MALICIOUS NODE {self.address} is creating a FAKE proof!")
            return CipAttestation(CipProof("fake_rna", hash_data("fake_anchors")), self.address)

# ==============================================================================
# SECTION 4: THE STENCIL
# ==============================================================================
class Stencil:
    """Represents the official registry of compliant software hashes."""
    def __init__(self): self.versions = {}
    def register_version(self, version: str, name: str):
        h = hash_data(name)
        self.versions[version] = h
        logging.info(f"Stencil: Official software version '{version}' registered with hash {h[:8]}...")
    def is_compliant(self, node: Node) -> bool:
        h = self.versions.get(node.software_version)
        if h and node.software_hash == h: return True
        logging.warning(f"STENCIL: Compliance check FAILED for {node.address}.")
        return False

# ==============================================================================
# SECTION 5: BLOCKCHAIN ORCHESTRATOR
# ==============================================================================
class Blockchain:
    def __init__(self, validator_nodes: List[ValidatorNode], neural_nodes: List[NeuralNode], stencil: Stencil):
        self.validator_nodes, self.neural_nodes, self.stencil = validator_nodes, neural_nodes, stencil
        self.chain: List[Block] = [self.create_genesis_block()]
        self.pending_transactions: List[Transaction] = []
        self.balances: Dict[str, float] = {}
        self.mining_reward = 100
        self.current_proposer_index = 0
        self.treasury_address = "ValoriumX_Treasury"
        self.reputation_threshold = 0.5
        self.slashing_penalty = 100.0

    def create_genesis_block(self) -> Block:
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
            logging.warning(f"Transaction from {tx.sender} failed: Insufficient funds.")
            return False
        self.pending_transactions.append(tx)
        logging.info(f"Transaction from {tx.sender} to {tx.recipient} for {tx.amount} VQXAI added to buffer.")
        return True

    def get_coherence_anchors(self) -> Dict[str, Any]: 
        return { "last_block_hash": self.last_block.block_hash }
    
    def process_block_creation_cycle(self):
        if not self.pending_transactions:
            logging.info("Network: No pending transactions to process.")
            return

        proposer_node = self.validator_nodes[self.current_proposer_index]
        self.current_proposer_index = (self.current_proposer_index + 1) % len(self.validator_nodes)
        
        logging.info(f"===== CYCLE {len(self.chain)} | Proposer: {proposer_node.address} =====")
        
        if not self.stencil.is_compliant(proposer_node) or proposer_node.reputation < self.reputation_threshold:
            logging.warning(f"IMMUNE SYSTEM: Proposer {proposer_node.address} is non-compliant or has low reputation. Slashing.")
            self.slash_node(proposer_node)
            return

        transactions_for_block = list(self.pending_transactions)
        self.pending_transactions = []
        rna_template = proposer_node.create_rna_template(transactions_for_block)
        
        participating_nodes = [n for n in self.neural_nodes if self.stencil.is_compliant(n) and n.reputation >= self.reputation_threshold]
        if not participating_nodes:
            logging.error("FAILURE: No reputable and compliant Neural Nodes available.")
            self.pending_transactions.extend(transactions_for_block)
            return
            
        logging.info(f"Network: {len(participating_nodes)} nodes participating in consensus.")
        core_cip_proof = CipProof(rna_template.template_hash, hash_data(self.get_coherence_anchors()))
        attestations = [node.attest_to_cip(core_cip_proof) for node in participating_nodes]

        cip_consensus_threshold = math.floor(len(participating_nodes) * 2 / 3) + 1
        logging.info(f"Consensus: Checking for consensus... (Threshold: {cip_consensus_threshold} attestations)")
        
        proof_counts = {}; [proof_counts.update({att.proof_hash: proof_counts.get(att.proof_hash, 0) + 1}) for att in attestations]
        winning_proof_hash, winning_count = max(proof_counts.items(), key=lambda item: item[1])

        for node in participating_nodes:
            node_attestation = next((att for att in attestations if att.node_address == node.address), None)
            if not node_attestation or node_attestation.proof_hash != winning_proof_hash:
                self.slash_node(node)

        if winning_proof_hash != core_cip_proof.proof_hash or winning_count < cip_consensus_threshold:
            logging.error(f"FAILURE: CIP Consensus failed. Block creation aborted.")
            self.pending_transactions.extend(transactions_for_block)
            return

        logging.info(f"Consensus: Reached with {winning_count} valid attestations!")
        
        new_block = Block(len(self.chain), time.time(), transactions_for_block, self.last_block.block_hash, rna_template.template_hash)
        new_block.winning_cip_proof = core_cip_proof
        new_block.attestations = [att for att in attestations if att.proof_hash == winning_proof_hash]
        new_block.block_hash = new_block.calculate_hash()
        
        self.chain.append(new_block)
        
        self.update_balances_and_rewards(proposer_node, [att.node_address for att in new_block.attestations], transactions_for_block)
        logging.info(f"SUCCESS: Block {new_block.block_number} 'welded' to the First Helix!")

    def slash_node(self, node: Node):
        slash_amount = min(node.stake, self.slashing_penalty)
        if slash_amount > 0:
            node.stake -= slash_amount
            node.reputation = max(0, node.reputation - 0.5)
            self.balances[self.treasury_address] = self.balances.get(self.treasury_address, 0) + slash_amount
            logging.warning(f"IMMUNE SYSTEM: Node {node.address} slashed! Stake reduced by {slash_amount:.2f}. New reputation: {node.reputation:.2f}")

    def update_balances_and_rewards(self, proposer_node: ValidatorNode, contributing_nodes: List[str], transactions: List[Transaction]):
        logging.info("Balances: Updating account balances and distributing rewards...")
        for tx in transactions:
            self.balances[tx.sender] -= tx.amount
            self.balances[tx.recipient] = self.balances.get(tx.recipient, 0) + tx.amount

        proposer_reward = self.mining_reward * 0.2
        self.balances[proposer_node.address] = self.balances.get(proposer_node.address, 0) + proposer_reward
        proposer_node.reputation = min(1.0, proposer_node.reputation + 0.05)

        if contributing_nodes:
            reward_per_node = (self.mining_reward * 0.8) / len(contributing_nodes)
            for address in contributing_nodes:
                self.balances[address] = self.balances.get(address, 0) + reward_per_node
                node = next((n for n in self.neural_nodes if n.address == address), None)
                if node: node.reputation = min(1.0, node.reputation + 0.02)
        logging.info("Balances: Rewards and reputations updated.")

    def save_to_file(self, filename: str):
        logging.info(f"Saving blockchain state to {filename}...")
        state = {
            "chain": [block.to_dict() for block in self.chain],
            "balances": self.balances,
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions]
        }
        with open(filename, 'w') as f: json.dump(state, f, indent=4)
        logging.info("Save complete.")

    @classmethod
    def load_from_file(cls, filename: str, validator_nodes, neural_nodes, stencil):
        try:
            with open(filename, 'r') as f: state = json.load(f)
            logging.info(f"Loading blockchain state from {filename}...")
            loaded_blockchain = cls(validator_nodes, neural_nodes, stencil)
            loaded_blockchain.chain = [Block.from_dict(block_data) for block_data in state['chain']]
            loaded_blockchain.balances = state['balances']
            loaded_blockchain.pending_transactions = [Transaction(**tx_data) for tx_data in state['pending_transactions']]
            return loaded_blockchain
        except FileNotFoundError: return cls(validator_nodes, neural_nodes, stencil)
        except Exception as e:
            logging.error(f"Failed to load state from {filename}: {e}. Starting fresh.")
            return cls(validator_nodes, neural_nodes, stencil)

# ==============================================================================
# SECTION 6: MAIN SIMULATION SCRIPT
# ==============================================================================
if __name__ == '__main__':
    logging.info("--- VALORIUM X SIMULATOR V8: HYPERDRIVE READY ---")

    STATE_FILE = "blockchain_state.json"

    stencil = Stencil()
    stencil.register_version("v1.0", "ValoriumX Node Software v1.0")
    
    validator_nodes = [ValidatorNode(f"Validator-{i+1:02}", "v1.0") for i in range(3)]
    neural_nodes = [
        NeuralNode("NeuralNode-01", "v1.0", is_honest=True),
        NeuralNode("NeuralNode-02", "v1.0", is_honest=True),
        NeuralNode("NeuralNode-03", "v1.0", is_honest=False), # Malicious
        NeuralNode("NeuralNode-04", "v1.1-beta") # Non-compliant
    ]
    
    valorium_chain = Blockchain.load_from_file(STATE_FILE, validator_nodes, neural_nodes, stencil)
    
    if len(valorium_chain.chain) == 1:
        logging.info("New blockchain detected. Initializing stakes and balances...")
        all_nodes = validator_nodes + neural_nodes
        for node in all_nodes: valorium_chain.balances[node.address] = node.stake
        valorium_chain.balances["Alice"] = 2000
    
    for i in range(3):
        logging.info(f"Preparing Cycle {len(valorium_chain.chain)}...")
        valorium_chain.add_transaction(Transaction("Alice", "Bob", 100))
        valorium_chain.add_transaction(Transaction("Alice", "Charlie", 50))
        valorium_chain.process_block_creation_cycle()

    valorium_chain.save_to_file(STATE_FILE)
    
    logging.info("\n--- FINAL STATE ---")
    logging.info(f"Blockchain Length: {len(valorium_chain.chain)} blocks")
    logging.info("Final Account Balances:")
    for address, balance in sorted(valorium_chain.balances.items()):
        logging.info(f"  - {address}: {balance:.2f} VQXAI")
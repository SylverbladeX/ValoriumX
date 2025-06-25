# File: nodes.py
import time, random
from quadrits import hash_data
from structures import RnaTemplate, CipAttestation, CipProof

class Node:
    """Base class for all network participants."""
    def __init__(self, address: str, software_version: str):
        self.address = address
        self.stake = 1000.0
        self.reputation = 1.0
        self.software_version = software_version
        # The node's software hash is an intrinsic property
        self.software_hash = hash_data(f"ValoriumX Node Software {self.software_version}")

class ValidatorNode(Node):
    def create_rna_template(self, transactions: list) -> RnaTemplate:
        logging.info(f"Validator {self.address}: Transcribing {len(transactions)} transactions...")
        return RnaTemplate(transactions, self.address)

class NeuralNode(Node):
    def __init__(self, address: str, software_version: str, is_honest: bool = True):
        super().__init__(address, software_version)
        self.is_honest = is_honest
        if not self.is_honest:
            # A malicious node might report a valid version but run different code,
            # which would be caught by deeper integrity checks in a real system.
            # For this simulation, their dishonesty is in their actions.
            pass

    def attest_to_cip(self, cip_proof: CipProof) -> CipAttestation:
        time.sleep(0.01)
        if self.is_honest:
            return CipAttestation(cip_proof, self.address)
        else:
            logging.warning(f"MALICIOUS NODE {self.address} is creating a FAKE proof!")
            return CipAttestation(CipProof("fake_rna", hash_data("fake_anchors")), self.address)


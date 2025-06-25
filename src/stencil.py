# File: stencil.py
from nodes import Node

class Stencil:
    """Represents the official registry of compliant software hashes."""
    def __init__(self):
        self.versions = {} # Maps version string to official hash

    def register_version_hash(self, version: str, official_hash: str):
        """Register a new official software version hash."""
        self.versions[version] = official_hash
        logging.info(f"Stencil: Official software v'{version}' registered with hash {official_hash[:8]}...")

    def is_compliant(self, node: Node) -> bool:
        """Checks if a node's software hash matches the official stencil."""
        official_hash = self.versions.get(node.software_version)
        if official_hash and node.software_hash == official_hash:
            return True
        logging.warning(f"STENCIL: Compliance check FAILED for {node.address}. Hash mismatch or unknown version '{node.software_version}'.")
        return False

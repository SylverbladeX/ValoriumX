# ==============================================================================
# File: main.py
# Module 4 of the Valorium X Simulator
# Version: 2.0
# Last Updated: 2025-06-20
#
# This is the main script to run the simulation, demonstrating the core
# functionalities of the blockchain, including state management and validation.
# Architect: Sylver Blade
# ==============================================================================

from blockchain import Blockchain
from structures import Transaction
from quadrits import string_to_quadrits, quadrits_to_string
import random

def create_axon_address():
    """Generates a fictitious, non-human wallet address for the simulation."""
    prefix = "VQX"
    # Quantum-like symbols for aesthetic
    symbols = ['Ψ', 'Φ', 'Σ', 'Ω', 'δ', 'ℏ'] 
    body = f"{random.choice(symbols)}|{''.join(random.choices('ABCDEF0123456789', k=4))}⟩"
    suffix = "AXON"
    return f"{prefix}_{body}_{suffix}"

if __name__ == "__main__":
    print("--- VALORIUM X BLOCKCHAIN SIMULATOR V2 ---")
    
    # --- 1. Demonstration of the Quadrits Module ---
    print("\n[DEMO] Testing the Quadrits encoding system...")
    original_text = "Valorium X: The Birth of a Star!"
    quadrit_encoded = string_to_quadrits(original_text)
    decoded_text = quadrits_to_string(quadrit_encoded)
    print(f"  Original: '{original_text}'")
    print(f"  Decoded:  '{decoded_text}'")
    print(f"  Integrity Check: {'✅ SUCCESS' if original_text == decoded_text else '❌ FAILURE'}")
    print("-" * 40)

    # --- 2. Initialize the Blockchain ---
    print("\n[Step 1] Initializing the Valorium X Blockchain...")
    # The difficulty is a placeholder for the future CIP complexity.
    valorium_chain = Blockchain(difficulty=3)
    print("  - Blockchain initialized successfully.")

    # --- 3. Create Fictitious Wallets and Set Initial Balances ---
    print("\n[Step 2] Creating AXON wallets and distributing initial funds...")
    wallet_A = create_axon_address()
    wallet_B = create_axon_address()
    wallet_C = create_axon_address()
    
    valorium_chain.balances[wallet_A] = 500
    valorium_chain.balances[wallet_B] = 200
    print(f"  - {wallet_A} balance: {valorium_chain.get_balance_of_address(wallet_A)} $VQXAI")
    print(f"  - {wallet_B} balance: {valorium_chain.get_balance_of_address(wallet_B)} $VQXAI")
    print("-" * 40)

    # --- 4. Add Valid Transactions to the "ARN Buffer" ---
    print("\n[Step 3] Adding valid transactions to the ARN Buffer...")
    try:
        valorium_chain.add_transaction(Transaction(sender=wallet_A, recipient=wallet_B, amount=100))
        valorium_chain.add_transaction(Transaction(sender=wallet_B, recipient=wallet_C, amount=50))
    except ValueError as e:
        print(f"  [UNEXPECTED ERROR] {e}")

    # --- 5. A Validator Node ("SylverBlade") Mines a Block ---
    print("\n[Step 4] Mining Block 1...")
    valorium_chain.mine_pending_transactions(mining_reward_address="SylverBlade_Wallet")

    # --- 6. Check Balances After Mining ---
    print("\n[Step 5] Checking balances after Block 1:")
    print(f"  - Balance of {wallet_A}: {valorium_chain.get_balance_of_address(wallet_A)}")
    print(f"  - Balance of {wallet_B}: {valorium_chain.get_balance_of_address(wallet_B)}")
    print(f"  - Balance of {wallet_C}: {valorium_chain.get_balance_of_address(wallet_C)}")
    print(f"  - Balance of SylverBlade_Wallet: {valorium_chain.get_balance_of_address('SylverBlade_Wallet')}")
    print("-" * 40)

    # --- 7. Test an Invalid Transaction (Insufficient Funds) ---
    print("\n[Step 6] Testing an invalid transaction (insufficient funds)...")
    try:
        invalid_tx = Transaction(sender=wallet_C, recipient=wallet_A, amount=100) # Wallet C only has 50
        valorium_chain.add_transaction(invalid_tx)
    except ValueError as e:
        print(f"  [SUCCESS] Successfully caught the expected error: {e}")
    print("-" * 40)

    # --- 8. Mine Another Block ---
    print("\n[Step 7] Mining Block 2...")
    valorium_chain.mine_pending_transactions(mining_reward_address="SylverBlade_Wallet")

    # --- 9. Display the Final Chain and Check Its Validity ---
    print("\n--- FINAL VALORIUM X BLOCKCHAIN STATE ---")
    for i, block in enumerate(valorium_chain.chain):
        print(f"--- Block {i} ---")
        print(f"  Hash: {block.block_hash[:16]}...")
        print(f"  Previous Hash: {block.previous_hash[:16]}...")
    
    print("\nVerifying final chain integrity...")
    is_valid = valorium_chain.is_chain_valid()
    print(f"  Is the Valorium X blockchain valid? -> {is_valid}")

    # --- 10. Tampering Test ---
    if len(valorium_chain.chain) > 1:
        print("\n--- TAMPERING TEST ---")
        print("  Tampering with Block 1 by changing a transaction amount...")
        # Directly changing data in a past block
        valorium_chain.chain[1].transactions[0].amount = 10000 
        
        print("  Re-verifying chain integrity after tampering...")
        # The is_chain_valid() method should now detect the inconsistency
        is_valid_after_tamper = valorium_chain.is_chain_valid()
        print(f"  Is the chain still valid after tampering? -> {is_valid_after_tamper}")


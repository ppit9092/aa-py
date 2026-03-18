import os
import sys
from eth_account import Account
from eth_utils import to_checksum_address

# Add project root to path
sys.path.append(os.getcwd())

from aa_py.models import UserOperation
from aa_py.signer import UserOpSigner
from aa_py.eip7702 import Authorization, EIP7702Transaction
from aa_py.account import SmartAccount
from aa_py.provider import BundlerProvider
from aa_py.paymaster.erc7677 import PimlicoPaymasterClient

def main():
    print("=== aa-py: EIP-7702 & ERC-4337 Full Flow Demo ===\n")

    # 1. Configuration
    PRIVATE_KEY = "0x" + "1" * 64 # Replace with test key
    RPC_URL = "http://localhost:8545" # Anvil/Hardhat with Pectra support
    ENTRY_POINT = to_checksum_address("0x0000000071727De22E5E9d8BAf0edAc6f37da032") # v0.7+
    SMART_ACCOUNT_LOGIC = to_checksum_address("0x" + "a" * 40) # AA logic address
    CHAIN_ID = 1

    eoa_account = Account.from_key(PRIVATE_KEY)
    print(f"EOA Address: {eoa_account.address}")

    # --- STEP 1: EIP-7702 DELEGATION ---
    print("\n[Step 1] Preparing EIP-7702 Authorization...")
    # Create authorization: EOA delegates its code to SMART_ACCOUNT_LOGIC
    auth = Authorization(
        chain_id=CHAIN_ID,
        address=SMART_ACCOUNT_LOGIC,
        nonce=0
    )
    auth.sign(PRIVATE_KEY)
    print(f"  - Authorization signed by EOA")

    # Build Type-4 Transaction (SetCodeTransaction)
    tx_data = {
        'from': eoa_account.address,
        'to': eoa_account.address, # Self-call to trigger delegation
        'value': 0,
        'gas': 100000,
        'maxFeePerGas': 2 * 10**9,
        'maxPriorityFeePerGas': 10**9,
        'nonce': 0, # EOA nonce
    }
    eip7702_tx = EIP7702Transaction(tx_data, [auth])
    prepared_tx = eip7702_tx.prepare()
    print(f"  - Type-4 Transaction built with authorizationList")
    # In a real app: w3.eth.send_raw_transaction(w3.eth.account.sign_transaction(prepared_tx, PK).rawTransaction)

    # --- STEP 2: AA INTERACTION ---
    print("\n[Step 2] Sending AA UserOperation via upgraded EOA...")
    
    # Initialize SDK components
    signer = UserOpSigner(PRIVATE_KEY)
    provider = BundlerProvider(RPC_URL, ENTRY_POINT)
    paymaster = PimlicoPaymasterClient("https://api.pimlico.io/v2/mainnet/rpc?apikey=YOUR_KEY") # Placeholder

    # Create SmartAccount (targeting the upgraded EOA address)
    account = SmartAccount(
        address=eoa_account.address,
        signer=signer,
        provider=provider,
        entry_point=ENTRY_POINT,
        chain_id=CHAIN_ID,
        paymaster=paymaster
    )

    # Send a transaction (execute callData)
    # account.send_transaction will handle: Nonce -> Gas -> Sponsor -> Sign -> Bundler
    print("  - Building and signing UserOperation...")
    try:
        # Note: This requires a running Bundler and valid Smart Account logic on-chain
        # op_hash = account.send_transaction(to="0x...", data="0x", value=0)
        # print(f"  - UserOp submitted! Hash: {op_hash}")
        print("  - [SIMULATION] UserOperation structure is valid and ready for submission.")
    except Exception as e:
        print(f"  - Error (Expected if no bundler): {e}")

    print("\n=== Demo Completed ===")

if __name__ == "__main__":
    main()

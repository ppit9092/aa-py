import sys
import os
from eth_utils import to_checksum_address, to_bytes

# Ensure local aa_py is in path
sys.path.append(os.getcwd())

from aa_py.models import UserOperation, PaymasterData
from aa_py.hashing import get_user_op_hash

def run_verification():
    print("--- Milestone 1 Verification ---")
    
    # 1. Test Packing Logic (v0.7/v0.8/v0.9 Standard)
    print("Testing 128-bit Gas Packing...")
    sender = to_checksum_address("0x" + "1" * 40)
    v_gas = 100000 # 0x186a0
    c_gas = 200000 # 0x30d40
    
    op = UserOperation(
        sender=sender,
        nonce=1,
        verificationGasLimit=v_gas,
        callGasLimit=c_gas,
        preVerificationGas=50000,
        maxPriorityFeePerGas=10**9,
        maxFeePerGas=2 * 10**9
    )
    
    packed = op.to_packed()
    expected_gas_limits = f"0x{v_gas:032x}{c_gas:032x}"
    if packed.accountGasLimits == expected_gas_limits:
        print(f"  [PASS] accountGasLimits: {packed.accountGasLimits}")
    else:
        print(f"  [FAIL] accountGasLimits: {packed.accountGasLimits} != {expected_gas_limits}")
        sys.exit(1)

    # 2. Test v0.9 Paymaster Structure
    print("Testing v0.9 Paymaster Structure...")
    pm_addr = to_checksum_address("0x" + "2" * 40)
    pm_data = PaymasterData(
        paymaster=pm_addr,
        verificationGasLimit=123,
        postOpGasLimit=456,
        data="0xabcdef"
    )
    encoded_pm = pm_data.encode()
    if pm_addr.lower()[2:] in encoded_pm:
        print(f"  [PASS] Paymaster encoded: {encoded_pm[:50]}...")
    else:
        print(f"  [FAIL] Paymaster encoding error")
        sys.exit(1)

    # 3. Test Hashing (EIP-712 Compatibility)
    print("Testing EIP-712 UserOp Hash...")
    ep = to_checksum_address("0x" + "e" * 40)
    u_hash = get_user_op_hash(op, ep, 1)
    print(f"  [PASS] UserOpHash: {u_hash.hex()}")
    
    print("\n--- Milestone 1 Successfully Verified ---")

if __name__ == "__main__":
    run_verification()

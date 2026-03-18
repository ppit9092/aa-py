import pytest
from eth_utils import to_checksum_address
from aa_py.models import UserOperation, PaymasterData, PackedUserOperation
from aa_py.hashing import get_user_op_hash

def test_user_op_packing():
    # Setup values
    sender = to_checksum_address("0x" + "1" * 40)
    v_gas_limit = 100000  # 0x186a0
    c_gas_limit = 200000  # 0x30d40
    
    op = UserOperation(
        sender=sender,
        nonce=1,
        verificationGasLimit=v_gas_limit,
        callGasLimit=c_gas_limit,
        preVerificationGas=50000,
        maxPriorityFeePerGas=10**9,
        maxFeePerGas=2 * 10**9
    )
    
    packed = op.to_packed()
    
    # Expected accountGasLimits: (v_gas_limit << 128) | c_gas_limit
    # v_gas_limit in hex: 000000000000000000000000000186a0
    # c_gas_limit in hex: 00000000000000000000000000030d40
    expected_gas_limits = f"0x{v_gas_limit:032x}{c_gas_limit:032x}"
    assert packed.accountGasLimits == expected_gas_limits

def test_paymaster_data_v09():
    pm_addr = to_checksum_address("0x" + "2" * 40)
    pm_data = PaymasterData(
        paymaster=pm_addr,
        verificationGasLimit=123,
        postOpGasLimit=456,
        data="0xabcdef"
    )
    
    encoded = pm_data.encode()
    # Length check: 20 (addr) + 16 (v_limit) + 16 (p_limit) + 3 (data) = 55 bytes
    # Hex string: 0x + 110 chars
    assert len(encoded) == 2 + 40 + 32 + 32 + 6
    assert pm_addr.lower()[2:] in encoded

def test_hashing_consistency():
    entry_point = to_checksum_address("0x" + "e" * 40)
    chain_id = 1
    
    op = UserOperation(
        sender=to_checksum_address("0x" + "a" * 40),
        nonce=0,
        verificationGasLimit=100,
        callGasLimit=200,
        preVerificationGas=300,
        maxPriorityFeePerGas=1,
        maxFeePerGas=2
    )
    
    hash1 = get_user_op_hash(op, entry_point, chain_id)
    hash2 = get_user_op_hash(op.to_packed(), entry_point, chain_id)
    
    assert hash1 == hash2
    assert len(hash1) == 32

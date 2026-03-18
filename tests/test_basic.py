import pytest
from aa_py.models import UserOperation
from aa_py.hashing import get_user_op_hash
from aa_py.signer import UserOpSigner

def test_user_op_to_packed():
    user_op = UserOperation(
        sender="0x" + "1" * 40,
        nonce=1,
        initCode="0x",
        callData="0x",
        verificationGasLimit=100000,
        callGasLimit=200000,
        preVerificationGas=50000,
        maxPriorityFeePerGas=10**9,
        maxFeePerGas=2 * 10**9,
        paymasterAndData="0x",
        signature="0x"
    )
    packed_op = user_op.to_packed()
    
    # accountGasLimits = (100000 << 128) | 200000
    expected_gas_limits = (100000 << 128) | 200000
    assert int(packed_op.accountGasLimits, 16) == expected_gas_limits
    
    # gasFees = (10**9 << 128) | (2 * 10**9)
    expected_gas_fees = (10**9 << 128) | (2 * 10**9)
    assert int(packed_op.gasFees, 16) == expected_gas_fees


def test_signer():
    private_key = "0x" + "1" * 64
    signer = UserOpSigner(private_key)
    
    user_op = UserOperation(
        sender="0x" + "1" * 40,
        nonce=1,
        initCode="0x",
        callData="0x",
        verificationGasLimit=100000,
        callGasLimit=200000,
        preVerificationGas=50000,
        maxPriorityFeePerGas=10**9,
        maxFeePerGas=2 * 10**9,
        paymasterAndData="0x",
        signature="0x"
    )
    
    entry_point = "0x0000000071727De22E5E9d8BAf0edAc6f37a032d" # EntryPoint v0.7
    chain_id = 1
    
    signature = signer.sign_user_op(user_op, entry_point, chain_id)
    assert signature.startswith("0x")
    assert len(signature) == 132 # 65 bytes + 0x

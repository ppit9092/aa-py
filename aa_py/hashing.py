from eth_abi import encode
from eth_utils import keccak, to_bytes, to_hex
from .models import UserOperation, PackedUserOperation

# TYPE_HASH for PackedUserOperation as defined in EntryPoint v0.7+
# Note: Field types must match the EIP-712 definition in the EntryPoint contract
PACKED_USER_OP_TYPEHASH = keccak(
    b"PackedUserOperation(address sender,uint256 nonce,bytes initCode,bytes callData,bytes32 accountGasLimits,uint256 preVerificationGas,bytes32 gasFees,bytes paymasterAndData)"
)

def pack_user_op(user_op: PackedUserOperation) -> bytes:
    """
    Packs the UserOperation for hashing.
    Used for keccak256(packUserOp(op)) in EntryPoint.
    """
    init_code_hash = keccak(to_bytes(hexstr=user_op.initCode))
    call_data_hash = keccak(to_bytes(hexstr=user_op.callData))
    paymaster_and_data_hash = keccak(to_bytes(hexstr=user_op.paymasterAndData))

    return encode(
        ['address', 'uint256', 'bytes32', 'bytes32', 'bytes32', 'uint256', 'bytes32', 'bytes32'],
        [
            to_bytes(hexstr=user_op.sender),
            user_op.nonce,
            init_code_hash,
            call_data_hash,
            to_bytes(hexstr=user_op.accountGasLimits),
            user_op.preVerificationGas,
            to_bytes(hexstr=user_op.gasFees),
            paymaster_and_data_hash
        ]
    )

def get_user_op_hash(user_op: UserOperation | PackedUserOperation, entry_point: str, chain_id: int) -> bytes:
    """
    Calculates the UserOperation hash (EIP-712).
    In EntryPoint v0.7+, this is keccak256(abi.encode(keccak256(pack(userOp)), entryPoint, chainId))
    """
    if isinstance(user_op, UserOperation):
        packed_op = user_op.to_packed()
    else:
        packed_op = user_op

    # EntryPoint.getUserOpHash(op) implementation:
    # return keccak256(abi.encode(keccak256(pack(userOp)), entryPoint, chainId))
    user_op_hash = keccak(pack_user_op(packed_op))
    
    return keccak(encode(
        ['bytes32', 'address', 'uint256'],
        [user_op_hash, to_bytes(hexstr=entry_point), chain_id]
    ))

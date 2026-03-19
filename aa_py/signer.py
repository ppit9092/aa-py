from typing import Union
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_bytes, to_hex
from .models import UserOperation, PackedUserOperation
from .hashing import get_user_op_hash

class UserOpSigner:
    """
    Signer for ERC-4337 UserOperations.
    Supports standard ECDSA signing.
    """
    def __init__(self, private_key: str):
        self.account = Account.from_key(private_key)
        self.address = self.account.address

    def sign_user_op(self, user_op: Union[UserOperation, PackedUserOperation], entry_point: str, chain_id: int) -> str:
        """
        Signs the UserOperation hash.
        """
        user_op_hash = get_user_op_hash(user_op, entry_point, chain_id)
        
        # AA standard signature for raw UserOp hash
        signature = self.account.unsafe_sign_hash(user_op_hash)
        
        return to_hex(signature.signature)

    def get_signature(self, user_op_hash: bytes) -> str:
        """
        Directly sign a pre-calculated hash.
        """
        return to_hex(self.account.unsafe_sign_hash(user_op_hash).signature)

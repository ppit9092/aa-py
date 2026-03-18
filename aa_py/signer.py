from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_bytes
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

    def sign_user_op(self, user_op: UserOperation | PackedUserOperation, entry_point: str, chain_id: int) -> str:
        """
        Signs the UserOperation hash.
        Note: Most Bundlers expect the signature to be the raw ECDSA signature (65 bytes).
        EntryPoint v0.8/v0.9 uses the hash derived from get_user_op_hash.
        """
        user_op_hash = get_user_op_hash(user_op, entry_point, chain_id)
        
        # In AA, we usually sign the raw hash without the EIP-191 prefix 
        # unless the account contract explicitly uses it. 
        # Most EntryPoints expect the signature of the hash itself.
        signature = self.account.sign_msg_hash(user_op_hash)
        
        return signature.signature.hex()

    def get_signature(self, user_op_hash: bytes) -> str:
        """
        Directly sign a pre-calculated hash.
        """
        return self.account.sign_msg_hash(user_op_hash).signature.hex()

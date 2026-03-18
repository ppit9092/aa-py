from typing import List, Optional, Union
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak, to_bytes, to_hex
import rlp
from rlp.sedes import List as RLPList, CountableList, Binary, big_endian_int, Binary

class Authorization:
    """
    EIP-7702 Authorization object.
    [chain_id, address, nonce, y_parity, r, s]
    """
    def __init__(self, chain_id: int, address: str, nonce: int, y_parity: int = 0, r: int = 0, s: int = 0):
        self.chain_id = chain_id
        self.address = address
        self.nonce = nonce
        self.y_parity = y_parity
        self.r = r
        self.s = s

    def get_payload(self) -> bytes:
        """
        Returns the RLP encoded [chain_id, address, nonce] for signing.
        """
        # Note: address must be 20 bytes
        addr_bytes = to_bytes(hexstr=self.address)
        return rlp.encode([self.chain_id, addr_bytes, self.nonce])

    def get_signing_hash(self) -> bytes:
        """
        Returns keccak256(0x05 || rlp([chain_id, address, nonce])).
        """
        return keccak(b'\x05' + self.get_payload())

    def sign(self, private_key: str):
        """
        Signs the authorization with the EOA private key.
        """
        account = Account.from_key(private_key)
        signing_hash = self.get_signing_hash()
        signature = account.sign_msg_hash(signing_hash)
        
        self.y_parity = signature.v % 2 # EIP-7702 uses y_parity (0 or 1)
        self.r = signature.r
        self.s = signature.s
        return self

    def to_list(self) -> List:
        """
        Returns the list format for RLP encoding in a Type-4 transaction.
        """
        return [
            self.chain_id,
            to_bytes(hexstr=self.address),
            self.nonce,
            self.y_parity,
            self.r,
            self.s
        ]

class EIP7702Transaction:
    """
    Helper for building Type-4 (0x04) transactions.
    """
    def __init__(self, tx_data: dict, authorizations: List[Authorization]):
        self.tx_data = tx_data
        self.authorizations = authorizations

    def prepare(self) -> dict:
        """
        Prepares the transaction dictionary for web3.py.
        """
        prepared = self.tx_data.copy()
        prepared['type'] = 4 # Type-4 Transaction
        prepared['authorizationList'] = [auth.to_list() for auth in self.authorizations]
        return prepared

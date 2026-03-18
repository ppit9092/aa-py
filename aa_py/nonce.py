from typing import Optional

class NonceManager:
    """
    Manages 2D nonces for ERC-4337 UserOperations.
    Structure: [192-bit key | 64-bit sequence]
    """
    @staticmethod
    def pack_nonce(key: int, sequence: int) -> int:
        """
        Packs key and sequence into a single uint256 nonce.
        """
        return (key << 64) | sequence

    @staticmethod
    def unpack_nonce(nonce: int) -> tuple[int, int]:
        """
        Unpacks a uint256 nonce into (key, sequence).
        """
        key = nonce >> 64
        sequence = nonce & 0xFFFFFFFFFFFFFFFF
        return key, sequence

    def __init__(self, w3, sender_address: str, entry_point_address: str):
        self.w3 = w3
        self.sender = sender_address
        self.entry_point = entry_point_address
        # Cache for local sequence tracking if needed
        self._local_sequences: dict[int, int] = {}

    def get_nonce(self, key: int = 0) -> int:
        """
        Fetches the next valid nonce from the EntryPoint contract for a specific key.
        """
        # EntryPoint.getNonce(address sender, uint192 key)
        # We use a raw call or the contract instance if available
        # For now, we'll assume a standard getNonce call via w3
        nonce = self.w3.eth.call({
            "to": self.entry_point,
            "data": f"0x35568e5a{self.sender[2:].zfill(64)}{hex(key)[2:].zfill(64)}" # getNonce selector
        })
        return int(nonce.hex(), 16)

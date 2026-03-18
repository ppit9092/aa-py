from typing import Any, Dict, Optional, Union
from web3 import Web3
from .base import PaymasterClient
from ..models import UserOperation, PackedUserOperation

class ERC7677PaymasterClient(PaymasterClient):
    """
    General purpose ERC-7677 Paymaster Client for providers like Pimlico, Alchemy, etc.
    """
    def __init__(self, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

    def get_paymaster_stub_data(
        self, 
        user_op: UserOperation | PackedUserOperation, 
        entry_point: str, 
        chain_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Implementation of pm_getPaymasterStubData.
        """
        packed_op = user_op.to_packed() if isinstance(user_op, UserOperation) else user_op
        op_dict = packed_op.model_dump()
        
        # ERC-7677 params: [userOp, entryPoint, chainId, context]
        return self.w3.manager.request_blocking(
            "pm_getPaymasterStubData",
            [op_dict, entry_point, hex(chain_id), context or {}]
        )

    def get_paymaster_and_data(
        self, 
        user_op: UserOperation | PackedUserOperation, 
        entry_point: str, 
        chain_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Implementation of pm_getPaymasterAndData.
        Handles both v0.7 (paymasterAndData) and v0.9 (paymasterData + paymasterSignature).
        """
        packed_op = user_op.to_packed() if isinstance(user_op, UserOperation) else user_op
        op_dict = packed_op.model_dump()

        return self.w3.manager.request_blocking(
            "pm_getPaymasterAndData",
            [op_dict, entry_point, hex(chain_id), context or {}]
        )

class PimlicoPaymasterClient(ERC7677PaymasterClient):
    """
    Pimlico specific adapter (inherits ERC-7677).
    """
    def sponsor_user_op(self, user_op: UserOperation, entry_point: str, chain_id: int) -> UserOperation:
        """
        High-level helper to sponsor a UserOp in one call.
        """
        stub = self.get_paymaster_stub_data(user_op, entry_point, chain_id)
        # Update UserOp with stub data (e.g. for gas estimation)
        # Final sponsorship:
        final = self.get_paymaster_and_data(user_op, entry_point, chain_id)
        # v0.9+ handling: if 'paymasterSignature' is in final, it's v0.9
        return final

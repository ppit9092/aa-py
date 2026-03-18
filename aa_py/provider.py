from typing import Any, Dict, List, Optional, Union
from web3 import Web3
from .models import UserOperation, PackedUserOperation

class BundlerProvider:
    """
    Provider for interacting with an ERC-4337 Bundler RPC.
    """
    def __init__(self, rpc_url: str, entry_point: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.entry_point = entry_point

    def send_user_op(self, user_op: UserOperation | PackedUserOperation) -> str:
        """
        Calls eth_sendUserOperation.
        """
        packed_op = user_op.to_packed() if isinstance(user_op, UserOperation) else user_op
        
        # Prepare params for JSON-RPC
        # Most bundlers expect a dict for the UserOp
        op_dict = packed_op.model_dump()
        
        response = self.w3.manager.request_blocking(
            "eth_sendUserOperation",
            [op_dict, self.entry_point]
        )
        return response

    def estimate_user_op_gas(self, user_op: UserOperation | PackedUserOperation) -> Dict[str, Any]:
        """
        Calls eth_estimateUserOperationGas.
        Returns verificationGasLimit, callGasLimit, preVerificationGas.
        """
        packed_op = user_op.to_packed() if isinstance(user_op, UserOperation) else user_op
        op_dict = packed_op.model_dump()
        
        return self.w3.manager.request_blocking(
            "eth_estimateUserOperationGas",
            [op_dict, self.entry_point]
        )

    def get_user_op_receipt(self, user_op_hash: str) -> Optional[Dict[str, Any]]:
        """
        Calls eth_getUserOperationReceipt.
        """
        return self.request("eth_getUserOperationReceipt", [user_op_hash])

    def request(self, method: str, params: List[Any]) -> Any:
        try:
            return self.w3.manager.request_blocking(method, params)
        except Exception as e:
            # Better error handling for AA-specific RPC errors
            raise Exception(f"Bundler RPC error {method}: {str(e)}")

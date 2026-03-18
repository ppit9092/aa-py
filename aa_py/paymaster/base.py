from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..models import UserOperation, PackedUserOperation

class PaymasterClient(ABC):
    """
    Abstract base class for Paymaster service interactions.
    Follows ERC-7677 standard.
    """
    
    @abstractmethod
    def get_paymaster_stub_data(
        self, 
        user_op: UserOperation | PackedUserOperation, 
        entry_point: str, 
        chain_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calls pm_getPaymasterStubData. 
        Used for gas estimation with a 'stub' signature.
        """
        pass

    @abstractmethod
    def get_paymaster_and_data(
        self, 
        user_op: UserOperation | PackedUserOperation, 
        entry_point: str, 
        chain_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calls pm_getPaymasterAndData.
        Returns the final paymasterAndData (v0.7) or paymasterData + paymasterSignature (v0.9).
        """
        pass

from typing import Any, Dict, List, Optional, Union
from eth_utils import to_checksum_address, to_hex
from .models import UserOperation, PaymasterData
from .signer import UserOpSigner
from .nonce import NonceManager
from .provider import BundlerProvider
from .paymaster.base import PaymasterClient

class SmartAccount:
    """
    High-level abstraction for an ERC-4337 Smart Account.
    Orchestrates nonce management, gas estimation, paymaster sponsorship, and signing.
    """
    def __init__(
        self,
        address: str,
        signer: UserOpSigner,
        provider: BundlerProvider,
        entry_point: str,
        chain_id: int,
        paymaster: Optional[PaymasterClient] = None
    ):
        self.address = to_checksum_address(address)
        self.signer = signer
        self.provider = provider
        self.entry_point = to_checksum_address(entry_point)
        self.chain_id = chain_id
        self.paymaster = paymaster
        self.nonce_manager = NonceManager(provider.w3, self.address, self.entry_point)

    def create_unsigned_user_op(self, call_data: str, nonce_key: int = 0) -> UserOperation:
        """
        Creates a basic UserOperation with current nonce and basic fields.
        """
        nonce = self.nonce_manager.get_nonce(nonce_key)
        return UserOperation(
            sender=self.address,
            nonce=nonce,
            callData=call_data,
            # Placeholder gas values (will be estimated later)
            verificationGasLimit=100000,
            callGasLimit=100000,
            preVerificationGas=50000,
            maxPriorityFeePerGas=10**9,
            maxFeePerGas=2 * 10**9
        )

    def send_transaction(self, to: str, data: str = "0x", value: int = 0) -> str:
        """
        Full flow: build -> estimate -> sponsor -> sign -> send.
        Returns UserOpHash.
        """
        # 1. Build simple execute(to, value, data) callData 
        # (Assuming standard execute selector: 0xb61d27f6)
        # For a real implementation, we'd use a contract factory or ABI.
        # This is a placeholder for the account-specific 'execute' logic.
        target = to[2:].zfill(64)
        val = hex(value)[2:].zfill(64)
        # Simplified: just raw callData for demo
        user_op = self.create_unsigned_user_op(data)

        # 2. Paymaster Sponsorship (Optional)
        if self.paymaster:
            stub_res = self.paymaster.get_paymaster_stub_data(user_op, self.entry_point, self.chain_id)
            # Update gas fields from stub if provided
            if "verificationGasLimit" in stub_res:
                user_op.verificationGasLimit = int(stub_res["verificationGasLimit"], 16)
            if "paymasterAndData" in stub_res:
                user_op.paymasterData = None # Ensure we don't mix modes
                # Directly update if v0.7
                pass

        # 3. Gas Estimation
        gas_estimates = self.provider.estimate_user_op_gas(user_op)
        user_op.verificationGasLimit = int(gas_estimates.get('verificationGasLimit', user_op.verificationGasLimit), 16)
        user_op.callGasLimit = int(gas_estimates.get('callGasLimit', user_op.callGasLimit), 16)
        user_op.preVerificationGas = int(gas_estimates.get('preVerificationGas', user_op.preVerificationGas), 16)

        # 4. Final Sponsorship
        if self.paymaster:
            final_pm = self.paymaster.get_paymaster_and_data(user_op, self.entry_point, self.chain_id)
            
            # v0.9+ Handling (Explicit paymasterData + paymasterSignature)
            if "paymasterData" in final_pm and "paymasterSignature" in final_pm:
                # In v0.9, signature is a separate field in the UserOp structure
                # We'll need to adapt the signature logic to include both user and PM signatures
                # or rely on the Bundler to handle the parallel signature.
                pass
            
            # v0.7 Handling (Legacy packed paymasterAndData)
            elif "paymasterAndData" in final_pm:
                # We use a special field in UserOperation to hold the raw bytes
                # For v0.7 compatibility in a v0.9 model
                pass

        # 5. Signing
        # Sign the UserOp hash (EIP-712)
        user_op.signature = self.signer.sign_user_op(user_op, self.entry_point, self.chain_id)

        # 6. Submission
        return self.provider.send_user_op(user_op)

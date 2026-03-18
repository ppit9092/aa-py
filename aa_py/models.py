from typing import Annotated, Optional
from pydantic import BaseModel, Field, field_validator
from eth_typing import ChecksumAddress, HexStr
from eth_utils import to_checksum_address, is_hex, is_hex_address, to_bytes


def validate_hex_address(v: str) -> ChecksumAddress:
    if not is_hex_address(v):
        raise ValueError("Invalid hex address")
    return to_checksum_address(v)


def validate_hex_str(v: str) -> HexStr:
    if not is_hex(v):
        raise ValueError("Invalid hex string")
    return HexStr(v)


class PaymasterData(BaseModel):
    """
    Structured Paymaster data for EntryPoint v0.7+.
    [address(20) | uint128(verificationGasLimit) | uint128(postOpGasLimit) | data(any)]
    """
    paymaster: str
    verificationGasLimit: int = 0
    postOpGasLimit: int = 0
    data: HexStr = Field(default="0x")

    def encode(self) -> str:
        if not self.paymaster or self.paymaster == "0x0000000000000000000000000000000000000000":
            return "0x"
        # address (20 bytes)
        addr = to_bytes(hexstr=self.paymaster).hex()
        # verificationGasLimit (16 bytes / 128 bits)
        v_limit = self.verificationGasLimit.to_bytes(16, "big").hex()
        # postOpGasLimit (16 bytes / 128 bits)
        p_limit = self.postOpGasLimit.to_bytes(16, "big").hex()
        # raw data
        raw_data = self.data[2:] if self.data.startswith("0x") else self.data
        return f"0x{addr}{v_limit}{p_limit}{raw_data}"


class UserOperation(BaseModel):
    """
    UserOperation for EntryPoint v0.8/v0.9+.
    """
    sender: str
    nonce: int
    initCode: HexStr = Field(default="0x")
    callData: HexStr = Field(default="0x")
    verificationGasLimit: int = 0
    callGasLimit: int = 0
    preVerificationGas: int = 0
    maxPriorityFeePerGas: int = 0
    maxFeePerGas: int = 0
    paymasterData: Optional[PaymasterData] = None
    signature: HexStr = Field(default="0x")

    @field_validator("sender", mode="before")
    @classmethod
    def validate_sender(cls, v: str) -> str:
        return validate_hex_address(v)

    def to_packed(self) -> "PackedUserOperation":
        # Pack uint128(verificationGasLimit) | uint128(callGasLimit)
        account_gas_limits = (self.verificationGasLimit << 128) | self.callGasLimit
        # Pack uint128(maxPriorityFeePerGas) | uint128(maxFeePerGas)
        gas_fees = (self.maxPriorityFeePerGas << 128) | self.maxFeePerGas
        
        pm_and_data = "0x"
        if self.paymasterData:
            pm_and_data = self.paymasterData.encode()

        return PackedUserOperation(
            sender=self.sender,
            nonce=self.nonce,
            initCode=self.initCode,
            callData=self.callData,
            accountGasLimits=f"0x{account_gas_limits:064x}",
            preVerificationGas=self.preVerificationGas,
            gasFees=f"0x{gas_fees:064x}",
            paymasterAndData=pm_and_data,
            signature=self.signature
        )


class PackedUserOperation(BaseModel):
    """
    PackedUserOperation for EntryPoint v0.7+ (and v0.8/v0.9 updates).
    Reference: EIP-4337 v0.7 changes.
    """
    sender: str
    nonce: int
    initCode: HexStr = Field(default="0x")
    callData: HexStr = Field(default="0x")
    # packed (uint128 verificationGasLimit | uint128 callGasLimit)
    accountGasLimits: HexStr
    preVerificationGas: int
    # packed (uint128 maxPriorityFeePerGas | uint128 maxFeePerGas)
    gasFees: HexStr
    paymasterAndData: HexStr = Field(default="0x")
    signature: HexStr = Field(default="0x")

    @field_validator("sender", mode="before")
    @classmethod
    def validate_sender(cls, v: str) -> str:
        return validate_hex_address(v)

    @field_validator("accountGasLimits", "gasFees", mode="before")
    @classmethod
    def validate_hex_fields(cls, v: str) -> str:
        if isinstance(v, int):
            return hex(v)
        return validate_hex_str(v)

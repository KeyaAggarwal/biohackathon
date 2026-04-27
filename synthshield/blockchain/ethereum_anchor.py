"""
Ethereum L2 Integration for SynthShield Forensic Black Box.
Submits daily Merkle roots to Ethereum L2 (Optimism, Arbitrum, Base) for S.3741 compliance.
"""

import os
import json
import time
from typing import Optional, Dict
from datetime import datetime

try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False


# ForensicAnchor Smart Contract ABI
FORENSIC_ANCHOR_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
            {"internalType": "string", "name": "hardwareId", "type": "string"},
            {"internalType": "string", "name": "dataUrl", "type": "string"}
        ],
        "name": "submitAnchor",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "synthesizer", "type": "address"},
            {"internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"}
        ],
        "name": "verifyAnchor",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "synthesizer", "type": "address"},
            {"indexed": True, "internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
            {"internalType": "string", "name": "hardwareId", "type": "string"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "string", "name": "dataUrl", "type": "string"}
        ],
        "name": "MerkleRootAnchored",
        "type": "event"
    }
]


class EthereumAnchor:
    """
    L2 Ethereum integration for Merkle root submission.
    Serves as the immutability layer for forensic audit trails per S.3741.
    """
    
    def __init__(
        self,
        contract_address: str,
        rpc_url: str,
        private_key: str,
        hardware_id: str,
        network: str = "optimism"
    ):
        """
        Initialize L2 anchor submission client.
        
        Args:
            contract_address: Deployed ForensicAnchor contract address on L2
            rpc_url: L2 RPC endpoint (e.g., https://mainnet.optimism.io)
            private_key: Synthesizer wallet private key (hex, without 0x prefix)
            hardware_id: Unique TPM/secure enclave identifier
            network: L2 network name ('optimism', 'arbitrum', 'base')
        """
        if not WEB3_AVAILABLE:
            raise ImportError("web3 library required. Install: pip install web3 eth-account")
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {network} at {rpc_url}")
        
        # Setup contract
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=FORENSIC_ANCHOR_ABI
        )
        
        # Setup account
        private_key_normalized = private_key if private_key.startswith('0x') else '0x' + private_key
        self.account = Account.from_key(private_key_normalized)
        
        self.hardware_id = hardware_id
        self.network = network
        self.rpc_url = rpc_url
        
        # Submission history
        self.submission_history = []
        
        self._log_init()
    
    @classmethod
    def from_env(cls):
        """Initialize from environment variables for production deployment."""
        import os
        return cls(
            contract_address=os.getenv("L2_CONTRACT_ADDRESS"),
            rpc_url=os.getenv("L2_RPC_URL"),
            private_key=os.getenv("L2_PRIVATE_KEY"),
            hardware_id=os.getenv("L2_HARDWARE_ID", "SYNTH-001"),
            network=os.getenv("L2_NETWORK", "optimism")
        )
    
    def _log_init(self):
        """Log initialization details."""
        print(f"[L2 ANCHOR] Initialized on {self.network.upper()}")
        print(f"  Contract:  {self.contract_address}")
        print(f"  Wallet:    {self.account.address}")
        print(f"  Hardware:  {self.hardware_id}")
    
    def submit_merkle_root(
        self,
        merkle_root_hex: str,
        data_url: str = "ipfs://bafkyabc123",
        simulate: bool = False,
        wait_for_receipt: bool = True
    ) -> Optional[Dict]:
        """
        Submit a Merkle root to the L2 smart contract.
        
        Args:
            merkle_root_hex: Root hash (with or without 0x prefix)
            data_url: IPFS hash or off-chain URL for full logs
            simulate: If True, estimate gas without submitting
            wait_for_receipt: If True, wait for transaction confirmation
        
        Returns:
            Dict with transaction details or None if simulated
        """
        try:
            # Normalize hex format
            if not merkle_root_hex.startswith('0x'):
                merkle_root_hex = '0x' + merkle_root_hex
            
            if len(merkle_root_hex) != 66:  # 0x + 64 hex chars
                raise ValueError(f"Invalid merkle root length: {merkle_root_hex}")
            
            merkle_root_bytes = bytes.fromhex(merkle_root_hex[2:])
            
            # Build transaction
            tx = self.contract.functions.submitAnchor(
                merkle_root_bytes,
                self.hardware_id,
                data_url
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.w3.eth.chain_id,
            })
            
            if simulate:
                # Estimate gas only
                gas_estimate = self.w3.eth.estimate_gas(tx)
                return {
                    'type': 'simulation',
                    'gas_estimate': gas_estimate,
                    'merkle_root': merkle_root_hex
                }
            
            # Sign and submit transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            result = {
                'type': 'submission',
                'network': self.network,
                'tx_hash': tx_hash.hex(),
                'merkle_root': merkle_root_hex,
                'hardware_id': self.hardware_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            print(f"\n[L2 ANCHOR] Merkle root submitted to {self.network.upper()}")
            print(f"  TX Hash:  {tx_hash.hex()}")
            print(f"  Root:     {merkle_root_hex[:20]}...{merkle_root_hex[-8:]}")
            
            # Wait for receipt if requested
            if wait_for_receipt:
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                result['status'] = 'confirmed' if receipt['status'] else 'failed'
                result['block_number'] = receipt['blockNumber']
                result['gas_used'] = receipt['gasUsed']
                print(f"  Status:   {result['status'].upper()}")
                print(f"  Block:    {receipt['blockNumber']}")
            
            # Record submission
            self.submission_history.append(result)
            return result
        
        except Exception as e:
            print(f"[L2 ANCHOR ERROR] {str(e)}")
            return None
    
    def verify_anchor_on_chain(
        self,
        synthesizer_address: str,
        merkle_root_hex: str
    ) -> bool:
        """
        Verify if a Merkle root is anchored on-chain for a synthesizer.
        
        Args:
            synthesizer_address: Wallet address that submitted the root
            merkle_root_hex: Root hash to verify
        
        Returns:
            True if verified on-chain, False otherwise
        """
        try:
            if not merkle_root_hex.startswith('0x'):
                merkle_root_hex = '0x' + merkle_root_hex
            
            merkle_root_bytes = bytes.fromhex(merkle_root_hex[2:])
            synthesizer_addr = Web3.to_checksum_address(synthesizer_address)
            
            is_valid = self.contract.functions.verifyAnchor(
                synthesizer_addr,
                merkle_root_bytes
            ).call()
            
            return is_valid
        except Exception as e:
            print(f"[L2 ANCHOR] Verification error: {str(e)}")
            return False
    
    def get_submission_history(self) -> list:
        """Get all Merkle root submissions from this session."""
        return self.submission_history
    
    @staticmethod
    def from_env() -> Optional['EthereumAnchor']:
        """
        Initialize EthereumAnchor from environment variables.
        
        Required env vars:
            - L2_CONTRACT_ADDRESS: Deployed contract address
            - L2_RPC_URL: L2 RPC endpoint
            - L2_PRIVATE_KEY: Wallet private key
            - L2_HARDWARE_ID: Hardware identifier
            - L2_NETWORK: Network name (default: optimism)
        """
        try:
            return EthereumAnchor(
                contract_address=os.getenv('L2_CONTRACT_ADDRESS'),
                rpc_url=os.getenv('L2_RPC_URL'),
                private_key=os.getenv('L2_PRIVATE_KEY'),
                hardware_id=os.getenv('L2_HARDWARE_ID'),
                network=os.getenv('L2_NETWORK', 'optimism')
            )
        except Exception as e:
            print(f"[L2 ANCHOR] Failed to initialize from env: {str(e)}")
            return None


class MockEthereumAnchor:
    """
    Mock L2 anchor for testing without network connectivity.
    Simulates submissions and maintains local verification.
    """
    
    def __init__(self, hardware_id: str = "mock-hardware-001"):
        self.hardware_id = hardware_id
        self.submissions = {}
        self.network = "mock"
        print(f"[MOCK L2 ANCHOR] Initialized (no network required)")
    
    def submit_merkle_root(
        self,
        merkle_root_hex: str,
        data_url: str = "ipfs://mock",
        simulate: bool = False,
        wait_for_receipt: bool = True
    ) -> Dict:
        """Simulate Merkle root submission."""
        if not merkle_root_hex.startswith('0x'):
            merkle_root_hex = '0x' + merkle_root_hex
        
        mock_tx_hash = f"0x{'a' * 64}"
        
        result = {
            'type': 'submission',
            'network': 'mock',
            'tx_hash': mock_tx_hash,
            'merkle_root': merkle_root_hex,
            'hardware_id': self.hardware_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'confirmed',
            'block_number': 12345678
        }
        
        self.submissions[merkle_root_hex] = result
        
        print(f"[MOCK L2 ANCHOR] Merkle root recorded")
        print(f"  Root: {merkle_root_hex[:20]}...{merkle_root_hex[-8:]}")
        print(f"  Mock TX: {mock_tx_hash[:20]}...")
        
        return result
    
    def verify_anchor_on_chain(
        self,
        synthesizer_address: str,
        merkle_root_hex: str
    ) -> bool:
        """Verify submission in mock storage."""
        if not merkle_root_hex.startswith('0x'):
            merkle_root_hex = '0x' + merkle_root_hex
        
        return merkle_root_hex in self.submissions
    
    def get_submission_history(self) -> list:
        """Get all mock submissions."""
        return list(self.submissions.values())

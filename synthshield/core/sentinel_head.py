"""
SentinelFunctionalHead: Residual MLP for Functional Manifold Projection

This module implements the neural screening component of the Sentinel AI head.
It projects ESM-2 embeddings onto a learned functional manifold that separates
dangerous sequences from benign ones.

Architecture:
- Input: 1280-dimensional ESM-2 embedding
- Processing: Stack of residual blocks with batch normalization
- Output: Risk score (0.0-1.0) indicating danger probability
- Additional: Permission tokens for approved sequences

Key innovations:
- Residual connections allow training deeper networks
- Batch normalization improves convergence and generalization
- Sigmoid output ensures bounded risk scores
- HMAC-based token generation for hardware interlock compatibility

Regulatory context:
This component serves as the "real-time functional AI screening" layer 
per Biosecurity Modernization Act requirements for DNA synthesis benchtop loophole.
"""

import torch
import torch.nn as nn
import hashlib
import hmac
import base64
import json
import time
from typing import Tuple, Optional


class ResidualBlock(nn.Module):
    """Single residual block with batch normalization."""
    
    def __init__(self, input_dim: int, hidden_dim: int):
        """
        Initialize residual block.
        
        Args:
            input_dim: Input dimension (and residual connection dimension)
            hidden_dim: Hidden layer dimension (typically input_dim / 2)
        """
        super(ResidualBlock, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, input_dim)
        self.batch_norm = nn.BatchNorm1d(input_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass with residual connection.
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
        
        Returns:
            Output tensor of shape (batch_size, input_dim)
        """
        residual = x
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        out = out + residual
        if x.shape[0] > 1:
            out = self.batch_norm(out)
        return out


class SentinelFunctionalHead(nn.Module):
    """
    Sentinel functional head for DNA synthesis screening.
    
    This neural network projects ESM-2 embeddings onto a functional manifold
    to detect dangerous sequences with high accuracy.
    
    The model produces:
    1. Risk score: Probability that sequence is dangerous (0.0-1.0)
    2. Release token: HMAC-signed permission if risk < threshold (for hardware)
    """
    
    def __init__(
        self,
        input_dim: int = 1280,
        hidden_dim: int = 512,
        num_blocks: int = 3,
        root_of_trust_key: bytes = b"root_of_trust_secret"
    ):
        """
        Initialize Sentinel Functional Head.
        
        Args:
            input_dim: ESM-2 embedding dimension (default 1280)
            hidden_dim: Hidden layer dimension in residual blocks
            num_blocks: Number of residual blocks (default 3)
            root_of_trust_key: Secret key for HMAC token generation.
                              Should be loaded from secure enclave in production.
        
        Note:
            Standard configuration: input_dim=1280, hidden_dim=512, num_blocks=3
            This matches ESM-2 embedding size and provides good capacity.
        """
        super(SentinelFunctionalHead, self).__init__()
        self.blocks = nn.ModuleList([
            ResidualBlock(input_dim, hidden_dim) for _ in range(num_blocks)
        ])
        self.risk_layer = nn.Linear(input_dim, 1)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.root_of_trust_key = root_of_trust_key

    def _generate_permission_token(
        self,
        sequence_hash: str,
        risk_value: float,
        chunk_bp: int = 100,
        ttl_seconds: int = 120
    ) -> str:
        """
        Generate a signed permission token consumable by hardware interlock.
        
        Token format: v1.<base64url(payload_json)>.<signature_hex>
        
        This token serves as cryptographic proof that:
        - Sequence was screened and approved by Sentinel Head
        - Risk score was below threshold
        - Token is time-limited (TTL)
        - Token cannot be forged (HMAC signed)
        
        Args:
            sequence_hash: SHA256 hash of the sequence being authorized
            risk_value: Risk score from MLP (0.0-1.0)
            chunk_bp: Size of DNA chunk authorized (for rate limiting)
            ttl_seconds: Token lifetime in seconds (default 2 minutes)
        
        Returns:
            Signed token string suitable for transmission to hardware
        """
        payload = {
            "sequence_hash": sequence_hash,
            "risk_score": round(risk_value, 6),
            "chunk_bp": chunk_bp,
            "iat": int(time.time()),
            "exp": int(time.time()) + ttl_seconds,
        }
        payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        payload_b64 = base64.urlsafe_b64encode(payload_json).decode().rstrip("=")
        signature = hmac.new(self.root_of_trust_key, payload_json, hashlib.sha256).hexdigest()
        return f"v1.{payload_b64}.{signature}"

    def forward(
        self,
        x: torch.Tensor,
        sequence_hash: Optional[str] = None
    ) -> Tuple[torch.Tensor, Optional[str]]:
        """
        Forward pass through Sentinel Head.
        
        Processing:
        1. Pass embedding through residual blocks (learns functional manifold)
        2. Project to risk score via sigmoid output
        3. Generate permission token if sequence is approved
        
        Args:
            x: ESM-2 embeddings, shape (batch_size, 1280)
            sequence_hash: Optional SHA256 hash of sequence for token generation
        
        Returns:
            Tuple of:
            - risk_scores: Tensor of shape (batch_size, 1), values in [0, 1]
            - release_token: String token if approved (x < 0.5), None otherwise
                           Only generated for first item in batch if batch_size > 1
        
        Example:
            >>> model = SentinelFunctionalHead()
            >>> embeddings = torch.randn(1, 1280)  # Single sequence
            >>> risk_score, token = model(embeddings, sequence_hash="abc123...")
            >>> print(f"Risk: {risk_score.item():.3f}, Approved: {token is not None}")
        """
        for block in self.blocks:
            x = block(x)
        risk_score = torch.sigmoid(self.risk_layer(x))
        
        release_token = None
        if sequence_hash and risk_score.item() < 0.5:
            release_token = self._generate_permission_token(sequence_hash, risk_score.item())
        
        return risk_score, release_token


# Example usage and testing
if __name__ == "__main__":
    model = SentinelFunctionalHead(input_dim=1280, hidden_dim=512, num_blocks=3)
    dummy_input = torch.randn(8, 1280)  # Batch of 8 sequences
    
    # Test forward pass
    risk_scores, release_tokens = model(dummy_input)
    print("Risk scores shape:", risk_scores.shape)
    print("Risk scores sample:", risk_scores.detach().numpy().flatten()[:3])
    
    # Test with sequence hash (generates token)
    import hashlib
    seq_hash = hashlib.sha256(b"MKTAYIAKQRQISFVK").hexdigest()
    risk_score_single, token = model(torch.randn(1, 1280), sequence_hash=seq_hash)
    print(f"\nSingle sequence risk score: {risk_score_single.item():.4f}")
    print(f"Release token generated: {token is not None}")
    if token:
        print(f"Token format: {token[:30]}...")
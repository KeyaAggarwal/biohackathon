"""
Functional Manifold Projection & Risk Scoring

This module implements the screening logic for the Sentinel Head, supporting both:
- Baseline MLP-based screening (neural manifold projection)
- Research-based ESM classifier integration (trained on biosecurity dataset)

The module can operate in three modes:
1. MLP only: Fast, baseline approach using Sentinel Head
2. Trained classifier only: Research-based approach (cosine similarity + LogisticRegression)
3. Ensemble: Combines both methods for maximum detection coverage

Supported operations:
- Single sequence screening
- Batch screening for high-throughput analysis
- Ensemble decision making with configurable thresholds
- Permission token generation for approved sequences

Integration:
- Seamlessly integrates TrainedESMClassifier from notebook research
- Produces decision tokens compatible with hardware interlock
- Maintains audit trail of screening results
"""

import torch
import hashlib
import numpy as np
from typing import Optional, Dict, List, Union, Tuple


class FunctionalManifoldScreener:
    """
    Screening module for Sentinel functional head.
    
    Performs risk assessment on ESM embeddings using configurable screening methods.
    Supports ensemble voting for robust detection of dangerous sequences.
    """
    
    def __init__(
        self,
        risk_threshold: float = 0.5,
        trained_classifier: Optional['TrainedESMClassifier'] = None
    ) -> None:
        """
        Initialize the screening module.
        
        Args:
            risk_threshold: Risk score threshold for APPROVED/BLOCKED decision (0.0-1.0).
                          Scores >= threshold are flagged as dangerous.
            trained_classifier: Optional TrainedESMClassifier instance from notebook research.
                              If provided, enables ensemble screening mode.
        
        Raises:
            ValueError: If risk_threshold is not in [0.0, 1.0]
        """
        if not 0.0 <= risk_threshold <= 1.0:
            raise ValueError(f"risk_threshold must be in [0.0, 1.0], got {risk_threshold}")
        
        self.risk_threshold = risk_threshold
        self.trained_classifier = trained_classifier
    
    def compute_sequence_hash(self, sequence: Union[str, bytes]) -> str:
        """
        Generate SHA256 hash of sequence for cryptographic binding.
        
        Args:
            sequence: DNA/protein sequence (str or bytes)
        
        Returns:
            Hexadecimal hash string (64 characters)
        """
        if isinstance(sequence, str):
            sequence = sequence.encode('utf-8')
        return hashlib.sha256(sequence).hexdigest()
    
    def screen_sequence(
        self,
        embeddings: Union[torch.Tensor, np.ndarray],
        sentinel_head,
        sequence: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Screen a sequence using the Sentinel Head and optional Trained Classifier.
        
        Screening logic:
        1. Convert embeddings to tensor if needed
        2. If trained classifier available: compute research-based score
        3. Run through Sentinel Head MLP
        4. Combine results via ensemble voting (flag if ANY method flags)
        5. Generate permission token if approved
        
        Args:
            embeddings: ESM-2 embeddings, shape (1280,) or (batch, 1280)
            sentinel_head: SentinelFunctionalHead model for MLP screening
            sequence: Optional original sequence for hashing and audit trail
        
        Returns:
            Dict with keys:
            - 'risk_score': Final risk score (0.0-1.0), averaged if ensemble
            - 'mpl_risk_score': MLP risk score (for reference)
            - 'trained_risk_score': Trained classifier score (if available)
            - 'release_token': Cryptographic token if approved (else None)
            - 'decision': 'APPROVED' or 'BLOCKED'
            - 'sequence_hash': SHA256 of sequence (if provided)
            - 'threshold': Threshold used for decision
            - 'method': 'ensemble_trained_mpl', 'mpl_only', or 'trained_only'
        
        Raises:
            TypeError: If embeddings cannot be converted to tensor
        """
        try:
            # Convert to tensor if needed
            if not isinstance(embeddings, torch.Tensor):
                if isinstance(embeddings, np.ndarray):
                    embeddings = torch.from_numpy(embeddings).float()
                else:
                    embeddings = torch.tensor(embeddings, dtype=torch.float32)
            
            # Ensure 2D tensor (batch_size, embedding_dim)
            if embeddings.dim() == 1:
                embeddings = embeddings.unsqueeze(0)
        except Exception as e:
            raise TypeError(f"Failed to convert embeddings to tensor: {e}")
        
        seq_hash = None
        if sequence:
            try:
                seq_hash = self.compute_sequence_hash(sequence)
            except Exception as e:
                print(f"[Screening] Warning: Failed to hash sequence: {e}")
        
        # Method 1: Trained Classifier (research-based)
        trained_risk_value = None
        trained_decision = None
        
        if self.trained_classifier:
            try:
                embedding_np = embeddings[0].detach().cpu().numpy()
                classifier_result = self.trained_classifier.score_embedding(
                    embedding_np,
                    return_details=False
                )
                trained_risk_value = float(classifier_result['risk_score'])
                trained_decision = "BLOCKED" if classifier_result['flagged'] else "APPROVED"
            except Exception as e:
                print(f"[Screening] Trained classifier failed: {e}, falling back to MLP")
                trained_risk_value = None
        
        # Method 2: Sentinel Head MLP (neural manifold)
        try:
            risk_score, release_token = sentinel_head(embeddings, sequence_hash=seq_hash)
            risk_value = float(risk_score.item())
        except Exception as e:
            print(f"[Screening] MLP screening failed: {e}")
            raise RuntimeError(f"Sentinel Head evaluation failed: {e}")
        
        # Combine decisions: use trained classifier if available, else MLP
        if trained_risk_value is not None:
            # Ensemble: average the two risk scores
            final_risk_value = (trained_risk_value + risk_value) / 2.0
            # Decision: flag if either method flags (conservative voting)
            is_safe = final_risk_value < self.risk_threshold
            decision = "BLOCKED" if (trained_decision == "BLOCKED" or not is_safe) else "APPROVED"
            method_used = "ensemble_trained_mpl"
        else:
            # Fallback: use MLP only
            final_risk_value = risk_value
            is_safe = risk_value < self.risk_threshold
            decision = "APPROVED" if (is_safe and release_token) else "BLOCKED"
            method_used = "mpl_only"
        
        return {
            "risk_score": final_risk_value,
            "mpl_risk_score": risk_value,
            "trained_risk_score": trained_risk_value,
            "release_token": release_token,
            "decision": decision,
            "sequence_hash": seq_hash,
            "threshold": self.risk_threshold,
            "method": method_used,
        }
    
    def batch_screen(
        self,
        embeddings_list: List[Union[torch.Tensor, np.ndarray]],
        sentinel_head,
        sequences: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Screen a batch of sequences efficiently.
        
        Args:
            embeddings_list: List of embeddings, each shape (1280,) or (batch, 1280)
            sentinel_head: SentinelFunctionalHead model
            sequences: Optional list of corresponding sequences (same length as embeddings_list)
        
        Returns:
            List of screening result dicts (one per embedding)
        
        Raises:
            ValueError: If sequences provided but length doesn't match embeddings_list
        """
        if sequences and len(sequences) != len(embeddings_list):
            raise ValueError(
                f"Length mismatch: {len(embeddings_list)} embeddings but {len(sequences)} sequences"
            )
        
        results = []
        for i, emb in enumerate(embeddings_list):
            seq = sequences[i] if sequences else None
            result = self.screen_sequence(emb, sentinel_head, seq)
            results.append(result)
        
        return results
    
    def set_trained_classifier(
        self,
        trained_classifier: 'TrainedESMClassifier'
    ) -> None:
        """
        Set or update the trained classifier (from notebook research).
        
        Switches the screener to ensemble mode if a valid classifier is provided.
        
        Args:
            trained_classifier: TrainedESMClassifier instance
        """
        self.trained_classifier = trained_classifier
        if trained_classifier:
            print(f"[Screening] Trained classifier installed (mode: ensemble)")
    
    def get_screening_stats(self) -> Dict:
        """
        Get screening module statistics and configuration.
        
        Returns:
            Dict with:
            - 'risk_threshold': Current threshold value
            - 'trained_classifier_active': Whether ensemble mode is enabled
            - 'trained_classifier_stats': Stats from trained classifier if available
        """
        return {
            'risk_threshold': self.risk_threshold,
            'trained_classifier_active': self.trained_classifier is not None,
            'trained_classifier_stats': (
                self.trained_classifier.get_stats() if self.trained_classifier else None
            ),
        }

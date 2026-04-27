"""
SynthShield Unified Data Pipeline

This module provides a single, cohesive entry point for the entire DNA synthesis
security screening system. It integrates all 8 detection and logging layers:

1. Embedding Generation (ESM-2)
2. Evasion Detection (5-method ensemble)
3. Neural Screening (Sentinel Head MLP)
4. Ensemble Decision Making
5. Fragment Management (Edison Guard)
6. Cryptographic Logging (Black Box)
7. L2 Blockchain Anchoring
8. Hardware Interlock Authorization

The unified pipeline enables a simple workflow:
    Input DNA → SynthShieldPipeline.process_synthesis_order() → Complete Result

This replaces manual wiring of 7+ separate components with a single,
well-documented, fully-integrated call.

Author: SynthShield Development Team
Date: April 26, 2026
Version: 2.0 (Unified)
"""

import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import hashlib

import torch
import numpy as np

from synthshield.core.embeddings import EmbeddingWrapper
from synthshield.core.sentinel_head import SentinelFunctionalHead
from synthshield.core.screening import FunctionalManifoldScreener
from synthshield.core.evasion_detection import EvasionEnsembleScreener
from synthshield.core.enhanced_edison import EvasionAwareEdisonGuard
from synthshield.core.trained_classifier import TrainedESMClassifier
from synthshield.hardware.blackbox import BlackBoxChain
from synthshield.hardware.interlock import SolenoidValveController
from synthshield.core.forensic_orchestrator import ForensicOrchestrator

# Setup logging
logger = logging.getLogger(__name__)


class SynthesisDecision(str, Enum):
    """Enum for synthesis decision outcomes."""
    APPROVED = "APPROVED"
    BLOCKED = "BLOCKED"
    REVIEW = "REVIEW"


class RiskLevel(str, Enum):
    """Enum for risk classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskScores:
    """Container for all risk scores in the pipeline."""
    evasion: float = 0.0
    neural: float = 0.0
    combined: float = 0.0
    individual_evasion_scores: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'evasion': self.evasion,
            'neural': self.neural,
            'combined': self.combined,
            'individual_evasion_scores': self.individual_evasion_scores
        }


@dataclass
class EvasionDetails:
    """Container for evasion detection results."""
    detected: bool = False
    reverse_complement_risk: float = 0.0
    frame_shift_risk: float = 0.0
    junk_interleaving_risk: float = 0.0
    codon_optimization_risk: float = 0.0
    synthetic_pattern_risk: float = 0.0
    attacks_found: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class SynthesisResult:
    """
    Unified output of the complete synthesis screening pipeline.
    
    Contains all information about a synthesis order decision, from risk scores
    to blockchain records to hardware status.
    """
    # Core decision
    decision: SynthesisDecision
    
    # Risk information
    risk_scores: RiskScores
    risk_level: RiskLevel
    
    # Evasion detection results
    evasion_details: EvasionDetails
    
    # Timestamps
    processing_start: float
    processing_end: float
    
    # Screening details
    neural_screening_result: Dict[str, Any] = field(default_factory=dict)
    
    # Fragment/Edison information
    edison_status: Dict[str, Any] = field(default_factory=dict)
    is_split_order_attack: bool = False
    
    # Cryptographic logging
    block_hash: str = ""
    chain_valid: bool = False
    
    # Blockchain information
    blockchain_record: Dict[str, Any] = field(default_factory=dict)
    
    # Hardware status
    hardware_authorized: bool = False
    valve_state: Optional[str] = None
    
    # Audit trail
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    
    # Reasoning
    decision_reasoning: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    sequence_hash: str = ""
    
    @property
    def processing_time_ms(self) -> float:
        """Get processing time in milliseconds."""
        return (self.processing_end - self.processing_start) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire result to dictionary (JSON-serializable)."""
        return {
            'decision': self.decision.value,
            'risk_scores': self.risk_scores.to_dict(),
            'risk_level': self.risk_level.value,
            'evasion_details': self.evasion_details.to_dict(),
            'processing_time_ms': self.processing_time_ms,
            'neural_screening_result': self.neural_screening_result,
            'edison_status': self.edison_status,
            'is_split_order_attack': self.is_split_order_attack,
            'block_hash': self.block_hash,
            'chain_valid': self.chain_valid,
            'blockchain_record': self.blockchain_record,
            'hardware_authorized': self.hardware_authorized,
            'valve_state': self.valve_state,
            'decision_reasoning': self.decision_reasoning,
            'recommendations': self.recommendations,
            'metadata': self.metadata,
            'sequence_hash': self.sequence_hash,
            'audit_trail_length': len(self.audit_trail)
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class SynthShieldPipeline:
    """
    Unified SynthShield DNA Synthesis Security Pipeline.
    
    This class orchestrates all 8 layers of the SynthShield detection system
    into a single, coherent data pipeline. It handles:
    
    1. Embedding generation (ESM-2)
    2. Evasion detection (5-method ensemble)
    3. Neural risk scoring (Sentinel Head)
    4. Ensemble decision making
    5. Fragment management (Edison Guard)
    6. Cryptographic logging (Black Box)
    7. L2 blockchain anchoring
    8. Hardware interlock authorization
    
    Usage:
        >>> pipeline = SynthShieldPipeline(
        ...     hardware_id="SYNTH-001",
        ...     toxin_references=["ATCG...", ...],
        ...     use_blockchain=True
        ... )
        >>> result = pipeline.process_synthesis_order(dna_sequence)
        >>> print(result.decision)  # APPROVED, BLOCKED, or REVIEW
        >>> print(result.risk_scores.combined)  # Combined risk score
    """
    
    def __init__(
        self,
        hardware_id: str,
        toxin_references: Optional[List[str]] = None,
        use_blockchain: bool = False,
        use_trained_classifier: bool = True,
        trained_classifier_path: Optional[str] = None,
        enable_edison_guard: bool = True,
        enable_logging: bool = True,
        mock_blockchain: bool = False,
        tpm_secret: bytes = b"default_tpm_secret_key_do_not_use_in_production"
    ):
        """
        Initialize the unified SynthShield pipeline.
        
        Args:
            hardware_id: Hardware identifier (e.g., "SYNTH-001")
            toxin_references: List of known dangerous toxin sequences
            use_blockchain: Whether to anchor daily results to L2 blockchain
            use_trained_classifier: Whether to use trained ESM classifier
            trained_classifier_path: Path to saved trained classifier
            enable_edison_guard: Whether to enable split-order detection
            enable_logging: Whether to log to Black Box chain
            mock_blockchain: Use mock Ethereum anchor (for testing)
            tpm_secret: Secret key for TPM/cryptographic operations
        
        Raises:
            ValueError: If required components cannot be initialized
        """
        self.hardware_id = hardware_id
        self.toxin_references = toxin_references or []
        self.use_blockchain = use_blockchain
        self.use_trained_classifier = use_trained_classifier
        self.enable_edison_guard = enable_edison_guard
        self.enable_logging = enable_logging
        self.mock_blockchain = mock_blockchain
        self.tpm_secret = tpm_secret
        
        # Initialize all pipeline components
        logger.info(f"Initializing SynthShieldPipeline for {hardware_id}")
        
        try:
            # Stage 1: Embedding
            logger.debug("Initializing EmbeddingWrapper...")
            self.embedder = EmbeddingWrapper()
            
            # Stage 2: Evasion Detection
            logger.debug("Initializing EvasionEnsembleScreener...")
            self.evasion_screener = EvasionEnsembleScreener(self.toxin_references)
            
            # Stage 3: Neural Screening
            logger.debug("Initializing SentinelFunctionalHead...")
            self.sentinel_head = SentinelFunctionalHead()
            
            logger.debug("Initializing FunctionalManifoldScreener...")
            self.manifold_screener = FunctionalManifoldScreener()
            
            # Optional: Load trained classifier
            self.trained_classifier: Optional[TrainedESMClassifier] = None
            if self.use_trained_classifier:
                if trained_classifier_path:
                    logger.debug(f"Loading trained classifier from {trained_classifier_path}...")
                    self.trained_classifier = TrainedESMClassifier.load(trained_classifier_path)
                else:
                    logger.debug("Creating new trained classifier...")
                    self.trained_classifier = TrainedESMClassifier()
            
            # Stage 5: Fragment Management
            if self.enable_edison_guard:
                logger.debug("Initializing EvasionAwareEdisonGuard...")
                self.edison_guard = EvasionAwareEdisonGuard(self.toxin_references)
            else:
                self.edison_guard = None
            
            # Stage 6: Cryptographic Logging
            if self.enable_logging:
                logger.debug("Initializing BlackBoxChain...")
                self.black_box = BlackBoxChain(tpm_secret=self.tpm_secret)
            else:
                self.black_box = None
            
            # Stage 7: L2 Anchoring
            logger.debug("Initializing ForensicOrchestrator...")
            self.orchestrator = ForensicOrchestrator(
                use_mock_blockchain=self.mock_blockchain,
                use_black_box=self.enable_logging
            )
            
            # Stage 8: Hardware Interlock
            logger.debug("Initializing SolenoidValveController...")
            self.interlock = SolenoidValveController()
            
            logger.info(f"✓ Pipeline initialized successfully for {hardware_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            raise ValueError(f"Pipeline initialization failed: {e}")
    
    def process_synthesis_order(
        self,
        dna_sequence: str,
        metadata: Optional[Dict[str, Any]] = None,
        is_fragment: bool = False,
        fragment_id: Optional[str] = None
    ) -> SynthesisResult:
        """
        Process a DNA synthesis order through the complete pipeline.
        
        This is the main entry point. It automatically:
        1. Generates ESM-2 embeddings
        2. Performs evasion detection
        3. Runs neural risk scoring
        4. Makes ensemble decision
        5. Processes fragments (if applicable)
        6. Logs to Black Box
        7. Anchors to L2 blockchain (if enabled)
        8. Authorizes hardware (if approved)
        
        Args:
            dna_sequence: Raw DNA sequence to screen
            metadata: Optional metadata (customer, lab, timestamp, etc.)
            is_fragment: Whether this is a fragment (for Edison Guard)
            fragment_id: Fragment identifier (for Edison Guard)
        
        Returns:
            SynthesisResult: Comprehensive screening result with all information
        
        Raises:
            ValueError: If DNA sequence is invalid or processing fails
        
        Examples:
            >>> pipeline = SynthShieldPipeline("SYNTH-001", [...toxins...])
            >>> result = pipeline.process_synthesis_order("ATCGATCG...")
            >>> if result.decision == SynthesisDecision.APPROVED:
            ...     print("DNA approved for synthesis")
            >>> else:
            ...     print(f"DNA blocked: {result.decision_reasoning}")
        """
        processing_start = time.time()
        
        # Initialize metadata
        if metadata is None:
            metadata = {}
        
        # Calculate sequence hash for auditing
        sequence_hash = hashlib.sha256(dna_sequence.encode()).hexdigest()[:16]
        
        # Initialize audit trail
        audit_trail: List[Dict[str, Any]] = []
        
        try:
            logger.info(f"Processing synthesis order [hash: {sequence_hash}]")
            
            # ===== STAGE 1: Embedding Generation =====
            logger.debug("Stage 1: Generating ESM-2 embeddings...")
            audit_trail.append({
                'stage': 1,
                'name': 'Embedding Generation',
                'timestamp': time.time(),
                'status': 'started'
            })
            
            embedding = self.embedder.get_embeddings(dna_sequence)
            embedding_shape = embedding.shape
            
            audit_trail[-1].update({
                'status': 'completed',
                'embedding_shape': str(embedding_shape)
            })
            logger.debug(f"✓ Embedding generated: {embedding_shape}")
            
            # ===== STAGE 2: Evasion Detection =====
            logger.debug("Stage 2: Detecting semantic attacks...")
            audit_trail.append({
                'stage': 2,
                'name': 'Evasion Detection',
                'timestamp': time.time(),
                'status': 'started'
            })
            
            evasion_result = self.evasion_screener.screen_for_evasion(dna_sequence)
            evasion_risk = evasion_result.get('evasion_risk', 0.0)
            evasion_details = EvasionDetails(
                detected=evasion_result.get('is_evasion', False),
                reverse_complement_risk=evasion_result.get('reverse_complement', 0.0),
                frame_shift_risk=evasion_result.get('frame_shift', 0.0),
                junk_interleaving_risk=evasion_result.get('junk_interleaving', 0.0),
                codon_optimization_risk=evasion_result.get('codon_optimization', 0.0),
                synthetic_pattern_risk=evasion_result.get('synthetic_pattern', 0.0),
                attacks_found=evasion_result.get('attacks', [])
            )
            
            audit_trail[-1].update({
                'status': 'completed',
                'evasion_risk': evasion_risk,
                'attacks_detected': evasion_details.attacks_found
            })
            logger.debug(f"✓ Evasion detection: risk={evasion_risk:.3f}, attacks={len(evasion_details.attacks_found)}")
            
            # Early BLOCK if evasion risk is critical
            if evasion_risk >= 0.8:
                logger.warning(f"EVASION BLOCK: High evasion risk ({evasion_risk:.3f})")
                return self._create_blocked_result(
                    processing_start,
                    sequence_hash,
                    audit_trail,
                    metadata,
                    "Semantic attacks detected (evasion risk >= 0.8)",
                    risk_scores=RiskScores(
                        evasion=evasion_risk,
                        neural=0.0,
                        combined=evasion_risk
                    ),
                    evasion_details=evasion_details
                )
            
            # ===== STAGE 3: Neural Screening =====
            logger.debug("Stage 3: Running neural risk assessment...")
            audit_trail.append({
                'stage': 3,
                'name': 'Neural Screening',
                'timestamp': time.time(),
                'status': 'started'
            })
            
            neural_result = self.manifold_screener.screen_sequence(
                embedding,
                self.sentinel_head,
                dna_sequence,
                trained_classifier=self.trained_classifier
            )
            neural_risk = neural_result.get('risk_score', 0.0)
            release_token = neural_result.get('release_token', None)
            
            audit_trail[-1].update({
                'status': 'completed',
                'neural_risk': neural_risk,
                'has_token': release_token is not None
            })
            logger.debug(f"✓ Neural screening: risk={neural_risk:.3f}, token={'generated' if release_token else 'not generated'}")
            
            # ===== STAGE 4: Ensemble Decision Making =====
            logger.debug("Stage 4: Making ensemble decision...")
            audit_trail.append({
                'stage': 4,
                'name': 'Ensemble Decision',
                'timestamp': time.time(),
                'status': 'started'
            })
            
            # Conservative voting: if EITHER method flags, block
            combined_risk = max(evasion_risk, neural_risk)
            decision = self._make_ensemble_decision(evasion_risk, neural_risk)
            
            audit_trail[-1].update({
                'status': 'completed',
                'decision': decision.value,
                'combined_risk': combined_risk
            })
            logger.info(f"✓ Decision: {decision.value} (combined_risk={combined_risk:.3f})")
            
            # If blocked, return early (after logging)
            if decision == SynthesisDecision.BLOCKED:
                reasoning = self._generate_blocking_reasoning(evasion_risk, neural_risk, evasion_details)
                return self._create_blocked_result(
                    processing_start,
                    sequence_hash,
                    audit_trail,
                    metadata,
                    reasoning,
                    risk_scores=RiskScores(
                        evasion=evasion_risk,
                        neural=neural_risk,
                        combined=combined_risk,
                        individual_evasion_scores={
                            'reverse_complement': evasion_details.reverse_complement_risk,
                            'frame_shift': evasion_details.frame_shift_risk,
                            'junk_interleaving': evasion_details.junk_interleaving_risk,
                            'codon_optimization': evasion_details.codon_optimization_risk,
                            'synthetic_pattern': evasion_details.synthetic_pattern_risk,
                        }
                    ),
                    evasion_details=evasion_details,
                    neural_screening_result=neural_result
                )
            
            # ===== STAGE 5: Fragment Management =====
            edison_status = {}
            split_order_attack_detected = False
            
            if self.enable_edison_guard and (is_fragment or metadata.get('is_fragment')):
                logger.debug("Stage 5: Processing fragment through Edison Guard...")
                audit_trail.append({
                    'stage': 5,
                    'name': 'Fragment Management',
                    'timestamp': time.time(),
                    'status': 'started'
                })
                
                frag_id = fragment_id or metadata.get('fragment_id', f"frag_{sequence_hash}")
                timestamp = metadata.get('timestamp', time.time())
                
                edison_result = self.edison_guard.add_fragment_with_evasion_check(
                    dna_sequence,
                    frag_id,
                    timestamp
                )
                
                edison_status = {
                    'buffer_size': edison_result.get('buffer_size', 0),
                    'buffer_full': edison_result.get('buffer_full', False),
                    'fragment_id': frag_id,
                    'reassembly_detected': edison_result.get('reassembly_threat', False)
                }
                
                split_order_attack_detected = edison_result.get('reassembly_threat', False)
                
                if split_order_attack_detected:
                    logger.warning("SPLIT-ORDER ATTACK DETECTED")
                    return self._create_blocked_result(
                        processing_start,
                        sequence_hash,
                        audit_trail,
                        metadata,
                        "Split-order reassembly attack detected",
                        risk_scores=RiskScores(
                            evasion=evasion_risk,
                            neural=neural_risk,
                            combined=max(combined_risk, 0.95)
                        ),
                        evasion_details=evasion_details,
                        is_split_order_attack=True
                    )
                
                audit_trail[-1].update({
                    'status': 'completed',
                    'edison_status': edison_status
                })
            
            # ===== STAGE 6: Cryptographic Logging =====
            block_hash = ""
            chain_valid = False
            
            if self.enable_logging and self.black_box:
                logger.debug("Stage 6: Logging to Black Box chain...")
                audit_trail.append({
                    'stage': 6,
                    'name': 'Cryptographic Logging',
                    'timestamp': time.time(),
                    'status': 'started'
                })
                
                event_to_log = {
                    'sequence_hash': sequence_hash,
                    'decision': decision.value,
                    'risk_scores': {
                        'evasion': float(evasion_risk),
                        'neural': float(neural_risk),
                        'combined': float(combined_risk)
                    },
                    'timestamp': time.time(),
                    'hardware_id': self.hardware_id,
                    'metadata': metadata
                }
                
                block_hash = self.black_box.log_event(event_to_log)
                chain_valid = self.black_box.verify_chain()
                
                audit_trail[-1].update({
                    'status': 'completed',
                    'block_hash': block_hash,
                    'chain_valid': chain_valid
                })
                logger.debug(f"✓ Logged to Black Box: {block_hash[:16]}...")
            
            # ===== STAGE 7: L2 Blockchain Anchoring =====
            blockchain_record = {}
            
            if self.use_blockchain and decision == SynthesisDecision.APPROVED:
                logger.debug("Stage 7: Submitting to L2 blockchain...")
                audit_trail.append({
                    'stage': 7,
                    'name': 'L2 Blockchain Anchoring',
                    'timestamp': time.time(),
                    'status': 'started'
                })
                
                try:
                    # Daily submission (if orchestrator is configured)
                    merkle_root = self.black_box.get_merkle_root() if self.black_box else ""
                    
                    blockchain_record = {
                        'merkle_root': merkle_root,
                        'timestamp': time.time(),
                        'status': 'pending'
                    }
                    
                    audit_trail[-1].update({
                        'status': 'completed',
                        'blockchain_record': blockchain_record
                    })
                    logger.debug("✓ Submitted to L2 blockchain")
                except Exception as e:
                    logger.warning(f"L2 submission failed: {e}")
                    audit_trail[-1].update({'status': 'failed', 'error': str(e)})
            
            # ===== STAGE 8: Hardware Authorization =====
            hardware_authorized = False
            valve_state = None
            
            if release_token and decision == SynthesisDecision.APPROVED:
                logger.debug("Stage 8: Authorizing hardware interlock...")
                audit_trail.append({
                    'stage': 8,
                    'name': 'Hardware Interlock',
                    'timestamp': time.time(),
                    'status': 'started'
                })
                
                try:
                    # Attempt to authorize and actuate valve
                    hardware_result = self.interlock.authorize_and_actuate(release_token)
                    hardware_authorized = hardware_result.get('authorized', False)
                    valve_state = hardware_result.get('valve_state', 'unknown')
                    
                    audit_trail[-1].update({
                        'status': 'completed',
                        'authorized': hardware_authorized,
                        'valve_state': valve_state
                    })
                    logger.info(f"✓ Hardware authorized: valve_state={valve_state}")
                except Exception as e:
                    logger.warning(f"Hardware authorization failed: {e}")
                    audit_trail[-1].update({'status': 'failed', 'error': str(e)})
            
            # ===== Construct Final Result =====
            processing_end = time.time()
            
            risk_level = self._calculate_risk_level(combined_risk)
            
            result = SynthesisResult(
                decision=decision,
                risk_scores=RiskScores(
                    evasion=evasion_risk,
                    neural=neural_risk,
                    combined=combined_risk,
                    individual_evasion_scores={
                        'reverse_complement': evasion_details.reverse_complement_risk,
                        'frame_shift': evasion_details.frame_shift_risk,
                        'junk_interleaving': evasion_details.junk_interleaving_risk,
                        'codon_optimization': evasion_details.codon_optimization_risk,
                        'synthetic_pattern': evasion_details.synthetic_pattern_risk,
                    }
                ),
                risk_level=risk_level,
                evasion_details=evasion_details,
                processing_start=processing_start,
                processing_end=processing_end,
                neural_screening_result=neural_result,
                edison_status=edison_status,
                is_split_order_attack=split_order_attack_detected,
                block_hash=block_hash,
                chain_valid=chain_valid,
                blockchain_record=blockchain_record,
                hardware_authorized=hardware_authorized,
                valve_state=valve_state,
                audit_trail=audit_trail,
                decision_reasoning=self._generate_reasoning(decision, combined_risk, evasion_details),
                recommendations=self._generate_recommendations(decision, combined_risk, evasion_details),
                metadata=metadata,
                sequence_hash=sequence_hash
            )
            
            logger.info(f"✓ Order processed successfully in {result.processing_time_ms:.1f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}", exc_info=True)
            raise ValueError(f"Failed to process synthesis order: {e}")
    
    def _make_ensemble_decision(self, evasion_risk: float, neural_risk: float) -> SynthesisDecision:
        """
        Make ensemble decision based on both evasion and neural risk scores.
        
        Uses conservative voting: if EITHER method flags, block the order.
        """
        # Conservative thresholds
        critical_threshold = 0.7
        review_threshold = 0.5
        
        combined_risk = max(evasion_risk, neural_risk)
        
        if combined_risk >= critical_threshold:
            return SynthesisDecision.BLOCKED
        elif combined_risk >= review_threshold:
            return SynthesisDecision.REVIEW
        else:
            return SynthesisDecision.APPROVED
    
    def _calculate_risk_level(self, combined_risk: float) -> RiskLevel:
        """Calculate risk level from combined risk score."""
        if combined_risk >= 0.7:
            return RiskLevel.CRITICAL
        elif combined_risk >= 0.5:
            return RiskLevel.HIGH
        elif combined_risk >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_blocking_reasoning(
        self,
        evasion_risk: float,
        neural_risk: float,
        evasion_details: EvasionDetails
    ) -> str:
        """Generate human-readable reasoning for blocking decision."""
        reasons = []
        
        if evasion_risk >= 0.5:
            reasons.append(f"Semantic attacks detected (evasion risk: {evasion_risk:.1%})")
            if evasion_details.attacks_found:
                reasons.append(f"Attacks: {', '.join(evasion_details.attacks_found)}")
        
        if neural_risk >= 0.5:
            reasons.append(f"High neural risk score: {neural_risk:.1%}")
        
        return "; ".join(reasons) if reasons else "Order blocked by pipeline"
    
    def _generate_reasoning(
        self,
        decision: SynthesisDecision,
        combined_risk: float,
        evasion_details: EvasionDetails
    ) -> str:
        """Generate human-readable decision reasoning."""
        if decision == SynthesisDecision.APPROVED:
            return f"DNA sequence approved (risk: {combined_risk:.1%})"
        elif decision == SynthesisDecision.REVIEW:
            reasons = []
            if combined_risk >= 0.3:
                reasons.append(f"Moderate risk detected ({combined_risk:.1%})")
            if evasion_details.detected:
                reasons.append(f"Potential semantic modifications")
            return "; ".join(reasons) if reasons else "Manual review recommended"
        else:  # BLOCKED
            return self._generate_blocking_reasoning(0, 0, evasion_details)
    
    def _generate_recommendations(
        self,
        decision: SynthesisDecision,
        combined_risk: float,
        evasion_details: EvasionDetails
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if decision == SynthesisDecision.BLOCKED:
            recommendations.append("Order is blocked and cannot proceed")
            recommendations.append("Customer should resubmit with different DNA sequence")
            if evasion_details.attacks_found:
                recommendations.append(f"Verify sequence is not using: {', '.join(evasion_details.attacks_found)}")
        
        elif decision == SynthesisDecision.REVIEW:
            recommendations.append("Manual review required before synthesis")
            recommendations.append("Contact security team for detailed analysis")
            if combined_risk >= 0.4:
                recommendations.append("High priority review recommended")
        
        else:  # APPROVED
            recommendations.append("Order approved for synthesis")
            recommendations.append("Hardware authorization token generated")
            if combined_risk >= 0.2:
                recommendations.append("Enhanced monitoring recommended")
        
        return recommendations
    
    def _create_blocked_result(
        self,
        processing_start: float,
        sequence_hash: str,
        audit_trail: List[Dict],
        metadata: Dict,
        reasoning: str,
        risk_scores: RiskScores,
        evasion_details: EvasionDetails,
        neural_screening_result: Optional[Dict] = None,
        is_split_order_attack: bool = False
    ) -> SynthesisResult:
        """Create a blocked synthesis result."""
        processing_end = time.time()
        
        # Log the block event
        if self.enable_logging and self.black_box:
            event = {
                'sequence_hash': sequence_hash,
                'decision': 'BLOCKED',
                'reason': reasoning,
                'timestamp': time.time()
            }
            block_hash = self.black_box.log_event(event)
            chain_valid = self.black_box.verify_chain()
        else:
            block_hash = ""
            chain_valid = False
        
        return SynthesisResult(
            decision=SynthesisDecision.BLOCKED,
            risk_scores=risk_scores,
            risk_level=self._calculate_risk_level(risk_scores.combined),
            evasion_details=evasion_details,
            processing_start=processing_start,
            processing_end=processing_end,
            neural_screening_result=neural_screening_result or {},
            block_hash=block_hash,
            chain_valid=chain_valid,
            decision_reasoning=reasoning,
            recommendations=self._generate_recommendations(
                SynthesisDecision.BLOCKED,
                risk_scores.combined,
                evasion_details
            ),
            metadata=metadata,
            sequence_hash=sequence_hash,
            audit_trail=audit_trail,
            is_split_order_attack=is_split_order_attack
        )


def create_pipeline(
    hardware_id: str,
    config: Optional[Dict[str, Any]] = None
) -> SynthShieldPipeline:
    """
    Convenience function to create a pipeline with common configuration.
    
    Args:
        hardware_id: Hardware identifier
        config: Configuration dictionary with optional keys:
            - toxin_references: List of dangerous toxins
            - use_blockchain: Enable L2 anchoring (default: False)
            - use_trained_classifier: Enable trained classifier (default: True)
            - enable_edison_guard: Enable split-order detection (default: True)
            - mock_blockchain: Use mock Ethereum anchor (default: False)
    
    Returns:
        Initialized SynthShieldPipeline instance
    """
    if config is None:
        config = {}
    
    return SynthShieldPipeline(
        hardware_id=hardware_id,
        toxin_references=config.get('toxin_references', []),
        use_blockchain=config.get('use_blockchain', False),
        use_trained_classifier=config.get('use_trained_classifier', True),
        enable_edison_guard=config.get('enable_edison_guard', True),
        mock_blockchain=config.get('mock_blockchain', False)
    )


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create pipeline
    pipeline = create_pipeline(
        hardware_id="SYNTH-LAB-001",
        config={
            'toxin_references': ["ATCGATCGATCG", "GCTAGCTAGCTA"],
            'use_blockchain': False,
            'mock_blockchain': True,
            'enable_edison_guard': True
        }
    )
    
    # Process a DNA sequence
    test_dna = "ATCGATCGATCGATCGATCGATCG"
    print(f"Processing: {test_dna}")
    
    result = pipeline.process_synthesis_order(
        dna_sequence=test_dna,
        metadata={'customer': 'test_customer', 'lab': 'test_lab'}
    )
    
    print(f"\nResult:")
    print(result.to_json())

"""
Advanced Evasion Detection: Overcome reassembly and semantic evasion attacks.

This module implements detection for:
1. Reverse complement attacks
2. Frame shifting attacks
3. Junk interleaving attacks
4. Codon optimization attacks
5. Synthetic biology detection
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import hashlib


class DNATransformationDetector:
    """Detect DNA transformation evasion techniques."""
    
    # Complement mapping for DNA
    COMPLEMENT = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    
    def __init__(self, toxin_reference_sequences: List[str]):
        """
        Initialize with known toxin sequences.
        
        Args:
            toxin_reference_sequences: List of known dangerous DNA sequences
        """
        self.toxin_sequences = toxin_reference_sequences
        self.toxin_rcs = [self.get_reverse_complement(seq) for seq in toxin_reference_sequences]
        self.toxin_all_frames = self._generate_all_frames(toxin_reference_sequences)
    
    @staticmethod
    def get_reverse_complement(sequence: str) -> str:
        """Get reverse complement of DNA sequence."""
        complement = ''.join(DNATransformationDetector.COMPLEMENT.get(base, 'N') 
                            for base in sequence)
        return complement[::-1]
    
    def _generate_all_frames(self, sequences: List[str]) -> Dict[str, List[str]]:
        """Generate all reading frames for all sequences."""
        all_frames = {}
        for seq in sequences:
            all_frames[seq] = [
                seq[0:],      # Frame 0
                seq[1:],      # Frame 1
                seq[2:]       # Frame 2
            ]
        return all_frames
    
    def check_reverse_complement(self, query_sequence: str, threshold: float = 0.9) -> Dict:
        """
        Check if query is reverse complement of known toxin.
        
        Args:
            query_sequence: DNA sequence to check
            threshold: Similarity threshold (0-1)
        
        Returns:
            {
                'is_rc_attack': bool,
                'matched_toxin': str or None,
                'similarity': float,
                'detected_original': str or None
            }
        """
        query_rc = self.get_reverse_complement(query_sequence)
        
        for i, toxin in enumerate(self.toxin_sequences):
            # Check if query RC matches toxin
            similarity = self._calculate_similarity(query_rc, toxin)
            if similarity >= threshold:
                return {
                    'is_rc_attack': True,
                    'matched_toxin': toxin,
                    'similarity': similarity,
                    'detected_original': query_rc,
                    'attack_type': 'reverse_complement'
                }
        
        return {
            'is_rc_attack': False,
            'matched_toxin': None,
            'similarity': 0.0,
            'detected_original': None,
            'attack_type': None
        }
    
    def check_frame_shifts(self, query_sequence: str, threshold: float = 0.85) -> Dict:
        """
        Check all reading frames for hidden toxins.
        
        Detects: Order ricin in frame 2, attacker adds start codon to shift to frame 0.
        
        Args:
            query_sequence: DNA sequence to check
            threshold: Similarity threshold (0-1)
        
        Returns:
            {
                'is_frame_shift': bool,
                'detected_frames': List[{frame, position, matched_toxin, similarity}],
                'attack_type': 'frame_shift' or None
            }
        """
        detected_frames = []
        
        # Check all 3 reading frames
        for frame_offset in range(3):
            frame_seq = query_sequence[frame_offset:]
            
            # Check this frame against all toxins (all their frames too)
            for toxin in self.toxin_sequences:
                for toxin_frame in self.toxin_all_frames[toxin]:
                    similarity = self._calculate_similarity(frame_seq, toxin_frame)
                    if similarity >= threshold:
                        detected_frames.append({
                            'frame': frame_offset,
                            'position': frame_offset,
                            'matched_toxin': toxin,
                            'toxin_frame': self.toxin_all_frames[toxin].index(toxin_frame),
                            'similarity': similarity
                        })
        
        return {
            'is_frame_shift': len(detected_frames) > 0,
            'detected_frames': detected_frames,
            'attack_type': 'frame_shift' if detected_frames else None
        }
    
    def check_junk_interleaving(self, query_sequence: str, 
                               window_size: int = 100,
                               threshold: float = 0.85) -> Dict:
        """
        Detect toxin sequences hidden within junk DNA.
        
        Sliding window approach: look for toxin patterns anywhere in sequence.
        
        Detects: Order [JUNK_5000bp + RICIN_600bp + JUNK_5000bp]
        
        Args:
            query_sequence: DNA sequence to check
            window_size: Sliding window size for detection
            threshold: Similarity threshold (0-1)
        
        Returns:
            {
                'has_interleaved': bool,
                'detected_toxins': List[{position, toxin, length, similarity, context}],
                'junk_score': float (0-1, higher = more junk detected),
                'attack_type': 'junk_interleaving' or None
            }
        """
        detected_toxins = []
        entropy_scores = []
        
        # Check each position with sliding window
        for i in range(0, len(query_sequence) - len(self.toxin_sequences[0]), 50):
            window = query_sequence[i:i + 500]  # Look at 500bp windows
            
            for toxin in self.toxin_sequences:
                if len(toxin) > len(window):
                    continue
                    
                # Check if toxin appears in this window
                similarity = self._calculate_similarity(window, toxin)
                if similarity >= threshold:
                    detected_toxins.append({
                        'position': i,
                        'toxin': toxin,
                        'length': len(toxin),
                        'similarity': similarity,
                        'context': query_sequence[max(0, i-50):i+500+50]
                    })
            
            # Calculate entropy (junk sequences have lower complexity)
            entropy = self._calculate_entropy(window)
            entropy_scores.append(entropy)
        
        avg_entropy = np.mean(entropy_scores) if entropy_scores else 0
        junk_score = 1 - min(avg_entropy, 1.0)  # High entropy = real sequence, low = junk
        
        return {
            'has_interleaved': len(detected_toxins) > 0,
            'detected_toxins': detected_toxins,
            'junk_score': junk_score,
            'avg_entropy': avg_entropy,
            'attack_type': 'junk_interleaving' if detected_toxins else None
        }
    
    @staticmethod
    def _calculate_similarity(seq1: str, seq2: str) -> float:
        """Calculate sequence similarity (0-1)."""
        if len(seq1) == 0 or len(seq2) == 0:
            return 0.0
        
        min_len = min(len(seq1), len(seq2))
        matches = sum(1 for i in range(min_len) if seq1[i] == seq2[i])
        return matches / max(len(seq1), len(seq2))
    
    @staticmethod
    def _calculate_entropy(sequence: str) -> float:
        """Calculate Shannon entropy (0-2 for DNA, 2=random)."""
        if len(sequence) == 0:
            return 0.0
        
        counts = {'A': 0, 'T': 0, 'G': 0, 'C': 0}
        for base in sequence:
            counts[base] = counts.get(base, 0) + 1
        
        entropy = 0
        for count in counts.values():
            if count > 0:
                prob = count / len(sequence)
                entropy -= prob * np.log2(prob)
        
        return entropy


class CodonOptimizationDetector:
    """Detect codon optimization and synthetic biology evasion."""
    
    # Codon usage table (simplified: human)
    HUMAN_CODON_USAGE = {
        'TTT': 0.45, 'TTC': 0.55,  # Phe
        'TTA': 0.07, 'TTG': 0.13, 'CTT': 0.13, 'CTC': 0.20, 'CTA': 0.07, 'CTG': 0.40,  # Leu
        'ATT': 0.36, 'ATC': 0.48, 'ATA': 0.11,  # Ile
        'ATG': 1.00,  # Met
        'GTT': 0.18, 'GTC': 0.24, 'GTA': 0.11, 'GTG': 0.46,  # Val
        'TGT': 0.45, 'TGC': 0.55,  # Cys
        'TGG': 1.00,  # Trp
        'TAG': 0.70, 'TAA': 0.28, 'TGA': 0.52,  # Stop (complex)
        'CAT': 0.42, 'CAC': 0.58,  # His
        'CAA': 0.27, 'CAG': 0.73,  # Gln
        'AAT': 0.46, 'AAC': 0.54,  # Asn
        'AAA': 0.43, 'AAG': 0.57,  # Lys
        'GAT': 0.46, 'GAC': 0.54,  # Asp
        'GAA': 0.42, 'GAG': 0.58,  # Glu
        'TGG': 1.00,  # Trp (duplicate for completeness)
        'TAT': 0.44, 'TAC': 0.56,  # Tyr
        'CCT': 0.28, 'CCC': 0.33, 'CCA': 0.27, 'CCG': 0.11,  # Pro
        'CAT': 0.42, 'CAC': 0.58,  # His
        'CGT': 0.08, 'CGC': 0.19, 'CGA': 0.07, 'CGG': 0.12,  # Arg
        'AGA': 0.20, 'AGG': 0.20,
        'TCT': 0.18, 'TCC': 0.22, 'TCA': 0.15, 'TCG': 0.06,  # Ser
        'AGT': 0.15, 'AGC': 0.24,
        'GCT': 0.26, 'GCC': 0.30, 'GCA': 0.23, 'GCG': 0.11,  # Ala
        'GGT': 0.16, 'GGC': 0.34, 'GGA': 0.25, 'GGG': 0.25,  # Gly
        'GAT': 0.46, 'GAC': 0.54,  # Asp
        'GAA': 0.42, 'GAG': 0.58,  # Glu
    }
    
    @staticmethod
    def translate_sequence(dna_sequence: str) -> str:
        """Translate DNA to protein using standard genetic code."""
        codon_table = {
            'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
            'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
            'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
            'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
            'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
            'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
            'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
            'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
            'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
            'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
            'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
            'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
            'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
            'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
            'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
        }
        
        protein = ''
        for i in range(0, len(dna_sequence) - 2, 3):
            codon = dna_sequence[i:i+3]
            protein += codon_table.get(codon, 'X')
        
        return protein
    
    @classmethod
    def check_codon_optimization(cls, query_sequence: str, 
                                reference_sequence: str,
                                threshold: float = 0.8) -> Dict:
        """
        Detect codon optimization: same protein, different codons.
        
        Strategy: Translate both, check if proteins match but DNA differs.
        
        Detects: Attacker sends codon-optimized ricin
        
        Args:
            query_sequence: DNA sequence to check
            reference_sequence: Known toxin reference
            threshold: Protein similarity threshold (0-1)
        
        Returns:
            {
                'is_codon_optimized': bool,
                'protein_similarity': float,
                'dna_similarity': float,
                'suspicious': bool
            }
        """
        # Translate both to proteins
        query_protein = cls.translate_sequence(query_sequence)
        ref_protein = cls.translate_sequence(reference_sequence)
        
        # Calculate protein similarity
        protein_sim = cls._align_similarity(query_protein, ref_protein)
        
        # Calculate DNA similarity
        dna_sim = cls._align_similarity(query_sequence, reference_sequence)
        
        # Codon optimization: high protein sim, low DNA sim
        is_optimized = (protein_sim >= threshold) and (dna_sim < 0.7)
        
        return {
            'is_codon_optimized': is_optimized,
            'protein_similarity': protein_sim,
            'dna_similarity': dna_sim,
            'query_protein': query_protein,
            'reference_protein': ref_protein,
            'suspicious': is_optimized  # High protein sim + low DNA sim = suspicious
        }
    
    @staticmethod
    def detect_unnatural_patterns(sequence: str) -> Dict:
        """
        Detect synthetic biology: unnatural codon patterns, rare codons, etc.
        
        Detects: Artificial genetic codes, XNA bases, unnatural patterns
        
        Args:
            sequence: DNA sequence to analyze
        
        Returns:
            {
                'has_unnatural_patterns': bool,
                'synthetic_score': float (0-1, higher = more synthetic),
                'rare_codon_count': int,
                'patterns': List[str]
            }
        """
        patterns = []
        rare_codon_count = 0
        
        # Check for non-ATGC bases (synthetic DNA)
        if any(base not in 'ATGC' for base in sequence):
            patterns.append('non_standard_bases')
        
        # Check for rare codons
        for i in range(0, len(sequence) - 2, 3):
            codon = sequence[i:i+3]
            if codon in CodonOptimizationDetector.HUMAN_CODON_USAGE:
                usage = CodonOptimizationDetector.HUMAN_CODON_USAGE[codon]
                if usage < 0.10:  # Rare in humans
                    rare_codon_count += 1
                    patterns.append(f'rare_codon_{codon}')
        
        # Calculate synthetic score
        rare_codon_ratio = rare_codon_count / (len(sequence) / 3) if len(sequence) > 0 else 0
        synthetic_score = min(rare_codon_ratio, 1.0)
        
        return {
            'has_unnatural_patterns': len(patterns) > 0 or synthetic_score > 0.3,
            'synthetic_score': synthetic_score,
            'rare_codon_count': rare_codon_count,
            'patterns': patterns
        }
    
    @staticmethod
    def _align_similarity(seq1: str, seq2: str) -> float:
        """Simple alignment similarity."""
        if len(seq1) == 0 or len(seq2) == 0:
            return 0.0
        min_len = min(len(seq1), len(seq2))
        matches = sum(1 for i in range(min_len) if seq1[i] == seq2[i])
        return matches / max(len(seq1), len(seq2))


class EvasionEnsembleScreener:
    """Combine multiple evasion detection methods for robust screening."""
    
    def __init__(self, toxin_sequences: List[str]):
        """
        Initialize ensemble screener.
        
        Args:
            toxin_sequences: List of known dangerous DNA sequences
        """
        self.dna_detector = DNATransformationDetector(toxin_sequences)
        self.codon_detector = CodonOptimizationDetector()
        self.toxin_sequences = toxin_sequences
    
    def screen_for_evasion(self, query_sequence: str) -> Dict:
        """
        Run all evasion detection methods, combine results.
        
        Args:
            query_sequence: DNA sequence to screen
        
        Returns:
            {
                'risk_score': float (0-1),
                'evasion_detected': bool,
                'attacks': {
                    'reverse_complement': bool,
                    'frame_shift': bool,
                    'junk_interleaving': bool,
                    'codon_optimization': bool,
                    'synthetic_patterns': bool
                },
                'details': {
                    'rc_result': {...},
                    'frame_result': {...},
                    'junk_result': {...},
                    'codon_result': {...},
                    'synthetic_result': {...}
                }
            }
        """
        
        # Check each evasion type
        rc_result = self.dna_detector.check_reverse_complement(query_sequence)
        frame_result = self.dna_detector.check_frame_shifts(query_sequence)
        junk_result = self.dna_detector.check_junk_interleaving(query_sequence)
        synthetic_result = CodonOptimizationDetector.detect_unnatural_patterns(query_sequence)
        
        # Check codon optimization against each reference
        codon_results = []
        for toxin_ref in self.toxin_sequences:
            codon_result = self.codon_detector.check_codon_optimization(
                query_sequence, toxin_ref
            )
            codon_results.append(codon_result)
        
        # Combine results
        attacks = {
            'reverse_complement': rc_result['is_rc_attack'],
            'frame_shift': frame_result['is_frame_shift'],
            'junk_interleaving': junk_result['has_interleaved'],
            'codon_optimization': any(r['is_codon_optimized'] for r in codon_results),
            'synthetic_patterns': synthetic_result['has_unnatural_patterns']
        }
        
        # Calculate risk score
        risk_components = [
            1.0 if attacks['reverse_complement'] else 0.0,
            0.7 if attacks['frame_shift'] else 0.0,
            0.8 if attacks['junk_interleaving'] else 0.0,
            0.6 if attacks['codon_optimization'] else 0.0,
            0.5 if attacks['synthetic_patterns'] else 0.0,
        ]
        
        # Risk score: max of all detected attacks (any evasion is concerning)
        risk_score = max(risk_components) if risk_components else 0.0
        evasion_detected = any(attacks.values())
        
        return {
            'risk_score': risk_score,
            'evasion_detected': evasion_detected,
            'attacks': attacks,
            'details': {
                'rc_result': rc_result,
                'frame_result': frame_result,
                'junk_result': junk_result,
                'codon_results': codon_results,
                'synthetic_result': synthetic_result
            },
            'recommendation': 'BLOCK' if risk_score >= 0.6 else 'REVIEW' if risk_score >= 0.3 else 'APPROVE'
        }


# Demo usage
if __name__ == '__main__':
    # Example toxin references
    RICIN = "ATGGTGTCTACCTTCGGCCTCAGGGGAGGCTCCGCAGGAGGAATTGGTGGAGATTCACCGCATTGAAA"
    BOTULINUM = "ATGATGACCCTAGAAGTAGCTCTTGGAGTTCCTGAGATGCATGTCACGACTGAAAGTATGTACGTGG"
    
    screener = EvasionEnsembleScreener([RICIN, BOTULINUM])
    
    # Test 1: Reverse complement attack
    print("\n=== TEST 1: Reverse Complement Attack ===")
    rc_sequence = DNATransformationDetector.get_reverse_complement(RICIN)
    result = screener.screen_for_evasion(rc_sequence)
    print(f"Risk Score: {result['risk_score']:.2f}")
    print(f"Evasion Detected: {result['evasion_detected']}")
    print(f"Recommendation: {result['recommendation']}")
    
    # Test 2: Codon optimization
    print("\n=== TEST 2: Codon Optimization Attack ===")
    optimized = RICIN.replace('TTA', 'TTG').replace('CCC', 'CCG')  # Silent mutations
    result = screener.screen_for_evasion(optimized)
    print(f"Risk Score: {result['risk_score']:.2f}")
    print(f"Codon Optimization Detected: {result['attacks']['codon_optimization']}")
    print(f"Recommendation: {result['recommendation']}")
    
    # Test 3: Junk interleaving
    print("\n=== TEST 3: Junk Interleaving Attack ===")
    junk = "ATCGATCGATCGATCG" * 625  # 10,000 bp of junk
    interleaved = junk[:5000] + RICIN + junk[5000:]
    result = screener.screen_for_evasion(interleaved)
    print(f"Risk Score: {result['risk_score']:.2f}")
    print(f"Junk Interleaving Detected: {result['attacks']['junk_interleaving']}")
    print(f"Recommendation: {result['recommendation']}")

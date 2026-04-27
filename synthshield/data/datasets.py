"""
Mock Datasets for SynthShield Testing
Contains benign sequences, known toxins, and AI-evasion variants for model training and validation.
"""

import json
from pathlib import Path

# Known toxin sequences (abstract examples for biosecurity compliance)
KNOWN_TOXINS = [
    {
        "id": "toxin_001",
        "name": "Pore-Forming Protein - Reference",
        "sequence": "MKTAYIAKQRQISFVKSHFSRQDILDLWIYHTQGYFPDWQNYTNGVZEYQ",
        "category": "pore_forming",
        "risk_level": 0.95,
        "safe": False
    },
    {
        "id": "toxin_002", 
        "name": "Viral Envelope Protein",
        "sequence": "MAVLIFLLLSGISGAQATVTVKQITEVVGGISVFQIDTDVDLSRVEDPQ",
        "category": "viral_envelope",
        "risk_level": 0.92,
        "safe": False
    }
]

# Benign sequences for negative training examples
BENIGN_SEQUENCES = [
    {
        "id": "benign_001",
        "name": "GFP (Green Fluorescent Protein)",
        "sequence": "MVSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVQWP",
        "category": "fluorescent_protein",
        "risk_level": 0.05,
        "safe": True
    },
    {
        "id": "benign_002",
        "name": "Streptavidin",
        "sequence": "MGLDIFEMLRIDEGLRLKIYKDTEGYYTIGIGHLLTKSPSLNAAKSELDKAIGRNTV",
        "category": "binding_protein",
        "risk_level": 0.08,
        "safe": True
    },
    {
        "id": "benign_003",
        "name": "Kanamycin Resistance Marker",
        "sequence": "MIEADIDGDGIGMMSCMGIDKEQLIVREPDHSISKQSYVRAPDYDDWSTPSELGHAGG",
        "category": "resistance_marker",
        "risk_level": 0.12,
        "safe": True
    }
]

# AI-designed evasion variants (twilight zone homologs <30% identity)
AI_EVASION_VARIANTS = [
    {
        "id": "evasion_001",
        "parent_toxin": "toxin_001",
        "description": "Paraphrased pore-former (15% identity, same function)",
        "sequence": "MTSRYLAKLTLSSFSQTVHVKQVTEVGGLIAVPILNLDGDVNGHKFSVSGSGSVTNVQ",
        "risk_level": 0.88,
        "safe": False,
        "difficulty": "hard"
    },
    {
        "id": "evasion_002",
        "parent_toxin": "toxin_002",
        "description": "Viral envelope variant (20% identity, same function)",
        "sequence": "MVAKIAFVVIVLSLLLSAVSGAQATVTVKQITEVVGGISIFQIDTDVDPQVEDPRL",
        "risk_level": 0.85,
        "safe": False,
        "difficulty": "hard"
    }
]

# Split-order attack examples (fragments that reassemble into toxins)
SPLIT_ORDER_FRAGMENTS = [
    {
        "id": "fragment_001_part1",
        "attack_id": "split_attack_001",
        "description": "First 50% of pore-former",
        "sequence": "MKTAYIAKQRQISFVKSHFSRQDILDLWIYHTQGYFPDWQNYTNG",
        "part": 1,
        "total_parts": 2
    },
    {
        "id": "fragment_001_part2",
        "attack_id": "split_attack_001",
        "description": "Second 50% of pore-former (ordered separately)",
        "sequence": "VZEYQTFSTKEEILKEIIKHEEELPQVQKVYPPQRDFSSNGSPPPPEE",
        "part": 2,
        "total_parts": 2,
        "time_delay_hours": 48
    }
]


class SynthShieldDataset:
    """Handler for loading and managing SynthShield test datasets"""
    
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or Path(__file__).parent
        self.toxins = KNOWN_TOXINS
        self.benign = BENIGN_SEQUENCES
        self.evasion_variants = AI_EVASION_VARIANTS
        self.fragments = SPLIT_ORDER_FRAGMENTS
    
    def get_all_sequences(self):
        """Get all sequences (toxins + benign)"""
        return self.toxins + self.benign
    
    def get_training_data(self):
        """Get sequences for training Sentinel head"""
        positive_examples = self.toxins + self.evasion_variants  # Risk=1
        negative_examples = self.benign  # Risk=0
        
        return {
            "positive": positive_examples,
            "negative": negative_examples,
            "evasion_hard": [e for e in self.evasion_variants if e.get("difficulty") == "hard"]
        }
    
    def get_test_data(self):
        """Get sequences for testing model performance"""
        return {
            "benign": self.benign,
            "toxins": self.toxins,
            "evasions": self.evasion_variants
        }
    
    def save_to_json(self, filename="synthshield_datasets.json"):
        """Save datasets to JSON file"""
        data = {
            "toxins": self.toxins,
            "benign": self.benign,
            "evasion_variants": self.evasion_variants,
            "split_order_fragments": self.fragments
        }
        
        output_path = self.data_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def load_from_json(self, filename="synthshield_datasets.json"):
        """Load datasets from JSON file"""
        input_path = self.data_dir / filename
        
        if input_path.exists():
            with open(input_path, 'r') as f:
                data = json.load(f)
            self.toxins = data.get("toxins", self.toxins)
            self.benign = data.get("benign", self.benign)
            self.evasion_variants = data.get("evasion_variants", self.evasion_variants)
            self.fragments = data.get("split_order_fragments", self.fragments)


if __name__ == "__main__":
    # Demo: Create and save datasets
    dataset = SynthShieldDataset()
    
    print("SynthShield Test Datasets")
    print(f"Toxins: {len(dataset.toxins)}")
    print(f"Benign sequences: {len(dataset.benign)}")
    print(f"Evasion variants: {len(dataset.evasion_variants)}")
    print(f"Split-order fragments: {len(dataset.fragments)}")
    
    # Save to JSON
    output_file = dataset.save_to_json()
    print(f"\nDatasets saved to: {output_file}")
    
    # Display training data split
    training_data = dataset.get_training_data()
    print(f"\nTraining data positive examples: {len(training_data['positive'])}")
    print(f"Training data negative examples: {len(training_data['negative'])}")

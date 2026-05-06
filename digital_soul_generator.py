"""
Digital Soul Generator Framework
Generates synthetic population with memories, emotions, and unique identities
for virtual city democracy simulation.
"""

import hashlib
import json
import random
import csv
import argparse
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import uuid


@dataclass
class EmotionalResonance:
    """Mathematical representation of citizen's emotional worldview"""
    trust: float  # 0.0 to 1.0 - trust in institutions
    fear: float   # 0.0 to 1.0 - fear of change/risk
    altruism: float  # 0.0 to 1.0 - concern for others
    ambition: float  # 0.0 to 1.0 - drive for success
    curiosity: float  # 0.0 to 1.0 - desire for new experiences
    
    def to_vector(self) -> List[float]:
        return [self.trust, self.fear, self.altruism, self.ambition, self.curiosity]


@dataclass
class MemoryAnchor:
    """Core memory that dictates citizen's worldview"""
    event_type: str  # e.g., "childhood_trauma", "triumph", "loss", "discovery"
    age_at_event: int
    emotional_weight: float  # 0.0 to 1.0 - how much this memory influences decisions
    narrative: str  # 50-word synthetic narrative
    associated_emotions: List[str]
    
    def influence_score(self) -> float:
        """Calculate how much this memory affects current behavior"""
        return self.emotional_weight * (1.0 - (self.age_at_event / 100.0))


@dataclass
class DigitalSoul:
    """Complete identity of a synthetic citizen"""
    citizen_id: str  # Synthetic identifier (e.g., ALPHA-77-902)
    digital_soul_hash: str  # Cryptographic unique ID
    birth_date: str
    age: int
    gender: str
    life_stage: str
    memory_anchor: MemoryAnchor
    emotional_resonance: EmotionalResonance
    archetype: str
    social_credit_score: float
    insurance_risk_tier: str
    behavioral_patterns: Dict[str, float]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for CSV/JSON export"""
        data = asdict(self)
        data['emotional_vector'] = self.emotional_resonance.to_vector()
        data['memory_influence'] = self.memory_anchor.influence_score()
        return data


class DigitalSoulHashGenerator:
    """Generates unique, non-copyable cryptographic IDs"""
    
    @staticmethod
    def generate_hash(birth_date: str, memory_text: str, biometric_seed: str) -> str:
        """
        Generate Digital Soul Hash (DSH)
        Combines birth date, core memory, and synthetic biometric seed
        """
        combined = f"{birth_date}|{memory_text}|{biometric_seed}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]


class SyntheticIDGenerator:
    """Generates safe, synthetic identifiers (no real PII)"""
    
    PREFIXES = ['ALPHA', 'BETA', 'GAMMA', 'DELTA', 'EPSILON', 'ZETA', 'OMEGA', 'SIGMA']
    
    @staticmethod
    def generate_citizen_id() -> str:
        """Generate synthetic ID like ALPHA-77-902"""
        prefix = random.choice(SyntheticIDGenerator.PREFIXES)
        sector = random.randint(10, 99)
        individual = random.randint(100, 999)
        return f"{prefix}-{sector}-{individual}"


class MemoryAnchorGenerator:
    """Procedurally generates core memories using archetypal templates"""
    
    MEMORY_TEMPLATES = {
        "childhood_triumph": [
            "The day I won the spelling bee while my father watched from the back row.",
            "Scoring the winning goal in rain-soaked mud, teammates lifting me up.",
            "Building my first radio from scrap parts, hearing static turn to music.",
        ],
        "early_loss": [
            "Grandmother's garden empty after she passed, roses still blooming.",
            "The family dog not waiting at the door when I came home from school.",
            "Moving away before saying goodbye to my best friend at the station.",
        ],
        "discovery": [
            "Finding astronomy books in the attic, realizing how small we are.",
            "First time coding 'Hello World' and feeling infinite possibility.",
            "Stumbling upon hidden jazz records that changed my taste forever.",
        ],
        "community_bond": [
            "Entire neighborhood coming together after the storm damaged homes.",
            "Church potluck where strangers became family over shared stories.",
            "Protest march where I felt part of something larger than myself.",
        ],
        "personal_failure": [
            "Failing the exam everyone expected me to ace, learning humility.",
            "Business collapsing in year one, rebuilding from zero.",
            "Losing the championship but gaining respect for sportsmanship.",
        ]
    }
    
    @classmethod
    def generate(cls, archetype: str, age: int) -> MemoryAnchor:
        """Generate a memory anchor based on archetype and age"""
        event_type = random.choice(list(cls.MEMORY_TEMPLATES.keys()))
        templates = cls.MEMORY_TEMPLATES[event_type]
        narrative = random.choice(templates)
        
        # Add procedural variation
        variations = [
            "in the summer of '98",
            "during the autumn of my youth",
            "that winter changed everything",
            "one spring morning",
            "on a Tuesday I'll never forget"
        ]
        narrative = narrative.replace(".", f" {random.choice(variations)}.")
        
        age_at_event = random.randint(5, min(age - 1, 25))
        emotional_weight = random.uniform(0.6, 1.0)
        
        emotions = {
            "childhood_triumph": ["pride", "confidence", "joy"],
            "early_loss": ["sadness", "resilience", "melancholy"],
            "discovery": ["wonder", "curiosity", "awe"],
            "community_bond": ["belonging", "trust", "solidarity"],
            "personal_failure": ["humility", "determination", "reflection"]
        }
        
        return MemoryAnchor(
            event_type=event_type,
            age_at_event=age_at_event,
            emotional_weight=emotional_weight,
            narrative=narrative,
            associated_emotions=emotions[event_type]
        )


class EmotionalResonanceGenerator:
    """Generates emotional vectors based on memory and archetype"""
    
    @classmethod
    def generate(cls, memory: MemoryAnchor, archetype: str) -> EmotionalResonance:
        """Generate emotional resonance influenced by memory anchor"""
        # Base values influenced by memory type
        base_values = {
            "childhood_triumph": {"trust": 0.7, "fear": 0.3, "altruism": 0.5, "ambition": 0.8, "curiosity": 0.6},
            "early_loss": {"trust": 0.4, "fear": 0.7, "altruism": 0.6, "ambition": 0.5, "curiosity": 0.4},
            "discovery": {"trust": 0.5, "fear": 0.4, "altruism": 0.4, "ambition": 0.7, "curiosity": 0.9},
            "community_bond": {"trust": 0.8, "fear": 0.3, "altruism": 0.9, "ambition": 0.5, "curiosity": 0.5},
            "personal_failure": {"trust": 0.5, "fear": 0.5, "altruism": 0.6, "ambition": 0.6, "curiosity": 0.7}
        }
        
        base = base_values.get(memory.event_type, {
            "trust": 0.5, "fear": 0.5, "altruism": 0.5, "ambition": 0.5, "curiosity": 0.5
        })
        
        # Apply memory influence
        influence = memory.influence_score()
        
        # Add random variation
        def vary(val: float) -> float:
            return max(0.0, min(1.0, val + random.uniform(-0.2, 0.2)))
        
        return EmotionalResonance(
            trust=vary(base["trust"]),
            fear=vary(base["fear"]),
            altruism=vary(base["altruism"]),
            ambition=vary(base["ambition"]),
            curiosity=vary(base["curiosity"])
        )


class ArchetypeSystem:
    """Defines citizen archetypes for procedural generation"""
    
    ARCHETYPES = {
        "The Stoic Engineer": {
            "base_age_range": (25, 55),
            "preferred_memories": ["discovery", "personal_failure"],
            "behavioral_traits": {"routine": 0.9, "risk_averse": 0.8, "tech_savvy": 0.9}
        },
        "The Disillusioned Artist": {
            "base_age_range": (18, 45),
            "preferred_memories": ["childhood_triumph", "early_loss"],
            "behavioral_traits": {"routine": 0.3, "risk_averse": 0.2, "tech_savvy": 0.6}
        },
        "The Community Builder": {
            "base_age_range": (30, 70),
            "preferred_memories": ["community_bond", "discovery"],
            "behavioral_traits": {"routine": 0.7, "risk_averse": 0.5, "tech_savvy": 0.5}
        },
        "The Ambitious Entrepreneur": {
            "base_age_range": (22, 50),
            "preferred_memories": ["childhood_triumph", "personal_failure"],
            "behavioral_traits": {"routine": 0.4, "risk_averse": 0.3, "tech_savvy": 0.8}
        },
        "The Traditional Elder": {
            "base_age_range": (55, 85),
            "preferred_memories": ["community_bond", "early_loss"],
            "behavioral_traits": {"routine": 0.9, "risk_averse": 0.9, "tech_savvy": 0.3}
        },
        "The Digital Native": {
            "base_age_range": (16, 30),
            "preferred_memories": ["discovery", "childhood_triumph"],
            "behavioral_traits": {"routine": 0.4, "risk_averse": 0.4, "tech_savvy": 0.95}
        }
    }
    
    @classmethod
    def get_random_archetype(cls) -> str:
        """Get random archetype name"""
        return random.choice(list(cls.ARCHETYPES.keys()))
    
    @classmethod
    def get_archetype_data(cls, archetype: str) -> Dict:
        """Get archetype configuration"""
        return cls.ARCHETYPES.get(archetype, cls.ARCHETYPES["The Stoic Engineer"])


class CensusWeightingSystem:
    """Statistical weighting based on real-world census data"""
    
    # Approximate age distribution (based on developed nations)
    AGE_DISTRIBUTION = [
        (16, 24, 0.15),  # 15% young adults
        (25, 34, 0.18),  # 18% early career
        (35, 44, 0.18),  # 18% mid career
        (45, 54, 0.16),  # 16% late career
        (55, 64, 0.14),  # 14% pre-retirement
        (65, 74, 0.12),  # 12% early retirement
        (75, 85, 0.07)   # 7% elderly
    ]
    
    # Gender distribution (approximate)
    GENDER_DISTRIBUTION = {
        "Male": 0.49,
        "Female": 0.49,
        "Non-Binary": 0.02
    }
    
    @classmethod
    def generate_age(cls) -> int:
        """Generate age based on census distribution"""
        rand = random.random()
        cumulative = 0.0
        for min_age, max_age, weight in cls.AGE_DISTRIBUTION:
            cumulative += weight
            if rand <= cumulative:
                return random.randint(min_age, max_age)
        return random.randint(16, 85)
    
    @classmethod
    def generate_gender(cls) -> str:
        """Generate gender based on census distribution"""
        rand = random.random()
        cumulative = 0.0
        for gender, weight in cls.GENDER_DISTRIBUTION.items():
            cumulative += weight
            if rand <= cumulative:
                return gender
        return "Female"
    
    @classmethod
    def determine_life_stage(cls, age: int) -> str:
        """Determine life stage based on age"""
        if age < 22:
            return "Student"
        elif age < 30:
            return "Early Career"
        elif age < 45:
            return "Mid-Career"
        elif age < 60:
            return "Late Career"
        elif age < 70:
            return "Pre-Retirement"
        else:
            return "Retirement"


class DigitalSoulGenerator:
    """Main generator for creating synthetic citizens"""
    
    def __init__(self):
        self.id_generator = SyntheticIDGenerator()
        self.hash_generator = DigitalSoulHashGenerator()
        self.census = CensusWeightingSystem()
        self.archetype_system = ArchetypeSystem()
        self.memory_generator = MemoryAnchorGenerator()
        self.emotional_generator = EmotionalResonanceGenerator()
    
    def generate_citizen(self) -> DigitalSoul:
        """Generate a single synthetic citizen with complete identity"""
        # Demographics
        age = self.census.generate_age()
        gender = self.census.generate_gender()
        life_stage = self.census.determine_life_stage(age)
        
        # Identity
        citizen_id = self.id_generator.generate_citizen_id()
        birth_date = self._generate_birth_date(age)
        
        # Archetype
        archetype = self.archetype_system.get_random_archetype()
        archetype_data = self.archetype_system.get_archetype_data(archetype)
        
        # Memory Anchor
        memory = self.memory_generator.generate(archetype, age)
        
        # Emotional Resonance
        emotional = self.emotional_generator.generate(memory, archetype)
        
        # Digital Soul Hash
        biometric_seed = str(uuid.uuid4())
        soul_hash = self.hash_generator.generate_hash(birth_date, memory.narrative, biometric_seed)
        
        # Behavioral patterns
        behavioral = archetype_data["behavioral_traits"].copy()
        behavioral["social_engagement"] = random.uniform(0.3, 0.9)
        behavioral["health_consciousness"] = random.uniform(0.2, 0.9)
        
        # Social credit and insurance risk
        social_credit = self._calculate_social_credit(emotional, behavioral)
        risk_tier = self._determine_risk_tier(social_credit, behavioral)
        
        return DigitalSoul(
            citizen_id=citizen_id,
            digital_soul_hash=soul_hash,
            birth_date=birth_date,
            age=age,
            gender=gender,
            life_stage=life_stage,
            memory_anchor=memory,
            emotional_resonance=emotional,
            archetype=archetype,
            social_credit_score=social_credit,
            insurance_risk_tier=risk_tier,
            behavioral_patterns=behavioral
        )
    
    def _generate_birth_date(self, age: int) -> str:
        """Generate birth date from age"""
        today = datetime.now()
        birth_year = today.year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        return datetime(birth_year, birth_month, birth_day).strftime("%Y-%m-%d")
    
    def _calculate_social_credit(self, emotional: EmotionalResonance, 
                                 behavioral: Dict) -> float:
        """Calculate social credit score from emotional and behavioral data"""
        base = 50.0
        base += (emotional.trust - 0.5) * 20
        base += (emotional.altruism - 0.5) * 15
        base += (behavioral["routine"] - 0.5) * 10
        base += (behavioral["health_consciousness"] - 0.5) * 15
        return max(0.0, min(100.0, base))
    
    def _determine_risk_tier(self, social_credit: float, 
                            behavioral: Dict) -> str:
        """Determine insurance risk tier"""
        if social_credit > 70:
            return "Low-Risk"
        elif social_credit > 50:
            return "Standard"
        elif social_credit > 30:
            return "Elevated"
        else:
            return "High-Risk"
    
    def generate_population(self, size: int) -> List[DigitalSoul]:
        """Generate a population of synthetic citizens"""
        population = []
        for _ in range(size):
            population.append(self.generate_citizen())
        return population


class DataExporter:
    """Exports synthetic population data to various formats"""
    
    @staticmethod
    def to_csv(population: List[DigitalSoul], filename: str):
        """Export population to CSV format"""
        fieldnames = [
            'citizen_id', 'digital_soul_hash', 'birth_date', 'age', 'gender',
            'life_stage', 'archetype', 'memory_event_type', 'memory_narrative',
            'memory_age_at_event', 'memory_emotional_weight', 'trust', 'fear',
            'altruism', 'ambition', 'curiosity', 'social_credit_score',
            'insurance_risk_tier', 'routine', 'risk_averse', 'tech_savvy',
            'social_engagement', 'health_consciousness'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for soul in population:
                writer.writerow({
                    'citizen_id': soul.citizen_id,
                    'digital_soul_hash': soul.digital_soul_hash,
                    'birth_date': soul.birth_date,
                    'age': soul.age,
                    'gender': soul.gender,
                    'life_stage': soul.life_stage,
                    'archetype': soul.archetype,
                    'memory_event_type': soul.memory_anchor.event_type,
                    'memory_narrative': soul.memory_anchor.narrative,
                    'memory_age_at_event': soul.memory_anchor.age_at_event,
                    'memory_emotional_weight': soul.memory_anchor.emotional_weight,
                    'trust': soul.emotional_resonance.trust,
                    'fear': soul.emotional_resonance.fear,
                    'altruism': soul.emotional_resonance.altruism,
                    'ambition': soul.emotional_resonance.ambition,
                    'curiosity': soul.emotional_resonance.curiosity,
                    'social_credit_score': soul.social_credit_score,
                    'insurance_risk_tier': soul.insurance_risk_tier,
                    'routine': soul.behavioral_patterns['routine'],
                    'risk_averse': soul.behavioral_patterns['risk_averse'],
                    'tech_savvy': soul.behavioral_patterns['tech_savvy'],
                    'social_engagement': soul.behavioral_patterns['social_engagement'],
                    'health_consciousness': soul.behavioral_patterns['health_consciousness']
                })
    
    @staticmethod
    def to_json(population: List[DigitalSoul], filename: str):
        """Export population to JSON format"""
        data = [soul.to_dict() for soul in population]
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)


def main():
    """Main execution function with command-line support"""
    parser = argparse.ArgumentParser(
        description="Generate synthetic digital souls for virtual city simulation"
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=100,
        help="Number of citizens to generate (default: 100)"
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="digital_souls.csv",
        help="Output CSV filename (default: digital_souls.csv)"
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="digital_souls.json",
        help="Output JSON filename (default: digital_souls.json)"
    )
    parser.add_argument(
        "--no-sample",
        action="store_true",
        help="Skip displaying sample citizen profile"
    )
    
    args = parser.parse_args()
    
    print("🧬 Digital Soul Generator v1.0")
    print("=" * 50)
    print(f"📊 Generating {args.scale:,} citizens...")
    
    # Initialize generator
    generator = DigitalSoulGenerator()
    
    # Generate population
    population = generator.generate_population(args.scale)
    
    # Export data
    print(f"💾 Exporting to {args.output_csv}...")
    DataExporter.to_csv(population, args.output_csv)
    
    print(f"💾 Exporting to {args.output_json}...")
    DataExporter.to_json(population, args.output_json)
    
    # Display sample unless disabled
    if not args.no_sample:
        print("\n🔍 Sample Citizen Profile:")
        sample = population[0]
        print(f"   ID: {sample.citizen_id}")
        print(f"   Age: {sample.age}, Gender: {sample.gender}")
        print(f"   Life Stage: {sample.life_stage}")
        print(f"   Archetype: {sample.archetype}")
        print(f"   Memory: {sample.memory_anchor.narrative}")
        print(f"   Social Credit: {sample.social_credit_score:.1f}")
        print(f"   Risk Tier: {sample.insurance_risk_tier}")
        print(f"   Emotional Vector: {sample.emotional_resonance.to_vector()}")
    
    print(f"\n✅ Generated {args.scale:,} citizens successfully!")
    print(f"📁 Data saved to {args.output_csv} and {args.output_json}")


if __name__ == "__main__":
    main()

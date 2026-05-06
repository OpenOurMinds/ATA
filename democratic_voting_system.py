"""
Democratic Voting System for Digital Souls
Implements voting logic, Lazarus Clause, and age-group specific behaviors
for maintaining democratic infrastructure during population collapse scenarios.
"""

import json
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


class VoteType(Enum):
    """Types of democratic votes"""
    POLICY = "policy"
    RESOURCE_ALLOCATION = "resource_allocation"
    SOCIAL_MOVEMENT = "social_movement"
    EMERGENCY_MEASURE = "emergency_measure"
    CONSTITUTIONAL_AMENDMENT = "constitutional_amendment"


class AgeGroup(Enum):
    """Age groups with specific voting behaviors"""
    YOUTH = (16, 24)  # 16-24: Students, early voters
    YOUNG_ADULT = (25, 34)  # 25-34: Early career
    MID_ADULT = (35, 44)  # 35-44: Mid career
    LATE_ADULT = (45, 54)  # 45-54: Late career
    PRE_RETIREMENT = (55, 64)  # 55-64: Pre-retirement
    RETIREE = (65, 74)  # 65-74: Early retirement
    ELDERLY = (75, 85)  # 75-85: Elderly
    
    @property
    def range(self) -> Tuple[int, int]:
        return self.value
    
    @classmethod
    def from_age(cls, age: int) -> 'AgeGroup':
        for group in cls:
            if group.range[0] <= age <= group.range[1]:
                return group
        return cls.ELDERLY


@dataclass
class VotingBehavior:
    """Voting behavior patterns for age groups"""
    turnout_rate: float  # Likelihood of voting
    issue_sensitivity: Dict[str, float]  # Sensitivity to different issues
    deliberation_time: float  # Time to make decision (hours)
    peer_influence: float  # Susceptibility to peer pressure
    tradition_weight: float  # Weight given to traditional values
    innovation_weight: float  # Weight given to innovation/change


class AgeGroupBehaviorProfiles:
    """Defines voting behaviors for each age group"""
    
    PROFILES = {
        AgeGroup.YOUTH: VotingBehavior(
            turnout_rate=0.45,
            issue_sensitivity={
                "climate": 0.9,
                "education": 0.85,
                "technology": 0.8,
                "healthcare": 0.6,
                "taxes": 0.4,
                "pensions": 0.2
            },
            deliberation_time=2.0,
            peer_influence=0.8,
            tradition_weight=0.3,
            innovation_weight=0.9
        ),
        AgeGroup.YOUNG_ADULT: VotingBehavior(
            turnout_rate=0.55,
            issue_sensitivity={
                "housing": 0.9,
                "employment": 0.85,
                "healthcare": 0.7,
                "education": 0.6,
                "taxes": 0.5,
                "pensions": 0.3
            },
            deliberation_time=4.0,
            peer_influence=0.6,
            tradition_weight=0.4,
            innovation_weight=0.8
        ),
        AgeGroup.MID_ADULT: VotingBehavior(
            turnout_rate=0.65,
            issue_sensitivity={
                "taxes": 0.8,
                "education": 0.75,
                "healthcare": 0.7,
                "housing": 0.6,
                "pensions": 0.5,
                "climate": 0.4
            },
            deliberation_time=6.0,
            peer_influence=0.5,
            tradition_weight=0.5,
            innovation_weight=0.6
        ),
        AgeGroup.LATE_ADULT: VotingBehavior(
            turnout_rate=0.75,
            issue_sensitivity={
                "taxes": 0.9,
                "healthcare": 0.8,
                "pensions": 0.7,
                "education": 0.6,
                "housing": 0.5,
                "climate": 0.3
            },
            deliberation_time=8.0,
            peer_influence=0.4,
            tradition_weight=0.6,
            innovation_weight=0.5
        ),
        AgeGroup.PRE_RETIREMENT: VotingBehavior(
            turnout_rate=0.80,
            issue_sensitivity={
                "pensions": 0.95,
                "healthcare": 0.85,
                "taxes": 0.8,
                "housing": 0.5,
                "education": 0.4,
                "climate": 0.3
            },
            deliberation_time=10.0,
            peer_influence=0.3,
            tradition_weight=0.7,
            innovation_weight=0.4
        ),
        AgeGroup.RETIREE: VotingBehavior(
            turnout_rate=0.85,
            issue_sensitivity={
                "pensions": 0.95,
                "healthcare": 0.9,
                "taxes": 0.7,
                "housing": 0.5,
                "education": 0.3,
                "climate": 0.2
            },
            deliberation_time=12.0,
            peer_influence=0.3,
            tradition_weight=0.8,
            innovation_weight=0.3
        ),
        AgeGroup.ELDERLY: VotingBehavior(
            turnout_rate=0.70,
            issue_sensitivity={
                "healthcare": 0.95,
                "pensions": 0.9,
                "tradition": 0.85,
                "taxes": 0.6,
                "housing": 0.4,
                "education": 0.2
            },
            deliberation_time=15.0,
            peer_influence=0.2,
            tradition_weight=0.9,
            innovation_weight=0.2
        )
    }
    
    @classmethod
    def get_behavior(cls, age_group: AgeGroup) -> VotingBehavior:
        return cls.PROFILES.get(age_group, cls.PROFILES[AgeGroup.MID_ADULT])


@dataclass
class Proposal:
    """Democratic proposal for voting"""
    proposal_id: str
    title: str
    description: str
    vote_type: VoteType
    issue_category: str  # e.g., "climate", "taxes", "healthcare"
    proposed_by: str
    timestamp: str
    voting_deadline: str
    options: List[str]  # Voting options
    current_votes: Dict[str, int]  # Option -> vote count
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['vote_type'] = self.vote_type.value
        return data


@dataclass
class Vote:
    """Individual vote cast by a digital soul"""
    vote_id: str
    citizen_id: str
    proposal_id: str
    selected_option: str
    timestamp: str
    age_group: str
    emotional_state: Dict[str, float]  # Emotional state at time of voting
    reasoning: str  # AI-generated reasoning based on memory anchor
    is_proxy: bool  # True if voting under Lazarus Clause
    confidence: float  # 0.0 to 1.0 - confidence in decision
    
    def to_dict(self) -> Dict:
        return asdict(self)


class LazarusClause:
    """
    The Lazarus Clause: In the event of population collapse,
    digital souls act as Democratic Proxies to maintain infrastructure
    until physical population recovers.
    """
    
    def __init__(self, activation_threshold: float = 0.3):
        """
        Initialize Lazarus Clause
        
        Args:
            activation_threshold: Democratic index below which Lazarus activates (default: 0.3)
        """
        self.activation_threshold = activation_threshold
        self.is_active = False
        self.activation_timestamp: Optional[str] = None
        self.proxy_voting_enabled = False
        self.emergency_powers: List[str] = []
    
    def check_activation(self, democratic_index: float, physical_population_ratio: float) -> bool:
        """
        Check if Lazarus Clause should activate
        
        Args:
            democratic_index: Current democratic health index (0.0 to 1.0)
            physical_population_ratio: Ratio of current to optimal physical population
        
        Returns:
            True if Lazarus Clause should activate
        """
        if democratic_index < self.activation_threshold or physical_population_ratio < 0.5:
            if not self.is_active:
                self.is_active = True
                self.activation_timestamp = datetime.now().isoformat()
                self.proxy_voting_enabled = True
                self.emergency_powers = [
                    "proxy_voting",
                    "emergency_resource_allocation",
                    "infrastructure_maintenance",
                    "constitutional_protection"
                ]
            return True
        return False
    
    def deactivate(self):
        """Deactivate Lazarus Clause when population recovers"""
        self.is_active = False
        self.proxy_voting_enabled = False
        self.emergency_powers = []


class DemocraticVotingSystem:
    """Main voting system for digital souls"""
    
    def __init__(self, citizens: List[Dict]):
        self.citizens = citizens
        self.citizen_map = {c["citizen_id"]: c for c in citizens}
        self.proposals: List[Proposal] = []
        self.votes: List[Vote] = []
        self.lazarus = LazarusClause()
        self.democratic_index = 0.5
        self.physical_population_ratio = 1.0
    
    def create_proposal(self, title: str, description: str, vote_type: VoteType,
                       issue_category: str, proposed_by: str, options: List[str],
                       voting_hours: int = 72) -> Proposal:
        """Create a new democratic proposal"""
        proposal_id = f"PROP-{random.randint(10000, 99999)}"
        now = datetime.now()
        deadline = now + timedelta(hours=voting_hours)
        
        proposal = Proposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            vote_type=vote_type,
            issue_category=issue_category,
            proposed_by=proposed_by,
            timestamp=now.isoformat(),
            voting_deadline=deadline.isoformat(),
            options=options,
            current_votes={option: 0 for option in options}
        )
        
        self.proposals.append(proposal)
        return proposal
    
    def calculate_vote_probability(self, citizen: Dict, proposal: Proposal) -> float:
        """Calculate probability that a citizen will vote on a proposal"""
        age_group = AgeGroup.from_age(citizen["age"])
        behavior = AgeGroupBehaviorProfiles.get_behavior(age_group)
        
        # Base turnout rate
        probability = behavior.turnout_rate
        
        # Issue sensitivity adjustment
        issue_sensitivity = behavior.issue_sensitivity.get(proposal.issue_category, 0.5)
        probability *= (0.5 + issue_sensitivity)
        
        # Social credit adjustment (higher credit = more engagement)
        social_credit = citizen.get("social_credit_score", 50.0)
        probability *= (0.5 + social_credit / 100.0)
        
        # Emotional resonance adjustment
        trust = citizen.get("trust", 0.5)
        if proposal.vote_type == VoteType.EMERGENCY_MEASURE:
            probability *= (0.5 + trust)  # Higher trust = more likely to vote on emergencies
        
        return max(0.0, min(1.0, probability))
    
    def generate_vote_reasoning(self, citizen: Dict, _proposal: Proposal,
                                selected_option: str) -> str:
        """Generate AI reasoning for vote based on memory anchor and emotional state"""
        memory = citizen.get("memory_narrative", "No memory available")
        archetype = citizen.get("archetype", "Unknown")
        
        # Generate reasoning based on archetype and memory
        reasoning_templates = {
            "The Stoic Engineer": [
                f"Based on my experience with {memory[:30]}..., I believe {selected_option} offers the most practical solution.",
                f"Considering the technical implications and my background, {selected_option} aligns with rational decision-making."
            ],
            "The Disillusioned Artist": [
                f"My memories of {memory[:30]}... inform my view that {selected_option} represents necessary change.",
                f"From my perspective shaped by past experiences, {selected_option} resonates with my values."
            ],
            "The Community Builder": [
                f"Drawing from my community experiences like {memory[:30]}..., {selected_option} best serves collective interests.",
                f"Considering the impact on our shared future, {selected_option} aligns with community values."
            ],
            "The Ambitious Entrepreneur": [
                f"Based on my journey including {memory[:30]}..., {selected_option} creates opportunity for growth.",
                f"From an innovation perspective, {selected_option} represents forward-thinking policy."
            ],
            "The Traditional Elder": [
                f"My life experience, including {memory[:30]}..., leads me to support {selected_option}.",
                f"Considering traditional values and wisdom, {selected_option} maintains stability."
            ],
            "The Digital Native": [
                f"Looking at modern challenges and my experience with {memory[:30]}..., {selected_option} is the progressive choice.",
                f"From a digital-native perspective, {selected_option} embraces necessary innovation."
            ]
        }
        
        templates = reasoning_templates.get(archetype, reasoning_templates["The Stoic Engineer"])
        return random.choice(templates)
    
    def cast_vote(self, citizen_id: str, proposal: Proposal) -> Optional[Vote]:
        """Cast a vote for a citizen"""
        if citizen_id not in self.citizen_map:
            return None
        
        citizen = self.citizen_map[citizen_id]
        
        # Check if citizen votes
        vote_probability = self.calculate_vote_probability(citizen, proposal)
        if random.random() > vote_probability:
            return None
        
        # Select option based on emotional state and issue alignment
        age_group = AgeGroup.from_age(citizen["age"])
        behavior = AgeGroupBehaviorProfiles.get_behavior(age_group)
        
        # Weight options based on issue sensitivity and emotional state
        option_weights = []
        for option in proposal.options:
            weight = 1.0
            
            # Tradition vs innovation weighting
            if "tradition" in option.lower() or "conservative" in option.lower():
                weight *= behavior.tradition_weight
            elif "innovation" in option.lower() or "progressive" in option.lower():
                weight *= behavior.innovation_weight
            
            # Fear-based decisions
            if citizen.get("fear", 0.5) > 0.7:
                if "security" in option.lower() or "safety" in option.lower():
                    weight *= 1.5
            
            # Altruism-based decisions
            if citizen.get("altruism", 0.5) > 0.7:
                if "community" in option.lower() or "collective" in option.lower():
                    weight *= 1.5
            
            option_weights.append(weight)
        
        # Select option based on weights
        total_weight = sum(option_weights)
        if total_weight == 0:
            selected_option = random.choice(proposal.options)
        else:
            rand = random.uniform(0, total_weight)
            cumulative = 0.0
            for i, weight in enumerate(option_weights):
                cumulative += weight
                if rand <= cumulative:
                    selected_option = proposal.options[i]
                    break
            else:
                selected_option = proposal.options[-1]
        
        # Generate reasoning
        reasoning = self.generate_vote_reasoning(citizen, proposal, selected_option)
        
        # Calculate confidence
        confidence = random.uniform(0.6, 0.95)
        if behavior.issue_sensitivity.get(proposal.issue_category, 0.5) > 0.7:
            confidence = min(1.0, confidence + 0.1)
        
        # Create vote
        vote = Vote(
            vote_id=f"VOTE-{random.randint(100000, 999999)}",
            citizen_id=citizen_id,
            proposal_id=proposal.proposal_id,
            selected_option=selected_option,
            timestamp=datetime.now().isoformat(),
            age_group=age_group.name,
            emotional_state={
                "trust": citizen.get("trust", 0.5),
                "fear": citizen.get("fear", 0.5),
                "altruism": citizen.get("altruism", 0.5),
                "ambition": citizen.get("ambition", 0.5),
                "curiosity": citizen.get("curiosity", 0.5)
            },
            reasoning=reasoning,
            is_proxy=self.lazarus.is_active,
            confidence=confidence
        )
        
        # Update proposal vote count
        proposal.current_votes[selected_option] += 1
        
        self.votes.append(vote)
        return vote
    
    def run_election(self, proposal: Proposal) -> Dict:
        """Run a complete election for a proposal"""
        print(f"\n🗳️  Running Election: {proposal.title}")
        print(f"   Issue: {proposal.issue_category}")
        print(f"   Options: {', '.join(proposal.options)}")
        
        votes_cast = 0
        age_group_breakdown = {}
        
        for citizen_id in self.citizen_map:
            vote = self.cast_vote(citizen_id, proposal)
            if vote:
                votes_cast += 1
                age_group = vote.age_group
                age_group_breakdown[age_group] = age_group_breakdown.get(age_group, 0) + 1
        
        # Calculate results
        total_votes = sum(proposal.current_votes.values())
        results = {
            "proposal_id": proposal.proposal_id,
            "total_eligible": len(self.citizen_map),
            "total_votes_cast": votes_cast,
            "turnout_rate": votes_cast / len(self.citizen_map) if self.citizen_map else 0,
            "vote_counts": proposal.current_votes,
            "vote_percentages": {
                option: (count / total_votes * 100) if total_votes > 0 else 0
                for option, count in proposal.current_votes.items()
            },
            "age_group_breakdown": age_group_breakdown,
            "winning_option": max(proposal.current_votes.items(), key=lambda x: x[1])[0] if proposal.current_votes else None,
            "is_proxy_election": self.lazarus.is_active
        }
        
        print(f"   Turnout: {results['turnout_rate']:.1%}")
        print(f"   Votes Cast: {votes_cast:,}")
        print(f"   Winning Option: {results['winning_option']}")
        
        return results
    
    def update_democratic_index(self, physical_population_ratio: float = 1.0):
        """Update democratic health index"""
        self.physical_population_ratio = physical_population_ratio
        
        # Check Lazarus Clause activation
        self.lazarus.check_activation(self.democratic_index, physical_population_ratio)
        
        if self.lazarus.is_active:
            print(f"\n⚠️  LAZARUS CLAUSE ACTIVATED")
            print(f"   Democratic Index: {self.democratic_index:.3f}")
            print(f"   Physical Population Ratio: {physical_population_ratio:.3f}")
            print(f"   Proxy Voting: ENABLED")
    
    def get_voting_statistics(self) -> Dict:
        """Get comprehensive voting statistics"""
        if not self.votes:
            return {}
        
        # Calculate average confidence
        avg_confidence = sum(v.confidence for v in self.votes) / len(self.votes)
        
        # Age group distribution
        age_distribution = {}
        for vote in self.votes:
            age = vote.age_group
            age_distribution[age] = age_distribution.get(age, 0) + 1
        
        # Proxy vote percentage
        proxy_votes = sum(1 for v in self.votes if v.is_proxy)
        proxy_percentage = proxy_votes / len(self.votes) if self.votes else 0
        
        return {
            "total_votes_cast": len(self.votes),
            "total_proposals": len(self.proposals),
            "average_confidence": avg_confidence,
            "age_group_distribution": age_distribution,
            "proxy_vote_percentage": proxy_percentage,
            "lazarus_active": self.lazarus.is_active,
            "democratic_index": self.democratic_index
        }
    
    def export_voting_data(self, prefix: str = "voting"):
        """Export voting data to CSV files"""
        import csv
        
        # Export proposals
        with open(f"{prefix}_proposals.csv", 'w', newline='', encoding='utf-8') as f:
            if self.proposals:
                writer = csv.DictWriter(f, fieldnames=self.proposals[0].to_dict().keys())
                writer.writeheader()
                for proposal in self.proposals:
                    writer.writerow(proposal.to_dict())
        
        # Export votes
        with open(f"{prefix}_votes.csv", 'w', newline='', encoding='utf-8') as f:
            if self.votes:
                writer = csv.DictWriter(f, fieldnames=self.votes[0].to_dict().keys())
                writer.writeheader()
                for vote in self.votes:
                    writer.writerow(vote.to_dict())
        
        print(f"💾 Voting data exported to {prefix}_*.csv")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Democratic Voting System for Digital Souls")
    parser.add_argument("--citizens", type=str, default="digital_souls.json",
                       help="Path to citizen JSON file")
    parser.add_argument("--proposals", type=int, default=5,
                       help="Number of proposals to create and vote on")
    parser.add_argument("--population-ratio", type=float, default=1.0,
                       help="Physical population ratio (1.0 = full population)")
    parser.add_argument("--output", type=str, default="voting",
                       help="Output file prefix")
    
    args = parser.parse_args()
    
    print("🗳️  Democratic Voting System v1.0")
    print("=" * 50)
    
    # Load citizens
    print(f"\n📂 Loading citizens from {args.citizens}...")
    try:
        with open(args.citizens, 'r', encoding='utf-8') as f:
            citizens = json.load(f)
        print(f"   Loaded {len(citizens)} citizens")
    except FileNotFoundError:
        print(f"   ❌ Error: {args.citizens} not found")
        return
    
    # Initialize voting system
    voting_system = DemocraticVotingSystem(citizens)
    voting_system.update_democratic_index(args.population_ratio)
    
    # Create and vote on proposals
    proposal_templates = [
        {
            "title": "Green Energy Transition Act",
            "description": "Accelerate transition to renewable energy sources with tax incentives",
            "vote_type": VoteType.POLICY,
            "issue_category": "climate",
            "options": ["Immediate Transition", "Gradual Phase-in", "Maintain Status Quo"]
        },
        {
            "title": "Healthcare Access Reform",
            "description": "Expand healthcare coverage for all age groups",
            "vote_type": VoteType.POLICY,
            "issue_category": "healthcare",
            "options": ["Universal Coverage", "Expanded Public Option", "Market-Based Reform"]
        },
        {
            "title": "Education Technology Investment",
            "description": "Invest in AI-powered education systems",
            "vote_type": VoteType.RESOURCE_ALLOCATION,
            "issue_category": "education",
            "options": ["Full Investment", "Pilot Program", "Minimal Investment"]
        },
        {
            "title": "Pension System Sustainability",
            "description": "Reform pension system to ensure long-term viability",
            "vote_type": VoteType.POLICY,
            "issue_category": "pensions",
            "options": ["Increase Contributions", "Raise Retirement Age", "Hybrid Approach"]
        },
        {
            "title": "Digital Privacy Protection Act",
            "description": "Strengthen protections for digital soul data",
            "vote_type": VoteType.CONSTITUTIONAL_AMENDMENT,
            "issue_category": "technology",
            "options": ["Strong Protection", "Balanced Approach", "Minimal Regulation"]
        }
    ]
    
    election_results = []
    for i in range(min(args.proposals, len(proposal_templates))):
        template = proposal_templates[i]
        proposal = voting_system.create_proposal(
            title=template["title"],
            description=template["description"],
            vote_type=template["vote_type"],
            issue_category=template["issue_category"],
            proposed_by=f"CIT-{random.randint(1000, 9999)}",
            options=template["options"]
        )
        
        result = voting_system.run_election(proposal)
        election_results.append(result)
    
    # Display statistics
    print("\n📊 Voting Statistics:")
    stats = voting_system.get_voting_statistics()
    print(f"   Total Votes Cast: {stats['total_votes_cast']:,}")
    print(f"   Total Proposals: {stats['total_proposals']}")
    print(f"   Average Confidence: {stats['average_confidence']:.3f}")
    print(f"   Age Group Distribution: {stats['age_group_distribution']}")
    if stats['lazarus_active']:
        print(f"   ⚠️  Proxy Vote Percentage: {stats['proxy_vote_percentage']:.1%}")
    
    # Export data
    print(f"\n💾 Exporting voting data...")
    voting_system.export_voting_data(args.output)
    
    print("\n✅ Voting simulation complete!")


if __name__ == "__main__":
    main()

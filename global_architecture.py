"""
Global Hierarchical Architecture System
Implements a distributed system with Global Soul Ledger, City Nodes,
data sharding, localization adapters, and cross-city migration.
"""

import json
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set
from datetime import datetime
from enum import Enum
from threading import Thread, Lock


class CityID(Enum):
    """City identifiers for sharding"""
    NEW_YORK = "NY"
    BEIJING = "BJ"
    TOKYO = "TK"
    GLOBAL_VIRTUAL = "GLOBAL"


class EnvironmentType(Enum):
    """Types of city environments"""
    HIGH_DENSITY_VERTICAL = "high_density_vertical"
    LARGE_SCALE_INFRASTRUCTURE = "large_scale_infrastructure"
    HIGH_TECH_ELDERLY = "high_tech_elderly"


@dataclass
class DigitalSoulRecord:
    """Record in the Identity Vault"""
    digital_soul_hash: str
    core_memory: str
    birth_date: str
    original_city: str
    current_city: str
    migration_history: List[Dict]
    created_at: str
    last_updated: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class InsuranceRiskProfile:
    """Insurance risk profile from Global Insurance Engine"""
    digital_soul_hash: str
    base_risk_score: float
    behavioral_adjustment: float
    location_adjustment: float
    final_premium: float
    risk_tier: str
    last_calculated: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LifeUpdatePacket:
    """API communication packet for life updates"""
    packet_id: str
    source_city: str
    digital_soul_hash: str
    activity_type: str
    activity_data: Dict
    timestamp: str
    packet_type: str  # "learning", "social", "migration", "insurance"
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class GlobalResilienceIndex:
    """Global democratic resilience index"""
    timestamp: str
    overall_index: float
    city_indices: Dict[str, float]
    sentiment_distribution: Dict[str, float]
    total_active_citizens: int
    collapse_risk_level: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class IdentityVault:
    """Central identity storage for Digital Soul Hashes"""
    
    def __init__(self):
        self.soul_records: Dict[str, DigitalSoulRecord] = {}
        self.lock = Lock()
    
    def register_soul(self, digital_soul_hash: str, core_memory: str, 
                     birth_date: str, city: str) -> DigitalSoulRecord:
        """Register a new digital soul"""
        with self.lock:
            if digital_soul_hash in self.soul_records:
                return self.soul_records[digital_soul_hash]
            
            record = DigitalSoulRecord(
                digital_soul_hash=digital_soul_hash,
                core_memory=core_memory,
                birth_date=birth_date,
                original_city=city,
                current_city=city,
                migration_history=[],
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
            
            self.soul_records[digital_soul_hash] = record
            return record
    
    def update_location(self, digital_soul_hash: str, new_city: str) -> bool:
        """Update citizen's current city (migration)"""
        with self.lock:
            if digital_soul_hash not in self.soul_records:
                return False
            
            record = self.soul_records[digital_soul_hash]
            old_city = record.current_city
            
            migration_entry = {
                "from_city": old_city,
                "to_city": new_city,
                "timestamp": datetime.now().isoformat()
            }
            
            record.migration_history.append(migration_entry)
            record.current_city = new_city
            record.last_updated = datetime.now().isoformat()
            
            return True
    
    def get_soul_record(self, digital_soul_hash: str) -> Optional[DigitalSoulRecord]:
        """Retrieve soul record"""
        with self.lock:
            return self.soul_records.get(digital_soul_hash)
    
    def get_souls_by_city(self, city: str) -> List[DigitalSoulRecord]:
        """Get all souls in a specific city"""
        with self.lock:
            return [r for r in self.soul_records.values() if r.current_city == city]


class GlobalInsuranceEngine:
    """Global insurance risk calculation engine"""
    
    def __init__(self):
        self.risk_profiles: Dict[str, InsuranceRiskProfile] = {}
        self.city_risk_multipliers = {
            CityID.NEW_YORK.value: 1.2,
            CityID.BEIJING.value: 1.0,
            CityID.TOKYO.value: 0.9,
            CityID.GLOBAL_VIRTUAL.value: 1.1
        }
        self.lock = Lock()
    
    def calculate_risk(self, digital_soul_hash: str, base_risk: float,
                     behavioral_score: float, city: str) -> InsuranceRiskProfile:
        """Calculate insurance risk profile"""
        with self.lock:
            location_multiplier = self.city_risk_multipliers.get(city, 1.0)
            behavioral_adjustment = (1.0 - behavioral_score) * 0.3
            location_adjustment = (location_multiplier - 1.0) * 0.2
            
            final_risk = base_risk + behavioral_adjustment + location_adjustment
            final_risk = max(0.0, min(1.0, final_risk))
            
            # Determine risk tier
            if final_risk < 0.3:
                risk_tier = "Low-Risk"
            elif final_risk < 0.6:
                risk_tier = "Standard"
            elif final_risk < 0.8:
                risk_tier = "Elevated"
            else:
                risk_tier = "High-Risk"
            
            profile = InsuranceRiskProfile(
                digital_soul_hash=digital_soul_hash,
                base_risk_score=base_risk,
                behavioral_adjustment=behavioral_adjustment,
                location_adjustment=location_adjustment,
                final_premium=final_risk * 1000,
                risk_tier=risk_tier,
                last_calculated=datetime.now().isoformat()
            )
            
            self.risk_profiles[digital_soul_hash] = profile
            return profile
    
    def get_city_average_risk(self, city: str) -> float:
        """Get average risk for a city"""
        with self.lock:
            city_profiles = [p for p in self.risk_profiles.values() 
                           if any(s.current_city == city for s in [])]
            if not city_profiles:
                return 0.5
            return sum(p.final_premium for p in city_profiles) / len(city_profiles)


class DemocraticHealthMonitor:
    """Global democratic health monitoring system"""
    
    def __init__(self):
        self.historical_indices: List[GlobalResilienceIndex] = []
        self.city_sentiment_buffers: Dict[str, List[float]] = {
            CityID.NEW_YORK.value: [],
            CityID.BEIJING.value: [],
            CityID.TOKYO.value: [],
            CityID.GLOBAL_VIRTUAL.value: []
        }
        self.lock = Lock()
    
    def add_sentiment(self, city: str, sentiment_score: float):
        """Add sentiment score from a city"""
        with self.lock:
            if city not in self.city_sentiment_buffers:
                self.city_sentiment_buffers[city] = []
            self.city_sentiment_buffers[city].append(sentiment_score)
            
            # Keep buffer size manageable
            if len(self.city_sentiment_buffers[city]) > 1000:
                self.city_sentiment_buffers[city] = self.city_sentiment_buffers[city][-1000:]
    
    def calculate_global_index(self, total_active_citizens: int) -> GlobalResilienceIndex:
        """Calculate global resilience index"""
        with self.lock:
            city_indices = {}
            for city, sentiments in self.city_sentiment_buffers.items():
                if sentiments:
                    city_indices[city] = sum(sentiments) / len(sentiments)
                else:
                    city_indices[city] = 0.5
            
            # Calculate overall index
            if city_indices:
                overall_index = sum(city_indices.values()) / len(city_indices)
            else:
                overall_index = 0.5
            
            # Determine collapse risk level
            if overall_index > 0.7:
                collapse_risk = "LOW"
            elif overall_index > 0.4:
                collapse_risk = "MODERATE"
            else:
                collapse_risk = "HIGH"
            
            # Sentiment distribution
            sentiment_distribution = {
                "positive": sum(1 for s in sum(self.city_sentiment_buffers.values(), []) if s > 0.5),
                "neutral": sum(1 for s in sum(self.city_sentiment_buffers.values(), []) if 0.3 <= s <= 0.5),
                "negative": sum(1 for s in sum(self.city_sentiment_buffers.values(), []) if s < 0.3)
            }
            
            index = GlobalResilienceIndex(
                timestamp=datetime.now().isoformat(),
                overall_index=overall_index,
                city_indices=city_indices,
                sentiment_distribution=sentiment_distribution,
                total_active_citizens=total_active_citizens,
                collapse_risk_level=collapse_risk
            )
            
            self.historical_indices.append(index)
            return index


class GlobalSoulLedger:
    """Central core of the global architecture"""
    
    def __init__(self):
        self.identity_vault = IdentityVault()
        self.insurance_engine = GlobalInsuranceEngine()
        self.democratic_monitor = DemocraticHealthMonitor()
        self.life_update_log: List[LifeUpdatePacket] = []
        self.lock = Lock()
    
    def register_citizen(self, digital_soul_hash: str, core_memory: str,
                        birth_date: str, city: str) -> DigitalSoulRecord:
        """Register a citizen in the global ledger"""
        return self.identity_vault.register_soul(digital_soul_hash, core_memory, birth_date, city)
    
    def process_life_update(self, packet: LifeUpdatePacket) -> bool:
        """Process a life update packet from a city node"""
        with self.lock:
            self.life_update_log.append(packet)
            
            # Route based on packet type
            if packet.packet_type == "learning":
                # Update behavioral score for insurance
                pass
            elif packet.packet_type == "social":
                # Add to democratic monitor
                sentiment = packet.activity_data.get("sentiment_score", 0.5)
                self.democratic_monitor.add_sentiment(packet.source_city, sentiment)
            elif packet.packet_type == "migration":
                # Update location in identity vault
                new_city = packet.activity_data.get("new_city")
                self.identity_vault.update_location(packet.digital_soul_hash, new_city)
            
            return True
    
    def get_global_resilience(self) -> GlobalResilienceIndex:
        """Get current global resilience index"""
        total_citizens = len(self.identity_vault.soul_records)
        return self.democratic_monitor.calculate_global_index(total_citizens)


class CityNode:
    """Base class for city nodes"""
    
    def __init__(self, city_id: CityID, environment_type: EnvironmentType,
                 global_ledger: GlobalSoulLedger):
        self.city_id = city_id
        self.environment_type = environment_type
        self.global_ledger = global_ledger
        self.local_citizens: Set[str] = set()
        self.adapter = None
        self.lock = Lock()
    
    def add_citizen(self, digital_soul_hash: str):
        """Add a citizen to this city node"""
        with self.lock:
            self.local_citizens.add(digital_soul_hash)
    
    def remove_citizen(self, digital_soul_hash: str):
        """Remove a citizen from this city node"""
        with self.lock:
            self.local_citizens.discard(digital_soul_hash)
    
    def send_life_update(self, packet: LifeUpdatePacket):
        """Send life update to global ledger"""
        self.global_ledger.process_life_update(packet)
    
    def localize_content(self, content: str, activity_type: str) -> str:
        """Localize content through city adapter"""
        if self.adapter:
            return self.adapter.localize(content, activity_type)
        return content


class NewYorkNode(CityNode):
    """New York City Node"""
    
    def __init__(self, global_ledger: GlobalSoulLedger):
        super().__init__(CityID.NEW_YORK, EnvironmentType.HIGH_DENSITY_VERTICAL, global_ledger)
        self.adapter = NewYorkAdapter()
        self.focus_areas = ["Financial Health", "Logistics Efficiency"]
        self.internet_space = ["Instagram", "YouTube", "LinkedIn"]
    
    def get_environmental_context(self) -> Dict:
        """Get New York environmental context"""
        return {
            "city": "New York",
            "environment": "High-density vertical movement",
            "focus": self.focus_areas,
            "internet_space": self.internet_space,
            "characteristics": [
                "Elevator-based vertical transport",
                "Fast-paced traffic patterns",
                "Financial district concentration",
                "Side hustle culture"
            ]
        }


class BeijingNode(CityNode):
    """Beijing City Node"""
    
    def __init__(self, global_ledger: GlobalSoulLedger):
        super().__init__(CityID.BEIJING, EnvironmentType.LARGE_SCALE_INFRASTRUCTURE, global_ledger)
        self.adapter = BeijingAdapter()
        self.focus_areas = ["Social Harmony", "Community Contribution"]
        self.internet_space = ["WeChat", "Weibo", "Douyin"]
    
    def get_environmental_context(self) -> Dict:
        """Get Beijing environmental context"""
        return {
            "city": "Beijing",
            "environment": "Large-scale public infrastructure",
            "focus": self.focus_areas,
            "internet_space": self.internet_space,
            "characteristics": [
                "High-speed rail integration",
                "Group-based social credit",
                "Community-focused activities",
                "Public service emphasis"
            ]
        }


class TokyoNode(CityNode):
    """Tokyo City Node"""
    
    def __init__(self, global_ledger: GlobalSoulLedger):
        super().__init__(CityID.TOKYO, EnvironmentType.HIGH_TECH_ELDERLY, global_ledger)
        self.adapter = TokyoAdapter()
        self.focus_areas = ["Active Aging", "Public Manners"]
        self.internet_space = ["Twitter", "Line", "Niche Forums"]
    
    def get_environmental_context(self) -> Dict:
        """Get Tokyo environmental context"""
        return {
            "city": "Tokyo",
            "environment": "High-tech elderly care focus",
            "focus": self.focus_areas,
            "internet_space": self.internet_space,
            "characteristics": [
                "Precise space management",
                "Elderly care technology",
                "High visual aesthetic standards",
                "Omotenashi (hospitality) culture"
            ]
        }


class CityAdapter:
    """Base class for city localization adapters"""
    
    def localize(self, content: str, activity_type: str) -> str:
        """Localize content for the city"""
        raise NotImplementedError


class NewYorkAdapter(CityAdapter):
    """New York localization adapter"""
    
    def localize(self, content: str, activity_type: str) -> str:
        """Localize content for New York"""
        if "box moving" in content.lower() or "moving boxes" in content.lower():
            return content.replace("box moving", "side hustle logistics").replace("moving boxes", "DIY home improvement project")
        elif "lifting" in content.lower():
            return content.replace("lifting", "functional fitness routine")
        return content


class BeijingAdapter(CityAdapter):
    """Beijing localization adapter"""
    
    def localize(self, content: str, activity_type: str) -> str:
        """Localize content for Beijing"""
        if "box moving" in content.lower() or "moving boxes" in content.lower():
            return content.replace("box moving", "community service activity").replace("moving boxes", "neighborhood assistance")
        elif "helping" in content.lower():
            return content.replace("helping", "contributing to social harmony")
        return content


class TokyoAdapter(CityAdapter):
    """Tokyo localization adapter"""
    
    def localize(self, content: str, activity_type: str) -> str:
        """Localize content for Tokyo"""
        if "box moving" in content.lower() or "moving boxes" in content.lower():
            return content.replace("box moving", "spring cleaning").replace("moving boxes", "seasonal organization")
        elif "organized" in content.lower():
            return content.replace("organized", "maintained omotenashi standards")
        return content


class DataShardingManager:
    """Manages data sharding by location"""
    
    def __init__(self):
        self.shards = {
            CityID.NEW_YORK.value: set(),
            CityID.BEIJING.value: set(),
            CityID.TOKYO.value: set(),
            CityID.GLOBAL_VIRTUAL.value: set()
        }
        self.shard_ranges = {
            CityID.NEW_YORK.value: (1, 30000),
            CityID.BEIJING.value: (30001, 60000),
            CityID.TOKYO.value: (60001, 90000),
            CityID.GLOBAL_VIRTUAL.value: (90001, 100000)
        }
        self.lock = Lock()
    
    def assign_shard(self, citizen_index: int) -> str:
        """Assign a citizen to a shard based on hash of index for even distribution"""
        import hashlib
        
        with self.lock:
            # Use hash of citizen index to distribute evenly across all cities
            hash_value = int(hashlib.md5(str(citizen_index).encode()).hexdigest(), 16)
            num_cities = len(self.shard_ranges)
            city_index = hash_value % num_cities
            
            # Get city name by index
            city_names = list(self.shard_ranges.keys())
            assigned_city = city_names[city_index]
            
            self.shards[assigned_city].add(citizen_index)
            return assigned_city
    
    def get_shard_citizens(self, city: str) -> Set[int]:
        """Get all citizens in a shard"""
        with self.lock:
            return self.shards.get(city, set())
    
    def migrate_citizen(self, citizen_index: int, from_city: str, to_city: str) -> bool:
        """Migrate a citizen between shards"""
        with self.lock:
            if citizen_index in self.shards.get(from_city, set()):
                self.shards[from_city].remove(citizen_index)
                self.shards[to_city].add(citizen_index)
                return True
            return False


class GlobalArchitecture:
    """Main orchestrator for global hierarchical architecture"""
    
    def __init__(self):
        self.global_ledger = GlobalSoulLedger()
        self.sharding_manager = DataShardingManager()
        
        # Initialize city nodes
        self.city_nodes = {
            CityID.NEW_YORK.value: NewYorkNode(self.global_ledger),
            CityID.BEIJING.value: BeijingNode(self.global_ledger),
            CityID.TOKYO.value: TokyoNode(self.global_ledger)
        }
        
        self.active_threads: List[Thread] = []
    
    def initialize_population(self, citizens: List[Dict]):
        """Initialize population with sharding"""
        print(f"\n🌍 Initializing Global Architecture with {len(citizens)} citizens...")
        
        for i, citizen in enumerate(citizens, 1):
            digital_soul_hash = citizen.get("digital_soul_hash", f"DSH-{i:06d}")
            core_memory = citizen.get("memory_narrative", "No memory")
            birth_date = citizen.get("birth_date", "1990-01-01")
            
            # Assign shard
            city = self.sharding_manager.assign_shard(i)
            
            # Register in global ledger
            self.global_ledger.register_citizen(digital_soul_hash, core_memory, birth_date, city)
            
            # Add to city node
            if city in self.city_nodes:
                self.city_nodes[city].add_citizen(digital_soul_hash)
            
            if i % 10000 == 0:
                print(f"   Processed {i}/{len(citizens)} citizens...")
        
        print(f"   ✅ Population initialization complete")
        self.print_shard_distribution()
    
    def print_shard_distribution(self):
        """Print distribution of citizens across shards"""
        print(f"\n📊 Shard Distribution:")
        for city, shard in self.sharding_manager.shards.items():
            print(f"   {city}: {len(shard):,} citizens")
    
    def migrate_citizen(self, digital_soul_hash: str, from_city: str, to_city: str) -> bool:
        """Migrate a citizen between cities"""
        print(f"\n✈️  Migrating citizen {digital_soul_hash[:16]} from {from_city} to {to_city}...")
        
        # Update in identity vault
        success = self.global_ledger.identity_vault.update_location(digital_soul_hash, to_city)
        
        if success:
            # Update city nodes
            if from_city in self.city_nodes:
                self.city_nodes[from_city].remove_citizen(digital_soul_hash)
            if to_city in self.city_nodes:
                self.city_nodes[to_city].add_citizen(digital_soul_hash)
            
            # Send migration packet
            packet = LifeUpdatePacket(
                packet_id=f"MIG-{random.randint(100000, 999999)}",
                source_city=from_city,
                digital_soul_hash=digital_soul_hash,
                activity_type="migration",
                activity_data={"new_city": to_city},
                timestamp=datetime.now().isoformat(),
                packet_type="migration"
            )
            self.global_ledger.process_life_update(packet)
            
            print(f"   ✅ Migration complete")
            return True
        
        print(f"   ❌ Migration failed")
        return False
    
    def simulate_city_activity(self, city: str, num_activities: int = 10):
        """Simulate activity in a specific city"""
        if city not in self.city_nodes:
            print(f"   ❌ City {city} not found")
            return
        
        node = self.city_nodes[city]
        citizens = list(node.local_citizens)
        
        if not citizens:
            print(f"   No citizens in {city}")
            return
        
        print(f"\n🏙️  Simulating activity in {city}...")
        
        for _ in range(num_activities):
            citizen = random.choice(citizens)
            sentiment = random.uniform(0.3, 0.9)
            
            # Localize content
            raw_content = "Completed box moving activity today"
            localized_content = node.localize_content(raw_content, "physical")
            
            # Send social update
            packet = LifeUpdatePacket(
                packet_id=f"ACT-{random.randint(100000, 999999)}",
                source_city=city,
                digital_soul_hash=citizen,
                activity_type="social",
                activity_data={
                    "content": localized_content,
                    "sentiment_score": sentiment
                },
                timestamp=datetime.now().isoformat(),
                packet_type="social"
            )
            node.send_life_update(packet)
        
        print(f"   ✅ Simulated {num_activities} activities")
    
    def get_global_status(self) -> Dict:
        """Get global system status"""
        resilience = self.global_ledger.get_global_resilience()
        
        city_stats = {}
        for city_id, node in self.city_nodes.items():
            city_stats[city_id] = {
                "citizens": len(node.local_citizens),
                "environment": node.get_environmental_context()
            }
        
        return {
            "global_resilience": resilience.to_dict(),
            "city_statistics": city_stats,
            "total_registered_souls": len(self.global_ledger.identity_vault.soul_records),
            "total_life_updates": len(self.global_ledger.life_update_log)
        }
    
    def export_global_data(self, prefix: str = "global_architecture"):
        """Export global architecture data"""
        import csv
        
        # Export soul records
        with open(f"{prefix}_souls.csv", 'w', newline='', encoding='utf-8') as f:
            if self.global_ledger.identity_vault.soul_records:
                first_record = next(iter(self.global_ledger.identity_vault.soul_records.values()))
                writer = csv.DictWriter(f, fieldnames=first_record.to_dict().keys())
                writer.writeheader()
                for record in self.global_ledger.identity_vault.soul_records.values():
                    writer.writerow(record.to_dict())
        
        # Export life updates
        with open(f"{prefix}_life_updates.csv", 'w', newline='', encoding='utf-8') as f:
            if self.global_ledger.life_update_log:
                writer = csv.DictWriter(f, fieldnames=self.global_ledger.life_update_log[0].to_dict().keys())
                writer.writeheader()
                for packet in self.global_ledger.life_update_log:
                    writer.writerow(packet.to_dict())
        
        print(f"\n💾 Global architecture data exported to {prefix}_*.csv")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Global Hierarchical Architecture System")
    parser.add_argument("--citizens", type=str, default="digital_souls_100k.json",
                       help="Path to citizen JSON file")
    parser.add_argument("--activities", type=int, default=100,
                       help="Number of activities to simulate per city")
    parser.add_argument("--output", type=str, default="global_architecture",
                       help="Output file prefix")
    
    args = parser.parse_args()
    
    print("🌍 Global Hierarchical Architecture System v1.0")
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
    
    # Initialize global architecture
    architecture = GlobalArchitecture()
    architecture.initialize_population(citizens)
    
    # Simulate activities in each city
    print(f"\n🔄 Simulating city activities...")
    for city_id in [CityID.NEW_YORK.value, CityID.BEIJING.value, CityID.TOKYO.value]:
        architecture.simulate_city_activity(city_id, args.activities)
    
    # Get global status
    print(f"\n📊 Global System Status:")
    status = architecture.get_global_status()
    print(f"   Total Registered Souls: {status['total_registered_souls']:,}")
    print(f"   Total Life Updates: {status['total_life_updates']:,}")
    print(f"   Global Resilience Index: {status['global_resilience']['overall_index']:.3f}")
    print(f"   Collapse Risk Level: {status['global_resilience']['collapse_risk_level']}")
    
    print(f"\n   City Statistics:")
    for city_id, stats in status['city_statistics'].items():
        print(f"   {city_id}: {stats['citizens']:,} citizens")
    
    # Simulate a migration
    if status['total_registered_souls'] > 0:
        ny_citizens = list(architecture.city_nodes[CityID.NEW_YORK.value].local_citizens)
        if ny_citizens:
            random_citizen = random.choice(ny_citizens)
            architecture.migrate_citizen(random_citizen, CityID.NEW_YORK.value, CityID.TOKYO.value)
    
    # Export data
    architecture.export_global_data(args.output)
    
    print("\n✅ Global architecture simulation complete!")


if __name__ == "__main__":
    main()

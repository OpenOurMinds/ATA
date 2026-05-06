"""
Decentralized Storage & Data Air-Gapping System
Implements air-gapped storage concepts for digital soul data to prevent
single point of failure and ensure city memory preservation.
"""

import json
import random
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import os


class StorageNode(Enum):
    """Types of storage nodes in decentralized network"""
    PRIMARY = "primary"
    BACKUP = "backup"
    ARCHIVE = "archive"
    EMERGENCY = "emergency"


class DataClassification(Enum):
    """Classification levels for data sensitivity"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class StorageShard:
    """A shard of data distributed across the network"""
    shard_id: str
    citizen_id: str
    shard_index: int
    total_shards: int
    data_hash: str
    node_type: str
    location: str
    encrypted: bool
    created_at: str
    last_accessed: str
    access_count: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class StorageNodeInfo:
    """A storage node in the decentralized network"""
    node_id: str
    node_type: str
    location: str
    capacity_gb: float
    used_gb: float
    online: bool
    last_heartbeat: str
    trust_score: float
    shard_count: int

    def to_dict(self) -> Dict:
        return asdict(self)


class DataAirGap:
    """
    Data Air-Gapping: Isolates sensitive data from external networks
    to prevent unauthorized access and ensure data sovereignty.
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or self._generate_key()
        self.air_gapped_vaults: Dict[str, List[Dict]] = {}
        self.access_logs: List[Dict] = []
    
    def _generate_key(self) -> str:
        """Generate encryption key for air-gapped vault"""
        return hashlib.sha256(os.urandom(32)).hexdigest()[:32]
    
    def encrypt_data(self, data: str) -> str:
        """Simulate encryption of data"""
        # In production, use actual encryption (AES-256)
        combined = data + self.encryption_key
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def store_in_air_gap(self, vault_id: str, citizen_data: Dict, 
                        classification: DataClassification) -> bool:
        """Store data in air-gapped vault"""
        if vault_id not in self.air_gapped_vaults:
            self.air_gapped_vaults[vault_id] = []
        
        # Encrypt restricted/confidential data
        if classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            encrypted = self.encrypt_data(json.dumps(citizen_data))
            stored_data = {
                "original_data": None,
                "encrypted_data": encrypted,
                "classification": classification.value,
                "stored_at": datetime.now().isoformat()
            }
        else:
            stored_data = {
                "original_data": citizen_data,
                "encrypted_data": None,
                "classification": classification.value,
                "stored_at": datetime.now().isoformat()
            }
        
        self.air_gapped_vaults[vault_id].append(stored_data)
        
        # Log access
        self.access_logs.append({
            "action": "store",
            "vault_id": vault_id,
            "classification": classification.value,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def retrieve_from_air_gap(self, vault_id: str, index: int, 
                            decryption_key: str) -> Optional[Dict]:
        """Retrieve data from air-gapped vault with proper authorization"""
        if vault_id not in self.air_gapped_vaults:
            return None
        
        if index >= len(self.air_gapped_vaults[vault_id]):
            return None
        
        stored_data = self.air_gapped_vaults[vault_id][index]
        
        # Verify decryption key
        if decryption_key != self.encryption_key:
            self.access_logs.append({
                "action": "access_denied",
                "vault_id": vault_id,
                "reason": "invalid_key",
                "timestamp": datetime.now().isoformat()
            })
            return None
        
        # Decrypt if necessary
        if stored_data["encrypted_data"]:
            # In production, use actual decryption
            # For simulation, return metadata only
            result = {
                "status": "encrypted",
                "classification": stored_data["classification"],
                "stored_at": stored_data["stored_at"],
                "note": "Data requires proper decryption in production environment"
            }
        else:
            result = stored_data["original_data"]
        
        # Log access
        self.access_logs.append({
            "action": "retrieve",
            "vault_id": vault_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return result


class DecentralizedStorageNetwork:
    """
    Decentralized storage network that distributes digital soul data
    across multiple nodes to prevent single point of failure.
    """
    
    def __init__(self, replication_factor: int = 3):
        """
        Initialize decentralized storage network
        
        Args:
            replication_factor: Number of copies of each data shard
        """
        self.replication_factor = replication_factor
        self.nodes: List[StorageNodeInfo] = []
        self.shards: List[StorageShard] = []
        self.data_index: Dict[str, List[str]] = {}
        self.air_gap = DataAirGap()
    
    def initialize_network(self, num_nodes: int = 10):
        """Initialize storage nodes across the network"""
        node_types = [StorageNode.PRIMARY, StorageNode.BACKUP,
                     StorageNode.ARCHIVE, StorageNode.EMERGENCY]

        locations = [
            "Seoul", "Tokyo", "Singapore", "London", "New York",
            "Frankfurt", "Sydney", "Toronto", "Zurich", "Hong Kong"
        ]

        for i in range(num_nodes):
            node = StorageNodeInfo(
                node_id=f"NODE-{i:04d}",
                node_type=random.choice(node_types).value,
                location=locations[i % len(locations)],
                capacity_gb=random.uniform(1000, 10000),
                used_gb=0.0,
                online=True,
                last_heartbeat=datetime.now().isoformat(),
                trust_score=random.uniform(0.8, 1.0),
                shard_count=0
            )
            self.nodes.append(node)

        print(f"   Initialized {num_nodes} storage nodes across {len(locations)} locations")
    
    def shard_data(self, citizen_data: Dict, num_shards: int = 5) -> List[Dict]:
        """Split citizen data into multiple shards"""
        citizen_id = citizen_data["citizen_id"]
        data_str = json.dumps(citizen_data, sort_keys=True)
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        shards = []
        shard_size = len(data_str) // num_shards
        
        for i in range(num_shards):
            start_idx = i * shard_size
            end_idx = start_idx + shard_size if i < num_shards - 1 else len(data_str)
            shard_data = data_str[start_idx:end_idx]
            
            shard_id_input = f"{citizen_id}{i}"
            shard_id_hash = hashlib.sha256(shard_id_input.encode()).hexdigest()[:16]
            
            shard = StorageShard(
                shard_id=f"SHARD-{shard_id_hash}",
                citizen_id=citizen_id,
                shard_index=i,
                total_shards=num_shards,
                data_hash=hashlib.sha256(shard_data.encode()).hexdigest(),
                node_type="",  # Will be assigned during distribution
                location="",  # Will be assigned during distribution
                encrypted=True,
                created_at=datetime.now().isoformat(),
                last_accessed=datetime.now().isoformat(),
                access_count=0
            )
            shards.append(shard)
        
        return shards
    
    def distribute_shards(self, shards: List[StorageShard]) -> bool:
        """Distribute shards across storage nodes with replication"""
        available_nodes = [node for node in self.nodes if node.online]
        
        if len(available_nodes) < self.replication_factor:
            print("   Warning: Not enough online nodes for full replication")
            return False
        
        for shard in shards:
            # Select nodes for this shard (avoid same location for replicas)
            selected_nodes = random.sample(available_nodes, 
                                         min(self.replication_factor, len(available_nodes)))
            
            for node in selected_nodes:
                # Create replica
                replica = StorageShard(
                    shard_id=f"{shard.shard_id}-REP-{node.node_id}",
                    citizen_id=shard.citizen_id,
                    shard_index=shard.shard_index,
                    total_shards=shard.total_shards,
                    data_hash=shard.data_hash,
                    node_type=node.node_type,
                    location=node.location,
                    encrypted=shard.encrypted,
                    created_at=shard.created_at,
                    last_accessed=datetime.now().isoformat(),
                    access_count=0
                )
                
                self.shards.append(replica)
                node.shard_count += 1
                node.used_gb += 0.1  # Simulate storage usage
                
                # Update index
                if shard.citizen_id not in self.data_index:
                    self.data_index[shard.citizen_id] = []
                self.data_index[shard.citizen_id].append(replica.shard_id)
        
        return True
    
    def store_citizen(self, citizen_data: Dict, 
                     classification: DataClassification = DataClassification.CONFIDENTIAL) -> bool:
        """Store citizen data in decentralized network with air-gapping"""
        citizen_id = citizen_data["citizen_id"]
        
        # Shard the data
        shards = self.shard_data(citizen_data)
        
        # Distribute shards
        success = self.distribute_shards(shards)
        
        if not success:
            return False
        
        # Store sensitive data in air-gapped vault
        if classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            vault_id = f"VAULT-{citizen_id[:8]}"
            self.air_gap.store_in_air_gap(vault_id, citizen_data, classification)
        
        return True
    
    def retrieve_citizen(self, citizen_id: str) -> Optional[Dict]:
        """Retrieve citizen data from decentralized network"""
        if citizen_id not in self.data_index:
            return None
        
        shard_ids = self.data_index[citizen_id]
        
        # In production, would reconstruct data from shards
        # For simulation, return metadata
        return {
            "citizen_id": citizen_id,
            "shard_count": len(shard_ids),
            "replication_factor": self.replication_factor,
            "storage_nodes": len([s for s in self.shards if s.citizen_id == citizen_id]),
            "status": "distributed",
            "note": "Full data reconstruction requires shard assembly in production"
        }
    
    def simulate_node_failure(self, node_id: str):
        """Simulate node failure to test redundancy"""
        for node in self.nodes:
            if node.node_id == node_id:
                node.online = False
                node.last_heartbeat = datetime.now().isoformat()
                print(f"   ⚠️  Node {node_id} went offline")
                return
        
        print(f"   Node {node_id} not found")
    
    def check_data_integrity(self) -> Dict:
        """Check integrity of distributed data"""
        total_citizens = len(self.data_index)
        fully_replicated = 0
        at_risk = 0
        
        for citizen_id, shard_ids in self.data_index.items():
            # Count available replicas
            available_replicas = len([s for s in self.shards 
                                    if s.citizen_id == citizen_id and 
                                    any(n.node_id == s.node_id.split("-REP-")[1] 
                                        for n in self.nodes if n.online)])
            
            if available_replicas >= self.replication_factor:
                fully_replicated += 1
            else:
                at_risk += 1
        
        return {
            "total_citizens_stored": total_citizens,
            "fully_replicated": fully_replicated,
            "at_risk": at_risk,
            "replication_health": fully_replicated / total_citizens if total_citizens > 0 else 0,
            "online_nodes": len([n for n in self.nodes if n.online]),
            "total_nodes": len(self.nodes)
        }
    
    def get_network_statistics(self) -> Dict:
        """Get network statistics"""
        total_capacity = sum(node.capacity_gb for node in self.nodes)
        total_used = sum(node.used_gb for node in self.nodes)
        
        shard_distribution = {}
        for node in self.nodes:
            shard_distribution[node.node_type] = shard_distribution.get(node.node_type, 0) + node.shard_count
        
        return {
            "total_nodes": len(self.nodes),
            "online_nodes": len([n for n in self.nodes if n.online]),
            "total_capacity_gb": total_capacity,
            "total_used_gb": total_used,
            "utilization_percent": (total_used / total_capacity * 100) if total_capacity > 0 else 0,
            "total_shards": len(self.shards),
            "shard_distribution": shard_distribution,
            "replication_factor": self.replication_factor,
            "air_gapped_vaults": len(self.air_gap.air_gapped_vaults)
        }
    
    def export_network_data(self, prefix: str = "storage_network"):
        """Export network data to CSV files"""
        import csv
        
        # Export nodes
        with open(f"{prefix}_nodes.csv", 'w', newline='', encoding='utf-8') as f:
            if self.nodes:
                writer = csv.DictWriter(f, fieldnames=self.nodes[0].to_dict().keys())
                writer.writeheader()
                for node in self.nodes:
                    writer.writerow(node.to_dict())
        
        # Export shards
        with open(f"{prefix}_shards.csv", 'w', newline='', encoding='utf-8') as f:
            if self.shards:
                writer = csv.DictWriter(f, fieldnames=self.shards[0].to_dict().keys())
                writer.writeheader()
                for shard in self.shards:
                    writer.writerow(shard.to_dict())
        
        # Export air gap access logs
        with open(f"{prefix}_airgap_logs.csv", 'w', newline='', encoding='utf-8') as f:
            if self.air_gap.access_logs:
                writer = csv.DictWriter(f, fieldnames=self.air_gap.access_logs[0].keys())
                writer.writeheader()
                for log in self.air_gap.access_logs:
                    writer.writerow(log)
        
        print(f"💾 Network data exported to {prefix}_*.csv")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Decentralized Storage & Data Air-Gapping")
    parser.add_argument("--citizens", type=str, default="digital_souls.json",
                       help="Path to citizen JSON file")
    parser.add_argument("--nodes", type=int, default=10,
                       help="Number of storage nodes")
    parser.add_argument("--replication", type=int, default=3,
                       help="Replication factor for data shards")
    parser.add_argument("--sample", type=int, default=1000,
                       help="Number of citizens to store (0 = all)")
    parser.add_argument("--output", type=str, default="storage_network",
                       help="Output file prefix")
    
    args = parser.parse_args()
    
    print("🔐 Decentralized Storage & Data Air-Gapping v1.0")
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
    
    # Sample citizens if specified
    if args.sample > 0 and args.sample < len(citizens):
        citizens = random.sample(citizens, args.sample)
        print(f"   Sampled {args.sample} citizens for storage")
    
    # Initialize network
    print(f"\n🌐 Initializing decentralized storage network...")
    network = DecentralizedStorageNetwork(replication_factor=args.replication)
    network.initialize_network(args.nodes)
    
    # Store citizens
    print(f"\n💾 Storing citizen data across network...")
    stored_count = 0
    for citizen in citizens:
        # Classify data based on sensitivity
        if citizen.get("insurance_risk_tier") == "High-Risk":
            classification = DataClassification.RESTRICTED
        elif citizen.get("insurance_risk_tier") in ["Elevated", "Standard"]:
            classification = DataClassification.CONFIDENTIAL
        else:
            classification = DataClassification.INTERNAL
        
        if network.store_citizen(citizen, classification):
            stored_count += 1
        
        if stored_count % 100 == 0:
            print(f"   Stored {stored_count}/{len(citizens)} citizens...")
    
    print(f"   ✅ Stored {stored_count} citizens successfully")
    
    # Display statistics
    print(f"\n📊 Network Statistics:")
    stats = network.get_network_statistics()
    print(f"   Total Nodes: {stats['total_nodes']} ({stats['online_nodes']} online)")
    print(f"   Total Capacity: {stats['total_capacity_gb']:.1f} GB")
    print(f"   Storage Used: {stats['total_used_gb']:.1f} GB ({stats['utilization_percent']:.1f}%)")
    print(f"   Total Shards: {stats['total_shards']:,}")
    print(f"   Shard Distribution: {stats['shard_distribution']}")
    print(f"   Air-Gapped Vaults: {stats['air_gapped_vaults']}")
    
    # Check integrity
    print(f"\n🔍 Data Integrity Check:")
    integrity = network.check_data_integrity()
    print(f"   Total Citizens Stored: {integrity['total_citizens_stored']:,}")
    print(f"   Fully Replicated: {integrity['fully_replicated']:,}")
    print(f"   At Risk: {integrity['at_risk']:,}")
    print(f"   Replication Health: {integrity['replication_health']:.1%}")
    
    # Simulate node failure
    print(f"\n⚠️  Simulating Node Failure...")
    if stats['online_nodes'] > 1:
        failed_node = random.choice([n for n in network.nodes if n.online]).node_id
        network.simulate_node_failure(failed_node)
        
        # Recheck integrity
        integrity_after = network.check_data_integrity()
        print(f"   Replication Health After Failure: {integrity_after['replication_health']:.1%}")
    
    # Export data
    print(f"\n💾 Exporting network data...")
    network.export_network_data(args.output)
    
    print("\n✅ Storage network setup complete!")


if __name__ == "__main__":
    main()

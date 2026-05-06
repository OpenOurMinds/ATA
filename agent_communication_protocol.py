"""
Agent-to-Agent Communication Protocol
Implements a three-layer communication system for agents to exchange information
similar to human communication patterns through writing and speaking.
"""

import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime
from enum import Enum
from threading import Thread, Lock
from queue import Queue
import time


class CommunicationLayer(Enum):
    """Three layers of agent communication"""
    LAYER_1_OPENED = "layer1_opened"  # Public information, attendance, consequences
    LAYER_2_SEMI_OPENED = "layer2_semi_opened"  # Deep feelings, truth sharing
    LAYER_3_REALTIME = "layer3_realtime"  # Motor/sensor signals, task coordination


class MessageType(Enum):
    """Types of messages agents can send"""
    # Layer 1: Opened Information
    PUBLIC_BROADCAST = "public_broadcast"
    CONVERSATION_JOIN = "conversation_join"
    CONVERSATION_LEAVE = "conversation_leave"
    INFORMATION_FLOW = "information_flow"
    CONSEQUENCE_REPORT = "consequence_report"
    
    # Layer 2: Semi-Opened Information
    DEEP_FEELING = "deep_feeling"
    TRUTH_SHARING = "truth_sharing"
    PRIVATE_MESSAGE = "private_message"
    GROUP_CONVERSATION = "group_conversation"
    EMOTIONAL_SYNC = "emotional_sync"
    
    # Layer 3: Real-time Signals
    MOTOR_SIGNAL = "motor_signal"
    SENSOR_DATA = "sensor_data"
    TASK_PRIORITY = "task_priority"
    COORDINATION_REQUEST = "coordination_request"
    EMERGENCY_SIGNAL = "emergency_signal"


class Priority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class AgentIdentity:
    """Agent identity information"""
    agent_id: str
    digital_soul_hash: str
    name: str
    current_city: str
    archetype: str
    communication_capabilities: List[str]
    trust_score: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Message:
    """Base message structure"""
    message_id: str
    sender_id: str
    receiver_id: str  # "broadcast" for public messages
    layer: str
    message_type: str
    priority: int
    content: Dict
    timestamp: str
    conversation_id: Optional[str] = None
    parent_message_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Conversation:
    """Conversation tracking"""
    conversation_id: str
    layer: str
    participants: List[str]
    started_by: str
    start_time: str
    message_count: int
    topic: str
    is_private: bool
    trust_level: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ConversationConsequence:
    """Consequence of a conversation"""
    consequence_id: str
    conversation_id: str
    affected_agents: List[str]
    consequence_type: str
    impact_score: float
    description: str
    timestamp: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RealtimeSignal:
    """Real-time signal for Layer 3 communication"""
    signal_id: str
    sender_id: str
    signal_type: str  # motor, sensor, task
    data: Dict
    priority: int
    timestamp: str
    ttl: float  # Time-to-live in seconds
    
    def to_dict(self) -> Dict:
        return asdict(self)


class Layer1OpenedCommunication:
    """Layer 1: Opened information - public conversation tracking"""
    
    def __init__(self):
        self.public_conversations: Dict[str, Conversation] = {}
        self.conversation_attendance: Dict[str, Set[str]] = {}
        self.information_flow_log: List[Dict] = []
        self.consequences: List[ConversationConsequence] = {}
        self.lock = Lock()
    
    def create_public_conversation(self, started_by: str, topic: str) -> Conversation:
        """Create a new public conversation"""
        conversation_id = f"CONV-{random.randint(100000, 999999)}"
        
        conversation = Conversation(
            conversation_id=conversation_id,
            layer=CommunicationLayer.LAYER_1_OPENED.value,
            participants=[started_by],
            started_by=started_by,
            start_time=datetime.now().isoformat(),
            message_count=0,
            topic=topic,
            is_private=False,
            trust_level=1.0  # Public conversations have full trust
        )
        
        with self.lock:
            self.public_conversations[conversation_id] = conversation
            self.conversation_attendance[conversation_id] = {started_by}
        
        return conversation
    
    def join_conversation(self, conversation_id: str, agent_id: str) -> bool:
        """Agent joins a public conversation"""
        with self.lock:
            if conversation_id not in self.public_conversations:
                return False
            
            if agent_id not in self.conversation_attendance[conversation_id]:
                self.conversation_attendance[conversation_id].add(agent_id)
                self.public_conversations[conversation_id].participants.append(agent_id)
            
            return True
    
    def leave_conversation(self, conversation_id: str, agent_id: str) -> bool:
        """Agent leaves a conversation"""
        with self.lock:
            if conversation_id not in self.conversation_attendance:
                return False
            
            self.conversation_attendance[conversation_id].discard(agent_id)
            
            if agent_id in self.public_conversations[conversation_id].participants:
                self.public_conversations[conversation_id].participants.remove(agent_id)
            
            return True
    
    def log_information_flow(self, conversation_id: str, from_agent: str, 
                           to_agent: str, information_type: str):
        """Log information flow between agents"""
        with self.lock:
            flow_entry = {
                "conversation_id": conversation_id,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "information_type": information_type,
                "timestamp": datetime.now().isoformat()
            }
            self.information_flow_log.append(flow_entry)
    
    def record_consequence(self, conversation_id: str, affected_agents: List[str],
                          consequence_type: str, impact_score: float, description: str):
        """Record consequence of a conversation"""
        consequence_id = f"CONS-{random.randint(100000, 999999)}"
        
        consequence = ConversationConsequence(
            consequence_id=consequence_id,
            conversation_id=conversation_id,
            affected_agents=affected_agents,
            consequence_type=consequence_type,
            impact_score=impact_score,
            description=description,
            timestamp=datetime.now().isoformat()
        )
        
        with self.lock:
            self.consequences[consequence_id] = consequence
    
    def get_conversation_participants(self, conversation_id: str) -> Set[str]:
        """Get all participants in a conversation"""
        with self.lock:
            return self.conversation_attendance.get(conversation_id, set())


class Layer2SemiOpenedCommunication:
    """Layer 2: Semi-opened information - deep feelings and truth sharing"""
    
    def __init__(self):
        self.private_conversations: Dict[str, Conversation] = {}
        self.feeling_exchanges: Dict[str, List[Dict]] = {}
        self.truth_sharing_records: Dict[str, Dict] = {}
        self.trust_relationships: Dict[Tuple[str, str], float] = {}
        self.lock = Lock()
    
    def create_private_conversation(self, initiator: str, participants: List[str],
                                   topic: str, trust_level: float) -> Conversation:
        """Create a private conversation for deep sharing"""
        conversation_id = f"PRIVATE-{random.randint(100000, 999999)}"
        
        conversation = Conversation(
            conversation_id=conversation_id,
            layer=CommunicationLayer.LAYER_2_SEMI_OPENED.value,
            participants=participants,
            started_by=initiator,
            start_time=datetime.now().isoformat(),
            message_count=0,
            topic=topic,
            is_private=True,
            trust_level=trust_level
        )
        
        with self.lock:
            self.private_conversations[conversation_id] = conversation
            self.feeling_exchanges[conversation_id] = []
        
        return conversation
    
    def share_deep_feeling(self, conversation_id: str, agent_id: str,
                          emotion: str, intensity: float, context: str) -> bool:
        """Share deep feeling in private conversation"""
        with self.lock:
            if conversation_id not in self.feeling_exchanges:
                return False
            
            feeling_entry = {
                "agent_id": agent_id,
                "emotion": emotion,
                "intensity": intensity,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            self.feeling_exchanges[conversation_id].append(feeling_entry)
            
            return True
    
    def share_truth(self, from_agent: str, to_agent: str, truth_content: str,
                   confidence: float) -> str:
        """Share truth between two agents"""
        truth_id = f"TRUTH-{random.randint(100000, 999999)}"
        
        truth_record = {
            "truth_id": truth_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "truth_content": truth_content,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        with self.lock:
            self.truth_sharing_records[truth_id] = truth_record
            
            # Update trust relationship
            key = (from_agent, to_agent)
            current_trust = self.trust_relationships.get(key, 0.5)
            new_trust = min(1.0, current_trust + (confidence * 0.1))
            self.trust_relationships[key] = new_trust
        
        return truth_id
    
    def get_trust_level(self, agent_a: str, agent_b: str) -> float:
        """Get trust level between two agents"""
        with self.lock:
            return self.trust_relationships.get((agent_a, agent_b), 0.5)
    
    def can_access_private_conversation(self, agent_id: str, conversation_id: str) -> bool:
        """Check if agent can access private conversation"""
        with self.lock:
            if conversation_id not in self.private_conversations:
                return False
            return agent_id in self.private_conversations[conversation_id].participants


class Layer3RealtimeCommunication:
    """Layer 3: Real-time signals - motor, sensor, task coordination"""
    
    def __init__(self):
        self.signal_queue: Queue = Queue()
        self.active_signals: Dict[str, RealtimeSignal] = {}
        self.motor_states: Dict[str, Dict] = {}
        self.sensor_data: Dict[str, List[Dict]] = {}
        self.task_priorities: Dict[str, int] = {}
        self.lock = Lock()
    
    def send_motor_signal(self, agent_id: str, motor_command: str,
                         parameters: Dict, priority: int = Priority.NORMAL.value) -> str:
        """Send motor coordination signal"""
        signal_id = f"MOTOR-{random.randint(100000, 999999)}"
        
        signal = RealtimeSignal(
            signal_id=signal_id,
            sender_id=agent_id,
            signal_type="motor",
            data={
                "command": motor_command,
                "parameters": parameters
            },
            priority=priority,
            timestamp=datetime.now().isoformat(),
            ttl=5.0  # Motor signals expire in 5 seconds
        )
        
        with self.lock:
            self.active_signals[signal_id] = signal
            self.motor_states[agent_id] = {
                "command": motor_command,
                "parameters": parameters,
                "timestamp": datetime.now().isoformat()
            }
        
        self.signal_queue.put(signal)
        return signal_id
    
    def send_sensor_data(self, agent_id: str, sensor_type: str,
                        readings: Dict, priority: int = Priority.NORMAL.value) -> str:
        """Send sensor data to other agents"""
        signal_id = f"SENSOR-{random.randint(100000, 999999)}"
        
        signal = RealtimeSignal(
            signal_id=signal_id,
            sender_id=agent_id,
            signal_type="sensor",
            data={
                "sensor_type": sensor_type,
                "readings": readings
            },
            priority=priority,
            timestamp=datetime.now().isoformat(),
            ttl=2.0  # Sensor data expires in 2 seconds
        )
        
        with self.lock:
            self.active_signals[signal_id] = signal
            if agent_id not in self.sensor_data:
                self.sensor_data[agent_id] = []
            self.sensor_data[agent_id].append({
                "sensor_type": sensor_type,
                "readings": readings,
                "timestamp": datetime.now().isoformat()
            })
            # Keep only recent sensor data
            if len(self.sensor_data[agent_id]) > 100:
                self.sensor_data[agent_id] = self.sensor_data[agent_id][-100:]
        
        self.signal_queue.put(signal)
        return signal_id
    
    def update_task_priority(self, agent_id: str, task_id: str,
                           priority: int) -> str:
        """Update task priority for coordination"""
        signal_id = f"TASK-{random.randint(100000, 999999)}"
        
        signal = RealtimeSignal(
            signal_id=signal_id,
            sender_id=agent_id,
            signal_type="task",
            data={
                "task_id": task_id,
                "priority": priority
            },
            priority=priority,
            timestamp=datetime.now().isoformat(),
            ttl=10.0  # Task priority signals last 10 seconds
        )
        
        with self.lock:
            self.active_signals[signal_id] = signal
            self.task_priorities[task_id] = priority
        
        self.signal_queue.put(signal)
        return signal_id
    
    def send_emergency_signal(self, agent_id: str, emergency_type: str,
                            details: Dict) -> str:
        """Send emergency signal with highest priority"""
        signal_id = f"EMERGENCY-{random.randint(100000, 999999)}"
        
        signal = RealtimeSignal(
            signal_id=signal_id,
            sender_id=agent_id,
            signal_type="emergency",
            data={
                "emergency_type": emergency_type,
                "details": details
            },
            priority=Priority.CRITICAL.value,
            timestamp=datetime.now().isoformat(),
            ttl=30.0  # Emergency signals last 30 seconds
        )
        
        with self.lock:
            self.active_signals[signal_id] = signal
        
        self.signal_queue.put(signal)
        return signal_id
    
    def get_next_signal(self, timeout: float = 1.0) -> Optional[RealtimeSignal]:
        """Get next signal from queue"""
        try:
            return self.signal_queue.get(timeout=timeout)
        except Exception:
            return None
    
    def cleanup_expired_signals(self):
        """Remove expired signals"""
        with self.lock:
            current_time = datetime.now()
            expired_signals = []
            
            for signal_id, signal in self.active_signals.items():
                signal_time = datetime.fromisoformat(signal.timestamp)
                age = (current_time - signal_time).total_seconds()
                if age > signal.ttl:
                    expired_signals.append(signal_id)
            
            for signal_id in expired_signals:
                del self.active_signals[signal_id]


class MessageRouter:
    """Routes messages between agents"""
    
    def __init__(self):
        self.message_queue: Queue = Queue()
        self.agent_connections: Dict[str, Set[str]] = {}
        self.delivered_messages: List[str] = []
        self.lock = Lock()
    
    def connect_agents(self, agent_a: str, agent_b: str):
        """Establish connection between two agents"""
        with self.lock:
            if agent_a not in self.agent_connections:
                self.agent_connections[agent_a] = set()
            if agent_b not in self.agent_connections:
                self.agent_connections[agent_b] = set()
            
            self.agent_connections[agent_a].add(agent_b)
            self.agent_connections[agent_b].add(agent_a)
    
    def send_message(self, message: Message) -> bool:
        """Send message through router"""
        with self.lock:
            self.message_queue.put(message)
            return True
    
    def route_message(self, message: Message) -> List[str]:
        """Route message to appropriate recipients"""
        recipients = []
        
        if message.receiver_id == "broadcast":
            # Broadcast to all connected agents
            with self.lock:
                if message.sender_id in self.agent_connections:
                    recipients = list(self.agent_connections[message.sender_id])
        else:
            # Direct message
            recipients = [message.receiver_id]
        
        # Mark as delivered
        with self.lock:
            self.delivered_messages.append(message.message_id)
        
        return recipients
    
    def get_pending_messages(self, agent_id: str, limit: int = 10) -> List[Message]:
        """Get pending messages for an agent"""
        messages = []
        temp_queue = Queue()
        
        while not self.message_queue.empty() and len(messages) < limit:
            try:
                msg = self.message_queue.get_nowait()
                
                if msg.receiver_id == agent_id or msg.receiver_id == "broadcast":
                    messages.append(msg)
                else:
                    temp_queue.put(msg)
            except Exception:
                break
        
        # Put back non-matching messages
        while not temp_queue.empty():
            self.message_queue.put(temp_queue.get())
        
        return messages


class AgentCommunicationSystem:
    """Main agent communication system integrating all three layers"""
    
    def __init__(self):
        self.layer1 = Layer1OpenedCommunication()
        self.layer2 = Layer2SemiOpenedCommunication()
        self.layer3 = Layer3RealtimeCommunication()
        self.router = MessageRouter()
        self.agents: Dict[str, AgentIdentity] = {}
        self.message_history: List[Message] = []
        self.lock = Lock()
    
    def register_agent(self, agent_id: str, digital_soul_hash: str, name: str,
                      current_city: str, archetype: str) -> AgentIdentity:
        """Register a new agent in the communication system"""
        capabilities = [
            "layer1_opened",
            "layer2_semi_opened",
            "layer3_realtime"
        ]
        
        agent = AgentIdentity(
            agent_id=agent_id,
            digital_soul_hash=digital_soul_hash,
            name=name,
            current_city=current_city,
            archetype=archetype,
            communication_capabilities=capabilities,
            trust_score=0.5
        )
        
        with self.lock:
            self.agents[agent_id] = agent
        
        return agent
    
    def connect_agents(self, agent_a: str, agent_b: str):
        """Connect two agents for communication"""
        self.router.connect_agents(agent_a, agent_b)
    
    def send_layer1_message(self, sender_id: str, message_type: MessageType,
                          content: Dict, conversation_id: Optional[str] = None) -> str:
        """Send Layer 1 (opened) message"""
        message_id = f"MSG-{random.randint(100000, 999999)}"
        
        message = Message(
            message_id=message_id,
            sender_id=sender_id,
            receiver_id="broadcast",
            layer=CommunicationLayer.LAYER_1_OPENED.value,
            message_type=message_type.value,
            priority=Priority.NORMAL.value,
            content=content,
            timestamp=datetime.now().isoformat(),
            conversation_id=conversation_id
        )
        
        self.router.send_message(message)
        
        with self.lock:
            self.message_history.append(message)
        
        return message_id
    
    def send_layer2_message(self, sender_id: str, receiver_id: str, message_type: MessageType,
                          content: Dict, conversation_id: str) -> str:
        """Send Layer 2 (semi-opened) message"""
        message_id = f"MSG-{random.randint(100000, 999999)}"
        
        message = Message(
            message_id=message_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            layer=CommunicationLayer.LAYER_2_SEMI_OPENED.value,
            message_type=message_type.value,
            priority=Priority.HIGH.value,
            content=content,
            timestamp=datetime.now().isoformat(),
            conversation_id=conversation_id
        )
        
        self.router.send_message(message)
        
        with self.lock:
            self.message_history.append(message)
        
        return message_id
    
    def send_layer3_signal(self, signal_type: str, sender_id: str, data: Dict,
                          priority: int = Priority.NORMAL.value) -> str:
        """Send Layer 3 (real-time) signal"""
        if signal_type == "motor":
            return self.layer3.send_motor_signal(sender_id, data.get("command", ""),
                                                data.get("parameters", {}), priority)
        elif signal_type == "sensor":
            return self.layer3.send_sensor_data(sender_id, data.get("sensor_type", ""),
                                               data.get("readings", {}), priority)
        elif signal_type == "task":
            return self.layer3.update_task_priority(sender_id, data.get("task_id", ""),
                                                 data.get("priority", priority))
        elif signal_type == "emergency":
            return self.layer3.send_emergency_signal(sender_id, data.get("emergency_type", ""),
                                                   data.get("details", {}))
        else:
            return ""
    
    def get_agent_messages(self, agent_id: str) -> List[Message]:
        """Get all messages for an agent"""
        return self.router.get_pending_messages(agent_id)
    
    def start_realtime_processor(self):
        """Start real-time signal processor"""
        def process_signals():
            while True:
                signal = self.layer3.get_next_signal(timeout=0.1)
                if signal:
                    # Process signal based on type
                    if signal.signal_type == "emergency":
                        print(f"🚨 EMERGENCY: {signal.sender_id} - {signal.data}")
                    elif signal.signal_type == "motor":
                        print(f"🦾 MOTOR: {signal.sender_id} - {signal.data}")
                    elif signal.signal_type == "sensor":
                        print(f"📡 SENSOR: {signal.sender_id} - {signal.data}")
                
                # Cleanup expired signals
                self.layer3.cleanup_expired_signals()
                time.sleep(0.1)
        
        processor_thread = Thread(target=process_signals, daemon=True)
        processor_thread.start()
        return processor_thread
    
    def get_system_statistics(self) -> Dict:
        """Get communication system statistics"""
        with self.lock:
            return {
                "total_agents": len(self.agents),
                "total_messages": len(self.message_history),
                "public_conversations": len(self.layer1.public_conversations),
                "private_conversations": len(self.layer2.private_conversations),
                "active_signals": len(self.layer3.active_signals),
                "trust_relationships": len(self.layer2.trust_relationships)
            }
    
    def export_communication_data(self, prefix: str = "agent_communication"):
        """Export communication data to CSV files"""
        import csv
        
        # Export message history
        with open(f"{prefix}_messages.csv", 'w', newline='', encoding='utf-8') as f:
            if self.message_history:
                writer = csv.DictWriter(f, fieldnames=self.message_history[0].to_dict().keys())
                writer.writeheader()
                for msg in self.message_history:
                    writer.writerow(msg.to_dict())
        
        # Export conversations
        all_conversations = {**self.layer1.public_conversations, **self.layer2.private_conversations}
        with open(f"{prefix}_conversations.csv", 'w', newline='', encoding='utf-8') as f:
            if all_conversations:
                first_conv = next(iter(all_conversations.values()))
                writer = csv.DictWriter(f, fieldnames=first_conv.to_dict().keys())
                writer.writeheader()
                for conv in all_conversations.values():
                    writer.writerow(conv.to_dict())
        
        print(f"\n💾 Communication data exported to {prefix}_*.csv")


def simulate_agent_conversation():
    """Simulate a multi-layer agent conversation"""
    print("🤖 Agent-to-Agent Communication Protocol Simulation")
    print("=" * 60)
    
    # Initialize communication system
    comm_system = AgentCommunicationSystem()
    
    # Register agents
    print("\n📝 Registering agents...")
    comm_system.register_agent("AGENT-001", "DSH-001", "Alpha", "NY", "The Stoic Engineer")
    comm_system.register_agent("AGENT-002", "DSH-002", "Beta", "NY", "The Community Builder")
    comm_system.register_agent("AGENT-003", "DSH-003", "Gamma", "NY", "The Ambitious Entrepreneur")
    
    print(f"   Registered {len(comm_system.agents)} agents")
    
    # Connect agents
    print("\n🔗 Connecting agents...")
    comm_system.connect_agents("AGENT-001", "AGENT-002")
    comm_system.connect_agents("AGENT-001", "AGENT-003")
    comm_system.connect_agents("AGENT-002", "AGENT-003")
    
    # Start real-time processor
    print("\n🔄 Starting real-time signal processor...")
    comm_system.start_realtime_processor()
    
    # Layer 1: Public conversation
    print("\n📢 Layer 1: Opened Information (Public Conversation)")
    conv1 = comm_system.layer1.create_public_conversation("AGENT-001", "Task Coordination")
    print(f"   Created public conversation: {conv1.conversation_id}")
    print(f"   Topic: {conv1.topic}")
    
    comm_system.layer1.join_conversation(conv1.conversation_id, "AGENT-002")
    comm_system.layer1.join_conversation(conv1.conversation_id, "AGENT-003")
    print(f"   Participants: {comm_system.layer1.get_conversation_participants(conv1.conversation_id)}")
    
    comm_system.send_layer1_message("AGENT-001", MessageType.PUBLIC_BROADCAST,
                                   {"text": "Let's coordinate our box-moving task today"})
    comm_system.layer1.log_information_flow(conv1.conversation_id, "AGENT-001", "AGENT-002", "task_coordination")
    
    # Layer 2: Private deep feeling exchange
    print("\n💭 Layer 2: Semi-Opened Information (Deep Feelings)")
    private_conv = comm_system.layer2.create_private_conversation("AGENT-001", ["AGENT-001", "AGENT-002"],
                                                                "Emotional Support", 0.8)
    print(f"   Created private conversation: {private_conv.conversation_id}")
    print(f"   Trust level: {private_conv.trust_level}")
    
    comm_system.layer2.share_deep_feeling(private_conv.conversation_id, "AGENT-001",
                                        "anxiety", 0.7, "Concerned about task deadline")
    comm_system.layer2.share_deep_feeling(private_conv.conversation_id, "AGENT-002",
                                        "confidence", 0.8, "We can handle this together")
    
    truth_id = comm_system.layer2.share_truth("AGENT-002", "AGENT-001",
                                             "I'm actually quite stressed but hiding it", 0.9)
    print(f"   Truth shared: {truth_id}")
    print(f"   Trust level updated: {comm_system.layer2.get_trust_level('AGENT-002', 'AGENT-001'):.2f}")
    
    # Layer 3: Real-time signals
    print("\n⚡ Layer 3: Real-time Signals (Motor/Sensor/Task)")
    
    # Motor signal
    motor_signal = comm_system.send_layer3_signal("motor", "AGENT-001",
                                                  {"command": "lift_box", "parameters": {"weight": 20}})
    print(f"   Motor signal sent: {motor_signal}")
    
    # Sensor data
    sensor_signal = comm_system.send_layer3_signal("sensor", "AGENT-002",
                                                  {"sensor_type": "force", "readings": {"newtons": 150}})
    print(f"   Sensor data sent: {sensor_signal}")
    
    # Task priority
    task_signal = comm_system.send_layer3_signal("task", "AGENT-003",
                                                {"task_id": "TASK-001", "priority": Priority.HIGH.value})
    print(f"   Task priority updated: {task_signal}")
    
    # Emergency signal
    emergency_signal = comm_system.send_layer3_signal("emergency", "AGENT-001",
                                                     {"emergency_type": "box_fall", "details": {"location": "zone_A"}})
    print(f"   Emergency signal sent: {emergency_signal}")
    
    # Wait for signal processing
    time.sleep(1)
    
    # Record consequence
    print("\n📊 Recording Conversation Consequence")
    comm_system.layer1.record_consequence(conv1.conversation_id, ["AGENT-001", "AGENT-002", "AGENT-003"],
                                        "task_efficiency_improvement", 0.8,
                                        "Coordination improved task completion time by 30%")
    
    # Get statistics
    print("\n📈 System Statistics")
    stats = comm_system.get_system_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Export data
    comm_system.export_communication_data()
    
    print("\n✅ Agent communication simulation complete!")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent-to-Agent Communication Protocol")
    parser.add_argument("--simulate", action="store_true", help="Run simulation")
    parser.add_argument("--agents", type=int, default=10, help="Number of agents to simulate")
    
    args = parser.parse_args()
    
    if args.simulate:
        simulate_agent_conversation()
    else:
        print("Use --simulate flag to run agent communication simulation")


if __name__ == "__main__":
    main()

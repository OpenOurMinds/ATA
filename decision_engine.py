"""
Decision Engine
Automated decision-making system for ATA self-sustaining operation
Provides policy recommendations and autonomous decision capabilities
"""

import random
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class DecisionType(Enum):
    """Types of decisions the engine can make"""
    PARAMETER_ADJUSTMENT = "parameter_adjustment"
    POLICY_RECOMMENDATION = "policy_recommendation"
    RESOURCE_ALLOCATION = "resource_allocation"
    EMERGENCY_RESPONSE = "emergency_response"
    LEARNING_TRIGGER = "learning_trigger"


class Priority(Enum):
    """Decision priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Decision:
    """A decision made by the engine"""
    decision_id: str
    decision_type: str
    priority: int
    trigger_condition: str
    recommended_action: str
    rationale: str
    expected_impact: Dict[str, float]
    timestamp: str
    executed: bool = False
    execution_result: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Rule:
    """A decision rule"""
    rule_id: str
    name: str
    condition: str
    decision_type: DecisionType
    priority: Priority
    action_template: str
    impact_estimate: Dict[str, float]
    
    def evaluate(self, context: Dict) -> bool:
        """Evaluate if rule condition is met"""
        # Simple rule evaluation based on context
        if "democratic_index" in self.condition:
            threshold = float(self.condition.split(">")[1].strip())
            return context.get('democratic_index', 0.5) < threshold
        
        if "collapse_risk" in self.condition:
            threshold = float(self.condition.split(">")[1].strip())
            return context.get('collapse_risk', 0.0) > threshold
        
        if "economic_health" in self.condition:
            threshold = float(self.condition.split("<")[1].strip())
            return context.get('economic_health', 0.5) < threshold
        
        return False
    
    def generate_decision(self, context: Dict) -> Decision:
        """Generate a decision from this rule"""
        decision_id = f"DEC-{random.randint(100000, 999999)}"
        
        # Fill in action template with context values
        action = self.action_template
        for key, value in context.items():
            action = action.replace(f"{{{key}}}", str(value))
        
        return Decision(
            decision_id=decision_id,
            decision_type=self.decision_type.value,
            priority=self.priority.value,
            trigger_condition=self.condition,
            recommended_action=action,
            rationale=f"Rule '{self.name}' triggered by condition: {self.condition}",
            expected_impact=self.impact_estimate,
            timestamp=datetime.now().isoformat()
        )


class DecisionEngine:
    """Main decision engine for autonomous decision-making"""
    
    def __init__(self):
        self.rules = self._initialize_default_rules()
        self.decision_history: List[Decision] = []
        self.pending_decisions: List[Decision] = []
        self.context: Dict = {}
    
    def _initialize_default_rules(self) -> List[Rule]:
        """Initialize default decision rules"""
        return [
            Rule(
                rule_id="RULE-001",
                name="Low Democratic Index Alert",
                condition="democratic_index < 0.4",
                decision_type=DecisionType.POLICY_RECOMMENDATION,
                priority=Priority.HIGH,
                action_template="Increase social cohesion activities by 20%. Focus on community building initiatives.",
                impact_estimate={"democratic_index": 0.1, "social_cohesion": 0.15}
            ),
            Rule(
                rule_id="RULE-002",
                name="High Collapse Risk Emergency",
                condition="collapse_risk > 0.6",
                decision_type=DecisionType.EMERGENCY_RESPONSE,
                priority=Priority.CRITICAL,
                action_template="Activate population collapse hedge. Increase virtual agent participation to 150% of baseline.",
                impact_estimate={"collapse_risk": -0.2, "democratic_index": 0.05}
            ),
            Rule(
                rule_id="RULE-003",
                name="Low Economic Health Warning",
                condition="economic_health < 0.3",
                decision_type=DecisionType.RESOURCE_ALLOCATION,
                priority=Priority.MEDIUM,
                action_template="Reallocate 10% of resources to economic stimulation programs.",
                impact_estimate={"economic_health": 0.1, "social_cohesion": 0.02}
            ),
            Rule(
                rule_id="RULE-004",
                name="Parameter Optimization Trigger",
                condition="democratic_index < 0.5 AND economic_health < 0.5",
                decision_type=DecisionType.LEARNING_TRIGGER,
                priority=Priority.HIGH,
                action_template="Trigger parameter optimization cycle with focus on trust and altruism weights.",
                impact_estimate={"democratic_index": 0.15, "economic_health": 0.1}
            ),
            Rule(
                rule_id="RULE-005",
                name="Trust Deficit Adjustment",
                condition="trust_weight < 0.2",
                decision_type=DecisionType.PARAMETER_ADJUSTMENT,
                priority=Priority.MEDIUM,
                action_template="Increase trust_weight parameter by 0.1 to improve democratic participation.",
                impact_estimate={"trust_weight": 0.1, "democratic_index": 0.05}
            ),
            Rule(
                rule_id="RULE-006",
                name="Altruism Boost",
                condition="social_cohesion < 0.4",
                decision_type=DecisionType.PARAMETER_ADJUSTMENT,
                priority=Priority.MEDIUM,
                action_template="Increase altruism_weight by 0.15 to enhance community contribution.",
                impact_estimate={"altruism_weight": 0.15, "social_cohesion": 0.2}
            ),
            Rule(
                rule_id="RULE-007",
                name="Ambition Stimulation",
                condition="economic_health < 0.4",
                decision_type=DecisionType.PARAMETER_ADJUSTMENT,
                priority=Priority.MEDIUM,
                action_template="Increase ambition_weight by 0.1 to stimulate economic activity.",
                impact_estimate={"ambition_weight": 0.1, "economic_health": 0.15}
            )
        ]
    
    def update_context(self, context: Dict):
        """Update the current context for decision making"""
        self.context = context
    
    def evaluate_rules(self) -> List[Decision]:
        """Evaluate all rules and generate decisions"""
        triggered_decisions = []
        
        for rule in self.rules:
            if rule.evaluate(self.context):
                decision = rule.generate_decision(self.context)
                triggered_decisions.append(decision)
        
        # Sort by priority (highest first)
        triggered_decisions.sort(key=lambda d: d.priority, reverse=True)
        
        return triggered_decisions
    
    def make_decisions(self) -> List[Decision]:
        """Make decisions based on current context"""
        decisions = self.evaluate_rules()
        
        # Add to pending decisions
        self.pending_decisions.extend(decisions)
        
        # Add to history
        self.decision_history.extend(decisions)
        
        return decisions
    
    def execute_decision(self, decision_id: str, execution_result: str = "Executed successfully"):
        """Mark a decision as executed"""
        for decision in self.pending_decisions:
            if decision.decision_id == decision_id:
                decision.executed = True
                decision.execution_result = execution_result
                break
        
        # Also update in history
        for decision in self.decision_history:
            if decision.decision_id == decision_id:
                decision.executed = True
                decision.execution_result = execution_result
                break
    
    def get_pending_decisions(self, priority_filter: Optional[Priority] = None) -> List[Decision]:
        """Get pending decisions, optionally filtered by priority"""
        if priority_filter:
            return [d for d in self.pending_decisions 
                   if not d.executed and d.priority == priority_filter.value]
        return [d for d in self.pending_decisions if not d.executed]
    
    def get_critical_decisions(self) -> List[Decision]:
        """Get only critical priority decisions"""
        return self.get_pending_decisions(Priority.CRITICAL)
    
    def auto_execute_critical(self) -> List[Decision]:
        """Automatically execute all critical decisions"""
        critical_decisions = self.get_critical_decisions()
        executed = []
        
        for decision in critical_decisions:
            self.execute_decision(decision.decision_id)
            executed.append(decision)
        
        return executed
    
    def get_decision_statistics(self) -> Dict:
        """Get statistics about decisions made"""
        total = len(self.decision_history)
        executed_count = sum(1 for d in self.decision_history if d.executed)
        pending_count = len(self.pending_decisions) - executed_count
        
        by_type = {}
        for decision in self.decision_history:
            dtype = decision.decision_type
            by_type[dtype] = by_type.get(dtype, 0) + 1
        
        by_priority = {}
        for decision in self.decision_history:
            priority = decision.priority
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        return {
            "total_decisions": total,
            "executed_decisions": executed_count,
            "pending_decisions": pending_count,
            "decisions_by_type": by_type,
            "decisions_by_priority": by_priority
        }
    
    def add_rule(self, rule: Rule):
        """Add a new decision rule"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_id: str):
        """Remove a decision rule"""
        self.rules = [r for r in self.rules if r.rule_id != rule_id]
    
    def export_decisions(self, filename: str = "decision_history.json"):
        """Export decision history to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([d.to_dict() for d in self.decision_history], f, indent=2)
    
    def load_rules(self, filename: str):
        """Load rules from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.rules = [Rule(**r) for r in data]
        except Exception:
            pass


class AutonomousController:
    """Controller for autonomous operation of ATA system"""
    
    def __init__(self):
        self.decision_engine = DecisionEngine()
        self.running = False
        self.cycle_count = 0
    
    def run_cycle(self, context: Dict) -> List[Decision]:
        """Run one autonomous decision cycle"""
        self.cycle_count += 1
        
        # Update context
        self.decision_engine.update_context(context)
        
        # Make decisions
        decisions = self.decision_engine.make_decisions()
        
        # Auto-execute critical decisions
        critical_executed = self.decision_engine.auto_execute_critical()
        
        return decisions
    
    def start_autonomous_mode(self, context_provider, action_executor, 
                            cycle_interval: float = 60.0):
        """Start autonomous mode with continuous cycles"""
        import time
        
        self.running = True
        
        while self.running:
            # Get current context
            context = context_provider()
            
            # Run decision cycle
            decisions = self.run_cycle(context)
            
            # Execute decisions
            for decision in decisions:
                if not decision.executed:
                    result = action_executor(decision)
                    self.decision_engine.execute_decision(decision.decision_id, result)
            
            # Wait for next cycle
            time.sleep(cycle_interval)
    
    def stop_autonomous_mode(self):
        """Stop autonomous mode"""
        self.running = False


def main():
    """Test the decision engine"""
    print("🧠 Decision Engine Test")
    print("=" * 50)
    
    engine = DecisionEngine()
    
    # Test scenario 1: Low democratic index
    print("\n📊 Scenario 1: Low Democratic Index")
    context1 = {
        "democratic_index": 0.35,
        "collapse_risk": 0.4,
        "economic_health": 0.6,
        "social_cohesion": 0.5,
        "trust_weight": 0.25,
        "altruism_weight": 0.2,
        "ambition_weight": 0.3
    }
    
    engine.update_context(context1)
    decisions1 = engine.make_decisions()
    
    print(f"   Triggered {len(decisions1)} decisions:")
    for decision in decisions1:
        print(f"   - {decision.decision_type}: {decision.recommended_action}")
    
    # Test scenario 2: High collapse risk
    print("\n📊 Scenario 2: High Collapse Risk")
    context2 = {
        "democratic_index": 0.25,
        "collapse_risk": 0.7,
        "economic_health": 0.4,
        "social_cohesion": 0.3,
        "trust_weight": 0.15,
        "altruism_weight": 0.15,
        "ambition_weight": 0.2
    }
    
    engine.update_context(context2)
    decisions2 = engine.make_decisions()
    
    print(f"   Triggered {len(decisions2)} decisions:")
    for decision in decisions2:
        print(f"   - {decision.decision_type}: {decision.recommended_action}")
    
    # Get statistics
    stats = engine.get_decision_statistics()
    print(f"\n📈 Decision Statistics:")
    print(f"   Total Decisions: {stats['total_decisions']}")
    print(f"   Executed: {stats['executed_decisions']}")
    print(f"   Pending: {stats['pending_decisions']}")
    
    # Export decisions
    engine.export_decisions()
    print(f"\n💾 Decision history exported to decision_history.json")


if __name__ == "__main__":
    main()

// Package decision implements the autonomous decision engine
// and parameter optimizer for the ATA closed loop.
package decision

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"time"

	"github.com/OpenOurMinds/ATA/internal/city"
)

// DecisionType classifies the kind of decision.
type DecisionType string

const (
	DecisionParamAdjust    DecisionType = "parameter_adjustment"
	DecisionPolicy         DecisionType = "policy_recommendation"
	DecisionResource       DecisionType = "resource_allocation"
	DecisionEmergency      DecisionType = "emergency_response"
	DecisionLearningTrigger DecisionType = "learning_trigger"
)

// Priority levels for decisions.
type Priority int

const (
	PriorityLow      Priority = 1
	PriorityMedium   Priority = 2
	PriorityHigh     Priority = 3
	PriorityCritical Priority = 4
)

// Decision is a single decision made by the engine.
type Decision struct {
	ID         string            `json:"id"`
	Type       DecisionType      `json:"type"`
	Priority   Priority          `json:"priority"`
	Action     string            `json:"action"`
	Rationale  string            `json:"rationale"`
	Impact     map[string]float64 `json:"expectedImpact"`
	Executed   bool              `json:"executed"`
	Result     string            `json:"result,omitempty"`
	Timestamp  time.Time         `json:"timestamp"`
}

// Parameters holds the tunable system parameters.
type Parameters struct {
	SoulCount      int     `json:"soulCount"`
	TrustWeight    float64 `json:"trustWeight"`
	AltruismWeight float64 `json:"altruismWeight"`
	AmbitionWeight float64 `json:"ambitionWeight"`
	CuriosityWeight float64 `json:"curiosityWeight"`
	FearWeight     float64 `json:"fearWeight"`
	LearningRate   float64 `json:"learningRate"`
	ExplorationRate float64 `json:"explorationRate"`
}

// DefaultParameters returns the initial parameter set.
func DefaultParameters() Parameters {
	return Parameters{
		SoulCount:       50,
		TrustWeight:     0.30,
		AltruismWeight:  0.25,
		AmbitionWeight:  0.20,
		CuriosityWeight: 0.15,
		FearWeight:      0.10,
		LearningRate:    0.01,
		ExplorationRate: 0.30,
	}
}

// Rule defines a condition-action pair for decision making.
type Rule struct {
	ID        string
	Name      string
	Evaluate  func(health city.DemocraticHealth, params Parameters) bool
	Type      DecisionType
	Priority  Priority
	Action    string
	Impact    map[string]float64
}

// Engine is the autonomous decision-making system.
type Engine struct {
	rules   []Rule
	history []Decision
	rng     *rand.Rand
}

// NewEngine creates a decision engine with default rules.
func NewEngine(seed int64) *Engine {
	e := &Engine{
		rng: rand.New(rand.NewSource(seed)),
	}
	e.rules = e.defaultRules()
	return e
}

func (e *Engine) defaultRules() []Rule {
	return []Rule{
		{
			ID: "RULE-001", Name: "Low Democratic Index",
			Evaluate: func(h city.DemocraticHealth, _ Parameters) bool {
				return h.DataSufficient && h.OverallIndex < 0.4
			},
			Type: DecisionPolicy, Priority: PriorityHigh,
			Action: "Increase social cohesion activities by 20%",
			Impact: map[string]float64{"democraticIndex": 0.1, "socialCohesion": 0.15},
		},
		{
			ID: "RULE-002", Name: "High Collapse Risk",
			Evaluate: func(h city.DemocraticHealth, _ Parameters) bool {
				return h.DataSufficient && h.CollapseRisk > 0.6
			},
			Type: DecisionEmergency, Priority: PriorityCritical,
			Action: "Activate population collapse hedge",
			Impact: map[string]float64{"collapseRisk": -0.2, "democraticIndex": 0.05},
		},
		{
			ID: "RULE-003", Name: "Low Economic Health",
			Evaluate: func(h city.DemocraticHealth, _ Parameters) bool {
				return h.DataSufficient && h.EconomicHealth < 0.3
			},
			Type: DecisionResource, Priority: PriorityMedium,
			Action: "Reallocate 10% resources to economic stimulation",
			Impact: map[string]float64{"economicHealth": 0.1},
		},
	}
}

// Evaluate runs all rules against current state, returns triggered decisions.
func (e *Engine) Evaluate(health city.DemocraticHealth, params Parameters) []Decision {
	var decisions []Decision
	for _, rule := range e.rules {
		if rule.Evaluate(health, params) {
			d := Decision{
				ID:        fmt.Sprintf("DEC-%06d", e.rng.Intn(999999)),
				Type:      rule.Type,
				Priority:  rule.Priority,
				Action:    rule.Action,
				Rationale: fmt.Sprintf("Rule %q triggered", rule.Name),
				Impact:    rule.Impact,
				Timestamp: time.Now().UTC(),
			}
			decisions = append(decisions, d)
		}
	}
	e.history = append(e.history, decisions...)
	return decisions
}

// OptimizeParameters adjusts parameters based on health metrics.
func (e *Engine) OptimizeParameters(health city.DemocraticHealth, current Parameters) Parameters {
	if !health.DataSufficient {
		return current
	}
	next := current
	lr := current.LearningRate

	// Increase trust if democratic index is low.
	if health.OverallIndex < 0.5 {
		next.TrustWeight = clamp(next.TrustWeight+lr, 0, 1)
		next.AltruismWeight = clamp(next.AltruismWeight+lr*0.5, 0, 1)
	}
	// Boost ambition if economic health is low.
	if health.EconomicHealth < 0.4 {
		next.AmbitionWeight = clamp(next.AmbitionWeight+lr, 0, 1)
	}
	// Reduce fear if collapse risk is high (counterintuitive but promotes engagement).
	if health.CollapseRisk > 0.5 {
		next.FearWeight = clamp(next.FearWeight-lr*0.5, 0, 1)
	}
	return next
}

// History returns all decisions made.
func (e *Engine) History() []Decision {
	return e.history
}

// MarshalHistory returns the decision history as JSON.
func (e *Engine) MarshalHistory() ([]byte, error) {
	return json.MarshalIndent(e.history, "", "  ")
}

func clamp(v, min, max float64) float64 {
	if v < min {
		return min
	}
	if v > max {
		return max
	}
	return v
}

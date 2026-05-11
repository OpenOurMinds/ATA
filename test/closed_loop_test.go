package test

import (
	"testing"

	"github.com/OpenOurMinds/ATA/internal/city"
	"github.com/OpenOurMinds/ATA/internal/decision"
	"github.com/OpenOurMinds/ATA/internal/soul"
)

// TestClosedLoop verifies the full soul→city→decision autonomous cycle.
func TestClosedLoop(t *testing.T) {
	// Phase 1: Generate souls.
	gen := soul.NewGenerator(42)
	souls := gen.GeneratePopulation(50)

	if len(souls) != 50 {
		t.Fatalf("generated %d souls, want 50", len(souls))
	}

	// Verify soul integrity.
	for _, s := range souls {
		if s.DigitalSoulHash == "" {
			t.Error("soul has empty hash")
		}
		if s.Age < 16 || s.Age > 85 {
			t.Errorf("soul age %d out of range [16, 85]", s.Age)
		}
	}

	// Phase 2: Run city simulation.
	sim := city.NewSimulator(42)
	result := sim.RunCycle(souls)

	if result.Citizens != 50 {
		t.Errorf("citizens = %d, want 50", result.Citizens)
	}
	if result.Observations == 0 {
		t.Error("expected observations > 0")
	}
	if result.Posts == 0 {
		t.Error("expected posts > 0")
	}
	if !result.Health.DataSufficient {
		t.Error("expected DataSufficient = true")
	}
	if result.Health.OverallIndex <= 0 || result.Health.OverallIndex > 1 {
		t.Errorf("democratic index %f out of range (0, 1]", result.Health.OverallIndex)
	}

	// Phase 3: Decision engine evaluation.
	engine := decision.NewEngine(42)
	params := decision.DefaultParameters()
	decisions := engine.Evaluate(result.Health, params)

	t.Logf("Democratic Index: %.3f", result.Health.OverallIndex)
	t.Logf("Collapse Risk: %.3f", result.Health.CollapseRisk)
	t.Logf("Decisions triggered: %d", len(decisions))

	// Phase 4: Parameter optimization.
	optimized := engine.OptimizeParameters(result.Health, params)

	// Verify parameters changed (optimization should adjust something).
	if result.Health.OverallIndex < 0.5 {
		if optimized.TrustWeight <= params.TrustWeight {
			t.Error("expected TrustWeight to increase when demIndex < 0.5")
		}
	}

	t.Logf("Original TrustWeight: %.4f → Optimized: %.4f", params.TrustWeight, optimized.TrustWeight)
}

// TestEmptyPopulationHandling verifies the system handles edge cases.
func TestEmptyPopulationHandling(t *testing.T) {
	sim := city.NewSimulator(42)
	result := sim.RunCycle(nil)

	if result.Health.DataSufficient {
		t.Error("expected DataSufficient = false for nil population")
	}
	if result.Health.OverallIndex != 0 {
		t.Errorf("expected zero index for empty population, got %f", result.Health.OverallIndex)
	}
}

// TestDecisionEngineWithInsufficientData verifies no decisions on bad data.
func TestDecisionEngineWithInsufficientData(t *testing.T) {
	engine := decision.NewEngine(42)
	health := city.DemocraticHealth{DataSufficient: false}
	params := decision.DefaultParameters()

	decisions := engine.Evaluate(health, params)
	if len(decisions) != 0 {
		t.Errorf("expected 0 decisions with insufficient data, got %d", len(decisions))
	}
}

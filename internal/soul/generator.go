package soul

import (
	"fmt"
	"math/rand"
)

// eventTypes for memory anchors.
var eventTypes = []string{
	"discovery", "loss", "triumph", "betrayal", "journey",
	"friendship", "innovation", "sacrifice", "awakening", "challenge",
}

// narrativeTemplates keyed by event type.
var narrativeTemplates = map[string][]string{
	"discovery":  {"Found a hidden collection of old books in the attic", "Witnessed an unexpected scientific phenomenon"},
	"loss":       {"Lost a close family member at a young age", "Experienced a sudden financial setback"},
	"triumph":    {"Won a regional academic competition against all odds", "Built something from scratch that changed the community"},
	"betrayal":   {"Trusted advisor turned out to have hidden motives", "Discovered a fundamental institutional lie"},
	"journey":    {"Traveled alone across three countries at age 18", "Relocated to an unfamiliar city for opportunity"},
	"friendship": {"Formed a lifelong bond during a crisis", "Met a mentor who reshaped their worldview"},
	"innovation": {"Invented a tool that solved a persistent local problem", "Proposed a novel approach that was initially rejected"},
	"sacrifice":  {"Gave up a promising career to care for a parent", "Chose community well-being over personal gain"},
	"awakening":  {"Realized the system they trusted was fundamentally flawed", "Had a sudden clarity about purpose"},
	"challenge":  {"Survived a natural disaster", "Overcame a physical limitation through persistence"},
}

// genders for census-weighted generation.
var genders = []string{"Male", "Female"}

// Generator produces synthetic Digital Soul populations.
type Generator struct {
	rng *rand.Rand
}

// NewGenerator creates a soul generator with the given random seed.
func NewGenerator(seed int64) *Generator {
	return &Generator{rng: rand.New(rand.NewSource(seed))}
}

// Generate creates a single Digital Soul.
func (g *Generator) Generate() Soul {
	age := 16 + g.rng.Intn(70) // 16-85
	gender := genders[g.rng.Intn(len(genders))]
	archetype := AllArchetypes[g.rng.Intn(len(AllArchetypes))]
	birthDate := generateBirthDate(g.rng, age)

	eventType := eventTypes[g.rng.Intn(len(eventTypes))]
	templates := narrativeTemplates[eventType]
	narrative := templates[g.rng.Intn(len(templates))]

	memory := MemoryAnchor{
		EventType:       eventType,
		AgeAtEvent:      5 + g.rng.Intn(age-4),
		EmotionalWeight: randFloat(g.rng, 0.3, 1.0),
		Narrative:       narrative,
		Emotions:        []string{"determination", "nostalgia"},
	}

	emotions := EmotionalResonance{
		Trust:     randFloat(g.rng, 0.1, 0.9),
		Fear:      randFloat(g.rng, 0.1, 0.9),
		Altruism:  randFloat(g.rng, 0.1, 0.9),
		Ambition:  randFloat(g.rng, 0.1, 0.9),
		Curiosity: randFloat(g.rng, 0.1, 0.9),
	}

	socialCredit := randFloat(g.rng, 20, 95)
	dsh := ComputeHash(birthDate, narrative, fmt.Sprintf("%d", g.rng.Int63()))

	behavior := BehavioralPatterns{
		Routine:             randFloat(g.rng, 0.1, 0.9),
		RiskAverse:          randFloat(g.rng, 0.1, 0.9),
		TechSavvy:           randFloat(g.rng, 0.1, 0.9),
		SocialEngagement:    randFloat(g.rng, 0.1, 0.9),
		HealthConsciousness: randFloat(g.rng, 0.1, 0.9),
	}

	return Soul{
		CitizenID:         fmt.Sprintf("ALPHA-%02d-%03d", g.rng.Intn(100), g.rng.Intn(1000)),
		DigitalSoulHash:   dsh,
		BirthDate:         birthDate,
		Age:               age,
		Gender:            gender,
		LifeStage:         LifeStageFromAge(age),
		Archetype:         archetype,
		Memory:            memory,
		Emotions:          emotions,
		SocialCreditScore: socialCredit,
		InsuranceRiskTier: riskTier(socialCredit),
		Behavior:          behavior,
	}
}

// GeneratePopulation creates n Digital Souls.
func (g *Generator) GeneratePopulation(n int) []Soul {
	souls := make([]Soul, 0, n)
	for i := 0; i < n; i++ {
		souls = append(souls, g.Generate())
	}
	return souls
}

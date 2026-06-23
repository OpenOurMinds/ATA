// Package soul implements the Digital Soul domain logic.
// It generates synthetic citizens with cryptographic identities,
// memory anchors, emotional vectors, and behavioral archetypes.
package soul

import (
	"crypto/sha256"
	"encoding/csv"
	"encoding/hex"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"time"
)

// Archetype represents a personality classification.
type Archetype string

const (
	ArchStoicEngineer       Archetype = "The Stoic Engineer"
	ArchDisillusionedArtist Archetype = "The Disillusioned Artist"
	ArchCommunityBuilder    Archetype = "The Community Builder"
	ArchAmbitiousEntrepreneur Archetype = "The Ambitious Entrepreneur"
	ArchCautiousObserver    Archetype = "The Cautious Observer"
	ArchIdealisticActivist  Archetype = "The Idealistic Activist"
)

// AllArchetypes is the complete list of archetypes.
var AllArchetypes = []Archetype{
	ArchStoicEngineer,
	ArchDisillusionedArtist,
	ArchCommunityBuilder,
	ArchAmbitiousEntrepreneur,
	ArchCautiousObserver,
	ArchIdealisticActivist,
}

// LifeStage classifies age-based phases.
type LifeStage string

const (
	StageYouth         LifeStage = "Youth"
	StageEarlyCareer   LifeStage = "Early Career"
	StageMidCareer     LifeStage = "Mid Career"
	StageLateCareer    LifeStage = "Late Career"
	StagePreRetirement LifeStage = "Pre-Retirement"
	StageRetired       LifeStage = "Retired"
	StageElderly       LifeStage = "Elderly"
)

// LifeStageFromAge returns the life stage for a given age.
func LifeStageFromAge(age int) LifeStage {
	switch {
	case age < 25:
		return StageYouth
	case age < 35:
		return StageEarlyCareer
	case age < 45:
		return StageMidCareer
	case age < 55:
		return StageLateCareer
	case age < 65:
		return StagePreRetirement
	case age < 75:
		return StageRetired
	default:
		return StageElderly
	}
}

// MemoryAnchor is a high-emotion root event that shapes worldview.
type MemoryAnchor struct {
	EventType       string   `json:"eventType"`
	AgeAtEvent      int      `json:"ageAtEvent"`
	EmotionalWeight float64  `json:"emotionalWeight"`
	Narrative       string   `json:"narrative"`
	Emotions        []string `json:"emotions"`
}

// EmotionalResonance is a 5-dimensional emotional vector.
type EmotionalResonance struct {
	Trust    float64 `json:"trust"`
	Fear     float64 `json:"fear"`
	Altruism float64 `json:"altruism"`
	Ambition float64 `json:"ambition"`
	Curiosity float64 `json:"curiosity"`
}

// BehavioralPatterns captures lifestyle tendencies.
type BehavioralPatterns struct {
	Routine             float64 `json:"routine"`
	RiskAverse          float64 `json:"riskAverse"`
	TechSavvy           float64 `json:"techSavvy"`
	SocialEngagement    float64 `json:"socialEngagement"`
	HealthConsciousness float64 `json:"healthConsciousness"`
}

// Soul is a complete digital citizen profile.
type Soul struct {
	CitizenID         string             `json:"citizenId"`
	DigitalSoulHash   string             `json:"digitalSoulHash"`
	BirthDate         string             `json:"birthDate"`
	Age               int                `json:"age"`
	Gender            string             `json:"gender"`
	LifeStage         LifeStage          `json:"lifeStage"`
	Archetype         Archetype          `json:"archetype"`
	Memory            MemoryAnchor       `json:"memoryAnchor"`
	Emotions          EmotionalResonance `json:"emotionalResonance"`
	SocialCreditScore float64            `json:"socialCreditScore"`
	InsuranceRiskTier string             `json:"insuranceRiskTier"`
	Behavior          BehavioralPatterns `json:"behavioralPatterns"`
}

// ComputeHash generates a deterministic Digital Soul Hash.
func ComputeHash(birthDate, narrative, seed string) string {
	data := fmt.Sprintf("%s|%s|%s", birthDate, narrative, seed)
	hash := sha256.Sum256([]byte(data))
	return hex.EncodeToString(hash[:])
}

// riskTier returns a risk classification based on score.
func riskTier(score float64) string {
	switch {
	case score >= 80:
		return "Low"
	case score >= 50:
		return "Standard"
	case score >= 30:
		return "High"
	default:
		return "Critical"
	}
}

// randFloat returns a random float64 in [min, max).
func randFloat(rng *rand.Rand, min, max float64) float64 {
	return min + rng.Float64()*(max-min)
}

// generateBirthDate creates a random birth date for the given age.
func generateBirthDate(rng *rand.Rand, age int) string {
	year := time.Now().Year() - age
	month := rng.Intn(12) + 1
	day := rng.Intn(28) + 1
	return fmt.Sprintf("%04d-%02d-%02d", year, month, day)
}

// LoadDemographics loads synthetic citizen profiles from a CSV dataset.
func LoadDemographics(path string) ([]Soul, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	if len(records) <= 1 {
		return nil, fmt.Errorf("empty CSV or only headers present")
	}

	var souls []Soul
	// Skip header (row 0)
	for i := 1; i < len(records); i++ {
		row := records[i]
		if len(row) < 15 {
			continue
		}

		age, _ := strconv.Atoi(row[1])
		socialCredit, _ := strconv.ParseFloat(row[4], 64)
		trust, _ := strconv.ParseFloat(row[5], 64)
		fear, _ := strconv.ParseFloat(row[6], 64)
		altruism, _ := strconv.ParseFloat(row[7], 64)
		ambition, _ := strconv.ParseFloat(row[8], 64)
		curiosity, _ := strconv.ParseFloat(row[9], 64)
		routine, _ := strconv.ParseFloat(row[10], 64)
		riskAverse, _ := strconv.ParseFloat(row[11], 64)
		techSavvy, _ := strconv.ParseFloat(row[12], 64)
		socialEngagement, _ := strconv.ParseFloat(row[13], 64)
		healthConsciousness, _ := strconv.ParseFloat(row[14], 64)

		archetype := Archetype(row[3])

		// Generate narrative memory anchored to archetype
		eventType := "discovery"
		narrative := "Witnessed an unexpected scientific phenomenon"
		switch archetype {
		case ArchDisillusionedArtist:
			eventType = "loss"
			narrative = "Experienced a sudden financial setback"
		case ArchCommunityBuilder:
			eventType = "friendship"
			narrative = "Met a mentor who reshaped their worldview"
		case ArchAmbitiousEntrepreneur:
			eventType = "triumph"
			narrative = "Built something from scratch that changed the community"
		case ArchCautiousObserver:
			eventType = "challenge"
			narrative = "Overcame a physical limitation through persistence"
		case ArchIdealisticActivist:
			eventType = "awakening"
			narrative = "Realized the system they trusted was fundamentally flawed"
		}

		// Instantiate random generator just for seed hashing
		rng := rand.New(rand.NewSource(int64(i + age)))
		birthDate := generateBirthDate(rng, age)

		soul := Soul{
			CitizenID:       row[0],
			DigitalSoulHash: ComputeHash(birthDate, narrative, fmt.Sprintf("%d", i)),
			BirthDate:       birthDate,
			Age:             age,
			Gender:          row[2],
			LifeStage:       LifeStageFromAge(age),
			Archetype:       archetype,
			Memory: MemoryAnchor{
				EventType:       eventType,
				AgeAtEvent:      5 + rng.Intn(max(1, age-6)),
				EmotionalWeight: randFloat(rng, 0.3, 1.0),
				Narrative:       narrative,
				Emotions:        []string{"determination", "nostalgia"},
			},
			Emotions: EmotionalResonance{
				Trust:     trust,
				Fear:      fear,
				Altruism:  altruism,
				Ambition:  ambition,
				Curiosity: curiosity,
			},
			SocialCreditScore: socialCredit,
			InsuranceRiskTier: riskTier(socialCredit),
			Behavior: BehavioralPatterns{
				Routine:             routine,
				RiskAverse:          riskAverse,
				TechSavvy:           techSavvy,
				SocialEngagement:    socialEngagement,
				HealthConsciousness: healthConsciousness,
			},
		}
		souls = append(souls, soul)
	}

	return souls, nil
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

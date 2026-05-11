// Package city implements the virtual city simulation engine.
// It replaces virtual_city_simulator.py, robot_internet_workflow.py,
// virtual_city_integration.py, and democratic_voting_system.py
// with a unified, data-driven simulation.
package city

import (
	"fmt"
	"math"
	"math/rand"
	"time"

	"github.com/OpenOurMinds/ATA/internal/soul"
)

// Activity represents a detected physical activity.
type Activity struct {
	Type        string    `json:"type"`
	RiskLevel   string    `json:"riskLevel"`
	Description string    `json:"description"`
	Timestamp   time.Time `json:"timestamp"`
}

// Observation is a single robot-observed event.
type Observation struct {
	SessionID   string   `json:"sessionId"`
	CitizenID   string   `json:"citizenId"`
	Activity    Activity `json:"activity"`
	SensorData  map[string]float64 `json:"sensorData"`
}

// SNSPost is content generated from an observation.
type SNSPost struct {
	PostID         string  `json:"postId"`
	CitizenID      string  `json:"citizenId"`
	TextContent    string  `json:"textContent"`
	Archetype      string  `json:"archetype"`
	SentimentScore float64 `json:"sentimentScore"`
	Timestamp      time.Time `json:"timestamp"`
}

// DemocraticHealth tracks the health of democratic systems.
type DemocraticHealth struct {
	OverallIndex    float64 `json:"overallIndex"`
	CollapseRisk    float64 `json:"collapseRisk"`
	SocialCohesion  float64 `json:"socialCohesion"`
	EconomicHealth  float64 `json:"economicHealth"`
	ParticipationRate float64 `json:"participationRate"`
	DataSufficient  bool    `json:"dataSufficient"`
}

// SimulationResult is the output of one simulation cycle.
type SimulationResult struct {
	CycleID        string           `json:"cycleId"`
	Citizens       int              `json:"citizenCount"`
	Observations   int              `json:"observationCount"`
	Posts          int              `json:"postCount"`
	Health         DemocraticHealth `json:"democraticHealth"`
	Timestamp      time.Time        `json:"timestamp"`
}

// activityTypes with risk levels and descriptions.
var activityTypes = []struct {
	Type        string
	Risk        string
	Description string
}{
	{"exercise", "LOW", "Running in the park"},
	{"exercise", "LOW", "Yoga session at home"},
	{"cooking", "LOW", "Preparing a healthy meal"},
	{"driving", "MEDIUM", "Commuting during rush hour"},
	{"heavy_lifting", "MEDIUM", "Moving boxes into building"},
	{"socializing", "LOW", "Meeting friends at cafe"},
	{"working", "LOW", "Focused desk work"},
	{"shopping", "LOW", "Grocery shopping"},
	{"fast_food", "HIGH", "Eating at fast food restaurant"},
	{"smoking", "HIGH", "Smoking outside building"},
	{"cycling", "MEDIUM", "Cycling without helmet"},
	{"gardening", "LOW", "Community garden maintenance"},
	{"volunteering", "LOW", "Helping at local shelter"},
	{"studying", "LOW", "Self-directed learning"},
	{"sports", "MEDIUM", "Playing basketball"},
}

// Simulator runs city simulation cycles.
type Simulator struct {
	rng *rand.Rand
}

// NewSimulator creates a city simulator.
func NewSimulator(seed int64) *Simulator {
	return &Simulator{rng: rand.New(rand.NewSource(seed))}
}

// RunCycle executes one simulation cycle: observe → generate posts → analyze.
func (s *Simulator) RunCycle(souls []soul.Soul) SimulationResult {
	cycleID := fmt.Sprintf("CYCLE-%06d", s.rng.Intn(999999))
	now := time.Now().UTC()

	observations := s.observe(souls)
	posts := s.generatePosts(observations, souls)
	health := s.analyze(posts, souls)

	return SimulationResult{
		CycleID:      cycleID,
		Citizens:     len(souls),
		Observations: len(observations),
		Posts:        len(posts),
		Health:       health,
		Timestamp:    now,
	}
}

// observe simulates robot observations of citizens.
func (s *Simulator) observe(souls []soul.Soul) []Observation {
	observations := make([]Observation, 0, len(souls))
	for _, citizen := range souls {
		act := activityTypes[s.rng.Intn(len(activityTypes))]
		obs := Observation{
			SessionID: fmt.Sprintf("SR-%06d", s.rng.Intn(999999)),
			CitizenID: citizen.CitizenID,
			Activity: Activity{
				Type:        act.Type,
				RiskLevel:   act.Risk,
				Description: act.Description,
				Timestamp:   time.Now().UTC(),
			},
			SensorData: map[string]float64{
				"confidence": 0.7 + s.rng.Float64()*0.3,
			},
		}
		observations = append(observations, obs)
	}
	return observations
}

// generatePosts creates SNS posts from observations.
func (s *Simulator) generatePosts(obs []Observation, souls []soul.Soul) []SNSPost {
	soulMap := make(map[string]soul.Soul, len(souls))
	for _, sl := range souls {
		soulMap[sl.CitizenID] = sl
	}
	posts := make([]SNSPost, 0, len(obs))
	for _, o := range obs {
		citizen, ok := soulMap[o.CitizenID]
		if !ok {
			continue
		}
		sentiment := (citizen.Emotions.Trust + citizen.Emotions.Altruism) / 2
		post := SNSPost{
			PostID:         fmt.Sprintf("POST-%06d", s.rng.Intn(999999)),
			CitizenID:      o.CitizenID,
			TextContent:    fmt.Sprintf("[%s] %s", citizen.Archetype, o.Activity.Description),
			Archetype:      string(citizen.Archetype),
			SentimentScore: sentiment,
			Timestamp:      time.Now().UTC(),
		}
		posts = append(posts, post)
	}
	return posts
}

// analyze computes democratic health from posts and population data.
func (s *Simulator) analyze(posts []SNSPost, souls []soul.Soul) DemocraticHealth {
	if len(posts) == 0 || len(souls) == 0 {
		return DemocraticHealth{DataSufficient: false}
	}

	var sentimentSum float64
	for _, p := range posts {
		sentimentSum += p.SentimentScore
	}
	avgSentiment := sentimentSum / float64(len(posts))

	var trustSum, altruismSum, ambitionSum float64
	for _, sl := range souls {
		trustSum += sl.Emotions.Trust
		altruismSum += sl.Emotions.Altruism
		ambitionSum += sl.Emotions.Ambition
	}
	n := float64(len(souls))

	socialCohesion := (trustSum/n + altruismSum/n) / 2
	economicHealth := ambitionSum / n
	participationRate := float64(len(posts)) / float64(len(souls))
	demIndex := avgSentiment*0.4 + socialCohesion*0.3 + economicHealth*0.2 + participationRate*0.1
	demIndex = math.Min(1.0, math.Max(0.0, demIndex))

	collapseRisk := 1.0 - demIndex

	return DemocraticHealth{
		OverallIndex:      demIndex,
		CollapseRisk:      collapseRisk,
		SocialCohesion:    socialCohesion,
		EconomicHealth:    economicHealth,
		ParticipationRate: participationRate,
		DataSufficient:    true,
	}
}

package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"time"

	"github.com/OpenOurMinds/ATA/internal/city"
	"github.com/OpenOurMinds/ATA/internal/decision"
	"github.com/OpenOurMinds/ATA/internal/soul"
)

type SimulationStepRecord struct {
	Timestep          string    `json:"timestep"`
	CycleID           string    `json:"cycleId"`
	Citizens          int       `json:"citizenCount"`
	Observations      int       `json:"observationCount"`
	Posts             int       `json:"postCount"`
	OverallIndex      float64   `json:"overallIndex"`
	CollapseRisk      float64   `json:"collapseRisk"`
	SocialCohesion    float64   `json:"socialCohesion"`
	EconomicHealth    float64   `json:"economicHealth"`
	ParticipationRate float64   `json:"participationRate"`
	TrustWeight       float64   `json:"trustWeight"`
	AltruismWeight    float64   `json:"altruismWeight"`
	AmbitionWeight    float64   `json:"ambitionWeight"`
	CuriosityWeight   float64   `json:"curiosityWeight"`
	FearWeight        float64   `json:"fearWeight"`
	DecisionsCount    int       `json:"decisionsCount"`
	Timestamp         time.Time `json:"timestamp"`
}

func main() {
	var (
		outputCSV  = flag.String("csv", "data/simulation_history_t1_t1000.csv", "Output CSV file path")
		outputJSON = flag.String("json", "data/simulation_history_t1_t1000.json", "Output JSON file path")
		seed       = flag.Int64("seed", 42, "Random seed for simulation")
		stepsCount = flag.Int("steps", 1000, "Number of simulation steps to run")
	)
	flag.Parse()

	fmt.Printf("🧬 Simulation Datafile Generator\n")
	fmt.Printf("===============================\n")
	fmt.Printf("Seed: %d\n", *seed)
	fmt.Printf("Steps: %d\n", *stepsCount)

	// Ensure output directory exists.
	if err := os.MkdirAll(filepath.Dir(*outputCSV), 0755); err != nil {
		fmt.Printf("Error creating output directory: %v\n", err)
		os.Exit(1)
	}

	// Initialize engines.
	rng := rand.New(rand.NewSource(*seed))
	soulGen := soul.NewGenerator(rng.Int63())
	sim := city.NewSimulator(rng.Int63())
	engine := decision.NewEngine(rng.Int63())
	params := decision.DefaultParameters()

	records := make([]SimulationStepRecord, 0, *stepsCount)

	fmt.Printf("Running simulation closed loop for %d steps...\n", *stepsCount)
	for t := 1; t <= *stepsCount; t++ {
		timestep := fmt.Sprintf("t%d", t)

		// 1. Generate souls.
		souls := soulGen.GeneratePopulation(params.SoulCount)

		// 2. Run simulation cycle.
		simResult := sim.RunCycle(souls)

		// 3. Evaluate decisions.
		decisions := engine.Evaluate(simResult.Health, params)

		// 4. Record state.
		record := SimulationStepRecord{
			Timestep:          timestep,
			CycleID:           simResult.CycleID,
			Citizens:          simResult.Citizens,
			Observations:      simResult.Observations,
			Posts:             simResult.Posts,
			OverallIndex:      simResult.Health.OverallIndex,
			CollapseRisk:      simResult.Health.CollapseRisk,
			SocialCohesion:    simResult.Health.SocialCohesion,
			EconomicHealth:    simResult.Health.EconomicHealth,
			ParticipationRate: simResult.Health.ParticipationRate,
			TrustWeight:       params.TrustWeight,
			AltruismWeight:    params.AltruismWeight,
			AmbitionWeight:    params.AmbitionWeight,
			CuriosityWeight:   params.CuriosityWeight,
			FearWeight:        params.FearWeight,
			DecisionsCount:    len(decisions),
			Timestamp:         time.Now().UTC(),
		}
		records = append(records, record)

		// 5. Optimize parameters.
		params = engine.OptimizeParameters(simResult.Health, params)
	}

	// Export to CSV.
	fmt.Printf("Exporting simulation data to CSV: %s...\n", *outputCSV)
	csvFile, err := os.Create(*outputCSV)
	if err != nil {
		fmt.Printf("Error creating CSV file: %v\n", err)
		os.Exit(1)
	}
	defer csvFile.Close()

	writer := csv.NewWriter(csvFile)
	defer writer.Flush()

	// Write header.
	header := []string{
		"timestep", "cycle_id", "citizens", "observations", "posts",
		"overall_index", "collapse_risk", "social_cohesion", "economic_health",
		"participation_rate", "trust_weight", "altruism_weight", "ambition_weight",
		"curiosity_weight", "fear_weight", "decisions_count",
	}
	if err := writer.Write(header); err != nil {
		fmt.Printf("Error writing CSV header: %v\n", err)
		os.Exit(1)
	}

	for _, r := range records {
		row := []string{
			r.Timestep,
			r.CycleID,
			fmt.Sprintf("%d", r.Citizens),
			fmt.Sprintf("%d", r.Observations),
			fmt.Sprintf("%d", r.Posts),
			fmt.Sprintf("%.6f", r.OverallIndex),
			fmt.Sprintf("%.6f", r.CollapseRisk),
			fmt.Sprintf("%.6f", r.SocialCohesion),
			fmt.Sprintf("%.6f", r.EconomicHealth),
			fmt.Sprintf("%.6f", r.ParticipationRate),
			fmt.Sprintf("%.6f", r.TrustWeight),
			fmt.Sprintf("%.6f", r.AltruismWeight),
			fmt.Sprintf("%.6f", r.AmbitionWeight),
			fmt.Sprintf("%.6f", r.CuriosityWeight),
			fmt.Sprintf("%.6f", r.FearWeight),
			fmt.Sprintf("%d", r.DecisionsCount),
		}
		if err := writer.Write(row); err != nil {
			fmt.Printf("Error writing CSV row: %v\n", err)
			os.Exit(1)
		}
	}

	// Export to JSON.
	fmt.Printf("Exporting simulation data to JSON: %s...\n", *outputJSON)
	jsonFile, err := os.Create(*outputJSON)
	if err != nil {
		fmt.Printf("Error creating JSON file: %v\n", err)
		os.Exit(1)
	}
	defer jsonFile.Close()

	encoder := json.NewEncoder(jsonFile)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(records); err != nil {
		fmt.Printf("Error encoding JSON: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("✅ Success! Simulation data generated successfully!\n")
}

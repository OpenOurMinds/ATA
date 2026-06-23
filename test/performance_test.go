package test

import (
	"encoding/json"
	"io"
	"log/slog"
	"math"
	"net/http/httptest"
	"os"
	"runtime"
	"testing"
	"time"

	"github.com/OpenOurMinds/ATA/internal/a2a"
	"github.com/OpenOurMinds/ATA/internal/city"
	"github.com/OpenOurMinds/ATA/internal/decision"
	"github.com/OpenOurMinds/ATA/internal/soul"
)

type ScaleResult struct {
	PopulationSize  int     `json:"populationSize"`
	GenerationTimeMS float64 `json:"generationTimeMs"`
	SimulationTimeMS float64 `json:"simulationTimeMs"`
	ClosedLoopTimeMS float64 `json:"closedLoopTimeMs"`
	AllocatedMB      float64 `json:"allocatedMb"`
	GCRuns           uint32  `json:"gcRuns"`
}

type SimulationStats struct {
	AvgDemocraticIndex float64 `json:"avgDemocraticIndex"`
	StdDemocraticIndex float64 `json:"stdDemocraticIndex"`
	AvgCollapseRisk    float64 `json:"avgCollapseRisk"`
	StdCollapseRisk    float64 `json:"stdCollapseRisk"`
}

type PerformanceReport struct {
	Timestamp       string          `json:"timestamp"`
	GoVersion       string          `json:"goVersion"`
	Scalability     []ScaleResult   `json:"scalability"`
	RandomSimStats  SimulationStats `json:"randomSimStats"`
	DatasetSimStats SimulationStats `json:"datasetSimStats"`
}

func TestPerformance(t *testing.T) {
	t.Log("Starting comprehensive Performance Evaluation...")

	demographicsPath := "../data/demographics_source.csv"
	sentimentPath := "../data/social_media_sentiment.csv"

	// 1. Scalability Benchmarking
	scales := []int{50, 100, 500, 1000, 5000}
	var results []ScaleResult

	for _, size := range scales {
		// Run GC to normalize memory measurements
		runtime.GC()
		var memBefore, memAfter runtime.MemStats
		runtime.ReadMemStats(&memBefore)

		// A. Generation Phase
		startGen := time.Now()
		gen := soul.NewGenerator(42)
		_ = gen.LoadDemographics(demographicsPath)
		souls := gen.GeneratePopulation(size)
		genTime := time.Since(startGen)

		// B. Simulation Phase
		startSim := time.Now()
		sim := city.NewSimulator(42)
		_ = sim.LoadSentimentData(sentimentPath)
		result := sim.RunCycle(souls)
		simTime := time.Since(startSim)

		// C. Decision & Optimisation Phase (Full Closed Loop)
		startLoop := time.Now()
		engine := decision.NewEngine(42)
		params := decision.DefaultParameters()
		decisions := engine.Evaluate(result.Health, params)
		_ = engine.OptimizeParameters(result.Health, params)
		loopTime := time.Since(startLoop)

		runtime.ReadMemStats(&memAfter)

		allocMB := float64(memAfter.TotalAlloc-memBefore.TotalAlloc) / (1024 * 1024)
		if allocMB < 0 {
			allocMB = 0 // handle GC cleanups during execution
		}

		results = append(results, ScaleResult{
			PopulationSize:  size,
			GenerationTimeMS: float64(genTime.Microseconds()) / 1000.0,
			SimulationTimeMS: float64(simTime.Microseconds()) / 1000.0,
			ClosedLoopTimeMS: float64((genTime + simTime + loopTime).Microseconds()) / 1000.0,
			AllocatedMB:      allocMB,
			GCRuns:           memAfter.NumGC - memBefore.NumGC,
		})

		t.Logf("Population Size %d: Gen=%.2fms, Sim=%.2fms, ClosedLoop=%.2fms, Alloc=%.2fMB, Decisions=%d",
			size, float64(genTime.Microseconds())/1000.0, float64(simTime.Microseconds())/1000.0,
			float64((genTime+simTime+loopTime).Microseconds())/1000.0, allocMB, len(decisions))
	}

	// 2. Statistical Simulation Comparison: Random vs Dataset-Driven
	steps := 100
	var randomDemIndices []float64
	var randomCollapseRisks []float64

	// Random (Default procedural fallback)
	genRand := soul.NewGenerator(101)
	simRand := city.NewSimulator(101)
	for i := 0; i < steps; i++ {
		souls := genRand.GeneratePopulation(100)
		res := simRand.RunCycle(souls)
		randomDemIndices = append(randomDemIndices, res.Health.OverallIndex)
		randomCollapseRisks = append(randomCollapseRisks, res.Health.CollapseRisk)
	}

	var datasetDemIndices []float64
	var datasetCollapseRisks []float64

	// Dataset-Driven
	genData := soul.NewGenerator(101)
	_ = genData.LoadDemographics(demographicsPath)
	simData := city.NewSimulator(101)
	_ = simData.LoadSentimentData(sentimentPath)

	for i := 0; i < steps; i++ {
		souls := genData.GeneratePopulation(100)
		res := simData.RunCycle(souls)
		datasetDemIndices = append(datasetDemIndices, res.Health.OverallIndex)
		datasetCollapseRisks = append(datasetCollapseRisks, res.Health.CollapseRisk)
	}

	randAvgDem, randStdDem := calcStats(randomDemIndices)
	randAvgCol, randStdCol := calcStats(randomCollapseRisks)

	dataAvgDem, dataStdDem := calcStats(datasetDemIndices)
	dataAvgCol, dataStdCol := calcStats(datasetCollapseRisks)

	t.Logf("Random Simulation (100 steps): Democratic Index Avg=%.4f (Std=%.4f), Collapse Risk Avg=%.4f (Std=%.4f)",
		randAvgDem, randStdDem, randAvgCol, randStdCol)
	t.Logf("Dataset Simulation (100 steps): Democratic Index Avg=%.4f (Std=%.4f), Collapse Risk Avg=%.4f (Std=%.4f)",
		dataAvgDem, dataStdDem, dataAvgCol, dataStdCol)

	// Save performance report
	report := PerformanceReport{
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		GoVersion: runtime.Version(),
		Scalability: results,
		RandomSimStats: SimulationStats{
			AvgDemocraticIndex: randAvgDem,
			StdDemocraticIndex: randStdDem,
			AvgCollapseRisk:    randAvgCol,
			StdCollapseRisk:    randStdCol,
		},
		DatasetSimStats: SimulationStats{
			AvgDemocraticIndex: dataAvgDem,
			StdDemocraticIndex: dataStdDem,
			AvgCollapseRisk:    dataAvgCol,
			StdCollapseRisk:    dataStdCol,
		},
	}

	reportFile, err := os.Create("../data/performance_report.json")
	if err != nil {
		t.Fatalf("Failed to create performance report file: %v", err)
	}
	defer reportFile.Close()

	encoder := json.NewEncoder(reportFile)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(report); err != nil {
		t.Fatalf("Failed to write performance report: %v", err)
	}

	t.Log("Successfully exported report to data/performance_report.json")
}

// calcStats calculates the average and standard deviation of values
func calcStats(values []float64) (float64, float64) {
	if len(values) == 0 {
		return 0, 0
	}
	var sum float64
	for _, v := range values {
		sum += v
	}
	mean := sum / float64(len(values))

	var varianceSum float64
	for _, v := range values {
		varianceSum += math.Pow(v-mean, 2)
	}
	variance := varianceSum / float64(len(values))
	stdDev := math.Sqrt(variance)
	return mean, stdDev
}

// ═══════════════════════════════════════════════════════════════════
// GO BENCHMARKS
// ═══════════════════════════════════════════════════════════════════

func BenchmarkSoulGeneration_Random(b *testing.B) {
	gen := soul.NewGenerator(42)
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = gen.GeneratePopulation(50)
	}
}

func BenchmarkSoulGeneration_Dataset(b *testing.B) {
	gen := soul.NewGenerator(42)
	err := gen.LoadDemographics("../data/demographics_source.csv")
	if err != nil {
		b.Fatalf("load failed: %v", err)
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = gen.GeneratePopulation(50)
	}
}

func BenchmarkCitySimulation_Random(b *testing.B) {
	gen := soul.NewGenerator(42)
	souls := gen.GeneratePopulation(50)
	sim := city.NewSimulator(42)
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = sim.RunCycle(souls)
	}
}

func BenchmarkCitySimulation_Dataset(b *testing.B) {
	gen := soul.NewGenerator(42)
	_ = gen.LoadDemographics("../data/demographics_source.csv")
	souls := gen.GeneratePopulation(50)

	sim := city.NewSimulator(42)
	_ = sim.LoadSentimentData("../data/social_media_sentiment.csv")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = sim.RunCycle(souls)
	}
}

func BenchmarkFullClosedLoop_Dataset(b *testing.B) {
	gen := soul.NewGenerator(42)
	_ = gen.LoadDemographics("../data/demographics_source.csv")
	sim := city.NewSimulator(42)
	_ = sim.LoadSentimentData("../data/social_media_sentiment.csv")
	engine := decision.NewEngine(42)
	params := decision.DefaultParameters()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		souls := gen.GeneratePopulation(50)
		res := sim.RunCycle(souls)
		_ = engine.Evaluate(res.Health, params)
		_ = engine.OptimizeParameters(res.Health, params)
	}
}

func BenchmarkFullClosedLoop_Network(b *testing.B) {
	logger := slog.New(slog.NewTextHandler(io.Discard, nil))

	// Setup soul agent server
	gen := soul.NewGenerator(42)
	_ = gen.LoadDemographics("../data/demographics_source.csv")
	soulCard := a2a.NewAgentCard("Soul", "", "", "1.0", []a2a.Skill{{ID: "generate"}})
	soulServer := a2a.NewServer(soulCard, logger)
	soulServer.RegisterHandler(a2a.MethodMessageSend, func(params json.RawMessage) (interface{}, *a2a.RPCError) {
		souls := gen.GeneratePopulation(50)
		task := &a2a.Task{
			ID:        "task-1",
			SessionID: "session-1",
			State:     a2a.TaskStateCompleted,
		}
		task.AddArtifact("souls", []a2a.Part{a2a.NewDataPart(souls)})
		return a2a.TaskResultFromTask(task), nil
	})
	tsSoul := httptest.NewServer(soulServer.Handler())
	defer tsSoul.Close()

	// Setup city agent server
	sim := city.NewSimulator(42)
	_ = sim.LoadSentimentData("../data/social_media_sentiment.csv")
	cityCard := a2a.NewAgentCard("City", "", "", "1.0", []a2a.Skill{{ID: "simulate"}})
	cityServer := a2a.NewServer(cityCard, logger)
	cityServer.RegisterHandler(a2a.MethodMessageSend, func(params json.RawMessage) (interface{}, *a2a.RPCError) {
		souls := gen.GeneratePopulation(50)
		result := sim.RunCycle(souls)
		task := &a2a.Task{
			ID:        "task-2",
			SessionID: "session-2",
			State:     a2a.TaskStateCompleted,
		}
		task.AddArtifact("simulation_result", []a2a.Part{a2a.NewDataPart(result)})
		return a2a.TaskResultFromTask(task), nil
	})
	tsCity := httptest.NewServer(cityServer.Handler())
	defer tsCity.Close()

	client := a2a.NewClient(logger)
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = client.SendMessage(tsSoul.URL, a2a.MessageSendParams{})
		_, _ = client.SendMessage(tsCity.URL, a2a.MessageSendParams{})
	}
}

func BenchmarkFullClosedLoop_InProcess(b *testing.B) {
	logger := slog.New(slog.NewTextHandler(io.Discard, nil))

	// Setup soul agent server
	gen := soul.NewGenerator(42)
	_ = gen.LoadDemographics("../data/demographics_source.csv")
	soulCard := a2a.NewAgentCard("Soul", "", "", "1.0", []a2a.Skill{{ID: "generate"}})
	soulServer := a2a.NewServer(soulCard, logger)
	soulServer.RegisterHandler(a2a.MethodMessageSend, func(params json.RawMessage) (interface{}, *a2a.RPCError) {
		souls := gen.GeneratePopulation(50)
		task := &a2a.Task{
			ID:        "task-1",
			SessionID: "session-1",
			State:     a2a.TaskStateCompleted,
		}
		task.AddArtifact("souls", []a2a.Part{a2a.NewDataPart(souls)})
		return a2a.TaskResultFromTask(task), nil
	})

	// Setup city agent server
	sim := city.NewSimulator(42)
	_ = sim.LoadSentimentData("../data/social_media_sentiment.csv")
	cityCard := a2a.NewAgentCard("City", "", "", "1.0", []a2a.Skill{{ID: "simulate"}})
	cityServer := a2a.NewServer(cityCard, logger)
	cityServer.RegisterHandler(a2a.MethodMessageSend, func(params json.RawMessage) (interface{}, *a2a.RPCError) {
		souls := gen.GeneratePopulation(50)
		result := sim.RunCycle(souls)
		task := &a2a.Task{
			ID:        "task-2",
			SessionID: "session-2",
			State:     a2a.TaskStateCompleted,
		}
		task.AddArtifact("simulation_result", []a2a.Part{a2a.NewDataPart(result)})
		return a2a.TaskResultFromTask(task), nil
	})

	client := a2a.NewClient(logger)
	client.RegisterLocalRoute("http://local-soul", soulServer.Handler())
	client.RegisterLocalRoute("http://local-city", cityServer.Handler())

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = client.SendMessage("http://local-soul", a2a.MessageSendParams{})
		_, _ = client.SendMessage("http://local-city", a2a.MessageSendParams{})
	}
}

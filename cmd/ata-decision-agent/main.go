// ata-decision-agent evaluates democratic health metrics
// and produces optimized parameters via the A2A protocol.
package main

import (
	"encoding/json"
	"flag"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/OpenOurMinds/ATA/internal/a2a"
	"github.com/OpenOurMinds/ATA/internal/city"
	"github.com/OpenOurMinds/ATA/internal/decision"
	"github.com/OpenOurMinds/ATA/internal/observability"
	"github.com/OpenOurMinds/ATA/internal/storage"
)

var version = "dev"

func main() {
	var (
		listenAddr = flag.String("listen", ":8083", "Listen address")
		dbPath     = flag.String("db", "data/decisions.db", "BoltDB database path")
		cityDB     = flag.String("city-db", "data/city.db", "City database for reading metrics")
	)
	flag.Parse()

	logger := observability.NewLogger("ata-decision-agent", slog.LevelInfo)
	logger.Info("starting decision agent", "version", version, "addr", *listenAddr)

	store, err := storage.Open(*dbPath)
	if err != nil {
		logger.Error("failed to open database", "error", err)
		os.Exit(1)
	}
	defer store.Close()

	engine := decision.NewEngine(time.Now().UnixNano())
	params := decision.DefaultParameters()

	card := a2a.NewAgentCard(
		"ATA Decision Agent",
		"Evaluates democratic health and optimizes system parameters",
		"http://127.0.0.1"+*listenAddr,
		version,
		[]a2a.Skill{
			{ID: "evaluate", Name: "Evaluate & Optimize", Description: "Evaluate health metrics and produce optimized parameters"},
		},
	)

	server := a2a.NewServer(card, logger)

	server.RegisterHandler(a2a.MethodMessageSend, func(raw json.RawMessage) (interface{}, *a2a.RPCError) {
		var p a2a.MessageSendParams
		if err := json.Unmarshal(raw, &p); err != nil {
			return nil, &a2a.RPCError{Code: a2a.ErrCodeInvalidParams, Message: err.Error()}
		}

		taskID := a2a.NewTaskID()
		task, err := server.Tasks().Create(taskID)
		if err != nil {
			return nil, &a2a.RPCError{Code: a2a.ErrCodeInvalidParams, Message: err.Error()}
		}
		task.Messages = append(task.Messages, p.Message)
		task.TransitionTo(a2a.TaskStateWorking, "reading metrics")

		// Read latest metrics from city DB.
		var latestHealth city.DemocraticHealth
		cityStore, err := storage.Open(*cityDB)
		if err != nil {
			task.TransitionTo(a2a.TaskStateFailed, "cannot open city db")
			return a2a.TaskResultFromTask(task), nil
		}

		var latestResult city.SimulationResult
		cityStore.ForEach(storage.BucketMetrics, func(key string, value []byte) error {
			var r city.SimulationResult
			if err := json.Unmarshal(value, &r); err == nil {
				if r.Timestamp.After(latestResult.Timestamp) {
					latestResult = r
				}
			}
			return nil
		})
		cityStore.Close()
		latestHealth = latestResult.Health

		// Evaluate rules.
		decisions := engine.Evaluate(latestHealth, params)
		logger.Info("decisions made", "count", len(decisions), "demIndex", latestHealth.OverallIndex)

		// Optimize parameters.
		params = engine.OptimizeParameters(latestHealth, params)

		// Persist decisions.
		for _, d := range decisions {
			store.Put(storage.BucketDecisions, d.ID, d)
		}
		store.Put(storage.BucketMetrics, "current_params", params)

		task.AddArtifact("decisions", []a2a.Part{a2a.NewDataPart(map[string]interface{}{
			"decisions":         decisions,
			"optimizedParams":   params,
			"democraticHealth":  latestHealth,
		})})
		task.TransitionTo(a2a.TaskStateCompleted, "evaluation completed")

		return a2a.TaskResultFromTask(task), nil
	})

	go func() {
		if err := http.ListenAndServe(*listenAddr, server.Handler()); err != nil {
			logger.Error("server failed", "error", err)
			os.Exit(1)
		}
	}()

	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
	<-sig
	logger.Info("decision agent shutting down")
}

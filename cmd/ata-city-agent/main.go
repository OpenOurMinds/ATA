// ata-city-agent is the virtual city simulation agent.
// It receives souls, runs simulation cycles, and produces
// democratic health metrics via the A2A protocol.
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
	"github.com/OpenOurMinds/ATA/internal/observability"
	"github.com/OpenOurMinds/ATA/internal/soul"
	"github.com/OpenOurMinds/ATA/internal/storage"
)

var version = "dev"

func main() {
	var (
		listenAddr = flag.String("listen", ":8082", "Listen address")
		dbPath     = flag.String("db", "data/city.db", "BoltDB database path")
		soulsDB    = flag.String("souls-db", "data/souls.db", "Souls database path for reading")
	)
	flag.Parse()

	logger := observability.NewLogger("ata-city-agent", slog.LevelInfo)
	logger.Info("starting city agent", "version", version, "addr", *listenAddr)

	store, err := storage.Open(*dbPath)
	if err != nil {
		logger.Error("failed to open database", "error", err)
		os.Exit(1)
	}
	defer store.Close()

	sim := city.NewSimulator(time.Now().UnixNano())

	card := a2a.NewAgentCard(
		"ATA City Agent",
		"Runs virtual city simulations and produces democratic health metrics",
		"http://127.0.0.1"+*listenAddr,
		version,
		[]a2a.Skill{
			{ID: "simulate", Name: "Run Simulation", Description: "Execute one city simulation cycle"},
		},
	)

	server := a2a.NewServer(card, logger)

	server.RegisterHandler(a2a.MethodMessageSend, func(params json.RawMessage) (interface{}, *a2a.RPCError) {
		var p a2a.MessageSendParams
		if err := json.Unmarshal(params, &p); err != nil {
			return nil, &a2a.RPCError{Code: a2a.ErrCodeInvalidParams, Message: err.Error()}
		}

		taskID := a2a.NewTaskID()
		task, err := server.Tasks().Create(taskID)
		if err != nil {
			return nil, &a2a.RPCError{Code: a2a.ErrCodeInvalidParams, Message: err.Error()}
		}
		task.Messages = append(task.Messages, p.Message)
		task.TransitionTo(a2a.TaskStateWorking, "loading souls")

		// Load souls from shared DB.
		var souls []soul.Soul
		soulsStore, err := storage.Open(*soulsDB)
		if err != nil {
			task.TransitionTo(a2a.TaskStateFailed, "cannot open souls db: "+err.Error())
			return a2a.TaskResultFromTask(task), nil
		}
		soulsStore.ForEach(storage.BucketSouls, func(key string, value []byte) error {
			var s soul.Soul
			if err := json.Unmarshal(value, &s); err == nil {
				souls = append(souls, s)
			}
			return nil
		})
		soulsStore.Close()

		if len(souls) == 0 {
			task.TransitionTo(a2a.TaskStateFailed, "no souls available")
			return a2a.TaskResultFromTask(task), nil
		}

		// Run simulation.
		result := sim.RunCycle(souls)
		logger.Info("simulation completed",
			"citizens", result.Citizens,
			"observations", result.Observations,
			"demIndex", result.Health.OverallIndex,
		)

		// Persist result.
		store.Put(storage.BucketMetrics, result.CycleID, result)

		task.AddArtifact("simulation_result", []a2a.Part{a2a.NewDataPart(result)})
		task.TransitionTo(a2a.TaskStateCompleted, "simulation completed")

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
	logger.Info("city agent shutting down")
}

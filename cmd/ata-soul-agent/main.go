// ata-soul-agent is the Digital Soul generation agent.
// It exposes an A2A endpoint for generating synthetic populations.
package main

import (
	"encoding/json"
	"flag"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/OpenOurMinds/ATA/internal/a2a"
	"github.com/OpenOurMinds/ATA/internal/observability"
	"github.com/OpenOurMinds/ATA/internal/soul"
	"github.com/OpenOurMinds/ATA/internal/storage"
)

var version = "dev"

func main() {
	var (
		listenAddr = flag.String("listen", ":8081", "Listen address")
		dbPath     = flag.String("db", "data/souls.db", "BoltDB database path")
	)
	flag.Parse()

	logger := observability.NewLogger("ata-soul-agent", slog.LevelInfo)
	logger.Info("starting soul agent", "version", version, "addr", *listenAddr)

	// Open storage.
	store, err := storage.Open(*dbPath)
	if err != nil {
		logger.Error("failed to open database", "error", err)
		os.Exit(1)
	}
	defer store.Close()

	gen := soul.NewGenerator(time.Now().UnixNano())

	// Build Agent Card.
	card := a2a.NewAgentCard(
		"ATA Soul Agent",
		"Generates synthetic Digital Soul populations with cryptographic identities",
		"http://127.0.0.1"+*listenAddr,
		version,
		[]a2a.Skill{
			{ID: "generate", Name: "Generate Souls", Description: "Generate a population of digital souls"},
		},
	)

	server := a2a.NewServer(card, logger)

	// Register message/send handler.
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
		task.TransitionTo(a2a.TaskStateWorking, "generating souls")

		// Parse count from message (default 50).
		count := 50
		for _, part := range p.Message.Parts {
			if part.Type == "data" {
				if m, ok := part.Data.(map[string]interface{}); ok {
					if c, ok := m["count"]; ok {
						if ci, err := strconv.Atoi(toString(c)); err == nil {
							count = ci
						}
					}
				}
			}
		}

		souls := gen.GeneratePopulation(count)

		// Persist to BoltDB.
		for _, s := range souls {
			if err := store.Put(storage.BucketSouls, s.DigitalSoulHash, s); err != nil {
				logger.Error("failed to persist soul", "hash", s.DigitalSoulHash, "error", err)
			}
		}

		logger.Info("generated souls", "count", len(souls))
		task.AddArtifact("souls", []a2a.Part{a2a.NewDataPart(map[string]interface{}{
			"count":  len(souls),
			"stored": true,
		})})
		task.TransitionTo(a2a.TaskStateCompleted, "generated")

		return a2a.TaskResultFromTask(task), nil
	})

	// Serve.
	go func() {
		if err := http.ListenAndServe(*listenAddr, server.Handler()); err != nil {
			logger.Error("server failed", "error", err)
			os.Exit(1)
		}
	}()

	// Wait for shutdown signal.
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
	<-sig
	logger.Info("soul agent shutting down")
}

func toString(v interface{}) string {
	switch t := v.(type) {
	case string:
		return t
	case float64:
		return strconv.FormatFloat(t, 'f', 0, 64)
	default:
		return ""
	}
}

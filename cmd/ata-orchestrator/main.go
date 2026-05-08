// ata-orchestrator is the master daemon that drives the closed-loop
// autonomous simulation. It coordinates soul, city, and decision agents
// via the A2A protocol, feeding optimized parameters back into each cycle.
package main

import (
	"context"
	"encoding/json"
	"flag"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/OpenOurMinds/ATA/internal/a2a"
	"github.com/OpenOurMinds/ATA/internal/observability"
)

var version = "dev"

func main() {
	var (
		soulAgentURL     = flag.String("soul-url", "http://127.0.0.1:8081", "Soul agent A2A endpoint")
		cityAgentURL     = flag.String("city-url", "http://127.0.0.1:8082", "City agent A2A endpoint")
		decisionAgentURL = flag.String("decision-url", "http://127.0.0.1:8083", "Decision agent A2A endpoint")
		cycleInterval    = flag.Duration("cycle-interval", 60*time.Second, "Time between autonomous cycles")
		listenAddr       = flag.String("listen", ":8080", "Orchestrator listen address")
	)
	flag.Parse()

	logger := observability.NewLogger("ata-orchestrator", slog.LevelInfo)
	logger.Info("starting orchestrator",
		"version", version,
		"soulAgent", *soulAgentURL,
		"cityAgent", *cityAgentURL,
		"decisionAgent", *decisionAgentURL,
		"cycleInterval", cycleInterval.String(),
	)

	// Build Agent Card for orchestrator.
	card := a2a.NewAgentCard(
		"ATA Orchestrator",
		"Master daemon coordinating the ATA multi-agent autonomous loop",
		"http://127.0.0.1"+*listenAddr,
		version,
		[]a2a.Skill{
			{ID: "orchestrate", Name: "Orchestrate Cycle", Description: "Run a complete soul→city→decision cycle"},
			{ID: "status", Name: "System Status", Description: "Report system-wide status"},
		},
	)

	// Create A2A server and client.
	server := a2a.NewServer(card, logger)
	client := a2a.NewClient(logger)

	// Register the orchestrate handler.
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
		task.TransitionTo(a2a.TaskStateWorking, "starting cycle")

		// Run one orchestration cycle.
		err := runCycle(client, *soulAgentURL, *cityAgentURL, *decisionAgentURL, logger)
		if err != nil {
			task.TransitionTo(a2a.TaskStateFailed, err.Error())
			return a2a.TaskResultFromTask(task), nil
		}

		task.TransitionTo(a2a.TaskStateCompleted, "cycle completed")
		return a2a.TaskResultFromTask(task), nil
	})

	// Start HTTP server in background.
	go func() {
		logger.Info("serving A2A endpoint", "addr", *listenAddr)
		if err := http.ListenAndServe(*listenAddr, server.Handler()); err != nil {
			logger.Error("http server failed", "error", err)
			os.Exit(1)
		}
	}()

	// Autonomous loop.
	ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer cancel()

	ticker := time.NewTicker(*cycleInterval)
	defer ticker.Stop()

	logger.Info("autonomous loop started")
	for {
		select {
		case <-ctx.Done():
			logger.Info("shutting down orchestrator")
			return
		case <-ticker.C:
			if err := runCycle(client, *soulAgentURL, *cityAgentURL, *decisionAgentURL, logger); err != nil {
				logger.Error("cycle failed", "error", err)
			} else {
				logger.Info("cycle completed successfully")
			}
		}
	}
}

// runCycle executes one soul→city→decision A2A cycle.
func runCycle(client *a2a.Client, soulURL, cityURL, decisionURL string, logger *slog.Logger) error {
	logger.Info("cycle: requesting soul generation")
	_, err := client.SendMessage(soulURL, a2a.MessageSendParams{
		Message: a2a.NewMessage(a2a.RoleUser, a2a.NewTextPart("generate 50 souls")),
	})
	if err != nil {
		return err
	}

	logger.Info("cycle: requesting city simulation")
	_, err = client.SendMessage(cityURL, a2a.MessageSendParams{
		Message: a2a.NewMessage(a2a.RoleUser, a2a.NewTextPart("run simulation cycle")),
	})
	if err != nil {
		return err
	}

	logger.Info("cycle: requesting decision evaluation")
	_, err = client.SendMessage(decisionURL, a2a.MessageSendParams{
		Message: a2a.NewMessage(a2a.RoleUser, a2a.NewTextPart("evaluate and optimize")),
	})
	if err != nil {
		return err
	}

	return nil
}



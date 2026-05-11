// Package observability provides structured logging and metrics.
// Replaces all print(), emoji logging, and Rich terminal output
// with machine-readable structured JSON logs via log/slog.
package observability

import (
	"log/slog"
	"os"
)

// NewLogger creates a structured JSON logger writing to stdout.
// This output is consumed by journald when running under systemd.
func NewLogger(serviceName string, level slog.Level) *slog.Logger {
	handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: level,
	})
	return slog.New(handler).With("service", serviceName)
}

// Metrics tracks operational counters for the agent.
type Metrics struct {
	TasksSubmitted  int64 `json:"tasksSubmitted"`
	TasksCompleted  int64 `json:"tasksCompleted"`
	TasksFailed     int64 `json:"tasksFailed"`
	MessagesRouted  int64 `json:"messagesRouted"`
	CyclesCompleted int64 `json:"cyclesCompleted"`
	SoulsGenerated  int64 `json:"soulsGenerated"`
	DecisionsMade   int64 `json:"decisionsMade"`
	UptimeSeconds   int64 `json:"uptimeSeconds"`
}

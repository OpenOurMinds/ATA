package a2a

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"strings"
	"time"

	"github.com/google/uuid"
)

// Handler processes A2A JSON-RPC requests for a specific method.
type Handler func(params json.RawMessage) (interface{}, *RPCError)

// StreamHandler processes A2A JSON-RPC requests that emit SSE events.
type StreamHandler func(params json.RawMessage, events chan<- SSEEvent)

// SSEEvent is a Server-Sent Event payload for message/stream.
type SSEEvent struct {
	Event string      `json:"event"` // "status", "artifact", "error", "done"
	Data  interface{} `json:"data"`
}

// AuthMiddleware validates incoming requests.
// Returns nil if authorized, or an RPCError if rejected.
type AuthMiddleware func(r *http.Request) *RPCError

// PushNotificationConfig holds webhook configuration for async task updates.
type PushNotificationConfig struct {
	URL     string            `json:"url"`
	Headers map[string]string `json:"headers,omitempty"`
	Token   string            `json:"token,omitempty"`
}

// PushNotificationConfigParams for tasks/pushNotificationConfig/set.
type PushNotificationConfigParams struct {
	TaskID string                 `json:"id"`
	Config PushNotificationConfig `json:"pushNotificationConfig"`
}

// Server is an A2A-compliant HTTP server that routes JSON-RPC requests.
type Server struct {
	card           AgentCard
	tasks          *TaskStore
	handlers       map[string]Handler
	streamHandlers map[string]StreamHandler
	auth           AuthMiddleware
	pushConfigs    map[string]PushNotificationConfig // taskID → webhook
	requireHTTPS   bool
	scanIncoming   bool     // Enable semantic guardrail scanning.
	stripPII        bool     // Enable PII redaction on outbound messages.
	toolACL        *ToolACL // Zero-trust tool access control.
	logger         *slog.Logger
	mux            *http.ServeMux
}

// NewServer creates an A2A server with the given Agent Card.
func NewServer(card AgentCard, logger *slog.Logger) *Server {
	s := &Server{
		card:           card,
		tasks:          NewTaskStore(),
		handlers:       make(map[string]Handler),
		streamHandlers: make(map[string]StreamHandler),
		pushConfigs:    make(map[string]PushNotificationConfig),
		logger:         logger,
		mux:            http.NewServeMux(),
	}

	// Serve Agent Card at spec-correct well-known path.
	s.mux.HandleFunc("GET /.well-known/agent-card.json", s.handleAgentCard)
	// Also serve at legacy path for backward compatibility.
	s.mux.HandleFunc("GET /.well-known/agent.json", s.handleAgentCard)

	// A2A JSON-RPC endpoint.
	s.mux.HandleFunc("POST /", s.handleRPC)

	// Health check.
	s.mux.HandleFunc("GET /healthz", s.handleHealth)

	// Register default task handlers.
	s.handlers[MethodTasksGet] = s.handleTasksGet
	s.handlers[MethodTasksCancel] = s.handleTasksCancel
	s.handlers[MethodPushNotifConfigSet] = s.handlePushNotifConfigSet
	s.handlers[MethodPushNotifConfigGet] = s.handlePushNotifConfigGet

	return s
}

// SetAuth installs an authentication middleware.
// When set, every incoming request is validated before routing.
func (s *Server) SetAuth(auth AuthMiddleware) {
	s.auth = auth
}

// SetRequireHTTPS enforces HTTPS-only connections.
// When enabled, plain HTTP requests are rejected with 403.
func (s *Server) SetRequireHTTPS(require bool) {
	s.requireHTTPS = require
}

// EnableGuardrails turns on semantic scanning and PII stripping.
func (s *Server) EnableGuardrails(scanIncoming, stripPII bool) {
	s.scanIncoming = scanIncoming
	s.stripPII = stripPII
}

// SetToolACL installs a zero-trust tool access control list.
func (s *Server) SetToolACL(acl *ToolACL) {
	s.toolACL = acl
}

// SkillAuthorized checks if the given skill ID is listed in this agent's card.
// Returns false if the skill is not advertised, preventing unauthorized tool access.
func (s *Server) SkillAuthorized(skillID string) bool {
	for _, skill := range s.card.Skills {
		if skill.ID == skillID {
			return true
		}
	}
	return false
}

// RegisterHandler registers a synchronous handler for an A2A method.
func (s *Server) RegisterHandler(method string, h Handler) {
	s.handlers[method] = h
}

// RegisterStreamHandler registers a streaming handler for an A2A method.
// The handler emits SSEEvent values to the channel; the server writes them
// as text/event-stream to the client.
func (s *Server) RegisterStreamHandler(method string, h StreamHandler) {
	s.streamHandlers[method] = h
}

// Tasks returns the task store for external access.
func (s *Server) Tasks() *TaskStore {
	return s.tasks
}

// Handler returns the HTTP handler for this server.
func (s *Server) Handler() http.Handler {
	return s.mux
}

// handleAgentCard serves the Agent Card JSON.
func (s *Server) handleAgentCard(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "public, max-age=3600")
	b, _ := json.MarshalIndent(s.card, "", "  ")
	w.Write(b)
}

// handleHealth returns 200 OK with operational metadata.
func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":    "ok",
		"agent":     s.card.Name,
		"version":   s.card.Version,
		"tasks":     s.tasks.Count(),
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	})
}

// handleRPC processes incoming JSON-RPC 2.0 requests.
// Routes to synchronous handlers or SSE stream handlers.
func (s *Server) handleRPC(w http.ResponseWriter, r *http.Request) {
	// HTTPS enforcement: reject plain HTTP in production.
	if s.requireHTTPS && r.TLS == nil && r.Header.Get("X-Forwarded-Proto") != "https" {
		w.WriteHeader(http.StatusForbidden)
		s.writeResponse(w, ErrorResponse(nil, ErrCodeAuthRequired, "HTTPS required"))
		return
	}

	// Auth check.
	if s.auth != nil {
		if rpcErr := s.auth(r); rpcErr != nil {
			s.writeResponse(w, Response{JSONRPC: JSONRPCVersion, Error: rpcErr})
			return
		}
	}

	var req Request
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		s.writeResponse(w, ErrorResponse(nil, ErrCodeParseError, "parse error"))
		return
	}

	if err := req.Validate(); err != nil {
		s.writeResponse(w, ErrorResponse(req.ID, ErrCodeInvalidRequest, err.Error()))
		return
	}

	s.logger.Info("rpc request", "method", req.Method, "id", req.ID)

	// Check for SSE stream handler first.
	if streamHandler, ok := s.streamHandlers[req.Method]; ok {
		s.handleSSE(w, r, req, streamHandler)
		return
	}

	// Synchronous handler.
	handler, ok := s.handlers[req.Method]
	if !ok {
		s.writeResponse(w, ErrorResponse(req.ID, ErrCodeMethodNotFound,
			fmt.Sprintf("method %q not found", req.Method)))
		return
	}

	result, rpcErr := handler(req.Params)
	if rpcErr != nil {
		s.writeResponse(w, Response{
			JSONRPC: JSONRPCVersion,
			Error:   rpcErr,
			ID:      req.ID,
		})
		return
	}

	s.writeResponse(w, SuccessResponse(req.ID, result))
}

// handleSSE writes Server-Sent Events for streaming methods.
func (s *Server) handleSSE(w http.ResponseWriter, r *http.Request, req Request, handler StreamHandler) {
	flusher, ok := w.(http.Flusher)
	if !ok {
		s.writeResponse(w, ErrorResponse(req.ID, ErrCodeInternal, "streaming not supported"))
		return
	}

	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("X-Accel-Buffering", "no")

	events := make(chan SSEEvent, 32)
	go handler(req.Params, events)

	for event := range events {
		data, _ := json.Marshal(event.Data)
		fmt.Fprintf(w, "event: %s\ndata: %s\n\n", event.Event, string(data))
		flusher.Flush()

		// Check if client disconnected.
		if r.Context().Err() != nil {
			s.logger.Info("sse client disconnected", "method", req.Method)
			return
		}
	}
}

func (s *Server) writeResponse(w http.ResponseWriter, resp Response) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

// handleTasksGet retrieves a task by ID.
func (s *Server) handleTasksGet(params json.RawMessage) (interface{}, *RPCError) {
	var p TaskGetParams
	if err := json.Unmarshal(params, &p); err != nil {
		return nil, &RPCError{Code: ErrCodeInvalidParams, Message: err.Error()}
	}
	task, ok := s.tasks.Get(p.TaskID)
	if !ok {
		return nil, &RPCError{Code: ErrCodeTaskNotFound, Message: "task not found"}
	}
	return TaskResultFromTask(task), nil
}

// handleTasksCancel cancels a task by ID.
func (s *Server) handleTasksCancel(params json.RawMessage) (interface{}, *RPCError) {
	var p TaskCancelParams
	if err := json.Unmarshal(params, &p); err != nil {
		return nil, &RPCError{Code: ErrCodeInvalidParams, Message: err.Error()}
	}
	task, ok := s.tasks.Get(p.TaskID)
	if !ok {
		return nil, &RPCError{Code: ErrCodeTaskNotFound, Message: "task not found"}
	}
	if err := task.TransitionTo(TaskStateCanceled, "canceled by client"); err != nil {
		return nil, &RPCError{Code: ErrCodeTaskFailed, Message: err.Error()}
	}
	return TaskResultFromTask(task), nil
}

// handlePushNotifConfigSet registers a webhook for async task updates.
func (s *Server) handlePushNotifConfigSet(params json.RawMessage) (interface{}, *RPCError) {
	var p PushNotificationConfigParams
	if err := json.Unmarshal(params, &p); err != nil {
		return nil, &RPCError{Code: ErrCodeInvalidParams, Message: err.Error()}
	}
	if p.TaskID == "" || p.Config.URL == "" {
		return nil, &RPCError{Code: ErrCodeInvalidParams, Message: "id and url are required"}
	}
	if !strings.HasPrefix(p.Config.URL, "https://") && !strings.HasPrefix(p.Config.URL, "http://") {
		return nil, &RPCError{Code: ErrCodeInvalidParams, Message: "url must be http(s)"}
	}
	s.pushConfigs[p.TaskID] = p.Config
	s.logger.Info("push notification configured", "taskId", p.TaskID, "url", p.Config.URL)
	return map[string]interface{}{"id": p.TaskID, "pushNotificationConfig": p.Config}, nil
}

// handlePushNotifConfigGet retrieves the push notification config for a task.
func (s *Server) handlePushNotifConfigGet(params json.RawMessage) (interface{}, *RPCError) {
	var p TaskGetParams
	if err := json.Unmarshal(params, &p); err != nil {
		return nil, &RPCError{Code: ErrCodeInvalidParams, Message: err.Error()}
	}
	config, ok := s.pushConfigs[p.TaskID]
	if !ok {
		return nil, &RPCError{Code: ErrCodeTaskNotFound, Message: "no push config for task"}
	}
	return map[string]interface{}{"id": p.TaskID, "pushNotificationConfig": config}, nil
}

// NewTaskID generates a unique task ID.
func NewTaskID() string {
	return uuid.New().String()
}

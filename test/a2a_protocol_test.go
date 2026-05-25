package test

import (
	"encoding/json"
	"testing"

	"github.com/OpenOurMinds/ATA/internal/a2a"
)

// TestAgentCardValidation verifies Agent Card field requirements.
func TestAgentCardValidation(t *testing.T) {
	tests := []struct {
		name    string
		card    a2a.AgentCard
		wantErr bool
	}{
		{
			name: "valid card",
			card: a2a.NewAgentCard("Test Agent", "A test agent", "http://localhost:8080", "1.0",
				[]a2a.Skill{{ID: "test", Name: "Test", Description: "A test skill"}}),
			wantErr: false,
		},
		{
			name:    "missing name",
			card:    a2a.AgentCard{URL: "http://x", Version: "1.0", Skills: []a2a.Skill{{ID: "x", Name: "x", Description: "x"}}},
			wantErr: true,
		},
		{
			name:    "missing url",
			card:    a2a.AgentCard{Name: "X", Version: "1.0", Skills: []a2a.Skill{{ID: "x", Name: "x", Description: "x"}}},
			wantErr: true,
		},
		{
			name:    "no skills",
			card:    a2a.AgentCard{Name: "X", URL: "http://x", Version: "1.0"},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.card.Validate()
			if (err != nil) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

// TestJSONRPCRequestValidation verifies JSON-RPC 2.0 conformance.
func TestJSONRPCRequestValidation(t *testing.T) {
	// Valid request.
	req, err := a2a.NewRequest("message/send", map[string]string{"test": "data"})
	if err != nil {
		t.Fatalf("NewRequest: %v", err)
	}
	if err := req.Validate(); err != nil {
		t.Errorf("valid request failed validation: %v", err)
	}
	if req.JSONRPC != "2.0" {
		t.Errorf("jsonrpc = %q, want %q", req.JSONRPC, "2.0")
	}

	// Invalid: wrong version.
	bad := &a2a.Request{JSONRPC: "1.0", Method: "test", ID: 1}
	if err := bad.Validate(); err == nil {
		t.Error("expected error for wrong jsonrpc version")
	}

	// Invalid: empty method.
	bad2 := &a2a.Request{JSONRPC: "2.0", Method: "", ID: 1}
	if err := bad2.Validate(); err == nil {
		t.Error("expected error for empty method")
	}
}

// TestTaskLifecycle verifies state machine transitions.
func TestTaskLifecycle(t *testing.T) {
	store := a2a.NewTaskStore()
	task, _ := store.Create("task-001")

	if task.State != a2a.TaskStateSubmitted {
		t.Fatalf("initial state = %s, want submitted", task.State)
	}

	// Valid: submitted → working.
	if err := task.TransitionTo(a2a.TaskStateWorking, "starting"); err != nil {
		t.Fatalf("submitted → working: %v", err)
	}

	// Valid: working → completed.
	if err := task.TransitionTo(a2a.TaskStateCompleted, "done"); err != nil {
		t.Fatalf("working → completed: %v", err)
	}

	// Invalid: completed → working (terminal state).
	if err := task.TransitionTo(a2a.TaskStateWorking, "retry"); err == nil {
		t.Error("expected error for completed → working")
	}

	if !task.IsTerminal() {
		t.Error("completed task should be terminal")
	}

	// Verify history.
	if len(task.History) != 3 { // submitted + working + completed
		t.Errorf("history length = %d, want 3", len(task.History))
	}
}

// TestInvalidTaskTransitions verifies rejection of illegal transitions.
func TestInvalidTaskTransitions(t *testing.T) {
	store := a2a.NewTaskStore()

	// submitted → completed (not allowed, must go through working).
	task, _ := store.Create("task-002")
	if err := task.TransitionTo(a2a.TaskStateCompleted, "skip"); err == nil {
		t.Error("expected error for submitted → completed")
	}
}

// TestMessageSerialization verifies JSON round-trip of messages.
func TestMessageSerialization(t *testing.T) {
	msg := a2a.NewMessage(a2a.RoleUser,
		a2a.NewTextPart("generate 50 souls"),
		a2a.NewDataPart(map[string]int{"count": 50}),
	)

	data, err := json.Marshal(msg)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}

	var decoded a2a.Message
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}

	if decoded.Role != a2a.RoleUser {
		t.Errorf("role = %s, want user", decoded.Role)
	}
	if len(decoded.Parts) != 2 {
		t.Errorf("parts = %d, want 2", len(decoded.Parts))
	}
}

// TestResponseFormats verifies success and error response structures.
func TestResponseFormats(t *testing.T) {
	success := a2a.SuccessResponse(1, "ok")
	if success.Error != nil {
		t.Error("success response should not have error")
	}
	if success.JSONRPC != "2.0" {
		t.Errorf("jsonrpc = %q, want 2.0", success.JSONRPC)
	}

	errResp := a2a.ErrorResponse(2, a2a.ErrCodeMethodNotFound, "not found")
	if errResp.Error == nil {
		t.Fatal("error response should have error")
	}
	if errResp.Error.Code != a2a.ErrCodeMethodNotFound {
		t.Errorf("error code = %d, want %d", errResp.Error.Code, a2a.ErrCodeMethodNotFound)
	}
}

// TestAgentCardProtocolVersion verifies the Agent Card includes protocolVersion.
func TestAgentCardProtocolVersion(t *testing.T) {
	card := a2a.NewAgentCard("Test", "test", "http://x", "1.0",
		[]a2a.Skill{{ID: "x", Name: "x", Description: "x"}})

	if card.ProtocolVersion == "" {
		t.Error("protocolVersion must not be empty")
	}
	if card.ProtocolVersion != "0.2.0" {
		t.Errorf("protocolVersion = %q, want 0.2.0", card.ProtocolVersion)
	}
}

// TestAgentCardProvider verifies Provider metadata is present.
func TestAgentCardProvider(t *testing.T) {
	card := a2a.NewAgentCard("Test", "test", "http://x", "1.0",
		[]a2a.Skill{{ID: "x", Name: "x", Description: "x"}})

	if card.Provider == nil {
		t.Fatal("provider must not be nil")
	}
	if card.Provider.Organization == "" {
		t.Error("provider organization must not be empty")
	}
}

// TestAgentCardCapabilities verifies streaming and push notifications are enabled.
func TestAgentCardCapabilities(t *testing.T) {
	card := a2a.NewAgentCard("Test", "test", "http://x", "1.0",
		[]a2a.Skill{{ID: "x", Name: "x", Description: "x"}})

	if !card.Capabilities.Streaming {
		t.Error("streaming should be true (SSE support)")
	}
	if !card.Capabilities.PushNotifications {
		t.Error("pushNotifications should be true")
	}
	if !card.Capabilities.StateTransitionHistory {
		t.Error("stateTransitionHistory should be true")
	}
}

// TestAgentCardJSONSerialization verifies Agent Card JSON includes all required fields.
func TestAgentCardJSONSerialization(t *testing.T) {
	card := a2a.NewAgentCard("Test Agent", "test desc", "http://localhost:8080", "1.0",
		[]a2a.Skill{{ID: "test", Name: "Test", Description: "Test skill"}})

	data, err := json.Marshal(card)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}

	var raw map[string]interface{}
	json.Unmarshal(data, &raw)

	requiredFields := []string{"name", "description", "url", "version", "protocolVersion",
		"capabilities", "skills", "authentication", "defaultInputModes", "defaultOutputModes"}
	for _, field := range requiredFields {
		if _, ok := raw[field]; !ok {
			t.Errorf("missing required field: %s", field)
		}
	}
}

// TestSessionIDTracking verifies session context is preserved in tasks.
func TestSessionIDTracking(t *testing.T) {
	store := a2a.NewTaskStore()
	task, _ := store.Create("task-session-001")
	task.SessionID = "session-abc-123"
	task.ContextID = "context-xyz-789"

	result := a2a.TaskResultFromTask(task)
	if result.SessionID != "session-abc-123" {
		t.Errorf("sessionId = %q, want session-abc-123", result.SessionID)
	}
	if result.ContextID != "context-xyz-789" {
		t.Errorf("contextId = %q, want context-xyz-789", result.ContextID)
	}
}

// TestAuthRequiredState verifies the auth-required state transition.
func TestAuthRequiredState(t *testing.T) {
	store := a2a.NewTaskStore()
	task, _ := store.Create("task-auth-001")

	// submitted → auth-required (valid).
	if err := task.TransitionTo(a2a.TaskStateAuthRequired, "oauth2 required"); err != nil {
		t.Fatalf("submitted → auth-required: %v", err)
	}
	if task.State != a2a.TaskStateAuthRequired {
		t.Errorf("state = %s, want auth-required", task.State)
	}

	// auth-required → working (valid, after auth provided).
	if err := task.TransitionTo(a2a.TaskStateWorking, "authorized"); err != nil {
		t.Fatalf("auth-required → working: %v", err)
	}

	// Also verify auth-required → canceled is valid.
	task2, _ := store.Create("task-auth-002")
	task2.TransitionTo(a2a.TaskStateAuthRequired, "need auth")
	if err := task2.TransitionTo(a2a.TaskStateCanceled, "user canceled"); err != nil {
		t.Fatalf("auth-required → canceled: %v", err)
	}
}

// TestInputRequiredState verifies the human-in-the-loop approval flow.
func TestInputRequiredState(t *testing.T) {
	store := a2a.NewTaskStore()
	task, _ := store.Create("task-hitl-001")

	task.TransitionTo(a2a.TaskStateWorking, "processing")
	// working → input-required (pause for human approval).
	if err := task.TransitionTo(a2a.TaskStateInputRequired, "tool approval needed"); err != nil {
		t.Fatalf("working → input-required: %v", err)
	}
	// input-required → working (approval granted, resume).
	if err := task.TransitionTo(a2a.TaskStateWorking, "approved, resuming"); err != nil {
		t.Fatalf("input-required → working: %v", err)
	}
	if err := task.TransitionTo(a2a.TaskStateCompleted, "done"); err != nil {
		t.Fatalf("working → completed: %v", err)
	}
}

// TestMessageSendParamsSessionID verifies session ID in message params.
func TestMessageSendParamsSessionID(t *testing.T) {
	params := a2a.MessageSendParams{
		TaskID:    "task-001",
		SessionID: "session-001",
		Message:   a2a.NewMessage(a2a.RoleUser, a2a.NewTextPart("hello")),
	}

	data, err := json.Marshal(params)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}

	var raw map[string]interface{}
	json.Unmarshal(data, &raw)

	if raw["sessionId"] != "session-001" {
		t.Errorf("sessionId = %v, want session-001", raw["sessionId"])
	}
}

// TestA2AMethodConstants verifies all required A2A methods are defined.
func TestA2AMethodConstants(t *testing.T) {
	methods := map[string]string{
		"message/send":                        a2a.MethodMessageSend,
		"message/stream":                      a2a.MethodMessageStream,
		"tasks/get":                           a2a.MethodTasksGet,
		"tasks/cancel":                        a2a.MethodTasksCancel,
		"tasks/pushNotificationConfig/set":    a2a.MethodPushNotifConfigSet,
		"tasks/pushNotificationConfig/get":    a2a.MethodPushNotifConfigGet,
	}
	for expected, actual := range methods {
		if actual != expected {
			t.Errorf("method %q = %q", expected, actual)
		}
	}
}

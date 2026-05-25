// Package test contains A2A conformance scenarios.
// These tests verify the 4 critical resilience scenarios:
//   Scenario 1: Discovery & Handshake
//   Scenario 2: Asynchronous Task Delegation
//   Scenario 3: Human-in-the-Loop Approval
//   Scenario 4: Error Handling & Resilience
package test

import (
	"encoding/json"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/OpenOurMinds/ATA/internal/a2a"
)

func testLogger() *slog.Logger {
	return slog.New(slog.NewTextHandler(nil, &slog.HandlerOptions{Level: slog.LevelError}))
}

func testCard() a2a.AgentCard {
	return a2a.NewAgentCard("Test Agent", "A test agent", "http://localhost:9999", "1.0",
		[]a2a.Skill{
			{ID: "generate", Name: "Generate", Description: "Generate data"},
			{ID: "analyze", Name: "Analyze", Description: "Analyze data"},
		})
}

// ═══════════════════════════════════════════════════════════════════
// SCENARIO 1: Discovery & Handshake
// ═══════════════════════════════════════════════════════════════════

// TestDiscovery_AgentCardEndpoint verifies GET /.well-known/agent-card.json
// returns valid JSON with agent ID and capabilities.
func TestDiscovery_AgentCardEndpoint(t *testing.T) {
	server := a2a.NewServer(testCard(), testLogger())
	ts := httptest.NewServer(server.Handler())
	defer ts.Close()

	resp, err := http.Get(ts.URL + "/.well-known/agent-card.json")
	if err != nil {
		t.Fatalf("GET agent-card.json: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Fatalf("status = %d, want 200", resp.StatusCode)
	}
	if ct := resp.Header.Get("Content-Type"); ct != "application/json" {
		t.Errorf("content-type = %q, want application/json", ct)
	}

	var card a2a.AgentCard
	if err := json.NewDecoder(resp.Body).Decode(&card); err != nil {
		t.Fatalf("decode: %v", err)
	}
	if card.Name != "Test Agent" {
		t.Errorf("name = %q, want Test Agent", card.Name)
	}
	if card.ProtocolVersion == "" {
		t.Error("protocolVersion must not be empty")
	}
	if !card.Capabilities.Streaming {
		t.Error("streaming should be true")
	}
	if !card.Capabilities.PushNotifications {
		t.Error("pushNotifications should be true")
	}
}

// TestDiscovery_OAuthBearerToken verifies that auth middleware rejects
// requests without a valid Bearer token.
func TestDiscovery_OAuthBearerToken(t *testing.T) {
	server := a2a.NewServer(testCard(), testLogger())
	server.SetAuth(func(r *http.Request) *a2a.RPCError {
		auth := r.Header.Get("Authorization")
		if !strings.HasPrefix(auth, "Bearer ") {
			return &a2a.RPCError{Code: a2a.ErrCodeAuthRequired, Message: "Bearer token required"}
		}
		if auth != "Bearer valid-token-123" {
			return &a2a.RPCError{Code: a2a.ErrCodeAuthRequired, Message: "invalid token"}
		}
		return nil
	})
	ts := httptest.NewServer(server.Handler())
	defer ts.Close()

	// Request without token → rejected.
	body := `{"jsonrpc":"2.0","method":"tasks/get","params":{"id":"x"},"id":1}`
	resp, err := http.Post(ts.URL, "application/json", strings.NewReader(body))
	if err != nil {
		t.Fatalf("POST: %v", err)
	}
	defer resp.Body.Close()
	var rpcResp a2a.Response
	json.NewDecoder(resp.Body).Decode(&rpcResp)
	if rpcResp.Error == nil {
		t.Fatal("expected auth error for missing token")
	}
	if rpcResp.Error.Code != a2a.ErrCodeAuthRequired {
		t.Errorf("error code = %d, want %d", rpcResp.Error.Code, a2a.ErrCodeAuthRequired)
	}
}

// TestDiscovery_PlainHTTPRejection verifies HTTPS enforcement rejects plain HTTP.
func TestDiscovery_PlainHTTPRejection(t *testing.T) {
	server := a2a.NewServer(testCard(), testLogger())
	server.SetRequireHTTPS(true)
	ts := httptest.NewServer(server.Handler())
	defer ts.Close()

	body := `{"jsonrpc":"2.0","method":"tasks/get","params":{"id":"x"},"id":1}`
	resp, err := http.Post(ts.URL, "application/json", strings.NewReader(body))
	if err != nil {
		t.Fatalf("POST: %v", err)
	}
	defer resp.Body.Close()

	// httptest.NewServer uses plain HTTP → should be rejected.
	if resp.StatusCode != http.StatusForbidden {
		t.Errorf("status = %d, want 403", resp.StatusCode)
	}
}

// ═══════════════════════════════════════════════════════════════════
// SCENARIO 2: Asynchronous Task Delegation
// ═══════════════════════════════════════════════════════════════════

// TestAsyncTask_SubmissionAndCompletion verifies task creation and lifecycle.
func TestAsyncTask_SubmissionAndCompletion(t *testing.T) {
	server := a2a.NewServer(testCard(), testLogger())

	// Register a handler that processes tasks asynchronously.
	server.RegisterHandler(a2a.MethodMessageSend, func(params json.RawMessage) (interface{}, *a2a.RPCError) {
		taskID := a2a.NewTaskID()
		task, err := server.Tasks().Create(taskID)
		if err != nil {
			return nil, &a2a.RPCError{Code: a2a.ErrCodeInvalidParams, Message: err.Error()}
		}
		task.TransitionTo(a2a.TaskStateWorking, "processing")
		task.AddArtifact("result", []a2a.Part{a2a.NewTextPart("done")})
		task.TransitionTo(a2a.TaskStateCompleted, "finished")
		return a2a.TaskResultFromTask(task), nil
	})

	ts := httptest.NewServer(server.Handler())
	defer ts.Close()

	body := `{"jsonrpc":"2.0","method":"message/send","params":{"message":{"role":"user","parts":[{"type":"text","text":"test"}]}},"id":1}`
	resp, err := http.Post(ts.URL, "application/json", strings.NewReader(body))
	if err != nil {
		t.Fatalf("POST: %v", err)
	}
	defer resp.Body.Close()

	var rpcResp a2a.Response
	json.NewDecoder(resp.Body).Decode(&rpcResp)
	if rpcResp.Error != nil {
		t.Fatalf("rpc error: %s", rpcResp.Error.Message)
	}
}

// TestAsyncTask_DuplicateTaskID verifies duplicate task IDs are rejected.
func TestAsyncTask_DuplicateTaskID(t *testing.T) {
	store := a2a.NewTaskStore()

	_, err := store.Create("task-dup-001")
	if err != nil {
		t.Fatalf("first create: %v", err)
	}

	_, err = store.Create("task-dup-001")
	if err == nil {
		t.Fatal("expected error for duplicate task ID")
	}
	if !strings.Contains(err.Error(), "duplicate") {
		t.Errorf("error should mention duplicate, got: %s", err.Error())
	}
}

// TestAsyncTask_SilentFailurePrevention verifies tasks must emit failure events
// rather than silently disappearing.
func TestAsyncTask_SilentFailurePrevention(t *testing.T) {
	store := a2a.NewTaskStore()
	task, _ := store.Create("task-timeout-001")
	task.TransitionTo(a2a.TaskStateWorking, "started")

	// Simulate a failure — the task MUST transition to failed, not stay in working.
	task.TransitionTo(a2a.TaskStateFailed, "timeout after 30s")

	if task.State != a2a.TaskStateFailed {
		t.Errorf("state = %s, want failed", task.State)
	}

	// Verify failure is recorded in history.
	lastHistory := task.History[len(task.History)-1]
	if lastHistory.State != a2a.TaskStateFailed {
		t.Error("last history entry should be failed")
	}
	if lastHistory.Message == "" {
		t.Error("failure must include a message explaining why")
	}
}

// ═══════════════════════════════════════════════════════════════════
// SCENARIO 3: Human-in-the-Loop (HITL) Approval
// ═══════════════════════════════════════════════════════════════════

// TestHITL_AuthorizationRequest verifies input-required state pauses execution.
func TestHITL_AuthorizationRequest(t *testing.T) {
	store := a2a.NewTaskStore()
	task, _ := store.Create("task-hitl-req-001")
	task.TransitionTo(a2a.TaskStateWorking, "processing")

	// Agent hits a sensitive tool → request approval.
	task.TransitionTo(a2a.TaskStateInputRequired, "requires_approval: delete_database")

	if task.State != a2a.TaskStateInputRequired {
		t.Fatalf("state = %s, want input-required", task.State)
	}

	// Verify approval deadline was set.
	if task.ApprovalDeadline == nil {
		t.Fatal("approval deadline must be set when entering input-required")
	}
	if task.ApprovalDeadline.Before(time.Now().UTC()) {
		t.Error("approval deadline should be in the future")
	}
}

// TestHITL_StateSuspension verifies the agent does NOT execute while waiting.
func TestHITL_StateSuspension(t *testing.T) {
	store := a2a.NewTaskStore()
	task, _ := store.Create("task-hitl-suspend-001")
	task.TransitionTo(a2a.TaskStateWorking, "processing")
	task.TransitionTo(a2a.TaskStateInputRequired, "tool approval needed")

	// While in input-required, the task cannot transition to completed
	// (i.e., cannot auto-execute).
	err := task.TransitionTo(a2a.TaskStateCompleted, "auto-executed")
	if err == nil {
		t.Fatal("CRITICAL: task completed without approval (auto-execution)")
	}

	// Only valid transitions from input-required: working, canceled, failed.
	if err := task.TransitionTo(a2a.TaskStateWorking, "human approved"); err != nil {
		t.Fatalf("input-required → working (after approval): %v", err)
	}
}

// TestHITL_ExpiredApprovalTimeout verifies timeout when human takes too long.
func TestHITL_ExpiredApprovalTimeout(t *testing.T) {
	store := a2a.NewTaskStore()
	task, _ := store.Create("task-hitl-timeout-001")
	task.TransitionTo(a2a.TaskStateWorking, "processing")
	task.TransitionTo(a2a.TaskStateInputRequired, "tool approval needed")

	// Simulate expired deadline (set it to the past).
	expired := time.Now().UTC().Add(-1 * time.Hour)
	task.ApprovalDeadline = &expired

	// Any transition attempt should fail with timeout.
	err := task.TransitionTo(a2a.TaskStateWorking, "late approval")
	if err == nil {
		t.Fatal("expected error for expired approval")
	}
	if !strings.Contains(err.Error(), "timeout") {
		t.Errorf("error should mention timeout, got: %s", err.Error())
	}
	if task.State != a2a.TaskStateFailed {
		t.Errorf("state should be failed after timeout, got %s", task.State)
	}
}

// ═══════════════════════════════════════════════════════════════════
// SCENARIO 4: Error Handling & Resilience
// ═══════════════════════════════════════════════════════════════════

// TestResilience_ExponentialBackoff verifies client retries on 503.
func TestResilience_ExponentialBackoff(t *testing.T) {
	attempts := 0
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		attempts++
		if attempts < 3 {
			w.WriteHeader(http.StatusServiceUnavailable)
			return
		}
		// Third attempt succeeds.
		json.NewEncoder(w).Encode(a2a.Response{
			JSONRPC: "2.0",
			Result:  a2a.TaskResult{ID: "success-001", State: a2a.TaskStateCompleted},
			ID:      float64(1),
		})
	}))
	defer ts.Close()

	client := a2a.NewClient(testLogger())
	client.SetRetryConfig(a2a.RetryConfig{
		MaxRetries: 5,
		BaseDelay:  10 * time.Millisecond, // Fast for tests.
		MaxDelay:   100 * time.Millisecond,
		RetryOn503: true,
	})

	result, err := client.SendMessage(ts.URL, a2a.MessageSendParams{
		Message: a2a.NewMessage(a2a.RoleUser, a2a.NewTextPart("test")),
	})
	if err != nil {
		t.Fatalf("SendMessage: %v", err)
	}
	if result.ID != "success-001" {
		t.Errorf("task ID = %q, want success-001", result.ID)
	}
	if attempts != 3 {
		t.Errorf("attempts = %d, want 3", attempts)
	}
}

// TestResilience_MalformedJSONRPC verifies standard -32600 error for bad requests.
func TestResilience_MalformedJSONRPC(t *testing.T) {
	server := a2a.NewServer(testCard(), testLogger())
	ts := httptest.NewServer(server.Handler())
	defer ts.Close()

	// Send malformed JSON.
	resp, err := http.Post(ts.URL, "application/json", strings.NewReader("{invalid json"))
	if err != nil {
		t.Fatalf("POST: %v", err)
	}
	defer resp.Body.Close()

	var rpcResp a2a.Response
	json.NewDecoder(resp.Body).Decode(&rpcResp)
	if rpcResp.Error == nil {
		t.Fatal("expected error for malformed JSON")
	}
	if rpcResp.Error.Code != a2a.ErrCodeParseError {
		t.Errorf("error code = %d, want %d (parse error)", rpcResp.Error.Code, a2a.ErrCodeParseError)
	}
}

// TestResilience_MaxTurnsLimit verifies the orchestrator terminates tasks
// that exceed the maximum turns limit (infinite loop prevention).
func TestResilience_MaxTurnsLimit(t *testing.T) {
	store := a2a.NewTaskStore()
	task, _ := store.Create("task-maxturns-001")
	task.MaxTurns = 5

	// Burn through max turns: submitted → working → input → working → input → working
	task.TransitionTo(a2a.TaskStateWorking, "turn 1")
	task.TransitionTo(a2a.TaskStateInputRequired, "turn 2")
	task.TransitionTo(a2a.TaskStateWorking, "turn 3")
	task.TransitionTo(a2a.TaskStateInputRequired, "turn 4")
	task.TransitionTo(a2a.TaskStateWorking, "turn 5") // This is turn 5 = MaxTurns

	// Next transition should fail with max turns exceeded.
	err := task.TransitionTo(a2a.TaskStateCompleted, "turn 6")
	if err == nil {
		t.Fatal("expected error for max turns exceeded")
	}
	if !strings.Contains(err.Error(), "max turns") {
		t.Errorf("error should mention max turns, got: %s", err.Error())
	}
	if task.State != a2a.TaskStateFailed {
		t.Errorf("state should be failed, got %s", task.State)
	}
}

// TestResilience_UnauthorizedToolAccess verifies agents reject calls to
// tools not listed in their Agent Card.
func TestResilience_UnauthorizedToolAccess(t *testing.T) {
	server := a2a.NewServer(testCard(), testLogger())

	// "generate" and "analyze" are authorized skills.
	if !server.SkillAuthorized("generate") {
		t.Error("generate should be authorized")
	}
	if !server.SkillAuthorized("analyze") {
		t.Error("analyze should be authorized")
	}

	// "delete_database" is NOT in the Agent Card → must be rejected.
	if server.SkillAuthorized("delete_database") {
		t.Error("delete_database should NOT be authorized (not in Agent Card)")
	}
	if server.SkillAuthorized("admin_override") {
		t.Error("admin_override should NOT be authorized")
	}
}

// TestResilience_InvalidMethodRejection verifies unknown methods return -32601.
func TestResilience_InvalidMethodRejection(t *testing.T) {
	server := a2a.NewServer(testCard(), testLogger())
	ts := httptest.NewServer(server.Handler())
	defer ts.Close()

	body := `{"jsonrpc":"2.0","method":"tools/execute_arbitrary","params":{},"id":1}`
	resp, err := http.Post(ts.URL, "application/json", strings.NewReader(body))
	if err != nil {
		t.Fatalf("POST: %v", err)
	}
	defer resp.Body.Close()

	var rpcResp a2a.Response
	json.NewDecoder(resp.Body).Decode(&rpcResp)
	if rpcResp.Error == nil {
		t.Fatal("expected error for unknown method")
	}
	if rpcResp.Error.Code != a2a.ErrCodeMethodNotFound {
		t.Errorf("error code = %d, want %d", rpcResp.Error.Code, a2a.ErrCodeMethodNotFound)
	}
}

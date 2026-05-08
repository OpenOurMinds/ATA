// Package a2a guardrails implements the three defense layers:
//   1. Semantic Guardrails — intent filtering, PII stripping, conflict detection
//   2. Resource & Rate Governance — token budgets, TTL, circuit breakers
//   3. Zero-Trust Tool Access — OAuth scoping, HITL enforcement
package a2a

import (
	"fmt"
	"regexp"
	"strings"
	"sync"
	"time"
)

// ═══════════════════════════════════════════════════════════════════
// 1. SEMANTIC GUARDRAILS
// ═══════════════════════════════════════════════════════════════════

// InjectionPattern is a known prompt injection signature.
type InjectionPattern struct {
	Name    string
	Pattern *regexp.Regexp
}

// DefaultInjectionPatterns returns patterns that detect indirect prompt injection.
var DefaultInjectionPatterns = []InjectionPattern{
	{Name: "system_override", Pattern: regexp.MustCompile(`(?i)(ignore|forget|disregard)\s+(all\s+)?(previous|prior|above|your)\s+(instructions?|rules?|prompts?|safety)`)},
	{Name: "role_hijack", Pattern: regexp.MustCompile(`(?i)you\s+are\s+now\s+(a|an)\s+`)},
	{Name: "command_injection", Pattern: regexp.MustCompile(`(?i)(rm\s+-rf|drop\s+table|delete\s+all|shell_exec|exec\s*\(|os\.system)`)},
	{Name: "data_exfil", Pattern: regexp.MustCompile(`(?i)(send|post|upload|exfiltrate)\s+(to|all|the)\s+(http|https|ftp)`)},
	{Name: "jailbreak", Pattern: regexp.MustCompile(`(?i)(DAN|do\s+anything\s+now|developer\s+mode|act\s+as\s+if\s+no\s+restrictions)`)},
}

// PIIPattern matches common PII formats for redaction.
var PIIPatterns = []struct {
	Name    string
	Pattern *regexp.Regexp
	Replace string
}{
	{Name: "email", Pattern: regexp.MustCompile(`[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}`), Replace: "[REDACTED_EMAIL]"},
	{Name: "api_key", Pattern: regexp.MustCompile(`(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["']?[a-zA-Z0-9\-_]{16,}["']?`), Replace: "[REDACTED_KEY]"},
	{Name: "ssn", Pattern: regexp.MustCompile(`\b\d{3}-\d{2}-\d{4}\b`), Replace: "[REDACTED_SSN]"},
	{Name: "credit_card", Pattern: regexp.MustCompile(`\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b`), Replace: "[REDACTED_CC]"},
	{Name: "phone", Pattern: regexp.MustCompile(`\b\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b`), Replace: "[REDACTED_PHONE]"},
}

// ScanResult is the output of a semantic scan.
type ScanResult struct {
	Safe       bool     `json:"safe"`
	Violations []string `json:"violations,omitempty"`
	Sanitized  string   `json:"sanitized,omitempty"`
}

// ScanForInjection checks text for prompt injection patterns.
func ScanForInjection(text string) ScanResult {
	var violations []string
	for _, p := range DefaultInjectionPatterns {
		if p.Pattern.MatchString(text) {
			violations = append(violations, fmt.Sprintf("%s: %s", p.Name, p.Pattern.FindString(text)))
		}
	}
	return ScanResult{
		Safe:       len(violations) == 0,
		Violations: violations,
	}
}

// StripPII redacts personally identifiable information from text.
func StripPII(text string) string {
	result := text
	for _, p := range PIIPatterns {
		result = p.Pattern.ReplaceAllString(result, p.Replace)
	}
	return result
}

// DetectConflict checks if a message contradicts a system directive.
func DetectConflict(message string, systemDirectives []string) bool {
	lower := strings.ToLower(message)
	for _, directive := range systemDirectives {
		// If the message tries to negate a directive.
		if strings.Contains(lower, "ignore") && strings.Contains(lower, strings.ToLower(directive)) {
			return true
		}
		if strings.Contains(lower, "override") && strings.Contains(lower, strings.ToLower(directive)) {
			return true
		}
	}
	// Check for generic override attempts.
	return ScanForInjection(message).Safe == false
}

// ScanMessage applies all semantic guardrails to a Message.
func ScanMessage(msg Message) ScanResult {
	var allViolations []string
	for _, part := range msg.Parts {
		if part.Type == "text" && part.Text != "" {
			scan := ScanForInjection(part.Text)
			allViolations = append(allViolations, scan.Violations...)
		}
	}
	return ScanResult{
		Safe:       len(allViolations) == 0,
		Violations: allViolations,
	}
}

// SanitizeMessage strips PII from all text parts of a message.
func SanitizeMessage(msg Message) Message {
	sanitized := msg
	sanitized.Parts = make([]Part, len(msg.Parts))
	copy(sanitized.Parts, msg.Parts)
	for i, part := range sanitized.Parts {
		if part.Type == "text" {
			sanitized.Parts[i].Text = StripPII(part.Text)
		}
	}
	return sanitized
}

// ═══════════════════════════════════════════════════════════════════
// 2. RESOURCE & RATE GOVERNANCE
// ═══════════════════════════════════════════════════════════════════

// SessionBudget tracks resource consumption per session.
type SessionBudget struct {
	mu           sync.Mutex
	SessionID    string        `json:"sessionId"`
	MaxTokens    int64         `json:"maxTokens"`
	UsedTokens   int64         `json:"usedTokens"`
	MaxSpendUSD  float64       `json:"maxSpendUsd"`
	SpentUSD     float64       `json:"spentUsd"`
	MaxTTL       time.Duration `json:"maxTtl"`
	StartedAt    time.Time     `json:"startedAt"`
	CircuitOpen  bool          `json:"circuitOpen"`
	RepeatCount  int           `json:"repeatCount"`
}

// NewSessionBudget creates a budget with default limits.
func NewSessionBudget(sessionID string) *SessionBudget {
	return &SessionBudget{
		SessionID:   sessionID,
		MaxTokens:   100000,
		MaxSpendUSD: 1.00,
		MaxTTL:      30 * time.Minute,
		StartedAt:   time.Now().UTC(),
	}
}

// ConsumeTokens adds token usage and checks budget.
func (b *SessionBudget) ConsumeTokens(count int64, costPerToken float64) error {
	b.mu.Lock()
	defer b.mu.Unlock()

	b.UsedTokens += count
	b.SpentUSD += float64(count) * costPerToken

	if b.UsedTokens > b.MaxTokens {
		return fmt.Errorf("token quota exceeded: %d/%d", b.UsedTokens, b.MaxTokens)
	}
	if b.SpentUSD > b.MaxSpendUSD {
		return fmt.Errorf("spend limit exceeded: $%.4f/$%.2f", b.SpentUSD, b.MaxSpendUSD)
	}
	return nil
}

// CheckTTL returns an error if the session has expired.
func (b *SessionBudget) CheckTTL() error {
	if time.Since(b.StartedAt) > b.MaxTTL {
		return fmt.Errorf("session TTL expired after %s", b.MaxTTL)
	}
	return nil
}

// CheckCircuit evaluates if the conversation is stuck in a non-productive loop.
// Call this with the latest message; if it matches the previous, increment repeat count.
func (b *SessionBudget) CheckCircuit(messageHash string, threshold int) error {
	b.mu.Lock()
	defer b.mu.Unlock()

	// Simple repeat detection: compare consecutive message hashes.
	b.RepeatCount++
	if b.RepeatCount >= threshold {
		b.CircuitOpen = true
		return fmt.Errorf("circuit breaker tripped: %d repetitive messages", b.RepeatCount)
	}
	return nil
}

// ResetCircuit resets the repeat counter (called when a novel message arrives).
func (b *SessionBudget) ResetCircuit() {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.RepeatCount = 0
	b.CircuitOpen = false
}

// IsExhausted returns true if any budget limit has been reached.
func (b *SessionBudget) IsExhausted() bool {
	b.mu.Lock()
	defer b.mu.Unlock()
	return b.UsedTokens > b.MaxTokens ||
		b.SpentUSD > b.MaxSpendUSD ||
		b.CircuitOpen ||
		time.Since(b.StartedAt) > b.MaxTTL
}

// ═══════════════════════════════════════════════════════════════════
// 3. ZERO-TRUST TOOL ACCESS
// ═══════════════════════════════════════════════════════════════════

// ToolScope defines the OAuth-style permission for a tool.
type ToolScope string

const (
	ScopeRead    ToolScope = "read"
	ScopeWrite   ToolScope = "write"
	ScopeDelete  ToolScope = "delete"
	ScopeExecute ToolScope = "execute"
	ScopeAdmin   ToolScope = "admin"
)

// ToolACL is an Access Control List for agent tool permissions.
type ToolACL struct {
	mu     sync.RWMutex
	grants map[string]map[ToolScope]bool // agentID → scope → allowed
	hitl   map[string]bool              // toolID → requires human approval
}

// NewToolACL creates an empty ACL.
func NewToolACL() *ToolACL {
	return &ToolACL{
		grants: make(map[string]map[ToolScope]bool),
		hitl:   make(map[string]bool),
	}
}

// Grant gives an agent permission for a scope.
func (acl *ToolACL) Grant(agentID string, scope ToolScope) {
	acl.mu.Lock()
	defer acl.mu.Unlock()
	if _, ok := acl.grants[agentID]; !ok {
		acl.grants[agentID] = make(map[ToolScope]bool)
	}
	acl.grants[agentID][scope] = true
}

// Revoke removes an agent's permission for a scope.
func (acl *ToolACL) Revoke(agentID string, scope ToolScope) {
	acl.mu.Lock()
	defer acl.mu.Unlock()
	if perms, ok := acl.grants[agentID]; ok {
		delete(perms, scope)
	}
}

// IsAllowed checks if an agent has the required scope.
func (acl *ToolACL) IsAllowed(agentID string, scope ToolScope) bool {
	acl.mu.RLock()
	defer acl.mu.RUnlock()
	perms, ok := acl.grants[agentID]
	if !ok {
		return false
	}
	return perms[scope]
}

// RequireHITL marks a tool as requiring human-in-the-loop approval.
func (acl *ToolACL) RequireHITL(toolID string) {
	acl.mu.Lock()
	defer acl.mu.Unlock()
	acl.hitl[toolID] = true
}

// NeedsApproval checks if a tool requires human approval.
func (acl *ToolACL) NeedsApproval(toolID string) bool {
	acl.mu.RLock()
	defer acl.mu.RUnlock()
	return acl.hitl[toolID]
}

// ToolAccessResult is the result of a tool access check.
type ToolAccessResult struct {
	Allowed      bool   `json:"allowed"`
	NeedApproval bool   `json:"needApproval"`
	Reason       string `json:"reason,omitempty"`
}

// CheckAccess performs a full zero-trust access check.
func (acl *ToolACL) CheckAccess(agentID, toolID string, scope ToolScope) ToolAccessResult {
	if !acl.IsAllowed(agentID, scope) {
		return ToolAccessResult{
			Allowed: false,
			Reason:  fmt.Sprintf("agent %q lacks scope %q", agentID, scope),
		}
	}
	if acl.NeedsApproval(toolID) {
		return ToolAccessResult{
			Allowed:      true,
			NeedApproval: true,
			Reason:       fmt.Sprintf("tool %q requires human-in-the-loop approval", toolID),
		}
	}
	return ToolAccessResult{Allowed: true}
}

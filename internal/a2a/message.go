package a2a

import "time"

// Role identifies the sender of a message.
type Role string

const (
	RoleUser  Role = "user"
	RoleAgent Role = "agent"
)

// Message is the atomic unit of communication in A2A.
type Message struct {
	Role      Role      `json:"role"`
	Parts     []Part    `json:"parts"`
	Metadata  map[string]string `json:"metadata,omitempty"`
	Timestamp time.Time `json:"timestamp"`
}

// Part is a content unit within a message.
// Only one of Text, File, or Data should be set.
type Part struct {
	Type string `json:"type"` // "text", "file", "data"

	// Text part.
	Text string `json:"text,omitempty"`

	// File part.
	FileURI  string `json:"uri,omitempty"`
	MimeType string `json:"mimeType,omitempty"`

	// Data part (structured JSON).
	Data interface{} `json:"data,omitempty"`
}

// NewTextPart creates a text content part.
func NewTextPart(text string) Part {
	return Part{
		Type: "text",
		Text: text,
	}
}

// NewDataPart creates a structured data part.
func NewDataPart(data interface{}) Part {
	return Part{
		Type: "data",
		Data: data,
	}
}

// NewMessage creates a message from the given role and parts.
func NewMessage(role Role, parts ...Part) Message {
	return Message{
		Role:      role,
		Parts:     parts,
		Timestamp: time.Now().UTC(),
	}
}

// MessageSendParams are the parameters for the message/send method.
type MessageSendParams struct {
	TaskID    string  `json:"id,omitempty"`
	SessionID string  `json:"sessionId,omitempty"`
	Message   Message `json:"message"`
}

// TaskGetParams are the parameters for the tasks/get method.
type TaskGetParams struct {
	TaskID string `json:"id"`
}

// TaskCancelParams are the parameters for the tasks/cancel method.
type TaskCancelParams struct {
	TaskID string `json:"id"`
}

// TaskResult is the response type for task-related operations.
type TaskResult struct {
	ID        string            `json:"id"`
	SessionID string            `json:"sessionId,omitempty"`
	ContextID string            `json:"contextId,omitempty"`
	State     TaskState         `json:"status"`
	Messages  []Message         `json:"messages,omitempty"`
	Artifacts []Artifact        `json:"artifacts,omitempty"`
	Metadata  map[string]string `json:"metadata,omitempty"`
	History   []TaskStateChange `json:"history,omitempty"`
}

// TaskResultFromTask converts a Task to a TaskResult.
func TaskResultFromTask(t *Task) TaskResult {
	return TaskResult{
		ID:        t.ID,
		SessionID: t.SessionID,
		ContextID: t.ContextID,
		State:     t.State,
		Messages:  t.Messages,
		Artifacts: t.Artifacts,
		Metadata:  t.Metadata,
		History:   t.History,
	}
}

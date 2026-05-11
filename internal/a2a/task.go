package a2a

import (
	"fmt"
	"sync"
	"time"
)

// TaskState represents the lifecycle state of a task.
type TaskState string

const (
	TaskStateSubmitted     TaskState = "submitted"
	TaskStateWorking       TaskState = "working"
	TaskStateInputRequired TaskState = "input-required"
	TaskStateAuthRequired  TaskState = "auth-required"
	TaskStateCompleted     TaskState = "completed"
	TaskStateFailed        TaskState = "failed"
	TaskStateCanceled      TaskState = "canceled"
)

// DefaultMaxTurns is the maximum number of state transitions before
// a task is forcibly failed to prevent infinite loops.
const DefaultMaxTurns = 50

// DefaultApprovalTimeout is the maximum time a task can wait in
// input-required or auth-required before being auto-failed.
var DefaultApprovalTimeout = 24 * time.Hour

// Task is the fundamental stateful unit of work in A2A.
type Task struct {
	ID               string            `json:"id"`
	SessionID        string            `json:"sessionId,omitempty"`
	ContextID        string            `json:"contextId,omitempty"`
	State            TaskState         `json:"status"`
	Messages         []Message         `json:"messages,omitempty"`
	Artifacts        []Artifact        `json:"artifacts,omitempty"`
	Metadata         map[string]string `json:"metadata,omitempty"`
	History          []TaskStateChange `json:"history,omitempty"`
	MaxTurns         int               `json:"maxTurns"`
	TurnCount        int               `json:"turnCount"`
	ApprovalDeadline *time.Time        `json:"approvalDeadline,omitempty"`
	CreatedAt        time.Time         `json:"createdAt"`
	UpdatedAt        time.Time         `json:"updatedAt"`
}

// TaskStateChange records a state transition.
type TaskStateChange struct {
	State     TaskState `json:"status"`
	Timestamp time.Time `json:"timestamp"`
	Message   string    `json:"message,omitempty"`
}

// Artifact is a terminal output produced by a task.
type Artifact struct {
	Name  string `json:"name,omitempty"`
	Parts []Part `json:"parts"`
	Index int    `json:"index"`
}

// validTransitions defines legal state transitions.
var validTransitions = map[TaskState][]TaskState{
	TaskStateSubmitted:     {TaskStateWorking, TaskStateCanceled, TaskStateFailed, TaskStateAuthRequired},
	TaskStateWorking:       {TaskStateCompleted, TaskStateFailed, TaskStateCanceled, TaskStateInputRequired, TaskStateAuthRequired},
	TaskStateInputRequired: {TaskStateWorking, TaskStateCanceled, TaskStateFailed},
	TaskStateAuthRequired:  {TaskStateWorking, TaskStateCanceled, TaskStateFailed},
	// Terminal states: no transitions out.
	TaskStateCompleted: {},
	TaskStateFailed:    {},
	TaskStateCanceled:  {},
}

// TransitionTo attempts to move the task to a new state.
// Enforces max turns limit and approval timeout.
func (t *Task) TransitionTo(newState TaskState, message string) error {
	// Max turns guard: prevent infinite loops.
	if t.MaxTurns > 0 && t.TurnCount >= t.MaxTurns {
		t.State = TaskStateFailed
		t.History = append(t.History, TaskStateChange{
			State:     TaskStateFailed,
			Timestamp: time.Now().UTC(),
			Message:   fmt.Sprintf("max turns exceeded (%d)", t.MaxTurns),
		})
		t.UpdatedAt = time.Now().UTC()
		return fmt.Errorf("max turns exceeded (%d)", t.MaxTurns)
	}

	// Approval timeout guard: fail if waiting too long.
	if t.ApprovalDeadline != nil && !t.ApprovalDeadline.IsZero() {
		if (t.State == TaskStateInputRequired || t.State == TaskStateAuthRequired) &&
			time.Now().UTC().After(*t.ApprovalDeadline) {
			t.State = TaskStateFailed
			t.History = append(t.History, TaskStateChange{
				State:     TaskStateFailed,
				Timestamp: time.Now().UTC(),
				Message:   "approval timeout expired",
			})
			t.UpdatedAt = time.Now().UTC()
			return fmt.Errorf("approval timeout expired")
		}
	}

	allowed, ok := validTransitions[t.State]
	if !ok {
		return fmt.Errorf("unknown current state: %s", t.State)
	}

	for _, s := range allowed {
		if s == newState {
			change := TaskStateChange{
				State:     newState,
				Timestamp: time.Now().UTC(),
				Message:   message,
			}
			t.History = append(t.History, change)
			t.State = newState
			t.TurnCount++
			t.UpdatedAt = time.Now().UTC()

			// Set approval deadline when entering approval-wait states.
			if newState == TaskStateInputRequired || newState == TaskStateAuthRequired {
				deadline := time.Now().UTC().Add(DefaultApprovalTimeout)
				t.ApprovalDeadline = &deadline
			} else {
				t.ApprovalDeadline = nil
			}

			return nil
		}
	}

	return fmt.Errorf("invalid transition: %s -> %s", t.State, newState)
}

// IsTerminal returns true if the task is in a terminal state.
func (t *Task) IsTerminal() bool {
	switch t.State {
	case TaskStateCompleted, TaskStateFailed, TaskStateCanceled:
		return true
	}
	return false
}

// AddArtifact appends an artifact to the task.
func (t *Task) AddArtifact(name string, parts []Part) {
	t.Artifacts = append(t.Artifacts, Artifact{
		Name:  name,
		Parts: parts,
		Index: len(t.Artifacts),
	})
	t.UpdatedAt = time.Now().UTC()
}

// TaskStore manages task lifecycle in memory.
type TaskStore struct {
	mu    sync.RWMutex
	tasks map[string]*Task
}

// NewTaskStore creates a new in-memory task store.
func NewTaskStore() *TaskStore {
	return &TaskStore{
		tasks: make(map[string]*Task),
	}
}

// Create registers a new task with initial submitted state.
// Returns an error if a task with the same ID already exists (idempotent guard).
func (s *TaskStore) Create(id string) (*Task, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if existing, ok := s.tasks[id]; ok {
		return existing, fmt.Errorf("duplicate task id: %s", id)
	}

	now := time.Now().UTC()
	t := &Task{
		ID:        id,
		State:     TaskStateSubmitted,
		Messages:  []Message{},
		Artifacts: []Artifact{},
		Metadata:  make(map[string]string),
		History: []TaskStateChange{
			{State: TaskStateSubmitted, Timestamp: now},
		},
		MaxTurns:  DefaultMaxTurns,
		CreatedAt: now,
		UpdatedAt: now,
	}

	s.tasks[id] = t
	return t, nil
}

// Get retrieves a task by ID.
func (s *TaskStore) Get(id string) (*Task, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	t, ok := s.tasks[id]
	return t, ok
}

// List returns all tasks.
func (s *TaskStore) List() []*Task {
	s.mu.RLock()
	defer s.mu.RUnlock()

	result := make([]*Task, 0, len(s.tasks))
	for _, t := range s.tasks {
		result = append(result, t)
	}
	return result
}

// Count returns the number of tasks.
func (s *TaskStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.tasks)
}

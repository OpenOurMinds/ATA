// Package a2a implements the Agent-to-Agent (A2A) protocol.
// It provides Agent Card discovery, JSON-RPC 2.0 transport,
// task lifecycle management, and message routing per the
// A2A specification (https://github.com/a2aproject/A2A).
package a2a

import (
	"encoding/json"
	"fmt"
	"time"
)

// AgentCard is the metadata document served at /.well-known/agent-card.json.
// It advertises the agent's identity, capabilities, and endpoints
// so that other agents can discover and interact with it.
type AgentCard struct {
	Name               string       `json:"name"`
	Description        string       `json:"description"`
	URL                string       `json:"url"`
	Version            string       `json:"version"`
	ProtocolVersion    string       `json:"protocolVersion"`
	Provider           *Provider    `json:"provider,omitempty"`
	DocumentationURL   string       `json:"documentationUrl,omitempty"`
	Capabilities       Capabilities `json:"capabilities"`
	Skills             []Skill      `json:"skills"`
	Authentication     AuthConfig   `json:"authentication"`
	DefaultInputModes  []string     `json:"defaultInputModes"`
	DefaultOutputModes []string     `json:"defaultOutputModes"`
}

// Provider identifies who published/operates the agent.
type Provider struct {
	Organization string `json:"organization"`
	URL          string `json:"url,omitempty"`
}

// Capabilities declares what protocol features the agent supports.
type Capabilities struct {
	Streaming          bool `json:"streaming"`
	PushNotifications  bool `json:"pushNotifications"`
	StateTransitionHistory bool `json:"stateTransitionHistory"`
}

// Skill describes a discrete capability the agent offers.
type Skill struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Tags        []string `json:"tags,omitempty"`
	InputModes  []string `json:"inputModes,omitempty"`
	OutputModes []string `json:"outputModes,omitempty"`
}

// AuthConfig describes the authentication requirements.
type AuthConfig struct {
	Schemes []AuthScheme `json:"schemes"`
}

// AuthScheme is a single authentication method.
type AuthScheme struct {
	Type string `json:"type"` // "apiKey", "oauth2", "none"
}

// NewAgentCard creates an AgentCard with sensible defaults.
func NewAgentCard(name, description, url, version string, skills []Skill) AgentCard {
	return AgentCard{
		Name:            name,
		Description:     description,
		URL:             url,
		Version:         version,
		ProtocolVersion: "0.2.0",
		Provider: &Provider{
			Organization: "OpenOurMinds",
			URL:          "https://github.com/OpenOurMinds/ATA",
		},
		Capabilities: Capabilities{
			Streaming:              true,
			PushNotifications:      true,
			StateTransitionHistory: true,
		},
		Skills: skills,
		Authentication: AuthConfig{
			Schemes: []AuthScheme{{Type: "none"}},
		},
		DefaultInputModes:  []string{"text", "data"},
		DefaultOutputModes: []string{"text", "data"},
	}
}

// MarshalJSON returns the Agent Card as indented JSON.
func (c AgentCard) MarshalJSON() ([]byte, error) {
	type Alias AgentCard
	return json.MarshalIndent(Alias(c), "", "  ")
}

// Validate checks that the Agent Card has required fields.
func (c AgentCard) Validate() error {
	if c.Name == "" {
		return fmt.Errorf("agent card: name is required")
	}
	if c.URL == "" {
		return fmt.Errorf("agent card: url is required")
	}
	if c.Version == "" {
		return fmt.Errorf("agent card: version is required")
	}
	if len(c.Skills) == 0 {
		return fmt.Errorf("agent card: at least one skill is required")
	}
	return nil
}

// AgentCardCreatedAt can be embedded for metadata tracking.
type AgentCardMeta struct {
	CreatedAt time.Time `json:"createdAt"`
	UpdatedAt time.Time `json:"updatedAt"`
}

package a2a

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"math"
	"net/http"
	"time"
)

// RetryConfig controls exponential backoff behavior.
type RetryConfig struct {
	MaxRetries  int           // Maximum number of retry attempts.
	BaseDelay   time.Duration // Initial delay before first retry.
	MaxDelay    time.Duration // Maximum delay cap.
	RetryOn503  bool          // Whether to retry on 503 Service Unavailable.
}

// DefaultRetryConfig returns sensible retry defaults.
func DefaultRetryConfig() RetryConfig {
	return RetryConfig{
		MaxRetries: 3,
		BaseDelay:  500 * time.Millisecond,
		MaxDelay:   30 * time.Second,
		RetryOn503: true,
	}
}

// Client is an A2A protocol client that sends requests to remote agents.
type Client struct {
	httpClient *http.Client
	logger     *slog.Logger
	retry      RetryConfig
	bearerToken string // OAuth 2.0 Bearer token for authenticated requests.
}

// NewClient creates a new A2A client with default retry config.
func NewClient(logger *slog.Logger) *Client {
	return &Client{
		httpClient: &http.Client{Timeout: 30 * time.Second},
		logger:     logger,
		retry:      DefaultRetryConfig(),
	}
}

// SetRetryConfig overrides the default retry configuration.
func (c *Client) SetRetryConfig(cfg RetryConfig) {
	c.retry = cfg
}

// SetBearerToken sets the OAuth 2.0 Bearer token for all requests.
func (c *Client) SetBearerToken(token string) {
	c.bearerToken = token
}

// DiscoverAgent fetches the Agent Card from a remote agent.
func (c *Client) DiscoverAgent(baseURL string) (*AgentCard, error) {
	resp, err := c.httpClient.Get(baseURL + "/.well-known/agent-card.json")
	if err != nil {
		return nil, fmt.Errorf("discover: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("discover: status %d", resp.StatusCode)
	}
	var card AgentCard
	if err := json.NewDecoder(resp.Body).Decode(&card); err != nil {
		return nil, fmt.Errorf("decode card: %w", err)
	}
	return &card, nil
}

// SendMessage sends a message/send request to a remote agent.
func (c *Client) SendMessage(agentURL string, params MessageSendParams) (*TaskResult, error) {
	req, err := NewRequest(MethodMessageSend, params)
	if err != nil {
		return nil, err
	}
	return c.doTaskRPC(agentURL, req)
}

// GetTask queries the status of a task on a remote agent.
func (c *Client) GetTask(agentURL string, taskID string) (*TaskResult, error) {
	req, err := NewRequest(MethodTasksGet, TaskGetParams{TaskID: taskID})
	if err != nil {
		return nil, err
	}
	return c.doTaskRPC(agentURL, req)
}

// CancelTask cancels a task on a remote agent.
func (c *Client) CancelTask(agentURL string, taskID string) (*TaskResult, error) {
	req, err := NewRequest(MethodTasksCancel, TaskCancelParams{TaskID: taskID})
	if err != nil {
		return nil, err
	}
	return c.doTaskRPC(agentURL, req)
}

// doTaskRPC sends a JSON-RPC request with exponential backoff retry on 503.
func (c *Client) doTaskRPC(agentURL string, req *Request) (*TaskResult, error) {
	body, _ := json.Marshal(req)

	var lastErr error
	for attempt := 0; attempt <= c.retry.MaxRetries; attempt++ {
		if attempt > 0 {
			delay := c.backoffDelay(attempt)
			c.logger.Info("retrying after backoff",
				"attempt", attempt,
				"delay", delay.String(),
				"method", req.Method,
			)
			time.Sleep(delay)
		}

		c.logger.Debug("a2a rpc", "method", req.Method, "url", agentURL, "attempt", attempt)

		httpReq, err := http.NewRequest("POST", agentURL, bytes.NewReader(body))
		if err != nil {
			return nil, fmt.Errorf("create request: %w", err)
		}
		httpReq.Header.Set("Content-Type", "application/json")
		if c.bearerToken != "" {
			httpReq.Header.Set("Authorization", "Bearer "+c.bearerToken)
		}

		httpResp, err := c.httpClient.Do(httpReq)
		if err != nil {
			lastErr = fmt.Errorf("rpc to %s: %w", agentURL, err)
			continue
		}

		// Retry on 503 Service Unavailable.
		if httpResp.StatusCode == http.StatusServiceUnavailable && c.retry.RetryOn503 {
			httpResp.Body.Close()
			lastErr = fmt.Errorf("service unavailable (503) from %s", agentURL)
			continue
		}

		respBody, err := io.ReadAll(httpResp.Body)
		httpResp.Body.Close()
		if err != nil {
			lastErr = fmt.Errorf("read response: %w", err)
			continue
		}

		var resp Response
		if err := json.Unmarshal(respBody, &resp); err != nil {
			return nil, fmt.Errorf("unmarshal: %w", err)
		}
		if resp.Error != nil {
			return nil, fmt.Errorf("rpc error %d: %s", resp.Error.Code, resp.Error.Message)
		}
		rb, _ := json.Marshal(resp.Result)
		var result TaskResult
		if err := json.Unmarshal(rb, &result); err != nil {
			return nil, fmt.Errorf("unmarshal result: %w", err)
		}
		return &result, nil
	}

	return nil, fmt.Errorf("all %d retries exhausted: %w", c.retry.MaxRetries, lastErr)
}

// backoffDelay computes exponential backoff with jitter.
func (c *Client) backoffDelay(attempt int) time.Duration {
	delay := time.Duration(float64(c.retry.BaseDelay) * math.Pow(2, float64(attempt-1)))
	if delay > c.retry.MaxDelay {
		delay = c.retry.MaxDelay
	}
	return delay
}

package a2a

import (
	"encoding/json"
	"fmt"
	"sync/atomic"
)

// JSON-RPC 2.0 protocol version.
const JSONRPCVersion = "2.0"

// Standard A2A methods.
const (
	MethodMessageSend   = "message/send"
	MethodMessageStream = "message/stream"
	MethodTasksGet      = "tasks/get"
	MethodTasksCancel   = "tasks/cancel"

	// Push notification configuration methods.
	MethodPushNotifConfigSet = "tasks/pushNotificationConfig/set"
	MethodPushNotifConfigGet = "tasks/pushNotificationConfig/get"
)

var requestCounter atomic.Int64

// Request is a JSON-RPC 2.0 request.
type Request struct {
	JSONRPC string          `json:"jsonrpc"`
	Method  string          `json:"method"`
	Params  json.RawMessage `json:"params,omitempty"`
	ID      interface{}     `json:"id"`
}

// Response is a JSON-RPC 2.0 response.
type Response struct {
	JSONRPC string      `json:"jsonrpc"`
	Result  interface{} `json:"result,omitempty"`
	Error   *RPCError   `json:"error,omitempty"`
	ID      interface{} `json:"id"`
}

// RPCError is a JSON-RPC 2.0 error object.
type RPCError struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// Standard JSON-RPC error codes.
const (
	ErrCodeParseError     = -32700
	ErrCodeInvalidRequest = -32600
	ErrCodeMethodNotFound = -32601
	ErrCodeInvalidParams  = -32602
	ErrCodeInternal       = -32603

	// A2A-specific error codes.
	ErrCodeTaskNotFound    = -32001
	ErrCodeTaskFailed      = -32002
	ErrCodeUnsupported     = -32003
	ErrCodeAuthRequired    = -32004
	ErrCodePushNotifFailed = -32005
)

// NewRequest creates a well-formed JSON-RPC 2.0 request.
func NewRequest(method string, params interface{}) (*Request, error) {
	id := requestCounter.Add(1)

	var rawParams json.RawMessage
	if params != nil {
		b, err := json.Marshal(params)
		if err != nil {
			return nil, fmt.Errorf("marshal params: %w", err)
		}
		rawParams = b
	}

	return &Request{
		JSONRPC: JSONRPCVersion,
		Method:  method,
		Params:  rawParams,
		ID:      id,
	}, nil
}

// SuccessResponse creates a success response for a request.
func SuccessResponse(id interface{}, result interface{}) Response {
	return Response{
		JSONRPC: JSONRPCVersion,
		Result:  result,
		ID:      id,
	}
}

// ErrorResponse creates an error response for a request.
func ErrorResponse(id interface{}, code int, message string) Response {
	return Response{
		JSONRPC: JSONRPCVersion,
		Error: &RPCError{
			Code:    code,
			Message: message,
		},
		ID: id,
	}
}

// Validate checks that a request conforms to JSON-RPC 2.0.
func (r *Request) Validate() error {
	if r.JSONRPC != JSONRPCVersion {
		return fmt.Errorf("jsonrpc must be %q, got %q", JSONRPCVersion, r.JSONRPC)
	}
	if r.Method == "" {
		return fmt.Errorf("method is required")
	}
	if r.ID == nil {
		return fmt.Errorf("id is required")
	}
	return nil
}

// ParseParams unmarshals the request params into dst.
func (r *Request) ParseParams(dst interface{}) error {
	if r.Params == nil {
		return fmt.Errorf("params is empty")
	}
	return json.Unmarshal(r.Params, dst)
}

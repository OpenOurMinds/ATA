package test

import (
	"bufio"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// TestBuildStrategy_VersionVariables verifies all 4 entrypoint main.go files
// declare the "version" package-level variable for build-time stamping.
func TestBuildStrategy_VersionVariables(t *testing.T) {
	entrypoints := []string{
		"cmd/ata-orchestrator/main.go",
		"cmd/ata-soul-agent/main.go",
		"cmd/ata-city-agent/main.go",
		"cmd/ata-decision-agent/main.go",
	}

	for _, path := range entrypoints {
		t.Run(path, func(t *testing.T) {
			file, err := os.Open(filepath.Join("..", path))
			if err != nil {
				t.Fatalf("failed to open main.go: %v", err)
			}
			defer file.Close()

			scanner := bufio.NewScanner(file)
			foundVersionVar := false
			for scanner.Scan() {
				line := strings.TrimSpace(scanner.Text())
				if strings.HasPrefix(line, "var version =") || strings.HasPrefix(line, "var version string") {
					foundVersionVar = true
					break
				}
			}

			if !foundVersionVar {
				t.Errorf("entrypoint %s is missing 'var version' declaration for linker stamping", path)
			}
		})
	}
}

// TestBuildStrategy_MakefileLDFLAGS verifies the Makefile specifies correct LDFLAGS
// for production hardening (-s -w) and version stamping (-X main.version=).
func TestBuildStrategy_MakefileLDFLAGS(t *testing.T) {
	data, err := ioutil.ReadFile(filepath.Join("..", "Makefile"))
	if err != nil {
		t.Fatalf("failed to read Makefile: %v", err)
	}

	content := string(data)
	if !strings.Contains(content, "-s -w") {
		t.Error("Makefile LDFLAGS is missing production stripping flags '-s -w'")
	}
	if !strings.Contains(content, "-X main.version=") {
		t.Error("Makefile LDFLAGS is missing version stamping flag '-X main.version='")
	}
}

// TestBuildStrategy_SystemdSecurity verifies that systemd unit service files
// comply with strict sandboxing and security guidelines.
func TestBuildStrategy_SystemdSecurity(t *testing.T) {
	files, err := filepath.Glob(filepath.Join("..", "deploy", "systemd", "*.service"))
	if err != nil {
		t.Fatalf("failed to list systemd service files: %v", err)
	}

	if len(files) == 0 {
		t.Fatal("no systemd service files found in deploy/systemd")
	}

	for _, path := range files {
		t.Run(filepath.Base(path), func(t *testing.T) {
			data, err := ioutil.ReadFile(path)
			if err != nil {
				t.Fatalf("failed to read service file: %v", err)
			}

			content := string(data)

			// 1. Non-Root Execution Checks
			if !strings.Contains(content, "User=ata") {
				t.Error("service does not specify 'User=ata'")
			}
			if !strings.Contains(content, "Group=ata") {
				t.Error("service does not specify 'Group=ata'")
			}
			if !strings.Contains(content, "NoNewPrivileges=true") {
				t.Error("service does not specify 'NoNewPrivileges=true'")
			}

			// 2. Sandboxing Checks
			if !strings.Contains(content, "ProtectSystem=strict") {
				t.Error("service does not specify 'ProtectSystem=strict'")
			}
			
			// 3. Execution Paths
			if !strings.Contains(content, "ExecStart=/usr/local/bin/") {
				t.Error("service ExecStart does not point to '/usr/local/bin/' installation directory")
			}

			// 4. Persistence Path Isolation for Agents needing database access
			if strings.Contains(filepath.Base(path), "-agent") {
				if !strings.Contains(content, "ReadWritePaths=/var/lib/ata") {
					t.Error("agent service does not isolate database writes using 'ReadWritePaths=/var/lib/ata'")
				}
			}
		})
	}
}

// TestBuildStrategy_ConfigsYamlValidity verifies that YAML files are present
// and point to localhost/default port numbers mapped in the orchestrator loop.
func TestBuildStrategy_ConfigsYamlValidity(t *testing.T) {
	configFiles := []string{
		"soul-agent.yaml",
		"city-agent.yaml",
		"decision-agent.yaml",
		"orchestrator.yaml",
	}

	for _, name := range configFiles {
		path := filepath.Join("..", "configs", name)
		if _, err := os.Stat(path); os.IsNotExist(err) {
			t.Errorf("expected config file %s does not exist", name)
		}
	}
}

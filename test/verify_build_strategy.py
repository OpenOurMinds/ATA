#!/usr/bin/env python3
import os
import sys
import glob

def print_result(check_name, success, error_msg=""):
    status_icon = "✅" if success else "❌"
    status_text = "PASS" if success else "FAIL"
    print(f"{status_icon} [{status_text}] {check_name}")
    if not success and error_msg:
        print(f"    Error: {error_msg}")

def test_version_variables():
    print("\n--- Running Version Variable Checks ---")
    entrypoints = [
        "cmd/ata-orchestrator/main.go",
        "cmd/ata-soul-agent/main.go",
        "cmd/ata-city-agent/main.go",
        "cmd/ata-decision-agent/main.go",
    ]
    all_pass = True
    for path in entrypoints:
        full_path = os.path.join(os.path.dirname(__file__), "..", path)
        if not os.path.exists(full_path):
            print_result(f"Check version in {path}", False, f"File {path} does not exist.")
            all_pass = False
            continue
        
        found = False
        with open(full_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("var version =") or line.startswith("var version string"):
                    found = True
                    break
        print_result(f"Check version in {path}", found, f"No 'var version' variable declared for build stamping.")
        if not found:
            all_pass = False
    return all_pass

def test_makefile_ldflags():
    print("\n--- Running Makefile LDFLAGS Checks ---")
    makefile_path = os.path.join(os.path.dirname(__file__), "..", "Makefile")
    if not os.path.exists(makefile_path):
        print_result("Check Makefile existence", False, "Makefile not found.")
        return False
    
    all_pass = True
    with open(makefile_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    has_stripping = "-s -w" in content
    has_stamping = "-X main.version=" in content
    
    print_result("Makefile contains production stripping flags (-s -w)", has_stripping, "Missing '-s -w' compiler optimization flags.")
    print_result("Makefile contains version stamping flag (-X main.version=)", has_stamping, "Missing '-X main.version=' stamping flag.")
    
    return has_stripping and has_stamping

def test_systemd_services():
    print("\n--- Running Systemd Service Security Checks ---")
    services_pattern = os.path.join(os.path.dirname(__file__), "..", "deploy", "systemd", "*.service")
    files = glob.glob(services_pattern)
    if not files:
        print_result("Systemd service list", False, "No systemd service files found in deploy/systemd")
        return False
    
    all_pass = True
    for path in files:
        basename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # User and Group Check
        has_user = "User=ata" in content
        has_group = "Group=ata" in content
        has_no_new_privs = "NoNewPrivileges=true" in content
        has_strict_system = "ProtectSystem=strict" in content
        has_exec_path = "ExecStart=/usr/local/bin/" in content
        
        # Write isolation check for agent units
        has_write_isolation = True
        if "-agent" in basename:
            has_write_isolation = "ReadWritePaths=/var/lib/ata" in content

        print_result(f"{basename} runs as non-root (User=ata, Group=ata, NoNewPrivileges=true)", 
                     has_user and has_group and has_no_new_privs, 
                     f"Security properties missing or wrong in {basename}.")
        print_result(f"{basename} sandboxing (ProtectSystem=strict)", has_strict_system, f"Missing ProtectSystem=strict sandboxing.")
        print_result(f"{basename} points to /usr/local/bin/", has_exec_path, f"ExecStart path wrong in {basename}.")
        
        if "-agent" in basename:
            print_result(f"{basename} database writes isolated", has_write_isolation, f"Missing 'ReadWritePaths=/var/lib/ata'.")

        if not (has_user and has_group and has_no_new_privs and has_strict_system and has_exec_path and has_write_isolation):
            all_pass = False
            
    return all_pass

def test_config_files():
    print("\n--- Running Config YAML Consistency Checks ---")
    config_files = ["soul-agent.yaml", "city-agent.yaml", "decision-agent.yaml", "orchestrator.yaml"]
    all_pass = True
    for name in config_files:
        path = os.path.join(os.path.dirname(__file__), "..", "configs", name)
        exists = os.path.exists(path)
        print_result(f"Check config file {name}", exists, f"Config file configs/{name} does not exist.")
        if not exists:
            all_pass = False
    return all_pass

def main():
    print("🧬 ATA Build Strategy Compliance Verifier")
    print("=========================================")
    
    v1 = test_version_variables()
    v2 = test_makefile_ldflags()
    v3 = test_systemd_services()
    v4 = test_config_files()
    
    print("\n=========================================")
    if v1 and v2 and v3 and v4:
        print("✅ SUCCESS: All build strategy validation tests passed successfully!")
        sys.exit(0)
    else:
        print("❌ FAILURE: Build strategy validation tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()

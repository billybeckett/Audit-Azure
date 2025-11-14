# Logging and Verbose Mode

## Overview

The Azure Audit Tool now includes comprehensive logging that tracks every Azure CLI command executed, timing information, and detailed debugging output.

## Features

### ✅ What is Logged

1. **Every Azure CLI Command** - Full command strings before execution
2. **Execution Timing** - How long each command takes
3. **Command Results** - Success/failure and response data
4. **Error Details** - Full error messages and stack traces
5. **JSON Responses** - Azure CLI output (in verbose mode)
6. **Summary Statistics** - Total commands, total time

### 📁 Log Files

All logs are automatically saved to timestamped files:

```
logs/azure_audit_2025-11-14_10-30-45.log
```

The log file location is printed at the start of every audit run.

## Usage

### Normal Mode (Default)

```bash
# Run audit - logs to file only
./audit-azure.sh
```

**What you see:**
- High-level progress messages
- Resource counts
- Success/error summaries

**What is logged to file:**
- All of the above PLUS
- Every Azure CLI command
- Execution times
- Error details

### Verbose Mode

```bash
# Run audit with verbose output
./audit-azure.sh --verbose

# Or use short flag
./audit-azure.sh -v
```

**What you see:**
- Everything from normal mode
- Every Azure CLI command as it executes
- Timing for each command
- Detailed error messages
- JSON response summaries

**What is logged to file:**
- Everything + full JSON responses

### Watch Logs in Real-Time

At the start of each audit, the tool prints:

```
📝 LOGGING:
   Log file: /path/to/logs/azure_audit_2025-11-14_10-30-45.log
   To watch in real-time, open a new terminal and run:
   tail -f /path/to/logs/azure_audit_2025-11-14_10-30-45.log
```

**To monitor in real-time:**

1. Copy the `tail -f` command shown
2. Open a new terminal window
3. Paste and run the command
4. Watch as commands execute

Example:
```bash
# Terminal 1: Run the audit
./audit-azure.sh --verbose

# Terminal 2: Watch the log file
tail -f logs/azure_audit_2025-11-14_10-30-45.log
```

## Log File Format

### Example Log Entries

```log
2025-11-14 10:30:45 - INFO - ================================================================================
2025-11-14 10:30:45 - INFO - Azure Infrastructure Audit - Logging Started
2025-11-14 10:30:45 - INFO - Verbose mode: False
2025-11-14 10:30:45 - INFO - ================================================================================
2025-11-14 10:30:46 - INFO - --------------------------------------------------------------------------------
2025-11-14 10:30:46 - INFO - SECTION: Azure Resource Discovery and Audit
2025-11-14 10:30:46 - INFO - --------------------------------------------------------------------------------
2025-11-14 10:30:47 - INFO - [Command #1] az account list --output json
2025-11-14 10:30:48 - INFO - [Result] Success in 1.23s
2025-11-14 10:30:48 - DEBUG - [Response] Received 2 items
2025-11-14 10:30:48 - INFO - [Command #2] az group list --subscription abc-123 --output json
2025-11-14 10:30:50 - INFO - [Result] Success in 1.87s
2025-11-14 10:30:50 - DEBUG - [Response] Received 15 items
2025-11-14 10:30:51 - INFO - [Command #3] az network vnet list --subscription abc-123 --output json
2025-11-14 10:30:53 - INFO - [Result] Success in 2.14s
2025-11-14 10:30:53 - DEBUG - [Response] Received 5 items
...
2025-11-14 10:45:23 - INFO - ================================================================================
2025-11-14 10:45:23 - INFO - AUDIT COMPLETE - Logging Summary
2025-11-14 10:45:23 - INFO - Total commands executed: 127
2025-11-14 10:45:23 - INFO - Total execution time: 234.56s
2025-11-14 10:45:23 - INFO - Log file: logs/azure_audit_2025-11-14_10-30-45.log
2025-11-14 10:45:23 - INFO - ================================================================================
```

## Python Script Usage

You can also run the Python script directly with flags:

```bash
# Normal mode
python3 scripts/azure_discovery.py

# Verbose mode
python3 scripts/azure_discovery.py --verbose

# Custom log directory
python3 scripts/azure_discovery.py --log-dir /custom/path

# Custom output directory
python3 scripts/azure_discovery.py --output-dir /custom/docs

# All options together
python3 scripts/azure_discovery.py --verbose --log-dir ./mylogs --output-dir ./mydocs
```

## Command-Line Options

### Shell Script

```bash
./audit-azure.sh [OPTIONS]

OPTIONS:
  --login         Perform Azure CLI login before running audit
  -v, --verbose   Enable verbose mode (shows all Azure CLI commands)
  --help          Display help message
```

### Python Script

```bash
python3 scripts/azure_discovery.py [OPTIONS]

OPTIONS:
  -v, --verbose       Enable verbose output
  --log-dir DIR       Directory for log files (default: logs/)
  --output-dir DIR    Directory for output docs (default: docs/)
  -h, --help          Show help message
```

## Examples

### Example 1: Standard Audit

```bash
./audit-azure.sh
```

Output:
```
════════════════════════════════════════════════════════════════════════
  Azure Infrastructure Audit Tool
════════════════════════════════════════════════════════════════════════
ℹ Checking Azure CLI installation...
✓ Azure CLI installed (version 2.79.0)
ℹ Checking Python installation...
✓ Python 3 installed (version 3.13.9)
ℹ Checking Azure authentication...
✓ Authenticated to Azure (subscription: Production)
ℹ Starting Azure infrastructure discovery...

════════════════════════════════════════════════════════════════════════
Azure Resource Discovery and Audit
════════════════════════════════════════════════════════════════════════
Started at: 2025-11-14 10:30:45

📝 LOGGING:
   Log file: logs/azure_audit_2025-11-14_10-30-45.log
   To watch in real-time, open a new terminal and run:
   tail -f logs/azure_audit_2025-11-14_10-30-45.log

📋 Discovering Azure Subscriptions...
   Found 2 subscription(s)
...
```

### Example 2: Verbose Audit

```bash
./audit-azure.sh --verbose
```

Output includes all the above PLUS:
```
    🔧 Executing: az account list --output json
    ✓ Completed in 1.23s
    📦 Received 2 items
    🔧 Executing: az group list --subscription abc-123 --output json
    ✓ Completed in 1.87s
    📦 Received 15 items
...
```

### Example 3: Watch Logs While Running

```bash
# Terminal 1
./audit-azure.sh

# Terminal 2 (copy the tail command from Terminal 1 output)
tail -f logs/azure_audit_2025-11-14_10-30-45.log
```

### Example 4: Login and Verbose

```bash
./audit-azure.sh --login --verbose
```

## Logging Summary

At the end of each audit, you'll see:

```
📊 Logging Summary:
   Commands executed: 127
   Total time: 234.56s
   Log file: logs/azure_audit_2025-11-14_10-30-45.log
```

This tells you:
- How many Azure CLI commands were executed
- Total time spent on Azure CLI commands
- Where the complete log file is located

## Log File Management

### Viewing Old Logs

```bash
# List all log files
ls -lah logs/

# View a specific log
cat logs/azure_audit_2025-11-14_10-30-45.log

# Search logs for errors
grep -i error logs/*.log

# Search logs for specific commands
grep "az network" logs/*.log
```

### Cleaning Up Logs

```bash
# Delete logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete

# Delete all logs
rm -rf logs/*.log

# Archive old logs
tar -czf logs_archive_$(date +%Y%m%d).tar.gz logs/
```

## Troubleshooting with Logs

### Find Failed Commands

```bash
grep -B 2 "ERROR" logs/azure_audit_*.log
```

### See All Executed Commands

```bash
grep "Command #" logs/azure_audit_*.log
```

### Find Slow Commands

```bash
grep "Success in" logs/azure_audit_*.log | grep -E "[0-9]{2,}\.[0-9]+s"
```

### Extract Timing Data

```bash
grep "Total execution time" logs/azure_audit_*.log
```

## Benefits

1. **Debugging** - See exactly what commands failed and why
2. **Performance** - Identify slow operations
3. **Audit Trail** - Complete record of what was queried
4. **Reproducibility** - Replay exact commands if needed
5. **Transparency** - Know exactly what the tool is doing

## Privacy & Security

**Important:** Log files contain:
- ✅ Azure CLI commands executed
- ✅ Subscription IDs and resource names
- ✅ Error messages
- ❌ NO credentials or secrets
- ❌ NO actual Key Vault secrets
- ❌ NO passwords or keys

Log files are automatically excluded from Git (in `.gitignore`).

---

**Tip:** Always use verbose mode (`--verbose`) when troubleshooting issues!

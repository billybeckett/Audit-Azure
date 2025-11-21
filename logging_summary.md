# 🎉 Logging Features Added!

## What's New

Your Azure Audit Tool now has **comprehensive logging** that tracks every Azure CLI command and shows you exactly what's happening behind the scenes!

## ✅ What Was Added

### 1. **Complete Command Logging**
- Every `az` command is logged before execution
- Example: `az network vnet list --subscription abc-123 --output json`
- Execution time for each command
- Success/failure status
- Response data summaries

### 2. **Verbose Mode**
- New `-v` or `--verbose` flag
- Shows all commands in real-time as they execute
- Displays timing information
- Shows response summaries

### 3. **Log Files**
- Automatically saved to `logs/` directory
- Timestamped filenames: `azure_audit_2025-11-14_10-30-45.log`
- Contains complete execution history
- Includes error stack traces

### 4. **Startup Message**
- **Prints log file location at startup** ✨
- **Shows exact `tail -f` command to watch logs** ✨
- Makes it easy to monitor in real-time

### 5. **Summary Statistics**
- Total commands executed
- Total execution time
- Log file location

## 🚀 How to Use

### Normal Mode (Logs to File Only)

```bash
./audit-azure.sh
```

**What you see:**
```
════════════════════════════════════════════════════════════════════════
  Azure Infrastructure Audit Tool
════════════════════════════════════════════════════════════════════════
...
📝 LOGGING:
   Log file: logs/azure_audit_2025-11-14_10-30-45.log
   To watch in real-time, open a new terminal and run:
   tail -f logs/azure_audit_2025-11-14_10-30-45.log

📋 Discovering Azure Subscriptions...
   Found 2 subscription(s)
...
```

### Verbose Mode (See Everything!)

```bash
./audit-azure.sh --verbose
```

**What you see:**
```
📝 LOGGING:
   Log file: logs/azure_audit_2025-11-14_10-30-45.log
   To watch in real-time, open a new terminal and run:
   tail -f logs/azure_audit_2025-11-14_10-30-45.log

📋 Discovering Azure Subscriptions...
    🔧 Executing: az account list --output json
    ✓ Completed in 1.23s
    📦 Received 2 items
   Found 2 subscription(s)

📦 Processing subscription: Production
   Subscription ID: abc-123...

   🌐 Discovering Networking Resources...
    🔧 Executing: az network vnet list --subscription abc-123 --output json
    ✓ Completed in 2.14s
    📦 Received 5 items
    🔧 Executing: az network nsg list --subscription abc-123 --output json
    ✓ Completed in 1.87s
    📦 Received 12 items
    ...
```

### Watch Logs in Real-Time (Recommended!)

**Terminal 1:**
```bash
./audit-azure.sh
```

**Terminal 2** (copy the command shown in Terminal 1):
```bash
tail -f logs/azure_audit_2025-11-14_10-30-45.log
```

This lets you see every command as it executes!

## 📊 End Summary

At the end of each audit:

```
📊 Logging Summary:
   Commands executed: 127
   Total time: 234.56s
   Log file: logs/azure_audit_2025-11-14_10-30-45.log
```

## 📄 Log File Example

```log
2025-11-14 10:30:45 - INFO - ===============================================================================
2025-11-14 10:30:45 - INFO - Azure Infrastructure Audit - Logging Started
2025-11-14 10:30:45 - INFO - Verbose mode: False
2025-11-14 10:30:45 - INFO - ===============================================================================
2025-11-14 10:30:47 - INFO - [Command #1] az account list --output json
2025-11-14 10:30:48 - INFO - [Result] Success in 1.23s
2025-11-14 10:30:48 - DEBUG - [Response] Received 2 items
2025-11-14 10:30:48 - INFO - [Command #2] az group list --subscription abc-123 --output json
2025-11-14 10:30:50 - INFO - [Result] Success in 1.87s
2025-11-14 10:30:50 - DEBUG - [Response] Received 15 items
2025-11-14 10:30:51 - INFO - [Command #3] az network vnet list --subscription abc-123 --output json
2025-11-14 10:30:53 - INFO - [Result] Success in 2.14s
...
```

## 🎯 Use Cases

### 1. **Debugging**
```bash
# Run in verbose mode to see exactly what fails
./audit-azure.sh --verbose

# Or check the log file
grep -i error logs/azure_audit_*.log
```

### 2. **Performance Monitoring**
```bash
# See which commands are slow
grep "Success in" logs/azure_audit_*.log | grep -E "[0-9]{2,}\.[0-9]+s"
```

### 3. **Audit Trail**
```bash
# See all commands executed
grep "Command #" logs/azure_audit_*.log
```

### 4. **Troubleshooting**
```bash
# Find failed commands
grep -B 2 "ERROR" logs/azure_audit_*.log
```

## 📚 Files Changed

**New Files:**
- `scripts/utils/logger.py` - Centralized logging system
- `scripts/utils/__init__.py` - Utils package
- `LOGGING.md` - Complete logging documentation
- `LOGGING_SUMMARY.md` - This file

**Updated Files:**
- `scripts/azure_discovery.py` - Added logging initialization and summary
- `scripts/discovery/*.py` - All discovery modules now use logger
- `audit-azure.sh` - Added --verbose flag support

## 🔧 Command Options

### Shell Script

```bash
./audit-azure.sh [OPTIONS]

OPTIONS:
  --login         Perform Azure CLI login before running audit
  -v, --verbose   Enable verbose mode ⭐ NEW!
  --help          Display help message
```

### Python Script

```bash
python3 scripts/azure_discovery.py [OPTIONS]

OPTIONS:
  -v, --verbose       Enable verbose output ⭐ NEW!
  --log-dir DIR       Directory for log files (default: logs/)
  --output-dir DIR    Directory for output docs (default: docs/)
```

## 💡 Pro Tips

1. **Always use verbose mode when troubleshooting:**
   ```bash
   ./audit-azure.sh --verbose
   ```

2. **Watch logs in real-time for large audits:**
   ```bash
   # Terminal 1
   ./audit-azure.sh

   # Terminal 2
   tail -f logs/azure_audit_TIMESTAMP.log
   ```

3. **Search logs for specific resources:**
   ```bash
   grep "az network" logs/*.log
   grep "virtual machine" logs/*.log
   ```

4. **Archive old logs:**
   ```bash
   tar -czf logs_archive.tar.gz logs/
   ```

## 🔒 Security

**Log files contain:**
- ✅ Command strings
- ✅ Subscription IDs
- ✅ Resource names
- ❌ NO credentials
- ❌ NO secrets
- ❌ NO passwords

Logs are excluded from Git (`.gitignore`).

## 📖 Documentation

For complete logging documentation, see:
- **[LOGGING.md](LOGGING.md)** - Full documentation
- **[README.md](README.md)** - Main documentation
- **[EXAMPLES.md](EXAMPLES.md)** - Usage examples

## ✅ All Changes Pushed to GitHub

All changes have been committed and pushed to:
**https://github.com/billybeckett/Audit-Azure**

Commit: `Add comprehensive logging and verbose mode`

---

## 🎉 Try It Now!

```bash
# Login and run with verbose mode
./audit-azure.sh --login --verbose
```

**You'll see exactly what commands are being executed!**

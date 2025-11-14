# Quick Start Guide

Get started with the Azure Infrastructure Audit Tool in under 5 minutes!

## Step 1: Verify Prerequisites

```bash
# Check if Azure CLI is installed
az --version

# If not installed, install it:
# macOS:
brew install azure-cli
```

## Step 2: Authenticate to Azure

```bash
# Login to your Azure account
az login

# This will open a browser window for authentication
# After successful login, you'll see your subscriptions listed
```

## Step 3: Run the Audit

```bash
# Navigate to the project directory
cd /Users/williambeckett/Documents/Projects/Audit-Azure

# Run the audit script
./audit-azure.sh
```

**That's it!** The tool will now:
1. Discover all subscriptions
2. Enumerate all resources in each subscription
3. Generate comprehensive markdown documentation
4. Save raw JSON data for further analysis

## Step 4: View the Results

```bash
# Open the main report
open docs/README.md

# Or browse the docs directory
cd docs
ls -la
```

## What You'll Get

After the audit completes, you'll find:

```
docs/
├── README.md                 # Executive summary and index
├── resources/
│   ├── subscriptions.md     # Subscription details
│   ├── networking.md        # All networking resources
│   ├── compute.md           # VMs, App Services, etc.
│   ├── storage.md           # Storage accounts and disks
│   ├── databases.md         # All database services
│   ├── dns.md               # DNS zones and records
│   └── security.md          # Key Vaults, security settings
└── data/
    └── azure_audit_*.json   # Raw JSON data
```

## Common Scenarios

### First Time Running

```bash
# Login and run in one command
./audit-azure.sh --login
```

### Multiple Subscriptions

```bash
# List all subscriptions
az account list --output table

# Set a specific subscription (optional)
az account set --subscription "Production"

# Run the audit
./audit-azure.sh
```

### Scheduled Audits

Create a cron job to run regular audits:

```bash
# Edit crontab
crontab -e

# Add this line to run weekly on Monday at 2 AM
0 2 * * 1 cd /Users/williambeckett/Documents/Projects/Audit-Azure && ./audit-azure.sh
```

### Export to GitHub

```bash
# Initialize git repository
git init

# Add files
git add .

# Commit
git commit -m "Initial Azure infrastructure audit"

# Push to GitHub (after creating a repository)
git remote add origin https://github.com/yourusername/azure-audit.git
git push -u origin main
```

## Troubleshooting Quick Fixes

### "command not found: az"
```bash
# Install Azure CLI
brew install azure-cli
```

### "Please run 'az login'"
```bash
# Authenticate to Azure
az login
```

### "Permission denied"
```bash
# Make the script executable
chmod +x audit-azure.sh
```

### "No subscriptions found"
```bash
# Verify authentication
az account show

# List available subscriptions
az account list --output table
```

## Next Steps

- Review the generated documentation in `docs/`
- Check `docs/data/` for raw JSON exports
- Customize the reports by editing `scripts/reports/markdown_generator.py`
- Add this to your CI/CD pipeline for regular audits
- Share the documentation with your team

## Tips

1. **Regular Audits**: Run this monthly to track infrastructure changes
2. **Version Control**: Keep reports in Git to track changes over time
3. **Team Sharing**: Share the `docs/` folder with your team
4. **Compliance**: Use reports for SOC2, ISO27001, etc. compliance
5. **Cost Optimization**: Review compute and storage resources for savings opportunities

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review Azure CLI docs: https://docs.microsoft.com/cli/azure/
- Ensure you have appropriate Azure permissions (Reader role minimum)

---

**Happy Auditing!** 🎉

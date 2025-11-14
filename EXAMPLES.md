# Azure Audit Tool - Usage Examples

## Basic Usage

### First Time Setup

```bash
# 1. Navigate to the project directory
cd /Users/williambeckett/Documents/Projects/Audit-Azure

# 2. Make sure the script is executable (already done)
ls -la audit-azure.sh

# 3. Login to Azure
az login

# 4. Run the audit
./audit-azure.sh
```

### Quick Run (Login + Audit)

```bash
# Login and run audit in one command
./audit-azure.sh --login
```

### Check Authentication

```bash
# See which account you're logged in with
az account show

# List all accessible subscriptions
az account list --output table

# Set a specific subscription
az account set --subscription "Production"
```

## Advanced Usage

### Audit Specific Subscription

```bash
# Set the subscription you want to audit
az account set --subscription "Your Subscription Name"

# Run the audit
./audit-azure.sh

# The tool will still see other subscriptions but can focus on one
```

### Run Python Script Directly

```bash
# Navigate to scripts directory
cd scripts

# Run with Python
python3 azure_discovery.py

# With more verbose output
python3 -u azure_discovery.py
```

### Schedule Regular Audits

```bash
# Open crontab editor
crontab -e

# Add one of these lines:

# Every Monday at 2 AM
0 2 * * 1 cd /Users/williambeckett/Documents/Projects/Audit-Azure && ./audit-azure.sh

# Every day at 3 AM
0 3 * * * cd /Users/williambeckett/Documents/Projects/Audit-Azure && ./audit-azure.sh

# First day of every month at midnight
0 0 1 * * cd /Users/williambeckett/Documents/Projects/Audit-Azure && ./audit-azure.sh
```

### Keep Historical Records

```bash
# Create a dated backup before running new audit
DATE=$(date +%Y%m%d)
cp -r docs docs_backup_$DATE

# Run new audit
./audit-azure.sh

# Compare changes
diff -r docs_backup_$DATE/resources docs/resources
```

### Version Control Workflow

```bash
# Initialize Git repository
git init

# Add all files
git add .

# First commit
git commit -m "Initial Azure infrastructure audit"

# Create GitHub repository, then:
git remote add origin https://github.com/yourusername/azure-audit.git
git branch -M main
git push -u origin main

# For subsequent audits:
./audit-azure.sh
git add docs/
git commit -m "Azure audit - $(date +%Y-%m-%d)"
git push
```

### Export Specific Resource Types

You can modify the Python script to export only specific resources:

```bash
# Edit the main script
nano scripts/azure_discovery.py

# Comment out resources you don't need:
# self.audit_data["compute"][sub_id] = discover_compute(sub_id)
```

## Viewing Results

### View with Command Line

```bash
# View main index
cat docs/README.md

# View specific reports
cat docs/resources/networking.md
cat docs/resources/compute.md

# Use less for pagination
less docs/README.md

# Use grep to find specific resources
grep "Virtual Machine" docs/resources/compute.md
```

### View with Markdown Viewers

```bash
# macOS - Open in default markdown viewer
open docs/README.md

# Or use a markdown viewer
npm install -g markdown-preview
markdown-preview docs/README.md

# VS Code
code docs/README.md
```

### View JSON Data

```bash
# View raw JSON export
cat docs/data/azure_audit_*.json

# Pretty print JSON
cat docs/data/azure_audit_*.json | python3 -m json.tool

# Query with jq
cat docs/data/azure_audit_*.json | jq '.subscriptions'
cat docs/data/azure_audit_*.json | jq '.networking'

# Search for specific resource
cat docs/data/azure_audit_*.json | jq '.compute[].virtual_machines[] | select(.name=="myvm")'
```

## Analysis Examples

### Count Resources

```bash
# Count VMs
cat docs/data/azure_audit_*.json | jq '[.compute[].virtual_machines[]] | length'

# Count Storage Accounts
cat docs/data/azure_audit_*.json | jq '[.storage[].storage_accounts[]] | length'

# List all VM names
cat docs/data/azure_audit_*.json | jq '.compute[].virtual_machines[].name'
```

### Find Resources by Tag

```bash
# Find resources with specific tag
cat docs/data/azure_audit_*.json | jq '.compute[].virtual_machines[] | select(.tags.Environment=="Production")'
```

### Find Public IPs

```bash
# List all public IPs
cat docs/data/azure_audit_*.json | jq '.networking[].public_ips[].ip_address'

# Find resources with public IPs
grep -r "publicIps" docs/resources/
```

### Security Analysis

```bash
# Find NSG rules allowing access from anywhere
grep "0.0.0.0" docs/resources/networking.md

# List all Key Vaults
grep "### " docs/resources/security.md | grep -v "##"

# Find VMs without extensions
cat docs/data/azure_audit_*.json | jq '.compute[].virtual_machines[] | select(.extensions | length == 0)'
```

## Integration Examples

### Slack Notification

```bash
#!/bin/bash
# Run audit and send notification to Slack

./audit-azure.sh

# Send notification
WEBHOOK_URL="your-slack-webhook-url"
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Azure audit completed! View results at: http://your-server/docs/"}' \
  $WEBHOOK_URL
```

### Email Report

```bash
#!/bin/bash
# Run audit and email the summary

./audit-azure.sh

# Email the report (requires mail command)
cat docs/README.md | mail -s "Azure Infrastructure Audit - $(date +%Y-%m-%d)" \
  you@example.com
```

### CI/CD Integration (GitHub Actions)

Create `.github/workflows/azure-audit.yml`:

```yaml
name: Azure Infrastructure Audit

on:
  schedule:
    - cron: '0 2 * * 1'  # Every Monday at 2 AM
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Run Audit
        run: |
          ./audit-azure.sh

      - name: Commit Results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/
          git commit -m "Automated audit - $(date +%Y-%m-%d)" || echo "No changes"
          git push
```

### Generate HTML Report

```bash
# Install pandoc
brew install pandoc

# Convert markdown to HTML
pandoc docs/README.md -o docs/report.html --standalone --toc

# Convert all reports
for file in docs/resources/*.md; do
  pandoc "$file" -o "${file%.md}.html" --standalone
done
```

### Generate PDF Report

```bash
# Install pandoc and LaTeX
brew install pandoc
brew install basictex

# Generate PDF
pandoc docs/README.md -o azure-audit-report.pdf --pdf-engine=pdflatex
```

## Troubleshooting Examples

### Debug Mode

```bash
# Run Python script with debug output
cd scripts
python3 -u azure_discovery.py 2>&1 | tee audit.log
```

### Test Individual Modules

```bash
# Test subscription discovery only
cd scripts
python3 -c "
from discovery.subscription_discovery import discover_subscriptions
import json
subs = discover_subscriptions()
print(json.dumps(subs, indent=2))
"
```

### Check Permissions

```bash
# List your role assignments
az role assignment list --assignee $(az account show --query user.name -o tsv) --output table

# Check access to a specific resource group
az group show --name "your-resource-group"
```

### Timeout Issues

```bash
# For large environments, modify timeout in discovery scripts
# Edit scripts/discovery/networking_discovery.py
# Change: timeout=120 to timeout=300
sed -i '' 's/timeout=120/timeout=300/g' scripts/discovery/*.py
```

## Customization Examples

### Add Custom Resource Type

Create `scripts/discovery/custom_discovery.py`:

```python
def discover_custom_resources(subscription_id):
    """Discover your custom Azure resources"""
    # Add your discovery logic here
    return {
        "custom_resources": [],
        "summary": {"count": 0}
    }
```

Then add to `scripts/azure_discovery.py`:

```python
from discovery.custom_discovery import discover_custom_resources

# In run_discovery():
self.audit_data["custom"] = discover_custom_resources(sub_id)
```

### Modify Report Template

Edit `scripts/reports/markdown_generator.py` to customize report format.

### Filter by Tags

Modify discovery scripts to filter resources by tags:

```python
# Only include production resources
if resource.get('tags', {}).get('Environment') == 'Production':
    # Include in results
```

## Best Practices

### Before Each Run

```bash
# 1. Verify authentication
az account show

# 2. Check available subscriptions
az account list --output table

# 3. Set desired subscription (optional)
az account set --subscription "Production"

# 4. Run audit
./audit-azure.sh
```

### After Each Run

```bash
# 1. Review the output
open docs/README.md

# 2. Check for errors in logs
grep -i error docs/data/azure_audit_*.json

# 3. Commit to version control
git add docs/
git commit -m "Audit - $(date +%Y-%m-%d)"
git push

# 4. Archive old reports (optional)
mv docs docs_$(date +%Y%m%d)
```

---

*These examples should cover most common use cases. Modify them to fit your specific needs!*

# Azure Infrastructure Audit Tool

A comprehensive tool for discovering, documenting, and auditing all resources in your Azure account. This tool automatically scans your Azure subscriptions and generates detailed markdown documentation covering networking, compute, storage, databases, DNS, security, and more.

## Features

- **Comprehensive Discovery**: Automatically discovers all Azure resources across your subscriptions
- **Detailed Documentation**: Generates well-structured markdown reports
- **Multiple Resource Types**: Covers 100+ Azure resource types including:
  - 🌐 Networking (VNets, NSGs, Load Balancers, Firewalls, VPN Gateways)
  - 💻 Compute (VMs, App Services, Functions, Containers, AKS)
  - 💾 Storage (Storage Accounts, Disks, Blob Containers, File Shares)
  - 🗄️ Databases (SQL, MySQL, PostgreSQL, CosmosDB, Redis)
  - 🔍 DNS (DNS Zones, Private DNS, Records)
  - 🔒 Security (Key Vaults, Managed Identities, Security Center)
- **Easy to Use**: Simple shell script interface
- **No Dependencies**: Uses Azure CLI commands (no Python packages required)
- **JSON Export**: Raw data exported to JSON for further analysis

## Prerequisites

### Required

1. **Azure CLI**: Must be installed and configured
   ```bash
   # macOS
   brew install azure-cli

   # Linux
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

   # Windows
   # Download from: https://aka.ms/installazurecliwindows
   ```

2. **Python 3.7+**: Required for running the discovery scripts
   ```bash
   # Check your Python version
   python3 --version
   ```

3. **Azure Account**: You need access to an Azure subscription with appropriate permissions

### Recommended Permissions

For the most complete audit, you should have:
- **Reader** role at the subscription level (minimum)
- **Security Reader** role for Security Center data
- **Key Vault Reader** for Key Vault inventory (secrets won't be exposed)

## Installation

1. **Clone or download this repository**
   ```bash
   cd /path/to/your/projects
   git clone <repository-url>
   cd Audit-Azure
   ```

2. **Make the script executable** (already done if you used git clone)
   ```bash
   chmod +x audit-azure.sh
   ```

3. **Verify Azure CLI installation**
   ```bash
   az --version
   ```

## Quick Start

### Option 1: If Already Authenticated

```bash
# Run the audit
./audit-azure.sh
```

### Option 2: Login First

```bash
# Login to Azure and run audit
./audit-azure.sh --login
```

### Option 3: Manual Login

```bash
# Login manually
az login

# Then run the audit
./audit-azure.sh
```

## Usage

### Basic Command

```bash
./audit-azure.sh [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--login` | Perform Azure CLI login before running audit |
| `--help` | Display help message |

### Examples

```bash
# Run audit with current authentication
./audit-azure.sh

# Login and run audit
./audit-azure.sh --login

# Show help
./audit-azure.sh --help
```

### Using Python Directly

You can also run the Python script directly:

```bash
cd scripts
python3 azure_discovery.py
```

## Output

The tool generates comprehensive documentation in the `docs/` directory:

```
docs/
├── README.md                    # Main index with executive summary
├── data/
│   └── azure_audit_*.json      # Raw JSON data export
└── resources/
    ├── subscriptions.md        # Subscription details
    ├── networking.md           # Networking resources
    ├── compute.md              # Compute resources
    ├── storage.md              # Storage resources
    ├── databases.md            # Database resources
    ├── dns.md                  # DNS resources
    └── security.md             # Security resources
```

### Viewing the Reports

```bash
# Open the main report
open docs/README.md

# Or browse to the directory
cd docs
```

## Project Structure

```
Audit-Azure/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies (minimal)
├── audit-azure.sh                      # Main shell orchestration script
├── scripts/
│   ├── azure_discovery.py             # Main Python orchestrator
│   ├── discovery/                     # Discovery modules
│   │   ├── __init__.py
│   │   ├── subscription_discovery.py # Subscription enumeration
│   │   ├── networking_discovery.py   # Network resource discovery
│   │   ├── compute_discovery.py      # Compute resource discovery
│   │   ├── storage_discovery.py      # Storage resource discovery
│   │   ├── database_discovery.py     # Database resource discovery
│   │   ├── dns_discovery.py          # DNS resource discovery
│   │   └── security_discovery.py     # Security resource discovery
│   └── reports/                       # Report generation
│       ├── __init__.py
│       └── markdown_generator.py     # Markdown report generator
├── docs/                              # Generated documentation (created at runtime)
└── templates/                         # Report templates (optional)
```

## What Gets Discovered

### Networking Resources
- Virtual Networks (VNets) and Subnets
- Network Security Groups (NSGs) and rules
- Public IP addresses
- Load Balancers (internal and external)
- Application Gateways
- VPN Gateways and Virtual Network Gateways
- ExpressRoute circuits
- Azure Firewalls
- Route Tables and routes
- Network Interfaces (NICs)
- VNet Peering connections

### Compute Resources
- Virtual Machines (with extensions and diagnostics)
- VM Scale Sets
- Availability Sets
- App Service Plans
- Web Apps / App Services
- Function Apps
- Container Instances
- Azure Kubernetes Service (AKS) clusters
- Batch Accounts

### Storage Resources
- Storage Accounts (with access policies)
- Blob Containers
- File Shares
- Queues and Tables
- Managed Disks
- Disk Snapshots

### Database Resources
- Azure SQL Servers and Databases
- MySQL Servers
- PostgreSQL Servers
- MariaDB Servers
- CosmosDB Accounts
- Redis Caches
- Database firewall rules

### DNS Resources
- Public DNS Zones
- Private DNS Zones
- DNS Records (A, AAAA, CNAME, MX, TXT, etc.)
- VNet links for Private DNS

### Security Resources
- Key Vaults (with secret/key/certificate counts)
- Managed Identities
- Role Assignments
- Security Center Alerts
- Security Center Recommendations
- Security Contacts

## Troubleshooting

### Authentication Issues

If you see "Please run 'az login'":
```bash
# Login to Azure
az login

# Verify authentication
az account show
```

### Multiple Subscriptions

If you have multiple subscriptions, the tool will discover resources in all accessible subscriptions. To limit to a specific subscription:

```bash
# Set default subscription
az account set --subscription "Your Subscription Name"

# Then run the audit
./audit-azure.sh
```

### Permission Errors

If you encounter permission errors:
- Verify you have at least **Reader** role on the subscription
- Some resources (like Key Vault secrets) require specific permissions
- The tool will continue and report errors for resources it cannot access

### Timeout Issues

For very large Azure environments, some commands may timeout. You can modify the timeout values in the Python scripts:

```python
# In scripts/discovery/*.py files
timeout=120  # Increase this value (in seconds)
```

## Customization

### Adding Custom Discovery

To add discovery for additional Azure resources:

1. Create a new discovery module in `scripts/discovery/`
2. Follow the pattern of existing modules
3. Import and call your module in `scripts/azure_discovery.py`
4. Add report generation in `scripts/reports/markdown_generator.py`

### Modifying Report Format

The markdown reports are generated in `scripts/reports/markdown_generator.py`. You can customize:
- Report structure and sections
- Table formats
- Level of detail
- Output format (could extend to HTML, PDF, etc.)

## Security Considerations

- **No Credentials Stored**: This tool uses Azure CLI authentication
- **Read-Only Operations**: All discovery operations are read-only
- **Sensitive Data**: The tool does NOT export actual secrets, keys, or passwords
- **JSON Export**: Contains resource metadata but no sensitive credentials
- **Local Storage**: All data is stored locally on your machine

## Performance

Discovery time depends on the number of resources:
- Small environment (< 50 resources): ~1-2 minutes
- Medium environment (50-500 resources): ~3-5 minutes
- Large environment (> 500 resources): ~5-15 minutes

## Use Cases

- **Infrastructure Audit**: Document existing Azure infrastructure
- **Compliance**: Generate reports for compliance requirements
- **Migration Planning**: Understand current state before migration
- **Cost Analysis**: Identify all resources for cost optimization
- **Security Review**: Audit security configurations and policies
- **Knowledge Transfer**: Document infrastructure for team onboarding
- **Disaster Recovery**: Maintain up-to-date infrastructure documentation

## Contributing

Contributions are welcome! Areas for improvement:
- Additional resource type discovery
- Enhanced report formatting
- Cost analysis integration
- Compliance check automation
- Export to additional formats (HTML, PDF, Excel)

## License

This project is provided as-is for auditing Azure infrastructure.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Azure CLI documentation
3. Verify your Azure permissions

## Acknowledgments

- Built with Azure CLI
- Uses Python 3 standard library
- Markdown formatting for universal compatibility

---

**Note**: This tool performs read-only operations on your Azure account. Always review the generated reports before sharing them, as they contain detailed infrastructure information.

# Azure VNet Terraform Configuration

This Terraform configuration creates an Azure Virtual Network (VNet) with two subnets.

## Quick Reference

```bash
# Setup and Deploy
./select_subscription.py   # Select subscription and configure
terraform init             # Initialize Terraform
terraform plan             # Preview changes
terraform apply            # Create resources

# Destroy
./destroy.py              # Safely destroy resources (recommended)
terraform destroy         # Alternative destroy method
```

## Features

- ✅ Creates a Virtual Network with customizable address space
- ✅ Creates two subnets with configurable address prefixes
- ✅ Interactive subscription selection script
- ✅ Analyzes existing VNets from audit data to suggest resource group names
- ✅ Fully customizable via variables
- ✅ Includes all necessary outputs

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and authenticated (`az login`)
- Python 3.6+ (for the subscription selector script)

## Quick Start

### Option 1: Using the Subscription Selector (Recommended)

The easiest way to get started is to use the included subscription selector script:

```bash
# Navigate to terraform directory
cd terraform

# Run the subscription selector
./select_subscription.py
```

The script will:
1. Display all available Azure subscriptions with their names and IDs
2. Let you select a subscription
3. Analyze your audit data (if available) to suggest a resource group name based on existing VNet patterns
4. Generate a `terraform.tfvars` file with your selections

### Option 2: Manual Configuration

1. Copy the example variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` and fill in your values:
   ```hcl
   subscription_id     = "your-subscription-id-here"
   resource_group_name = "rg-networking"
   location            = "eastus"
   ```

## Deploy the Infrastructure

Once you have your `terraform.tfvars` file configured:

```bash
# Initialize Terraform
terraform init

# Review the execution plan
terraform plan

# Apply the configuration
terraform apply
```

## Configuration

### Main Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `subscription_id` | Azure Subscription ID | *Required* |
| `resource_group_name` | Name of the resource group | `rg-networking` |
| `location` | Azure region | `eastus` |
| `vnet_name` | Name of the Virtual Network | `vnet-terraform` |
| `vnet_address_space` | Address space for the VNet | `["10.0.0.0/16"]` |
| `subnet1_name` | Name of the first subnet | `subnet-web` |
| `subnet1_address_prefix` | Address prefix for subnet 1 | `10.0.1.0/24` |
| `subnet2_name` | Name of the second subnet | `subnet-app` |
| `subnet2_address_prefix` | Address prefix for subnet 2 | `10.0.2.0/24` |
| `tags` | Tags to apply to resources | See variables.tf |

### Example Custom Configuration

```hcl
subscription_id     = "12345678-1234-1234-1234-123456789012"
resource_group_name = "rg-production-networking"
location            = "westus2"

vnet_name          = "vnet-prod"
vnet_address_space = ["172.16.0.0/16"]

subnet1_name           = "subnet-frontend"
subnet1_address_prefix = "172.16.1.0/24"

subnet2_name           = "subnet-backend"
subnet2_address_prefix = "172.16.2.0/24"

tags = {
  Environment = "Production"
  ManagedBy   = "Terraform"
  Team        = "Platform"
}
```

## Outputs

After applying, the following outputs will be available:

- `resource_group_name` - Name of the created resource group
- `resource_group_id` - ID of the resource group
- `vnet_name` - Name of the VNet
- `vnet_id` - ID of the VNet
- `vnet_address_space` - Address space of the VNet
- `subnet1_id` - ID of the first subnet
- `subnet1_name` - Name of the first subnet
- `subnet1_address_prefix` - Address prefix of the first subnet
- `subnet2_id` - ID of the second subnet
- `subnet2_name` - Name of the second subnet
- `subnet2_address_prefix` - Address prefix of the second subnet

View outputs with:
```bash
terraform output
```

## How the Subscription Selector Works

The `select_subscription.py` script:

1. **Fetches Subscriptions**: Uses `az account list` to get all available subscriptions
2. **Displays Options**: Shows subscription names, IDs, and states
3. **Analyzes Audit Data**: If audit data exists in `../docs/data/`, it analyzes:
   - All VNets across all subscriptions
   - Resource group naming patterns
   - Most commonly used locations
4. **Makes Suggestions**: Based on the analysis, suggests:
   - Resource group name (based on most common pattern, e.g., `rg-networking`)
   - Azure region (based on most commonly used location)
5. **Generates Config**: Creates `terraform.tfvars` with your selections

### Example Session

```
================================================================================
Azure Subscription Selector for Terraform
================================================================================
Fetching Azure subscriptions...

================================================================================
AVAILABLE AZURE SUBSCRIPTIONS
================================================================================

  1. ✓ Production-Subscription
     ID: 12345678-1234-1234-1234-123456789012
     State: Enabled

  2. ✓ Development-Subscription
     ID: 87654321-4321-4321-4321-210987654321
     State: Enabled

Select subscription (1-2): 1

✓ Selected: Production-Subscription
  Subscription ID: 12345678-1234-1234-1234-123456789012

📊 Analyzing audit data from: azure_audit_2025-01-15_10-30-45.json
   Total VNets found: 5
   Most common resource group: rg-networking
   Most common location: eastus

💡 Suggested resource group: rg-networking
Resource group name [rg-networking]:

💡 Suggested location: eastus
Location [eastus]:

✅ Created terraform.tfvars with your selections

================================================================================
✅ Configuration complete!
================================================================================

Next steps:
  1. Review and edit terraform.tfvars if needed
  2. Run: terraform init
  3. Run: terraform plan
  4. Run: terraform apply
```

## Files

- `main.tf` - Main Terraform configuration
- `variables.tf` - Variable definitions
- `outputs.tf` - Output definitions
- `terraform.tfvars.example` - Example variables file
- `select_subscription.py` - Interactive subscription selector
- `destroy.py` - Safe destruction helper with confirmations
- `.gitignore` - Protects sensitive files from version control
- `README.md` - This file

## Destroy Resources

⚠️ **IMPORTANT**: Destroying resources is permanent and cannot be undone!

### Option 1: Using the Destroy Helper (Recommended)

The safest way to destroy resources is using the included destroy helper:

```bash
./destroy.py
```

The destroy helper will:
1. Show you exactly what will be destroyed
2. Require double confirmation (yes + typing "DESTROY")
3. Execute the destruction
4. Optionally clean up Terraform state files

### Option 2: Manual Terraform Destroy

You can also use Terraform directly:

```bash
# Preview what will be destroyed
terraform plan -destroy

# Destroy the resources
terraform destroy
```

You will be prompted to confirm the destruction by typing `yes`.

### Option 3: Force Destroy (Use with Caution)

To destroy without interactive prompts:

```bash
terraform destroy -auto-approve
```

⚠️ **WARNING**: This skips all confirmations. Use only in automation or when you're absolutely certain.

### What Gets Destroyed

When you run destroy, the following resources will be permanently deleted:
- ✗ Virtual Network (`vnet-terraform` or your custom name)
- ✗ Subnet 1 (default: `subnet-web`)
- ✗ Subnet 2 (default: `subnet-app`)
- ✗ Resource Group (if it was created by Terraform and is empty)

### Clean Up State Files

After destroying resources, you may want to clean up Terraform state files:

```bash
# The destroy.py script offers this as an option, or manually:
rm -f terraform.tfstate terraform.tfstate.backup .terraform.lock.hcl
rm -rf .terraform
```

⚠️ Only remove state files if you're completely done with this Terraform configuration.

## Notes

- The resource group will be created if it doesn't exist
- Subnet address prefixes must be within the VNet address space
- The configuration uses the Azure RM provider v3.x
- Tags can be customized in `terraform.tfvars`

## Integration with Audit Tool

This Terraform configuration is designed to work alongside the Azure audit tool in this repository:

1. Run the audit to discover your current infrastructure:
   ```bash
   cd ..
   python3 scripts/azure_discovery.py
   ```

2. The audit creates a JSON file in `docs/data/`

3. The subscription selector automatically analyzes this data to suggest appropriate resource group names and locations based on your existing patterns

4. This ensures your new infrastructure follows the same naming conventions as your existing resources

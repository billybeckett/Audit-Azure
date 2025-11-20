#!/usr/bin/env python3
"""
Azure Subscription Selector for Terraform
This script helps you select an Azure subscription and suggests resource group names
based on existing VNet patterns in your audit data.
"""

import json
import subprocess
import sys
from pathlib import Path
from collections import Counter


def run_az_command(command):
    """Run an Azure CLI command and return the JSON result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"Error output: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None


def get_subscriptions():
    """Get all Azure subscriptions"""
    print("Fetching Azure subscriptions...")
    subscriptions = run_az_command("az account list --output json")

    if not subscriptions:
        print("❌ No subscriptions found or authentication failed.")
        print("   Please run 'az login' first.")
        sys.exit(1)

    return subscriptions


def analyze_audit_data():
    """Analyze audit data to suggest resource group names"""
    # Look for the most recent audit JSON file
    data_dir = Path("../docs/data")

    if not data_dir.exists():
        return None

    json_files = sorted(data_dir.glob("azure_audit_*.json"), reverse=True)

    if not json_files:
        return None

    # Load the most recent audit file
    latest_audit = json_files[0]
    print(f"\n📊 Analyzing audit data from: {latest_audit.name}")

    try:
        with open(latest_audit, 'r') as f:
            audit_data = json.load(f)
    except Exception as e:
        print(f"   ⚠ Could not read audit file: {e}")
        return None

    # Analyze VNet resource group naming patterns
    rg_names = []
    locations = []

    for sub_id, networking_data in audit_data.get('networking', {}).items():
        for vnet in networking_data.get('vnets', []):
            rg = vnet.get('resource_group')
            loc = vnet.get('location')
            if rg:
                rg_names.append(rg)
            if loc:
                locations.append(loc)

    if not rg_names:
        return None

    # Find most common patterns
    rg_counter = Counter(rg_names)
    loc_counter = Counter(locations)

    most_common_rg = rg_counter.most_common(1)[0][0] if rg_counter else None
    most_common_loc = loc_counter.most_common(1)[0][0] if loc_counter else None

    return {
        'resource_groups': rg_names,
        'most_common_rg': most_common_rg,
        'locations': locations,
        'most_common_location': most_common_loc,
        'total_vnets': len(rg_names)
    }


def display_subscriptions(subscriptions):
    """Display available subscriptions"""
    print("\n" + "=" * 80)
    print("AVAILABLE AZURE SUBSCRIPTIONS")
    print("=" * 80)
    print()

    for idx, sub in enumerate(subscriptions, 1):
        state_icon = "✓" if sub.get("state") == "Enabled" else "✗"
        print(f"  {idx}. {state_icon} {sub.get('name')}")
        print(f"     ID: {sub.get('id')}")
        print(f"     State: {sub.get('state')}")
        print()


def select_subscription(subscriptions):
    """Prompt user to select a subscription"""
    while True:
        try:
            choice = input(f"Select subscription (1-{len(subscriptions)}): ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= len(subscriptions):
                return subscriptions[choice_num - 1]
            else:
                print(f"❌ Invalid choice. Please enter 1-{len(subscriptions)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n❌ Selection cancelled by user.")
            sys.exit(1)


def suggest_resource_group(analysis):
    """Suggest a resource group name based on analysis"""
    if not analysis:
        return "rg-networking", "eastus"

    print(f"\n📋 Analysis of existing VNets:")
    print(f"   Total VNets found: {analysis['total_vnets']}")
    print(f"   Most common resource group: {analysis['most_common_rg']}")
    print(f"   Most common location: {analysis['most_common_location']}")
    print()

    # Suggest based on pattern
    suggested_rg = analysis['most_common_rg']
    suggested_location = analysis['most_common_location']

    # If the pattern is something like "rg-networking", "rg-prod", etc., use it
    # Otherwise suggest a sensible default
    if not suggested_rg or not suggested_rg.startswith('rg-'):
        suggested_rg = "rg-networking"

    if not suggested_location:
        suggested_location = "eastus"

    return suggested_rg, suggested_location


def generate_tfvars(subscription_id, resource_group, location):
    """Generate terraform.tfvars file"""
    tfvars_content = f'''# Auto-generated by select_subscription.py
# Azure subscription configuration

subscription_id     = "{subscription_id}"
resource_group_name = "{resource_group}"
location            = "{location}"

# VNet configuration
vnet_name           = "vnet-terraform"
vnet_address_space  = ["10.0.0.0/16"]

# Subnet 1 configuration
subnet1_name           = "subnet-web"
subnet1_address_prefix = "10.0.1.0/24"

# Subnet 2 configuration
subnet2_name           = "subnet-app"
subnet2_address_prefix = "10.0.2.0/24"

# Tags
tags = {{
  Environment = "Development"
  ManagedBy   = "Terraform"
  CreatedBy   = "select_subscription.py"
}}
'''

    with open('terraform.tfvars', 'w') as f:
        f.write(tfvars_content)

    print(f"\n✅ Created terraform.tfvars with your selections")


def main():
    """Main function"""
    print("=" * 80)
    print("Azure Subscription Selector for Terraform")
    print("=" * 80)

    # Get subscriptions
    subscriptions = get_subscriptions()

    # Display subscriptions
    display_subscriptions(subscriptions)

    # Select subscription
    selected_sub = select_subscription(subscriptions)
    print(f"\n✓ Selected: {selected_sub.get('name')}")
    print(f"  Subscription ID: {selected_sub.get('id')}")

    # Analyze audit data for suggestions
    analysis = analyze_audit_data()
    suggested_rg, suggested_location = suggest_resource_group(analysis)

    # Ask for resource group name
    print(f"\n💡 Suggested resource group: {suggested_rg}")
    rg_input = input(f"Resource group name [{suggested_rg}]: ").strip()
    resource_group = rg_input if rg_input else suggested_rg

    # Ask for location
    print(f"\n💡 Suggested location: {suggested_location}")
    loc_input = input(f"Location [{suggested_location}]: ").strip()
    location = loc_input if loc_input else suggested_location

    # Generate terraform.tfvars
    generate_tfvars(selected_sub.get('id'), resource_group, location)

    print("\n" + "=" * 80)
    print("✅ Configuration complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Review and edit terraform.tfvars if needed")
    print("  2. Run: terraform init")
    print("  3. Run: terraform plan")
    print("  4. Run: terraform apply")
    print()


if __name__ == "__main__":
    main()

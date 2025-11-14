"""
Azure Subscription Discovery Module
Discovers all subscriptions and basic account information
"""

import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from logger import run_az_command


def discover_subscriptions():
    """
    Discover all Azure subscriptions accessible to the authenticated user

    Returns:
        list: List of subscription dictionaries with details
    """
    subscriptions = []

    # Get all subscriptions
    subs = run_az_command("az account list --output json")

    for sub in subs:
        # Get detailed subscription info
        sub_info = {
            "id": sub.get("id"),
            "name": sub.get("name"),
            "state": sub.get("state"),
            "tenant_id": sub.get("tenantId"),
            "is_default": sub.get("isDefault", False),
            "cloud_name": sub.get("cloudName"),
            "home_tenant_id": sub.get("homeTenantId"),
        }

        # Get resource groups for this subscription
        try:
            rgs = run_az_command(f"az group list --subscription {sub['id']} --output json")
            sub_info["resource_groups"] = [
                {
                    "name": rg.get("name"),
                    "location": rg.get("location"),
                    "provisioning_state": rg.get("properties", {}).get("provisioningState"),
                    "tags": rg.get("tags", {})
                }
                for rg in rgs
            ]
            sub_info["resource_group_count"] = len(rgs)
        except Exception as e:
            sub_info["resource_groups"] = []
            sub_info["resource_group_count"] = 0
            sub_info["error"] = str(e)

        # Get resource providers registration status
        try:
            providers = run_az_command(
                f"az provider list --subscription {sub['id']} --output json"
            )
            sub_info["registered_providers"] = [
                p.get("namespace")
                for p in providers
                if p.get("registrationState") == "Registered"
            ]
        except Exception as e:
            sub_info["registered_providers"] = []

        # Get subscription locations (this is global, not per-subscription)
        try:
            locations = run_az_command(
                "az account list-locations --output json"
            )
            sub_info["available_locations"] = [
                {
                    "name": loc.get("name"),
                    "display_name": loc.get("displayName"),
                    "region": loc.get("metadata", {}).get("regionType")
                }
                for loc in locations
            ]
        except Exception as e:
            sub_info["available_locations"] = []

        subscriptions.append(sub_info)

    return subscriptions


def get_account_info():
    """
    Get general Azure account information

    Returns:
        dict: Account information
    """
    try:
        account = run_az_command("az account show --output json")
        return {
            "user": account.get("user", {}).get("name"),
            "tenant_id": account.get("tenantId"),
            "subscription_name": account.get("name"),
            "subscription_id": account.get("id"),
            "environment": account.get("environmentName")
        }
    except Exception as e:
        return {"error": str(e)}

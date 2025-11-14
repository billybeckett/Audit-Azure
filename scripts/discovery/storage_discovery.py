"""
Azure Storage Discovery Module
Discovers Storage Accounts, Disks, File Shares, Blob Containers, etc.
"""

import subprocess
import json


def run_az_command(command):
    """Execute Azure CLI command and return JSON output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            return []
        return json.loads(result.stdout) if result.stdout else []
    except:
        return []


def discover_storage(subscription_id):
    """
    Discover all storage resources in a subscription

    Args:
        subscription_id: Azure subscription ID

    Returns:
        dict: Dictionary containing all storage resources
    """
    storage_data = {
        "storage_accounts": [],
        "managed_disks": [],
        "disk_snapshots": [],
        "summary": {}
    }

    # Storage Accounts
    storage_accounts = run_az_command(
        f"az storage account list --subscription {subscription_id} --output json"
    )
    for sa in storage_accounts:
        sa_info = {
            "name": sa.get("name"),
            "id": sa.get("id"),
            "location": sa.get("location"),
            "resource_group": sa.get("resourceGroup"),
            "sku": {
                "name": sa.get("sku", {}).get("name"),
                "tier": sa.get("sku", {}).get("tier")
            },
            "kind": sa.get("kind"),
            "access_tier": sa.get("accessTier"),
            "provisioning_state": sa.get("provisioningState"),
            "primary_location": sa.get("primaryLocation"),
            "status_of_primary": sa.get("statusOfPrimary"),
            "secondary_location": sa.get("secondaryLocation"),
            "status_of_secondary": sa.get("statusOfSecondary"),
            "creation_time": sa.get("creationTime"),
            "https_only": sa.get("supportsHttpsTrafficOnly"),
            "allow_blob_public_access": sa.get("allowBlobPublicAccess"),
            "allow_shared_key_access": sa.get("allowSharedKeyAccess"),
            "minimum_tls_version": sa.get("minimumTlsVersion"),
            "network_rule_set": {
                "default_action": sa.get("networkRuleSet", {}).get("defaultAction"),
                "bypass": sa.get("networkRuleSet", {}).get("bypass"),
                "ip_rules": [
                    rule.get("value") for rule in sa.get("networkRuleSet", {}).get("ipRules", [])
                ],
                "virtual_network_rules": [
                    rule.get("id") for rule in sa.get("networkRuleSet", {}).get("virtualNetworkRules", [])
                ]
            },
            "encryption": {
                "key_source": sa.get("encryption", {}).get("keySource"),
                "services": {
                    "blob": sa.get("encryption", {}).get("services", {}).get("blob", {}).get("enabled"),
                    "file": sa.get("encryption", {}).get("services", {}).get("file", {}).get("enabled"),
                    "table": sa.get("encryption", {}).get("services", {}).get("table", {}).get("enabled"),
                    "queue": sa.get("encryption", {}).get("services", {}).get("queue", {}).get("enabled")
                }
            },
            "tags": sa.get("tags", {})
        }

        # Get blob containers
        try:
            containers = run_az_command(
                f"az storage container list --account-name {sa.get('name')} "
                f"--subscription {subscription_id} --output json --auth-mode login"
            )
            sa_info["blob_containers"] = [
                {
                    "name": c.get("name"),
                    "public_access": c.get("properties", {}).get("publicAccess"),
                    "last_modified": c.get("properties", {}).get("lastModified"),
                    "lease_state": c.get("properties", {}).get("leaseState")
                }
                for c in containers
            ]
            sa_info["blob_container_count"] = len(containers)
        except:
            sa_info["blob_containers"] = []
            sa_info["blob_container_count"] = 0

        # Get file shares
        try:
            shares = run_az_command(
                f"az storage share list --account-name {sa.get('name')} "
                f"--subscription {subscription_id} --output json --auth-mode login"
            )
            sa_info["file_shares"] = [
                {
                    "name": s.get("name"),
                    "quota": s.get("properties", {}).get("quota"),
                    "last_modified": s.get("properties", {}).get("lastModified")
                }
                for s in shares
            ]
            sa_info["file_share_count"] = len(shares)
        except:
            sa_info["file_shares"] = []
            sa_info["file_share_count"] = 0

        # Get queues
        try:
            queues = run_az_command(
                f"az storage queue list --account-name {sa.get('name')} "
                f"--subscription {subscription_id} --output json --auth-mode login"
            )
            sa_info["queues"] = [q.get("name") for q in queues]
            sa_info["queue_count"] = len(queues)
        except:
            sa_info["queues"] = []
            sa_info["queue_count"] = 0

        # Get tables
        try:
            tables = run_az_command(
                f"az storage table list --account-name {sa.get('name')} "
                f"--subscription {subscription_id} --output json --auth-mode login"
            )
            sa_info["tables"] = [t.get("name") for t in tables]
            sa_info["table_count"] = len(tables)
        except:
            sa_info["tables"] = []
            sa_info["table_count"] = 0

        storage_data["storage_accounts"].append(sa_info)

    # Managed Disks
    disks = run_az_command(
        f"az disk list --subscription {subscription_id} --output json"
    )
    for disk in disks:
        disk_info = {
            "name": disk.get("name"),
            "id": disk.get("id"),
            "location": disk.get("location"),
            "resource_group": disk.get("resourceGroup"),
            "sku": {
                "name": disk.get("sku", {}).get("name"),
                "tier": disk.get("sku", {}).get("tier")
            },
            "disk_size_gb": disk.get("diskSizeGb"),
            "disk_size_bytes": disk.get("diskSizeBytes"),
            "os_type": disk.get("osType"),
            "disk_state": disk.get("diskState"),
            "time_created": disk.get("timeCreated"),
            "provisioning_state": disk.get("provisioningState"),
            "disk_iops_read_write": disk.get("diskIOPSReadWrite"),
            "disk_mbps_read_write": disk.get("diskMBpsReadWrite"),
            "encryption_type": disk.get("encryption", {}).get("type"),
            "network_access_policy": disk.get("networkAccessPolicy"),
            "public_network_access": disk.get("publicNetworkAccess"),
            "attached_to": disk.get("managedBy"),
            "zones": disk.get("zones", []),
            "tags": disk.get("tags", {})
        }
        storage_data["managed_disks"].append(disk_info)

    # Disk Snapshots
    snapshots = run_az_command(
        f"az snapshot list --subscription {subscription_id} --output json"
    )
    for snapshot in snapshots:
        snapshot_info = {
            "name": snapshot.get("name"),
            "id": snapshot.get("id"),
            "location": snapshot.get("location"),
            "resource_group": snapshot.get("resourceGroup"),
            "sku": {
                "name": snapshot.get("sku", {}).get("name"),
                "tier": snapshot.get("sku", {}).get("tier")
            },
            "disk_size_gb": snapshot.get("diskSizeGb"),
            "os_type": snapshot.get("osType"),
            "time_created": snapshot.get("timeCreated"),
            "provisioning_state": snapshot.get("provisioningState"),
            "source_disk": snapshot.get("creationData", {}).get("sourceResourceId"),
            "incremental": snapshot.get("incremental"),
            "tags": snapshot.get("tags", {})
        }
        storage_data["disk_snapshots"].append(snapshot_info)

    # Calculate summary
    storage_data["summary"] = {
        "storage_accounts": len(storage_data["storage_accounts"]),
        "disks": len(storage_data["managed_disks"]),
        "snapshots": len(storage_data["disk_snapshots"])
    }

    return storage_data

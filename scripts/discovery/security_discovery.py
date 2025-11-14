"""
Azure Security Discovery Module
Discovers Key Vaults, Security Center, Role Assignments, Managed Identities, etc.
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


def discover_security(subscription_id):
    """
    Discover all security resources in a subscription

    Args:
        subscription_id: Azure subscription ID

    Returns:
        dict: Dictionary containing all security resources
    """
    security_data = {
        "key_vaults": [],
        "managed_identities": [],
        "role_assignments": [],
        "security_center_alerts": [],
        "security_center_recommendations": [],
        "security_contacts": [],
        "summary": {}
    }

    # Key Vaults
    key_vaults = run_az_command(
        f"az keyvault list --subscription {subscription_id} --output json"
    )
    for kv in key_vaults:
        kv_info = {
            "name": kv.get("name"),
            "id": kv.get("id"),
            "location": kv.get("location"),
            "resource_group": kv.get("resourceGroup"),
            "vault_uri": kv.get("properties", {}).get("vaultUri"),
            "sku": kv.get("properties", {}).get("sku", {}).get("name"),
            "tenant_id": kv.get("properties", {}).get("tenantId"),
            "enabled_for_deployment": kv.get("properties", {}).get("enabledForDeployment"),
            "enabled_for_disk_encryption": kv.get("properties", {}).get("enabledForDiskEncryption"),
            "enabled_for_template_deployment": kv.get("properties", {}).get("enabledForTemplateDeployment"),
            "enable_soft_delete": kv.get("properties", {}).get("enableSoftDelete"),
            "soft_delete_retention_days": kv.get("properties", {}).get("softDeleteRetentionInDays"),
            "enable_purge_protection": kv.get("properties", {}).get("enablePurgeProtection"),
            "enable_rbac_authorization": kv.get("properties", {}).get("enableRbacAuthorization"),
            "public_network_access": kv.get("properties", {}).get("publicNetworkAccess"),
            "network_acls": {
                "default_action": kv.get("properties", {}).get("networkAcls", {}).get("defaultAction"),
                "bypass": kv.get("properties", {}).get("networkAcls", {}).get("bypass"),
                "ip_rules": [
                    rule.get("value") for rule in kv.get("properties", {}).get("networkAcls", {}).get("ipRules", [])
                ],
                "virtual_network_rules": [
                    rule.get("id") for rule in kv.get("properties", {}).get("networkAcls", {}).get("virtualNetworkRules", [])
                ]
            },
            "tags": kv.get("tags", {})
        }

        # Get secrets count (without listing actual secrets for security)
        try:
            secrets = run_az_command(
                f"az keyvault secret list --vault-name {kv.get('name')} "
                f"--subscription {subscription_id} --output json"
            )
            kv_info["secret_count"] = len(secrets)
        except:
            kv_info["secret_count"] = 0

        # Get keys count
        try:
            keys = run_az_command(
                f"az keyvault key list --vault-name {kv.get('name')} "
                f"--subscription {subscription_id} --output json"
            )
            kv_info["key_count"] = len(keys)
        except:
            kv_info["key_count"] = 0

        # Get certificates count
        try:
            certificates = run_az_command(
                f"az keyvault certificate list --vault-name {kv.get('name')} "
                f"--subscription {subscription_id} --output json"
            )
            kv_info["certificate_count"] = len(certificates)
        except:
            kv_info["certificate_count"] = 0

        security_data["key_vaults"].append(kv_info)

    # Managed Identities
    managed_identities = run_az_command(
        f"az identity list --subscription {subscription_id} --output json"
    )
    for identity in managed_identities:
        identity_info = {
            "name": identity.get("name"),
            "id": identity.get("id"),
            "location": identity.get("location"),
            "resource_group": identity.get("resourceGroup"),
            "principal_id": identity.get("principalId"),
            "client_id": identity.get("clientId"),
            "tenant_id": identity.get("tenantId"),
            "type": identity.get("type"),
            "tags": identity.get("tags", {})
        }
        security_data["managed_identities"].append(identity_info)

    # Role Assignments (limited to subscription scope)
    try:
        role_assignments = run_az_command(
            f"az role assignment list --subscription {subscription_id} "
            f"--include-inherited --output json"
        )
        # Limit to first 100 to avoid overwhelming output
        for assignment in role_assignments[:100]:
            assignment_info = {
                "id": assignment.get("id"),
                "name": assignment.get("name"),
                "principal_id": assignment.get("principalId"),
                "principal_name": assignment.get("principalName"),
                "principal_type": assignment.get("principalType"),
                "role_definition_name": assignment.get("roleDefinitionName"),
                "scope": assignment.get("scope"),
                "created_on": assignment.get("createdOn"),
                "updated_on": assignment.get("updatedOn")
            }
            security_data["role_assignments"].append(assignment_info)
    except:
        security_data["role_assignments"] = []

    # Security Center Alerts
    try:
        alerts = run_az_command(
            f"az security alert list --subscription {subscription_id} --output json"
        )
        for alert in alerts:
            alert_info = {
                "name": alert.get("name"),
                "id": alert.get("id"),
                "display_name": alert.get("properties", {}).get("alertDisplayName"),
                "severity": alert.get("properties", {}).get("severity"),
                "status": alert.get("properties", {}).get("status"),
                "description": alert.get("properties", {}).get("description"),
                "compromised_entity": alert.get("properties", {}).get("compromisedEntity"),
                "start_time": alert.get("properties", {}).get("startTimeUtc"),
                "end_time": alert.get("properties", {}).get("endTimeUtc"),
                "resource_identifiers": alert.get("properties", {}).get("resourceIdentifiers")
            }
            security_data["security_center_alerts"].append(alert_info)
    except:
        security_data["security_center_alerts"] = []

    # Security Center Recommendations
    try:
        recommendations = run_az_command(
            f"az security assessment list --subscription {subscription_id} --output json"
        )
        # Limit to unhealthy recommendations
        for rec in recommendations:
            status_code = rec.get("properties", {}).get("status", {}).get("code")
            if status_code in ["Unhealthy", "NotApplicable"]:
                rec_info = {
                    "name": rec.get("name"),
                    "id": rec.get("id"),
                    "display_name": rec.get("properties", {}).get("displayName"),
                    "status": status_code,
                    "severity": rec.get("properties", {}).get("metadata", {}).get("severity"),
                    "description": rec.get("properties", {}).get("metadata", {}).get("description"),
                    "remediation_description": rec.get("properties", {}).get("metadata", {}).get("remediationDescription"),
                    "resource_details": rec.get("properties", {}).get("resourceDetails", {}).get("id")
                }
                security_data["security_center_recommendations"].append(rec_info)
    except:
        security_data["security_center_recommendations"] = []

    # Security Contacts
    try:
        contacts = run_az_command(
            f"az security contact list --subscription {subscription_id} --output json"
        )
        for contact in contacts:
            contact_info = {
                "name": contact.get("name"),
                "email": contact.get("properties", {}).get("email"),
                "phone": contact.get("properties", {}).get("phone"),
                "alert_notifications": contact.get("properties", {}).get("alertNotifications"),
                "alerts_to_admins": contact.get("properties", {}).get("alertsToAdmins")
            }
            security_data["security_contacts"].append(contact_info)
    except:
        security_data["security_contacts"] = []

    # Calculate summary
    security_data["summary"] = {
        "key_vaults": len(security_data["key_vaults"]),
        "managed_identities": len(security_data["managed_identities"]),
        "role_assignments": len(security_data["role_assignments"]),
        "security_alerts": len(security_data["security_center_alerts"]),
        "security_recommendations": len(security_data["security_center_recommendations"]),
        "security_contacts": len(security_data["security_contacts"])
    }

    return security_data

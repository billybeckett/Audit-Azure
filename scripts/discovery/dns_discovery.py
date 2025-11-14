"""
Azure DNS Discovery Module
Discovers DNS Zones, Private DNS Zones, DNS Records, etc.
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


def discover_dns(subscription_id):
    """
    Discover all DNS resources in a subscription

    Args:
        subscription_id: Azure subscription ID

    Returns:
        dict: Dictionary containing all DNS resources
    """
    dns_data = {
        "dns_zones": [],
        "private_dns_zones": [],
        "summary": {}
    }

    # Public DNS Zones
    dns_zones = run_az_command(
        f"az network dns zone list --subscription {subscription_id} --output json"
    )
    for zone in dns_zones:
        zone_info = {
            "name": zone.get("name"),
            "id": zone.get("id"),
            "location": zone.get("location"),
            "resource_group": zone.get("resourceGroup"),
            "number_of_record_sets": zone.get("numberOfRecordSets"),
            "max_number_of_record_sets": zone.get("maxNumberOfRecordSets"),
            "name_servers": zone.get("nameServers", []),
            "zone_type": zone.get("zoneType"),
            "tags": zone.get("tags", {})
        }

        # Get DNS records for this zone
        record_sets = run_az_command(
            f"az network dns record-set list --subscription {subscription_id} "
            f"--resource-group {zone.get('resourceGroup')} "
            f"--zone-name {zone.get('name')} --output json"
        )

        zone_info["record_sets"] = []
        for record_set in record_sets:
            record_info = {
                "name": record_set.get("name"),
                "type": record_set.get("type"),
                "ttl": record_set.get("ttl"),
                "fqdn": record_set.get("fqdn")
            }

            # Extract record data based on type
            record_type = record_set.get("type", "").split("/")[-1] if record_set.get("type") else ""

            if record_type == "A":
                record_info["a_records"] = [
                    r.get("ipv4Address") for r in record_set.get("aRecords", [])
                ]
            elif record_type == "AAAA":
                record_info["aaaa_records"] = [
                    r.get("ipv6Address") for r in record_set.get("aaaaRecords", [])
                ]
            elif record_type == "CNAME":
                record_info["cname_record"] = record_set.get("cnameRecord", {}).get("cname")
            elif record_type == "MX":
                record_info["mx_records"] = [
                    {
                        "preference": r.get("preference"),
                        "exchange": r.get("exchange")
                    }
                    for r in record_set.get("mxRecords", [])
                ]
            elif record_type == "NS":
                record_info["ns_records"] = [
                    r.get("nsdname") for r in record_set.get("nsRecords", [])
                ]
            elif record_type == "PTR":
                record_info["ptr_records"] = [
                    r.get("ptrdname") for r in record_set.get("ptrRecords", [])
                ]
            elif record_type == "SOA":
                soa = record_set.get("soaRecord", {})
                record_info["soa_record"] = {
                    "host": soa.get("host"),
                    "email": soa.get("email"),
                    "serial": soa.get("serialNumber"),
                    "refresh": soa.get("refreshTime"),
                    "retry": soa.get("retryTime"),
                    "expire": soa.get("expireTime"),
                    "minimum": soa.get("minimumTtl")
                }
            elif record_type == "SRV":
                record_info["srv_records"] = [
                    {
                        "priority": r.get("priority"),
                        "weight": r.get("weight"),
                        "port": r.get("port"),
                        "target": r.get("target")
                    }
                    for r in record_set.get("srvRecords", [])
                ]
            elif record_type == "TXT":
                record_info["txt_records"] = [
                    r.get("value") for r in record_set.get("txtRecords", [])
                ]
            elif record_type == "CAA":
                record_info["caa_records"] = [
                    {
                        "flags": r.get("flags"),
                        "tag": r.get("tag"),
                        "value": r.get("value")
                    }
                    for r in record_set.get("caaRecords", [])
                ]

            zone_info["record_sets"].append(record_info)

        dns_data["dns_zones"].append(zone_info)

    # Private DNS Zones
    private_dns_zones = run_az_command(
        f"az network private-dns zone list --subscription {subscription_id} --output json"
    )
    for zone in private_dns_zones:
        zone_info = {
            "name": zone.get("name"),
            "id": zone.get("id"),
            "location": zone.get("location"),
            "resource_group": zone.get("resourceGroup"),
            "number_of_record_sets": zone.get("numberOfRecordSets"),
            "max_number_of_record_sets": zone.get("maxNumberOfRecordSets"),
            "number_of_virtual_network_links": zone.get("numberOfVirtualNetworkLinks"),
            "max_number_of_virtual_network_links": zone.get("maxNumberOfVirtualNetworkLinks"),
            "provisioning_state": zone.get("provisioningState"),
            "tags": zone.get("tags", {})
        }

        # Get virtual network links
        vnet_links = run_az_command(
            f"az network private-dns link vnet list --subscription {subscription_id} "
            f"--resource-group {zone.get('resourceGroup')} "
            f"--zone-name {zone.get('name')} --output json"
        )
        zone_info["virtual_network_links"] = [
            {
                "name": link.get("name"),
                "virtual_network": link.get("virtualNetwork", {}).get("id"),
                "registration_enabled": link.get("registrationEnabled"),
                "provisioning_state": link.get("provisioningState")
            }
            for link in vnet_links
        ]

        # Get private DNS records
        record_sets = run_az_command(
            f"az network private-dns record-set list --subscription {subscription_id} "
            f"--resource-group {zone.get('resourceGroup')} "
            f"--zone-name {zone.get('name')} --output json"
        )

        zone_info["record_sets"] = []
        for record_set in record_sets:
            record_info = {
                "name": record_set.get("name"),
                "type": record_set.get("type"),
                "ttl": record_set.get("ttl"),
                "fqdn": record_set.get("fqdn")
            }

            # Extract record data
            record_type = record_set.get("type", "").split("/")[-1] if record_set.get("type") else ""

            if record_type == "A":
                record_info["a_records"] = [
                    r.get("ipv4Address") for r in record_set.get("aRecords", [])
                ]
            elif record_type == "AAAA":
                record_info["aaaa_records"] = [
                    r.get("ipv6Address") for r in record_set.get("aaaaRecords", [])
                ]
            elif record_type == "CNAME":
                record_info["cname_record"] = record_set.get("cnameRecord", {}).get("cname")
            elif record_type == "MX":
                record_info["mx_records"] = [
                    {
                        "preference": r.get("preference"),
                        "exchange": r.get("exchange")
                    }
                    for r in record_set.get("mxRecords", [])
                ]
            elif record_type == "PTR":
                record_info["ptr_records"] = [
                    r.get("ptrdname") for r in record_set.get("ptrRecords", [])
                ]
            elif record_type == "SOA":
                soa = record_set.get("soaRecord", {})
                record_info["soa_record"] = {
                    "host": soa.get("host"),
                    "email": soa.get("email"),
                    "serial": soa.get("serialNumber"),
                    "refresh": soa.get("refreshTime"),
                    "retry": soa.get("retryTime"),
                    "expire": soa.get("expireTime"),
                    "minimum": soa.get("minimumTtl")
                }
            elif record_type == "SRV":
                record_info["srv_records"] = [
                    {
                        "priority": r.get("priority"),
                        "weight": r.get("weight"),
                        "port": r.get("port"),
                        "target": r.get("target")
                    }
                    for r in record_set.get("srvRecords", [])
                ]
            elif record_type == "TXT":
                record_info["txt_records"] = [
                    r.get("value") for r in record_set.get("txtRecords", [])
                ]

            zone_info["record_sets"].append(record_info)

        dns_data["private_dns_zones"].append(zone_info)

    # Calculate summary
    dns_data["summary"] = {
        "dns_zones": len(dns_data["dns_zones"]),
        "private_dns_zones": len(dns_data["private_dns_zones"])
    }

    return dns_data

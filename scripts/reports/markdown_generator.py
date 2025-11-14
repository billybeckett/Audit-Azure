"""
Markdown Report Generator for Azure Resources
Generates comprehensive, well-formatted markdown documentation
"""

from pathlib import Path
from datetime import datetime


class MarkdownGenerator:
    """Generates markdown reports from Azure discovery data"""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.resources_dir = self.output_dir / "resources"
        self.resources_dir.mkdir(exist_ok=True, parents=True)

    def _write_file(self, filename, content):
        """Write content to a markdown file"""
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    def generate_index(self, audit_data):
        """Generate the main index/README file"""
        subscriptions = audit_data.get("subscriptions", [])
        timestamp = audit_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        content = f"""# Azure Infrastructure Audit Report

**Generated:** {timestamp}

## Executive Summary

This report provides a comprehensive overview of all Azure resources discovered across your subscriptions.

### Subscriptions Overview

| Subscription Name | ID | State | Resource Groups |
|------------------|-----|-------|----------------|
"""
        for sub in subscriptions:
            content += f"| {sub.get('name', 'N/A')} | `{sub.get('id', 'N/A')[:20]}...` | {sub.get('state', 'N/A')} | {sub.get('resource_group_count', 0)} |\n"

        content += f"""

## Resource Categories

This audit covers the following resource categories:

### 🌐 [Networking Resources](resources/networking.md)
Virtual Networks, Subnets, NSGs, Load Balancers, VPN Gateways, Firewalls, and more.

### 💻 [Compute Resources](resources/compute.md)
Virtual Machines, VM Scale Sets, App Services, Functions, Containers, AKS clusters, and more.

### 💾 [Storage Resources](resources/storage.md)
Storage Accounts, Managed Disks, Blob Containers, File Shares, and more.

### 🗄️ [Database Resources](resources/databases.md)
SQL Databases, MySQL, PostgreSQL, CosmosDB, Redis Cache, and more.

### 🔍 [DNS Resources](resources/dns.md)
DNS Zones, Private DNS Zones, DNS Records, and domain configurations.

### 🔒 [Security Resources](resources/security.md)
Key Vaults, Managed Identities, Role Assignments, Security Center alerts, and more.

## Detailed Reports

- [Subscription Details](resources/subscriptions.md) - Detailed subscription information
- [Resource Groups](resources/resource-groups.md) - All resource groups and their contents
- [Cost Analysis](resources/cost-analysis.md) - Resource cost overview (requires additional data)

## Quick Statistics

"""
        # Calculate totals across all subscriptions
        total_stats = self._calculate_totals(audit_data)

        content += "### Resources by Type\n\n"
        content += "| Resource Type | Count |\n"
        content += "|--------------|-------|\n"

        for resource_type, count in sorted(total_stats.items()):
            if count > 0:
                content += f"| {resource_type} | {count} |\n"

        content += """

## Navigation

- [Back to Top](#azure-infrastructure-audit-report)
- [Networking Details](resources/networking.md)
- [Compute Details](resources/compute.md)
- [Storage Details](resources/storage.md)
- [Database Details](resources/databases.md)
- [DNS Details](resources/dns.md)
- [Security Details](resources/security.md)

---

*This report was automatically generated using the Azure Infrastructure Discovery Tool.*
"""

        filepath = self._write_file("README.md", content)
        print(f"   ✓ Index report: {filepath}")

    def _calculate_totals(self, audit_data):
        """Calculate total counts across all subscriptions"""
        totals = {}

        # Networking
        for sub_data in audit_data.get("networking", {}).values():
            summary = sub_data.get("summary", {})
            for key, value in summary.items():
                totals[f"Networking - {key}"] = totals.get(f"Networking - {key}", 0) + value

        # Compute
        for sub_data in audit_data.get("compute", {}).values():
            summary = sub_data.get("summary", {})
            for key, value in summary.items():
                totals[f"Compute - {key}"] = totals.get(f"Compute - {key}", 0) + value

        # Storage
        for sub_data in audit_data.get("storage", {}).values():
            summary = sub_data.get("summary", {})
            for key, value in summary.items():
                totals[f"Storage - {key}"] = totals.get(f"Storage - {key}", 0) + value

        # Databases
        for sub_data in audit_data.get("databases", {}).values():
            summary = sub_data.get("summary", {})
            for key, value in summary.items():
                totals[f"Database - {key}"] = totals.get(f"Database - {key}", 0) + value

        # DNS
        for sub_data in audit_data.get("dns", {}).values():
            summary = sub_data.get("summary", {})
            for key, value in summary.items():
                totals[f"DNS - {key}"] = totals.get(f"DNS - {key}", 0) + value

        # Security
        for sub_data in audit_data.get("security", {}).values():
            summary = sub_data.get("summary", {})
            for key, value in summary.items():
                totals[f"Security - {key}"] = totals.get(f"Security - {key}", 0) + value

        return totals

    def generate_subscription_report(self, audit_data):
        """Generate detailed subscription report"""
        subscriptions = audit_data.get("subscriptions", [])

        content = """# Azure Subscriptions

## Overview

This document provides detailed information about all Azure subscriptions.

"""
        for sub in subscriptions:
            content += f"""
## {sub.get('name', 'Unknown')}

### Basic Information

| Property | Value |
|----------|-------|
| **Subscription ID** | `{sub.get('id', 'N/A')}` |
| **State** | {sub.get('state', 'N/A')} |
| **Tenant ID** | `{sub.get('tenant_id', 'N/A')}` |
| **Cloud Name** | {sub.get('cloud_name', 'N/A')} |
| **Is Default** | {sub.get('is_default', False)} |

### Resource Groups ({sub.get('resource_group_count', 0)})

"""
            if sub.get('resource_groups'):
                content += "| Name | Location | State | Tags |\n"
                content += "|------|----------|-------|------|\n"
                for rg in sub.get('resource_groups', []):
                    tags = ", ".join([f"{k}={v}" for k, v in rg.get('tags', {}).items()]) or "None"
                    content += f"| {rg.get('name')} | {rg.get('location')} | {rg.get('provisioning_state')} | {tags} |\n"
            else:
                content += "*No resource groups found.*\n"

            content += f"""

### Registered Resource Providers

{', '.join(sub.get('registered_providers', [])) or '*None*'}

---

"""

        content += "\n[← Back to Index](../README.md)\n"

        filepath = self.resources_dir / "subscriptions.md"
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"   ✓ Subscription report: {filepath}")

    def generate_networking_report(self, audit_data):
        """Generate networking resources report"""
        content = """# Networking Resources

## Overview

This document details all networking resources including VNets, Subnets, NSGs, Load Balancers, and more.

"""
        networking_data = audit_data.get("networking", {})

        for sub_id, net_data in networking_data.items():
            if net_data.get("error"):
                content += f"\n**Error discovering networking resources:** {net_data.get('error')}\n"
                continue

            summary = net_data.get("summary", {})
            content += f"""
## Summary

| Resource Type | Count |
|--------------|-------|
| Virtual Networks | {summary.get('vnets', 0)} |
| Subnets | {summary.get('subnets', 0)} |
| Network Security Groups | {summary.get('nsgs', 0)} |
| Public IP Addresses | {summary.get('public_ips', 0)} |
| Load Balancers | {summary.get('load_balancers', 0)} |
| Application Gateways | {summary.get('application_gateways', 0)} |
| VPN Gateways | {summary.get('vpn_gateways', 0)} |
| Virtual Network Gateways | {summary.get('vnet_gateways', 0)} |
| Azure Firewalls | {summary.get('firewalls', 0)} |
| Route Tables | {summary.get('route_tables', 0)} |
| Network Interfaces | {summary.get('network_interfaces', 0)} |

"""

            # Virtual Networks
            vnets = net_data.get("vnets", [])
            if vnets:
                content += "## Virtual Networks\n\n"
                for vnet in vnets:
                    content += f"""
### {vnet.get('name')}

**Location:** {vnet.get('location')} | **Resource Group:** {vnet.get('resource_group')}

**Address Space:** {', '.join(vnet.get('address_space', []))}

**Subnets:**

| Name | Address Prefix | NSG | Service Endpoints |
|------|----------------|-----|-------------------|
"""
                    for subnet in vnet.get('subnets', []):
                        nsg = "Yes" if subnet.get('nsg') else "No"
                        endpoints = ', '.join(subnet.get('service_endpoints', [])) or 'None'
                        content += f"| {subnet.get('name')} | {subnet.get('address_prefix')} | {nsg} | {endpoints} |\n"

                    if vnet.get('peerings'):
                        content += "\n**Peering Connections:**\n\n"
                        for peer in vnet.get('peerings', []):
                            content += f"- {peer.get('name')} → {peer.get('remote_vnet')} (State: {peer.get('peering_state')})\n"

                    content += "\n"

            # Network Security Groups
            nsgs = net_data.get("nsgs", [])
            if nsgs:
                content += "## Network Security Groups\n\n"
                for nsg in nsgs:
                    content += f"""
### {nsg.get('name')}

**Location:** {nsg.get('location')} | **Resource Group:** {nsg.get('resource_group')}

**Security Rules:**

| Name | Priority | Direction | Access | Protocol | Source | Destination |
|------|----------|-----------|--------|----------|--------|-------------|
"""
                    for rule in nsg.get('security_rules', []):
                        content += (f"| {rule.get('name')} | {rule.get('priority')} | "
                                  f"{rule.get('direction')} | {rule.get('access')} | "
                                  f"{rule.get('protocol')} | {rule.get('source_address_prefix')}:{rule.get('source_port_range')} | "
                                  f"{rule.get('destination_address_prefix')}:{rule.get('destination_port_range')} |\n")
                    content += "\n"

            # Public IP Addresses
            public_ips = net_data.get("public_ips", [])
            if public_ips:
                content += "## Public IP Addresses\n\n"
                content += "| Name | IP Address | SKU | Allocation | DNS FQDN | Resource Group |\n"
                content += "|------|-----------|-----|------------|----------|----------------|\n"
                for pip in public_ips:
                    content += (f"| {pip.get('name')} | {pip.get('ip_address', 'Not Assigned')} | "
                              f"{pip.get('sku', 'N/A')} | {pip.get('allocation_method')} | "
                              f"{pip.get('dns_fqdn', 'N/A')} | {pip.get('resource_group')} |\n")
                content += "\n"

            # Load Balancers
            lbs = net_data.get("load_balancers", [])
            if lbs:
                content += "## Load Balancers\n\n"
                for lb in lbs:
                    content += f"""
### {lb.get('name')}

**SKU:** {lb.get('sku')} | **Location:** {lb.get('location')} | **Resource Group:** {lb.get('resource_group')}

**Frontend IP Configurations:** {len(lb.get('frontend_ip_configurations', []))}
**Backend Pools:** {len(lb.get('backend_pools', []))}
**Load Balancing Rules:** {len(lb.get('rules', []))}
**Health Probes:** {len(lb.get('probes', []))}

"""

            # Firewalls
            firewalls = net_data.get("firewalls", [])
            if firewalls:
                content += "## Azure Firewalls\n\n"
                content += "| Name | SKU | Tier | Threat Intel Mode | Location | Resource Group |\n"
                content += "|------|-----|------|-------------------|----------|----------------|\n"
                for fw in firewalls:
                    content += (f"| {fw.get('name')} | {fw.get('sku')} | {fw.get('tier')} | "
                              f"{fw.get('threat_intel_mode')} | {fw.get('location')} | {fw.get('resource_group')} |\n")
                content += "\n"

        content += "\n[← Back to Index](../README.md)\n"

        filepath = self.resources_dir / "networking.md"
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"   ✓ Networking report: {filepath}")

    def generate_compute_report(self, audit_data):
        """Generate compute resources report"""
        content = """# Compute Resources

## Overview

This document details all compute resources including Virtual Machines, App Services, Functions, and Containers.

"""
        compute_data = audit_data.get("compute", {})

        for sub_id, comp_data in compute_data.items():
            if comp_data.get("error"):
                content += f"\n**Error discovering compute resources:** {comp_data.get('error')}\n"
                continue

            summary = comp_data.get("summary", {})
            content += f"""
## Summary

| Resource Type | Count |
|--------------|-------|
| Virtual Machines | {summary.get('vms', 0)} |
| VM Scale Sets | {summary.get('vmss', 0)} |
| App Services | {summary.get('app_services', 0)} |
| App Service Plans | {summary.get('app_service_plans', 0)} |
| Function Apps | {summary.get('functions', 0)} |
| Container Instances | {summary.get('containers', 0)} |
| AKS Clusters | {summary.get('aks_clusters', 0)} |
| Batch Accounts | {summary.get('batch_accounts', 0)} |
| Availability Sets | {summary.get('availability_sets', 0)} |

"""

            # Virtual Machines
            vms = comp_data.get("virtual_machines", [])
            if vms:
                content += "## Virtual Machines\n\n"
                content += "| Name | Size | OS | Power State | Location | Private IPs | Public IPs |\n"
                content += "|------|------|----| ------------|----------|-------------|------------|\n"
                for vm in vms:
                    private_ips = ', '.join(vm.get('private_ips', [])) or 'None'
                    public_ips = ', '.join(vm.get('public_ips', [])) or 'None'
                    content += (f"| {vm.get('name')} | {vm.get('size')} | {vm.get('os_type')} | "
                              f"{vm.get('power_state', 'Unknown')} | {vm.get('location')} | "
                              f"{private_ips} | {public_ips} |\n")
                content += "\n"

                # Detailed VM information
                for vm in vms:
                    content += f"""
### {vm.get('name')} Details

**Resource Group:** {vm.get('resource_group')} | **Location:** {vm.get('location')}

- **Size:** {vm.get('size')}
- **OS Type:** {vm.get('os_type')}
- **Power State:** {vm.get('power_state', 'Unknown')}
- **Provisioning State:** {vm.get('provisioning_state')}
- **OS Disk Size:** {vm.get('os_disk_size')} GB
- **Availability Zone:** {', '.join(vm.get('zones', [])) or 'None'}
- **Extensions:** {len(vm.get('extensions', []))}
- **Boot Diagnostics:** {'Enabled' if vm.get('boot_diagnostics_enabled') else 'Disabled'}

"""
                    if vm.get('image_reference', {}).get('publisher'):
                        img = vm.get('image_reference', {})
                        content += f"**Image:** {img.get('publisher')} {img.get('offer')} {img.get('sku')}\n\n"

            # App Services
            app_services = comp_data.get("app_services", [])
            if app_services:
                content += "## App Services\n\n"
                content += "| Name | State | Runtime | HTTPS Only | Location | Default Hostname |\n"
                content += "|------|-------|---------|------------|----------|------------------|\n"
                for app in app_services:
                    runtime = app.get('runtime', {}).get('linux_fx_version') or app.get('runtime', {}).get('windows_fx_version') or 'N/A'
                    content += (f"| {app.get('name')} | {app.get('state')} | {runtime} | "
                              f"{'Yes' if app.get('https_only') else 'No'} | {app.get('location')} | "
                              f"{app.get('default_hostname')} |\n")
                content += "\n"

            # Function Apps
            function_apps = comp_data.get("function_apps", [])
            if function_apps:
                content += "## Function Apps\n\n"
                content += "| Name | State | Runtime | HTTPS Only | Location | Default Hostname |\n"
                content += "|------|-------|---------|------------|----------|------------------|\n"
                for func in function_apps:
                    content += (f"| {func.get('name')} | {func.get('state')} | {func.get('runtime')} | "
                              f"{'Yes' if func.get('https_only') else 'No'} | {func.get('location')} | "
                              f"{func.get('default_hostname')} |\n")
                content += "\n"

            # AKS Clusters
            aks_clusters = comp_data.get("kubernetes_services", [])
            if aks_clusters:
                content += "## Azure Kubernetes Service (AKS)\n\n"
                for aks in aks_clusters:
                    content += f"""
### {aks.get('name')}

**Resource Group:** {aks.get('resource_group')} | **Location:** {aks.get('location')}

- **Kubernetes Version:** {aks.get('kubernetes_version')}
- **FQDN:** {aks.get('fqdn')}
- **DNS Prefix:** {aks.get('dns_prefix')}
- **RBAC Enabled:** {'Yes' if aks.get('enable_rbac') else 'No'}
- **Network Plugin:** {aks.get('network_profile', {}).get('network_plugin')}

**Node Pools:**

| Name | Count | VM Size | OS Type | Mode |
|------|-------|---------|---------|------|
"""
                    for pool in aks.get('agent_pools', []):
                        content += (f"| {pool.get('name')} | {pool.get('count')} | {pool.get('vm_size')} | "
                                  f"{pool.get('os_type')} | {pool.get('mode')} |\n")
                    content += "\n"

        content += "\n[← Back to Index](../README.md)\n"

        filepath = self.resources_dir / "compute.md"
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"   ✓ Compute report: {filepath}")

    def generate_storage_report(self, audit_data):
        """Generate storage resources report"""
        content = """# Storage Resources

## Overview

This document details all storage resources including Storage Accounts, Managed Disks, and more.

"""
        storage_data = audit_data.get("storage", {})

        for sub_id, stor_data in storage_data.items():
            if stor_data.get("error"):
                content += f"\n**Error discovering storage resources:** {stor_data.get('error')}\n"
                continue

            summary = stor_data.get("summary", {})
            content += f"""
## Summary

| Resource Type | Count |
|--------------|-------|
| Storage Accounts | {summary.get('storage_accounts', 0)} |
| Managed Disks | {summary.get('disks', 0)} |
| Disk Snapshots | {summary.get('snapshots', 0)} |

"""

            # Storage Accounts
            storage_accounts = stor_data.get("storage_accounts", [])
            if storage_accounts:
                content += "## Storage Accounts\n\n"
                for sa in storage_accounts:
                    content += f"""
### {sa.get('name')}

**Resource Group:** {sa.get('resource_group')} | **Location:** {sa.get('location')}

| Property | Value |
|----------|-------|
| **SKU** | {sa.get('sku', {}).get('name')} ({sa.get('sku', {}).get('tier')}) |
| **Kind** | {sa.get('kind')} |
| **Access Tier** | {sa.get('access_tier', 'N/A')} |
| **HTTPS Only** | {'Yes' if sa.get('https_only') else 'No'} |
| **Public Blob Access** | {'Allowed' if sa.get('allow_blob_public_access') else 'Disabled'} |
| **Min TLS Version** | {sa.get('minimum_tls_version', 'N/A')} |
| **Primary Location** | {sa.get('primary_location')} |
| **Secondary Location** | {sa.get('secondary_location', 'N/A')} |

**Contents:**
- Blob Containers: {sa.get('blob_container_count', 0)}
- File Shares: {sa.get('file_share_count', 0)}
- Queues: {sa.get('queue_count', 0)}
- Tables: {sa.get('table_count', 0)}

**Network Access:**
- Default Action: {sa.get('network_rule_set', {}).get('default_action', 'N/A')}
- IP Rules: {len(sa.get('network_rule_set', {}).get('ip_rules', []))}
- VNet Rules: {len(sa.get('network_rule_set', {}).get('virtual_network_rules', []))}

"""

            # Managed Disks
            disks = stor_data.get("managed_disks", [])
            if disks:
                content += "## Managed Disks\n\n"
                content += "| Name | Size (GB) | SKU | OS Type | State | Attached To | Location |\n"
                content += "|------|-----------|-----|---------|-------|-------------|----------|\n"
                for disk in disks:
                    attached = disk.get('attached_to', '').split('/')[-1] if disk.get('attached_to') else 'Unattached'
                    content += (f"| {disk.get('name')} | {disk.get('disk_size_gb')} | "
                              f"{disk.get('sku', {}).get('name')} | {disk.get('os_type', 'Data')} | "
                              f"{disk.get('disk_state')} | {attached} | {disk.get('location')} |\n")
                content += "\n"

        content += "\n[← Back to Index](../README.md)\n"

        filepath = self.resources_dir / "storage.md"
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"   ✓ Storage report: {filepath}")

    def generate_database_report(self, audit_data):
        """Generate database resources report"""
        content = """# Database Resources

## Overview

This document details all database resources including SQL, MySQL, PostgreSQL, CosmosDB, and Redis.

"""
        database_data = audit_data.get("databases", {})

        for sub_id, db_data in database_data.items():
            if db_data.get("error"):
                content += f"\n**Error discovering database resources:** {db_data.get('error')}\n"
                continue

            summary = db_data.get("summary", {})
            content += f"""
## Summary

| Resource Type | Count |
|--------------|-------|
| SQL Servers | {summary.get('sql_servers', 0)} |
| SQL Databases | {summary.get('sql_databases', 0)} |
| MySQL Servers | {summary.get('mysql', 0)} |
| PostgreSQL Servers | {summary.get('postgresql', 0)} |
| CosmosDB Accounts | {summary.get('cosmosdb', 0)} |
| Redis Caches | {summary.get('redis', 0)} |
| MariaDB Servers | {summary.get('mariadb', 0)} |

"""

            # SQL Servers
            sql_servers = db_data.get("sql_servers", [])
            if sql_servers:
                content += "## SQL Servers\n\n"
                for server in sql_servers:
                    content += f"""
### {server.get('name')}

**Resource Group:** {server.get('resource_group')} | **Location:** {server.get('location')}

| Property | Value |
|----------|-------|
| **FQDN** | {server.get('fully_qualified_domain_name')} |
| **Version** | {server.get('version')} |
| **Admin Login** | {server.get('administrator_login')} |
| **Public Network Access** | {server.get('public_network_access', 'N/A')} |
| **Min TLS Version** | {server.get('minimal_tls_version', 'N/A')} |
| **State** | {server.get('state')} |

**Databases ({len(server.get('databases', []))}):**

"""
                    if server.get('databases'):
                        content += "| Name | SKU | Max Size | Status |\n"
                        content += "|------|-----|----------|--------|\n"
                        for db in server.get('databases', []):
                            max_size = f"{int(db.get('max_size_bytes', 0) / (1024**3))} GB" if db.get('max_size_bytes') else 'N/A'
                            content += (f"| {db.get('name')} | {db.get('sku', {}).get('name')} | "
                                      f"{max_size} | {db.get('status')} |\n")

                    content += "\n**Firewall Rules:**\n\n"
                    if server.get('firewall_rules'):
                        for rule in server.get('firewall_rules', []):
                            content += f"- {rule.get('name')}: {rule.get('start_ip')} - {rule.get('end_ip')}\n"
                    else:
                        content += "*No firewall rules configured.*\n"
                    content += "\n"

            # MySQL Servers
            mysql_servers = db_data.get("mysql_servers", [])
            if mysql_servers:
                content += "## MySQL Servers\n\n"
                content += "| Name | Version | SKU | Storage (MB) | SSL | Location |\n"
                content += "|------|---------|-----|--------------|-----|----------|\n"
                for server in mysql_servers:
                    content += (f"| {server.get('name')} | {server.get('version')} | "
                              f"{server.get('sku', {}).get('name')} | {server.get('storage_mb')} | "
                              f"{server.get('ssl_enforcement')} | {server.get('location')} |\n")
                content += "\n"

            # PostgreSQL Servers
            postgresql_servers = db_data.get("postgresql_servers", [])
            if postgresql_servers:
                content += "## PostgreSQL Servers\n\n"
                content += "| Name | Version | SKU | Storage (MB) | SSL | Location |\n"
                content += "|------|---------|-----|--------------|-----|----------|\n"
                for server in postgresql_servers:
                    content += (f"| {server.get('name')} | {server.get('version')} | "
                              f"{server.get('sku', {}).get('name')} | {server.get('storage_mb')} | "
                              f"{server.get('ssl_enforcement')} | {server.get('location')} |\n")
                content += "\n"

            # CosmosDB
            cosmosdb_accounts = db_data.get("cosmosdb_accounts", [])
            if cosmosdb_accounts:
                content += "## CosmosDB Accounts\n\n"
                for account in cosmosdb_accounts:
                    content += f"""
### {account.get('name')}

**Resource Group:** {account.get('resource_group')} | **Location:** {account.get('location')}

- **Kind:** {account.get('kind')}
- **Document Endpoint:** {account.get('document_endpoint')}
- **Consistency Level:** {account.get('consistency_policy', {}).get('default_consistency_level')}
- **Multi-Region Writes:** {'Enabled' if account.get('enable_multiple_write_locations') else 'Disabled'}
- **Automatic Failover:** {'Enabled' if account.get('enable_automatic_failover') else 'Disabled'}

**Locations:**
"""
                    for loc in account.get('locations', []):
                        content += f"- {loc.get('location')} (Priority: {loc.get('failover_priority')})\n"
                    content += "\n"

            # Redis Cache
            redis_caches = db_data.get("redis_caches", [])
            if redis_caches:
                content += "## Redis Caches\n\n"
                content += "| Name | Version | SKU | Hostname | SSL Port | Location |\n"
                content += "|------|---------|-----|----------|----------|----------|\n"
                for redis in redis_caches:
                    content += (f"| {redis.get('name')} | {redis.get('redis_version')} | "
                              f"{redis.get('sku', {}).get('name')} | {redis.get('hostname')} | "
                              f"{redis.get('ssl_port')} | {redis.get('location')} |\n")
                content += "\n"

        content += "\n[← Back to Index](../README.md)\n"

        filepath = self.resources_dir / "databases.md"
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"   ✓ Database report: {filepath}")

    def generate_dns_report(self, audit_data):
        """Generate DNS resources report"""
        content = """# DNS Resources

## Overview

This document details all DNS resources including DNS Zones and Private DNS Zones.

"""
        dns_data = audit_data.get("dns", {})

        for sub_id, dns_info in dns_data.items():
            if dns_info.get("error"):
                content += f"\n**Error discovering DNS resources:** {dns_info.get('error')}\n"
                continue

            summary = dns_info.get("summary", {})
            content += f"""
## Summary

| Resource Type | Count |
|--------------|-------|
| Public DNS Zones | {summary.get('dns_zones', 0)} |
| Private DNS Zones | {summary.get('private_dns_zones', 0)} |

"""

            # Public DNS Zones
            dns_zones = dns_info.get("dns_zones", [])
            if dns_zones:
                content += "## Public DNS Zones\n\n"
                for zone in dns_zones:
                    content += f"""
### {zone.get('name')}

**Resource Group:** {zone.get('resource_group')}

- **Number of Record Sets:** {zone.get('number_of_record_sets')}
- **Zone Type:** {zone.get('zone_type', 'Public')}

**Name Servers:**
"""
                    for ns in zone.get('name_servers', []):
                        content += f"- {ns}\n"

                    content += "\n**DNS Records:**\n\n"
                    content += "| Name | Type | TTL | Records |\n"
                    content += "|------|------|-----|----------|\n"

                    for record in zone.get('record_sets', [])[:50]:  # Limit to 50 records
                        record_type = record.get('type', '').split('/')[-1]
                        records_str = ""

                        if 'a_records' in record:
                            records_str = ', '.join(record['a_records'])
                        elif 'cname_record' in record:
                            records_str = record['cname_record']
                        elif 'mx_records' in record:
                            records_str = ', '.join([f"{r.get('preference')} {r.get('exchange')}" for r in record['mx_records']])
                        elif 'txt_records' in record:
                            records_str = ', '.join([str(r)[:50] for r in record['txt_records']])

                        content += f"| {record.get('name')} | {record_type} | {record.get('ttl')} | {records_str[:100]} |\n"
                    content += "\n"

            # Private DNS Zones
            private_dns_zones = dns_info.get("private_dns_zones", [])
            if private_dns_zones:
                content += "## Private DNS Zones\n\n"
                for zone in private_dns_zones:
                    content += f"""
### {zone.get('name')}

**Resource Group:** {zone.get('resource_group')}

- **Number of Record Sets:** {zone.get('number_of_record_sets')}
- **Virtual Network Links:** {zone.get('number_of_virtual_network_links')}

**VNet Links:**
"""
                    for link in zone.get('virtual_network_links', []):
                        reg_status = "Registration Enabled" if link.get('registration_enabled') else "No Registration"
                        content += f"- {link.get('name')}: {link.get('virtual_network')} ({reg_status})\n"
                    content += "\n"

        content += "\n[← Back to Index](../README.md)\n"

        filepath = self.resources_dir / "dns.md"
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"   ✓ DNS report: {filepath}")

    def generate_security_report(self, audit_data):
        """Generate security resources report"""
        content = """# Security Resources

## Overview

This document details all security-related resources including Key Vaults, Managed Identities, and Security Center findings.

"""
        security_data = audit_data.get("security", {})

        for sub_id, sec_data in security_data.items():
            if sec_data.get("error"):
                content += f"\n**Error discovering security resources:** {sec_data.get('error')}\n"
                continue

            summary = sec_data.get("summary", {})
            content += f"""
## Summary

| Resource Type | Count |
|--------------|-------|
| Key Vaults | {summary.get('key_vaults', 0)} |
| Managed Identities | {summary.get('managed_identities', 0)} |
| Role Assignments | {summary.get('role_assignments', 0)} |
| Security Alerts | {summary.get('security_alerts', 0)} |
| Security Recommendations | {summary.get('security_recommendations', 0)} |
| Security Contacts | {summary.get('security_contacts', 0)} |

"""

            # Key Vaults
            key_vaults = sec_data.get("key_vaults", [])
            if key_vaults:
                content += "## Key Vaults\n\n"
                for kv in key_vaults:
                    content += f"""
### {kv.get('name')}

**Resource Group:** {kv.get('resource_group')} | **Location:** {kv.get('location')}

| Property | Value |
|----------|-------|
| **Vault URI** | {kv.get('vault_uri')} |
| **SKU** | {kv.get('sku')} |
| **Soft Delete** | {'Enabled' if kv.get('enable_soft_delete') else 'Disabled'} ({kv.get('soft_delete_retention_days', 0)} days) |
| **Purge Protection** | {'Enabled' if kv.get('enable_purge_protection') else 'Disabled'} |
| **RBAC Authorization** | {'Enabled' if kv.get('enable_rbac_authorization') else 'Disabled'} |
| **Public Network Access** | {kv.get('public_network_access', 'N/A')} |

**Contents:**
- Secrets: {kv.get('secret_count', 0)}
- Keys: {kv.get('key_count', 0)}
- Certificates: {kv.get('certificate_count', 0)}

**Network Access:**
- Default Action: {kv.get('network_acls', {}).get('default_action', 'N/A')}
- Bypass: {kv.get('network_acls', {}).get('bypass', 'N/A')}
- IP Rules: {len(kv.get('network_acls', {}).get('ip_rules', []))}
- VNet Rules: {len(kv.get('network_acls', {}).get('virtual_network_rules', []))}

"""

            # Managed Identities
            managed_identities = sec_data.get("managed_identities", [])
            if managed_identities:
                content += "## Managed Identities\n\n"
                content += "| Name | Type | Principal ID | Location | Resource Group |\n"
                content += "|------|------|--------------|----------|----------------|\n"
                for identity in managed_identities:
                    content += (f"| {identity.get('name')} | {identity.get('type')} | "
                              f"`{identity.get('principal_id')}` | {identity.get('location')} | "
                              f"{identity.get('resource_group')} |\n")
                content += "\n"

            # Security Center Alerts
            security_alerts = sec_data.get("security_center_alerts", [])
            if security_alerts:
                content += "## Security Center Alerts\n\n"
                content += "| Display Name | Severity | Status | Compromised Entity | Start Time |\n"
                content += "|--------------|----------|--------|-------------------|------------|\n"
                for alert in security_alerts[:20]:  # Limit to 20 alerts
                    content += (f"| {alert.get('display_name', 'N/A')} | {alert.get('severity')} | "
                              f"{alert.get('status')} | {alert.get('compromised_entity', 'N/A')} | "
                              f"{alert.get('start_time', 'N/A')} |\n")
                content += "\n"

            # Security Recommendations
            security_recommendations = sec_data.get("security_center_recommendations", [])
            if security_recommendations:
                content += "## Security Center Recommendations\n\n"
                for rec in security_recommendations[:10]:  # Limit to 10 recommendations
                    content += f"""
### {rec.get('display_name', 'Recommendation')}

- **Status:** {rec.get('status')}
- **Severity:** {rec.get('severity')}
- **Description:** {rec.get('description', 'N/A')}
- **Remediation:** {rec.get('remediation_description', 'N/A')}

"""

        content += "\n[← Back to Index](../README.md)\n"

        filepath = self.resources_dir / "security.md"
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"   ✓ Security report: {filepath}")


def generate_all_reports(audit_data, output_dir):
    """Generate all markdown reports"""
    generator = MarkdownGenerator(output_dir)

    generator.generate_index(audit_data)
    generator.generate_subscription_report(audit_data)
    generator.generate_networking_report(audit_data)
    generator.generate_compute_report(audit_data)
    generator.generate_storage_report(audit_data)
    generator.generate_database_report(audit_data)
    generator.generate_dns_report(audit_data)
    generator.generate_security_report(audit_data)

    print(f"\n✓ All reports generated successfully in: {output_dir}")

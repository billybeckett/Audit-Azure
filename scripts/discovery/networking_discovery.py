"""
Azure Networking Discovery Module
Discovers VNets, Subnets, NSGs, Public IPs, Load Balancers, VPN Gateways, etc.
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


def discover_networking(subscription_id):
    """
    Discover all networking resources in a subscription

    Args:
        subscription_id: Azure subscription ID

    Returns:
        dict: Dictionary containing all networking resources
    """
    networking_data = {
        "vnets": [],
        "subnets": [],
        "nsgs": [],
        "public_ips": [],
        "load_balancers": [],
        "application_gateways": [],
        "vpn_gateways": [],
        "vnet_gateways": [],
        "express_routes": [],
        "firewalls": [],
        "route_tables": [],
        "network_interfaces": [],
        "peering_connections": [],
        "summary": {}
    }

    # Virtual Networks
    vnets = run_az_command(
        f"az network vnet list --subscription {subscription_id} --output json"
    )
    for vnet in vnets:
        vnet_info = {
            "name": vnet.get("name"),
            "id": vnet.get("id"),
            "location": vnet.get("location"),
            "resource_group": vnet.get("resourceGroup"),
            "address_space": vnet.get("addressSpace", {}).get("addressPrefixes", []),
            "dns_servers": vnet.get("dhcpOptions", {}).get("dnsServers", []),
            "enable_ddos_protection": vnet.get("enableDdosProtection", False),
            "enable_vm_protection": vnet.get("enableVmProtection", False),
            "provisioning_state": vnet.get("provisioningState"),
            "tags": vnet.get("tags", {}),
            "subnets": []
        }

        # Get subnets for this VNet
        if vnet.get("subnets"):
            for subnet in vnet.get("subnets", []):
                subnet_info = {
                    "name": subnet.get("name"),
                    "id": subnet.get("id"),
                    "address_prefix": subnet.get("addressPrefix"),
                    "nsg": subnet.get("networkSecurityGroup", {}).get("id"),
                    "route_table": subnet.get("routeTable", {}).get("id"),
                    "service_endpoints": [
                        ep.get("service") for ep in subnet.get("serviceEndpoints", [])
                    ],
                    "delegations": [
                        d.get("serviceName") for d in subnet.get("delegations", [])
                    ],
                    "private_endpoint_network_policies": subnet.get(
                        "privateEndpointNetworkPolicies"
                    ),
                    "provisioning_state": subnet.get("provisioningState")
                }
                vnet_info["subnets"].append(subnet_info)
                networking_data["subnets"].append(subnet_info)

        # Get VNet peerings
        peerings = run_az_command(
            f"az network vnet peering list --subscription {subscription_id} "
            f"--resource-group {vnet.get('resourceGroup')} "
            f"--vnet-name {vnet.get('name')} --output json"
        )
        vnet_info["peerings"] = [
            {
                "name": p.get("name"),
                "peering_state": p.get("peeringState"),
                "remote_vnet": p.get("remoteVirtualNetwork", {}).get("id"),
                "allow_forwarded_traffic": p.get("allowForwardedTraffic"),
                "allow_gateway_transit": p.get("allowGatewayTransit"),
                "use_remote_gateways": p.get("useRemoteGateways")
            }
            for p in peerings
        ]

        networking_data["vnets"].append(vnet_info)

    # Network Security Groups
    nsgs = run_az_command(
        f"az network nsg list --subscription {subscription_id} --output json"
    )
    for nsg in nsgs:
        nsg_info = {
            "name": nsg.get("name"),
            "id": nsg.get("id"),
            "location": nsg.get("location"),
            "resource_group": nsg.get("resourceGroup"),
            "provisioning_state": nsg.get("provisioningState"),
            "tags": nsg.get("tags", {}),
            "security_rules": []
        }

        # Get security rules
        for rule in nsg.get("securityRules", []):
            rule_info = {
                "name": rule.get("name"),
                "priority": rule.get("priority"),
                "direction": rule.get("direction"),
                "access": rule.get("access"),
                "protocol": rule.get("protocol"),
                "source_address_prefix": rule.get("sourceAddressPrefix"),
                "source_port_range": rule.get("sourcePortRange"),
                "destination_address_prefix": rule.get("destinationAddressPrefix"),
                "destination_port_range": rule.get("destinationPortRange"),
                "description": rule.get("description")
            }
            nsg_info["security_rules"].append(rule_info)

        networking_data["nsgs"].append(nsg_info)

    # Public IP Addresses
    public_ips = run_az_command(
        f"az network public-ip list --subscription {subscription_id} --output json"
    )
    for pip in public_ips:
        pip_info = {
            "name": pip.get("name"),
            "id": pip.get("id"),
            "location": pip.get("location"),
            "resource_group": pip.get("resourceGroup"),
            "ip_address": pip.get("ipAddress"),
            "allocation_method": pip.get("publicIPAllocationMethod"),
            "sku": pip.get("sku", {}).get("name"),
            "ip_version": pip.get("publicIPAddressVersion"),
            "dns_fqdn": pip.get("dnsSettings", {}).get("fqdn"),
            "idle_timeout": pip.get("idleTimeoutInMinutes"),
            "associated_resource": pip.get("ipConfiguration", {}).get("id"),
            "tags": pip.get("tags", {})
        }
        networking_data["public_ips"].append(pip_info)

    # Load Balancers
    lbs = run_az_command(
        f"az network lb list --subscription {subscription_id} --output json"
    )
    for lb in lbs:
        lb_info = {
            "name": lb.get("name"),
            "id": lb.get("id"),
            "location": lb.get("location"),
            "resource_group": lb.get("resourceGroup"),
            "sku": lb.get("sku", {}).get("name"),
            "frontend_ip_configurations": [
                {
                    "name": fip.get("name"),
                    "private_ip": fip.get("privateIPAddress"),
                    "public_ip": fip.get("publicIPAddress", {}).get("id"),
                    "subnet": fip.get("subnet", {}).get("id")
                }
                for fip in lb.get("frontendIPConfigurations", [])
            ],
            "backend_pools": [
                {
                    "name": pool.get("name"),
                    "id": pool.get("id")
                }
                for pool in lb.get("backendAddressPools", [])
            ],
            "probes": [
                {
                    "name": probe.get("name"),
                    "protocol": probe.get("protocol"),
                    "port": probe.get("port"),
                    "interval": probe.get("intervalInSeconds")
                }
                for probe in lb.get("probes", [])
            ],
            "rules": [
                {
                    "name": rule.get("name"),
                    "protocol": rule.get("protocol"),
                    "frontend_port": rule.get("frontendPort"),
                    "backend_port": rule.get("backendPort")
                }
                for rule in lb.get("loadBalancingRules", [])
            ],
            "tags": lb.get("tags", {})
        }
        networking_data["load_balancers"].append(lb_info)

    # Application Gateways
    app_gws = run_az_command(
        f"az network application-gateway list --subscription {subscription_id} --output json"
    )
    for agw in app_gws:
        agw_info = {
            "name": agw.get("name"),
            "id": agw.get("id"),
            "location": agw.get("location"),
            "resource_group": agw.get("resourceGroup"),
            "sku": agw.get("sku", {}).get("name"),
            "tier": agw.get("sku", {}).get("tier"),
            "capacity": agw.get("sku", {}).get("capacity"),
            "operational_state": agw.get("operationalState"),
            "tags": agw.get("tags", {})
        }
        networking_data["application_gateways"].append(agw_info)

    # VPN Gateways
    vpn_gws = run_az_command(
        f"az network vpn-gateway list --subscription {subscription_id} --output json"
    )
    for vpn in vpn_gws:
        vpn_info = {
            "name": vpn.get("name"),
            "id": vpn.get("id"),
            "location": vpn.get("location"),
            "resource_group": vpn.get("resourceGroup"),
            "provisioning_state": vpn.get("provisioningState"),
            "tags": vpn.get("tags", {})
        }
        networking_data["vpn_gateways"].append(vpn_info)

    # Virtual Network Gateways
    vnet_gws = run_az_command(
        f"az network vnet-gateway list --subscription {subscription_id} --output json"
    )
    for vgw in vnet_gws:
        vgw_info = {
            "name": vgw.get("name"),
            "id": vgw.get("id"),
            "location": vgw.get("location"),
            "resource_group": vgw.get("resourceGroup"),
            "gateway_type": vgw.get("gatewayType"),
            "vpn_type": vgw.get("vpnType"),
            "sku": vgw.get("sku", {}).get("name"),
            "active_active": vgw.get("activeActive"),
            "enable_bgp": vgw.get("enableBgp"),
            "provisioning_state": vgw.get("provisioningState"),
            "tags": vgw.get("tags", {})
        }
        networking_data["vnet_gateways"].append(vgw_info)

    # Azure Firewalls
    firewalls = run_az_command(
        f"az network firewall list --subscription {subscription_id} --output json"
    )
    for fw in firewalls:
        fw_info = {
            "name": fw.get("name"),
            "id": fw.get("id"),
            "location": fw.get("location"),
            "resource_group": fw.get("resourceGroup"),
            "sku": fw.get("sku", {}).get("name"),
            "tier": fw.get("sku", {}).get("tier"),
            "threat_intel_mode": fw.get("threatIntelMode"),
            "provisioning_state": fw.get("provisioningState"),
            "tags": fw.get("tags", {})
        }
        networking_data["firewalls"].append(fw_info)

    # Route Tables
    route_tables = run_az_command(
        f"az network route-table list --subscription {subscription_id} --output json"
    )
    for rt in route_tables:
        rt_info = {
            "name": rt.get("name"),
            "id": rt.get("id"),
            "location": rt.get("location"),
            "resource_group": rt.get("resourceGroup"),
            "disable_bgp_route_propagation": rt.get("disableBgpRoutePropagation"),
            "routes": [
                {
                    "name": route.get("name"),
                    "address_prefix": route.get("addressPrefix"),
                    "next_hop_type": route.get("nextHopType"),
                    "next_hop_ip": route.get("nextHopIpAddress")
                }
                for route in rt.get("routes", [])
            ],
            "tags": rt.get("tags", {})
        }
        networking_data["route_tables"].append(rt_info)

    # Network Interfaces
    nics = run_az_command(
        f"az network nic list --subscription {subscription_id} --output json"
    )
    for nic in nics:
        nic_info = {
            "name": nic.get("name"),
            "id": nic.get("id"),
            "location": nic.get("location"),
            "resource_group": nic.get("resourceGroup"),
            "mac_address": nic.get("macAddress"),
            "primary": nic.get("primary"),
            "enable_accelerated_networking": nic.get("enableAcceleratedNetworking"),
            "enable_ip_forwarding": nic.get("enableIPForwarding"),
            "network_security_group": nic.get("networkSecurityGroup", {}).get("id"),
            "ip_configurations": [
                {
                    "name": ip.get("name"),
                    "private_ip": ip.get("privateIPAddress"),
                    "private_ip_allocation": ip.get("privateIPAllocationMethod"),
                    "public_ip": ip.get("publicIPAddress", {}).get("id"),
                    "subnet": ip.get("subnet", {}).get("id"),
                    "primary": ip.get("primary")
                }
                for ip in nic.get("ipConfigurations", [])
            ],
            "dns_servers": nic.get("dnsSettings", {}).get("dnsServers", []),
            "attached_to": nic.get("virtualMachine", {}).get("id"),
            "tags": nic.get("tags", {})
        }
        networking_data["network_interfaces"].append(nic_info)

    # Calculate summary
    networking_data["summary"] = {
        "vnets": len(networking_data["vnets"]),
        "subnets": len(networking_data["subnets"]),
        "nsgs": len(networking_data["nsgs"]),
        "public_ips": len(networking_data["public_ips"]),
        "load_balancers": len(networking_data["load_balancers"]),
        "application_gateways": len(networking_data["application_gateways"]),
        "vpn_gateways": len(networking_data["vpn_gateways"]),
        "vnet_gateways": len(networking_data["vnet_gateways"]),
        "firewalls": len(networking_data["firewalls"]),
        "route_tables": len(networking_data["route_tables"]),
        "network_interfaces": len(networking_data["network_interfaces"])
    }

    return networking_data

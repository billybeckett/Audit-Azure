"""
Network Diagram Generator for Azure Infrastructure
Generates both Mermaid (markdown) and Graphviz (DOT) diagrams
"""

import json
from pathlib import Path


class NetworkDiagramGenerator:
    """Generates network topology diagrams from Azure audit data"""

    def __init__(self, audit_data, output_dir="docs/diagrams"):
        self.audit_data = audit_data
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.colors = {
            'vnet': '#e1f5ff',
            'subnet_web': '#e1f5ff',
            'subnet_app': '#fff4e1',
            'subnet_db': '#ffe1e1',
            'subnet_default': '#f0f0f0',
            'vm': '#90EE90',
            'lb': '#FFB6C1',
            'gateway': '#DDA0DD',
            'firewall': '#FF6347'
        }

    def generate_all_diagrams(self):
        """Generate all diagram formats"""
        print("\n🎨 Generating Network Diagrams...")

        # Generate diagrams for each subscription
        for sub_id, networking_data in self.audit_data.get("networking", {}).items():
            if networking_data.get("error"):
                continue

            # Find subscription name
            sub_name = "Unknown"
            for sub in self.audit_data.get("subscriptions", []):
                if sub.get("id") == sub_id:
                    sub_name = sub.get("name", "Unknown")
                    break

            # Generate Mermaid diagram
            mermaid = self.generate_mermaid_diagram(sub_name, sub_id, networking_data)
            mermaid_file = self.output_dir / f"network_{sub_name.replace(' ', '_')}.mermaid.md"
            with open(mermaid_file, 'w') as f:
                f.write(mermaid)
            print(f"   ✓ Mermaid diagram: {mermaid_file}")

            # Generate Graphviz DOT diagram
            dot = self.generate_graphviz_diagram(sub_name, sub_id, networking_data)
            dot_file = self.output_dir / f"network_{sub_name.replace(' ', '_')}.dot"
            with open(dot_file, 'w') as f:
                f.write(dot)
            print(f"   ✓ Graphviz DOT: {dot_file}")

        # Generate overall topology
        if len(self.audit_data.get("networking", {})) > 0:
            overall_mermaid = self.generate_overall_mermaid()
            overall_file = self.output_dir / "network_overview.mermaid.md"
            with open(overall_file, 'w') as f:
                f.write(overall_mermaid)
            print(f"   ✓ Overall diagram: {overall_file}")

    def generate_mermaid_diagram(self, sub_name, sub_id, networking_data):
        """Generate Mermaid diagram for a subscription's network"""
        lines = []
        lines.append(f"# Network Topology: {sub_name}")
        lines.append("")
        lines.append("```mermaid")
        lines.append("graph TB")
        lines.append("")

        vnets = networking_data.get("vnets", [])
        compute_data = self.audit_data.get("compute", {}).get(sub_id, {})
        vms = compute_data.get("virtual_machines", [])

        # Generate VNets and Subnets
        for vnet in vnets:
            vnet_name = vnet.get("name", "unknown")
            vnet_id = vnet_name.replace("-", "_").replace(".", "_")
            address_space = ", ".join(vnet.get("address_space", []))

            lines.append(f"    subgraph {vnet_id}[\"{vnet_name}<br/>{address_space}\"]")

            # Add subnets
            for subnet in vnet.get("subnets", []):
                subnet_name = subnet.get("name", "unknown")
                subnet_id = f"{vnet_id}_{subnet_name}".replace("-", "_").replace(".", "_")
                subnet_prefix = subnet.get("address_prefix", "")

                # Determine subnet color based on name
                color = self.colors['subnet_default']
                if 'web' in subnet_name.lower() or 'frontend' in subnet_name.lower():
                    color = self.colors['subnet_web']
                elif 'app' in subnet_name.lower() or 'application' in subnet_name.lower():
                    color = self.colors['subnet_app']
                elif 'db' in subnet_name.lower() or 'data' in subnet_name.lower() or 'sql' in subnet_name.lower():
                    color = self.colors['subnet_db']

                lines.append(f"        {subnet_id}[\"{subnet_name}<br/>{subnet_prefix}\"]")
                lines.append(f"        style {subnet_id} fill:{color}")

            lines.append("    end")
            lines.append("")

        # Add VMs and their connections
        for vm in vms:
            vm_name = vm.get("name", "unknown")
            vm_id = vm_name.replace("-", "_").replace(".", "_")
            private_ips = ", ".join(vm.get("private_ips", [])) or "No IP"
            vm_size = vm.get("size", "Unknown")
            power_state = vm.get("power_state", "Unknown")

            # Determine which subnet this VM is in
            nics = vm.get("network_profile", [])

            lines.append(f"    {vm_id}[\"{vm_name}<br/>{private_ips}<br/>{vm_size}\"]")
            lines.append(f"    style {vm_id} fill:{self.colors['vm']}")

            # Try to connect VM to subnet (simplified - would need NIC details)
            lines.append("")

        # Add Load Balancers
        load_balancers = networking_data.get("load_balancers", [])
        for lb in load_balancers:
            lb_name = lb.get("name", "unknown")
            lb_id = lb_name.replace("-", "_").replace(".", "_")
            lb_sku = lb.get("sku", "Unknown")

            lines.append(f"    {lb_id}[\"⚖️ {lb_name}<br/>{lb_sku}\"]")
            lines.append(f"    style {lb_id} fill:{self.colors['lb']}")
            lines.append("")

        # Add VNet Peering
        for vnet in vnets:
            vnet_id = vnet.get("name", "unknown").replace("-", "_").replace(".", "_")
            for peering in vnet.get("peerings", []):
                remote_vnet_name = peering.get("remote_vnet", "").split("/")[-1]
                if remote_vnet_name:
                    remote_id = remote_vnet_name.replace("-", "_").replace(".", "_")
                    peering_state = peering.get("peering_state", "Unknown")
                    lines.append(f"    {vnet_id} -.\"peering<br/>{peering_state}\".-> {remote_id}")

        lines.append("```")
        lines.append("")
        lines.append("## Legend")
        lines.append("")
        lines.append("- **Blue boxes**: Web/Frontend subnets")
        lines.append("- **Yellow boxes**: Application subnets")
        lines.append("- **Red boxes**: Database subnets")
        lines.append("- **Green boxes**: Virtual Machines")
        lines.append("- **Pink boxes**: Load Balancers")
        lines.append("- **Dotted lines**: VNet Peering")
        lines.append("")

        return "\n".join(lines)

    def generate_graphviz_diagram(self, sub_name, sub_id, networking_data):
        """Generate Graphviz DOT diagram"""
        lines = []
        lines.append(f"// Azure Network Topology: {sub_name}")
        lines.append("digraph AzureNetwork {")
        lines.append("    rankdir=TB;")
        lines.append("    node [shape=box, style=filled];")
        lines.append("    ")

        vnets = networking_data.get("vnets", [])

        # VNets as clusters
        for i, vnet in enumerate(vnets):
            vnet_name = vnet.get("name", "unknown")
            vnet_id = vnet_name.replace("-", "_").replace(".", "_")
            address_space = "\\n".join(vnet.get("address_space", []))

            lines.append(f"    subgraph cluster_{i} {{")
            lines.append(f"        label=\"{vnet_name}\\n{address_space}\";")
            lines.append("        style=filled;")
            lines.append("        color=lightblue;")
            lines.append("")

            # Subnets
            for subnet in vnet.get("subnets", []):
                subnet_name = subnet.get("name", "unknown")
                subnet_id = f"{vnet_id}_{subnet_name}".replace("-", "_").replace(".", "_")
                subnet_prefix = subnet.get("address_prefix", "")

                # Determine color
                color = "lightgray"
                if 'web' in subnet_name.lower():
                    color = "lightblue"
                elif 'app' in subnet_name.lower():
                    color = "lightyellow"
                elif 'db' in subnet_name.lower():
                    color = "lightpink"

                lines.append(f"        {subnet_id} [label=\"{subnet_name}\\n{subnet_prefix}\", fillcolor={color}];")

            lines.append("    }")
            lines.append("")

        # VMs
        compute_data = self.audit_data.get("compute", {}).get(sub_id, {})
        vms = compute_data.get("virtual_machines", [])

        for vm in vms:
            vm_name = vm.get("name", "unknown")
            vm_id = vm_name.replace("-", "_").replace(".", "_")
            private_ips = "\\n".join(vm.get("private_ips", [])) or "No IP"
            vm_size = vm.get("size", "Unknown")

            lines.append(f"    {vm_id} [label=\"VM: {vm_name}\\n{private_ips}\\n{vm_size}\", fillcolor=lightgreen];")

        lines.append("")

        # Load Balancers
        load_balancers = networking_data.get("load_balancers", [])
        for lb in load_balancers:
            lb_name = lb.get("name", "unknown")
            lb_id = lb_name.replace("-", "_").replace(".", "_")
            lb_sku = lb.get("sku", "Unknown")

            lines.append(f"    {lb_id} [label=\"LB: {lb_name}\\n{lb_sku}\", shape=hexagon, fillcolor=pink];")

        lines.append("")

        # VNet Peering connections
        for vnet in vnets:
            vnet_id = vnet.get("name", "unknown").replace("-", "_").replace(".", "_")
            for peering in vnet.get("peerings", []):
                remote_vnet_name = peering.get("remote_vnet", "").split("/")[-1]
                if remote_vnet_name:
                    remote_id = remote_vnet_name.replace("-", "_").replace(".", "_")
                    peering_state = peering.get("peering_state", "Unknown")
                    lines.append(f"    {vnet_id} -> {remote_id} [label=\"{peering_state}\", style=dashed];")

        lines.append("}")

        return "\n".join(lines)

    def generate_overall_mermaid(self):
        """Generate an overall network overview across all subscriptions"""
        lines = []
        lines.append("# Azure Network Overview")
        lines.append("")
        lines.append("```mermaid")
        lines.append("graph TB")
        lines.append("")

        # Count resources across all subscriptions
        total_vnets = 0
        total_subnets = 0
        total_vms = 0

        for sub_id, networking_data in self.audit_data.get("networking", {}).items():
            if networking_data.get("error"):
                continue

            # Find subscription name
            sub_name = "Unknown"
            for sub in self.audit_data.get("subscriptions", []):
                if sub.get("id") == sub_id:
                    sub_name = sub.get("name", "Unknown")
                    break

            sub_id_clean = sub_name.replace(" ", "_").replace("-", "_")

            vnets = networking_data.get("vnets", [])
            total_vnets += len(vnets)

            compute_data = self.audit_data.get("compute", {}).get(sub_id, {})
            vms = compute_data.get("virtual_machines", [])
            total_vms += len(vms)

            lines.append(f"    subgraph {sub_id_clean}[\"{sub_name}\"]")

            for vnet in vnets[:5]:  # Limit to 5 VNets per subscription for clarity
                vnet_name = vnet.get("name", "unknown")
                vnet_id = f"{sub_id_clean}_{vnet_name}".replace("-", "_").replace(".", "_")
                subnet_count = len(vnet.get("subnets", []))
                total_subnets += subnet_count

                lines.append(f"        {vnet_id}[\"{vnet_name}<br/>{subnet_count} subnets\"]")

            if len(vnets) > 5:
                lines.append(f"        {sub_id_clean}_more[\"...and {len(vnets) - 5} more VNets\"]")

            lines.append("    end")
            lines.append("")

        lines.append("```")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total VNets**: {total_vnets}")
        lines.append(f"- **Total Subnets**: {total_subnets}")
        lines.append(f"- **Total VMs**: {total_vms}")
        lines.append("")

        return "\n".join(lines)

    def get_mermaid_for_markdown(self, sub_id):
        """Get Mermaid diagram code for embedding in markdown reports"""
        networking_data = self.audit_data.get("networking", {}).get(sub_id, {})
        if networking_data.get("error") or not networking_data.get("vnets"):
            return ""

        # Find subscription name
        sub_name = "Unknown"
        for sub in self.audit_data.get("subscriptions", []):
            if sub.get("id") == sub_id:
                sub_name = sub.get("name", "Unknown")
                break

        return self.generate_mermaid_diagram(sub_name, sub_id, networking_data)

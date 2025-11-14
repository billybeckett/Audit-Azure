#!/usr/bin/env python3
"""
Azure Resource Discovery and Documentation Tool
This script discovers all resources in an Azure account and generates comprehensive documentation.
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add the discovery directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'discovery'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from discovery.subscription_discovery import discover_subscriptions
from discovery.networking_discovery import discover_networking
from discovery.compute_discovery import discover_compute
from discovery.storage_discovery import discover_storage
from discovery.database_discovery import discover_databases
from discovery.dns_discovery import discover_dns
from discovery.security_discovery import discover_security
from reports.markdown_generator import generate_all_reports
from utils.logger import init_logger, get_logger


class AzureAuditor:
    """Main class for Azure resource discovery and audit"""

    def __init__(self, output_dir="docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.data_dir = self.output_dir / "data"
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.audit_data = {
            "timestamp": self.timestamp,
            "subscriptions": [],
            "networking": {},
            "compute": {},
            "storage": {},
            "databases": {},
            "dns": {},
            "security": {},
            "summary": {}
        }

    def save_raw_data(self):
        """Save raw discovery data to JSON"""
        output_file = self.data_dir / f"azure_audit_{self.timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(self.audit_data, f, indent=2, default=str)
        print(f"✓ Raw data saved to: {output_file}")
        return output_file

    def run_discovery(self):
        """Run complete Azure discovery process"""
        logger = get_logger()
        logger.log_section("Azure Resource Discovery and Audit")

        print("=" * 80)
        print("Azure Resource Discovery and Audit")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Print log file information
        log_file = logger.log_file
        print()
        print("📝 LOGGING:")
        print(f"   Log file: {log_file}")
        print(f"   To watch in real-time, open a new terminal and run:")
        print(f"   \033[1;36mtail -f {log_file}\033[0m")
        print()

        # Discover subscriptions
        print("📋 Discovering Azure Subscriptions...")
        try:
            self.audit_data["subscriptions"] = discover_subscriptions()
            print(f"   Found {len(self.audit_data['subscriptions'])} subscription(s)")
        except Exception as e:
            print(f"   ⚠ Error: {e}")
            self.audit_data["subscriptions"] = []

        if not self.audit_data["subscriptions"]:
            print("\n❌ No subscriptions found or authentication failed.")
            print("   Please run 'az login' first.")
            return False

        # Process each subscription
        for sub in self.audit_data["subscriptions"]:
            sub_id = sub.get("id", "unknown")
            sub_name = sub.get("name", "unknown")
            print(f"\n📦 Processing subscription: {sub_name}")
            print(f"   Subscription ID: {sub_id}")

            # Networking
            print("\n   🌐 Discovering Networking Resources...")
            try:
                self.audit_data["networking"][sub_id] = discover_networking(sub_id)
                counts = self.audit_data["networking"][sub_id].get("summary", {})
                print(f"      - VNets: {counts.get('vnets', 0)}")
                print(f"      - Subnets: {counts.get('subnets', 0)}")
                print(f"      - NSGs: {counts.get('nsgs', 0)}")
                print(f"      - Public IPs: {counts.get('public_ips', 0)}")
                print(f"      - Load Balancers: {counts.get('load_balancers', 0)}")
            except Exception as e:
                print(f"      ⚠ Error: {e}")
                self.audit_data["networking"][sub_id] = {"error": str(e)}

            # Compute
            print("\n   💻 Discovering Compute Resources...")
            try:
                self.audit_data["compute"][sub_id] = discover_compute(sub_id)
                counts = self.audit_data["compute"][sub_id].get("summary", {})
                print(f"      - Virtual Machines: {counts.get('vms', 0)}")
                print(f"      - VM Scale Sets: {counts.get('vmss', 0)}")
                print(f"      - App Services: {counts.get('app_services', 0)}")
                print(f"      - Functions: {counts.get('functions', 0)}")
                print(f"      - Containers: {counts.get('containers', 0)}")
            except Exception as e:
                print(f"      ⚠ Error: {e}")
                self.audit_data["compute"][sub_id] = {"error": str(e)}

            # Storage
            print("\n   💾 Discovering Storage Resources...")
            try:
                self.audit_data["storage"][sub_id] = discover_storage(sub_id)
                counts = self.audit_data["storage"][sub_id].get("summary", {})
                print(f"      - Storage Accounts: {counts.get('storage_accounts', 0)}")
                print(f"      - Disks: {counts.get('disks', 0)}")
            except Exception as e:
                print(f"      ⚠ Error: {e}")
                self.audit_data["storage"][sub_id] = {"error": str(e)}

            # Databases
            print("\n   🗄️  Discovering Database Resources...")
            try:
                self.audit_data["databases"][sub_id] = discover_databases(sub_id)
                counts = self.audit_data["databases"][sub_id].get("summary", {})
                print(f"      - SQL Servers: {counts.get('sql_servers', 0)}")
                print(f"      - SQL Databases: {counts.get('sql_databases', 0)}")
                print(f"      - MySQL: {counts.get('mysql', 0)}")
                print(f"      - PostgreSQL: {counts.get('postgresql', 0)}")
                print(f"      - CosmosDB: {counts.get('cosmosdb', 0)}")
            except Exception as e:
                print(f"      ⚠ Error: {e}")
                self.audit_data["databases"][sub_id] = {"error": str(e)}

            # DNS
            print("\n   🔍 Discovering DNS Resources...")
            try:
                self.audit_data["dns"][sub_id] = discover_dns(sub_id)
                counts = self.audit_data["dns"][sub_id].get("summary", {})
                print(f"      - DNS Zones: {counts.get('dns_zones', 0)}")
                print(f"      - Private DNS Zones: {counts.get('private_dns_zones', 0)}")
            except Exception as e:
                print(f"      ⚠ Error: {e}")
                self.audit_data["dns"][sub_id] = {"error": str(e)}

            # Security
            print("\n   🔒 Discovering Security Resources...")
            try:
                self.audit_data["security"][sub_id] = discover_security(sub_id)
                counts = self.audit_data["security"][sub_id].get("summary", {})
                print(f"      - Key Vaults: {counts.get('key_vaults', 0)}")
                print(f"      - Security Center Alerts: {counts.get('security_alerts', 0)}")
            except Exception as e:
                print(f"      ⚠ Error: {e}")
                self.audit_data["security"][sub_id] = {"error": str(e)}

        # Save raw data
        print("\n" + "=" * 80)
        print("💾 Saving Discovery Data...")
        self.save_raw_data()

        # Generate reports
        print("\n" + "=" * 80)
        print("📝 Generating Markdown Documentation...")
        try:
            generate_all_reports(self.audit_data, self.output_dir)
            print("✓ Documentation generated successfully!")
        except Exception as e:
            print(f"⚠ Error generating reports: {e}")

        print("\n" + "=" * 80)
        print(f"✅ Azure Audit Complete!")
        print(f"📁 Documentation available in: {self.output_dir.absolute()}")

        # Print logging summary
        logger = get_logger()
        stats = logger.get_stats()
        print()
        print("📊 Logging Summary:")
        print(f"   Commands executed: {stats['commands_executed']}")
        print(f"   Total time: {stats['total_time']:.2f}s")
        print(f"   Log file: {stats['log_file']}")
        logger.print_summary()

        print("=" * 80)

        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Azure Infrastructure Discovery and Audit Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output (shows all Azure CLI commands and responses)'
    )
    parser.add_argument(
        '--log-dir',
        default='logs',
        help='Directory for log files (default: logs/)'
    )
    parser.add_argument(
        '--output-dir',
        default='docs',
        help='Directory for output documentation (default: docs/)'
    )

    args = parser.parse_args()

    # Initialize logger
    init_logger(log_dir=args.log_dir, verbose=args.verbose)

    # Run audit
    auditor = AzureAuditor(output_dir=args.output_dir)
    success = auditor.run_discovery()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

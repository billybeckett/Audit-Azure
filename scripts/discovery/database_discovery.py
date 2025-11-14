"""
Azure Database Discovery Module
Discovers SQL Databases, MySQL, PostgreSQL, CosmosDB, Redis Cache, etc.
"""

import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from logger import run_az_command


def discover_databases(subscription_id):
    """
    Discover all database resources in a subscription

    Args:
        subscription_id: Azure subscription ID

    Returns:
        dict: Dictionary containing all database resources
    """
    database_data = {
        "sql_servers": [],
        "sql_databases": [],
        "mysql_servers": [],
        "postgresql_servers": [],
        "cosmosdb_accounts": [],
        "redis_caches": [],
        "mariadb_servers": [],
        "summary": {}
    }

    # SQL Servers
    sql_servers = run_az_command(
        f"az sql server list --subscription {subscription_id} --output json"
    )
    for server in sql_servers:
        server_info = {
            "name": server.get("name"),
            "id": server.get("id"),
            "location": server.get("location"),
            "resource_group": server.get("resourceGroup"),
            "fully_qualified_domain_name": server.get("fullyQualifiedDomainName"),
            "version": server.get("version"),
            "administrator_login": server.get("administratorLogin"),
            "state": server.get("state"),
            "public_network_access": server.get("publicNetworkAccess"),
            "minimal_tls_version": server.get("minimalTlsVersion"),
            "tags": server.get("tags", {})
        }

        # Get databases for this server
        databases = run_az_command(
            f"az sql db list --subscription {subscription_id} "
            f"--resource-group {server.get('resourceGroup')} "
            f"--server {server.get('name')} --output json"
        )
        server_info["databases"] = []
        for db in databases:
            if db.get("name") != "master":  # Skip master database
                db_info = {
                    "name": db.get("name"),
                    "id": db.get("id"),
                    "location": db.get("location"),
                    "sku": {
                        "name": db.get("sku", {}).get("name"),
                        "tier": db.get("sku", {}).get("tier"),
                        "capacity": db.get("sku", {}).get("capacity")
                    },
                    "kind": db.get("kind"),
                    "max_size_bytes": db.get("maxSizeBytes"),
                    "status": db.get("status"),
                    "collation": db.get("collation"),
                    "creation_date": db.get("creationDate"),
                    "zone_redundant": db.get("zoneRedundant"),
                    "read_scale": db.get("readScale"),
                    "tags": db.get("tags", {})
                }
                server_info["databases"].append(db_info)
                database_data["sql_databases"].append(db_info)

        # Get firewall rules
        firewall_rules = run_az_command(
            f"az sql server firewall-rule list --subscription {subscription_id} "
            f"--resource-group {server.get('resourceGroup')} "
            f"--server {server.get('name')} --output json"
        )
        server_info["firewall_rules"] = [
            {
                "name": rule.get("name"),
                "start_ip": rule.get("startIpAddress"),
                "end_ip": rule.get("endIpAddress")
            }
            for rule in firewall_rules
        ]

        database_data["sql_servers"].append(server_info)

    # MySQL Servers
    mysql_servers = run_az_command(
        f"az mysql server list --subscription {subscription_id} --output json"
    )
    for server in mysql_servers:
        server_info = {
            "name": server.get("name"),
            "id": server.get("id"),
            "location": server.get("location"),
            "resource_group": server.get("resourceGroup"),
            "fully_qualified_domain_name": server.get("fullyQualifiedDomainName"),
            "version": server.get("version"),
            "administrator_login": server.get("administratorLogin"),
            "user_visible_state": server.get("userVisibleState"),
            "sku": {
                "name": server.get("sku", {}).get("name"),
                "tier": server.get("sku", {}).get("tier"),
                "capacity": server.get("sku", {}).get("capacity"),
                "family": server.get("sku", {}).get("family")
            },
            "storage_mb": server.get("storageProfile", {}).get("storageMb"),
            "backup_retention_days": server.get("storageProfile", {}).get("backupRetentionDays"),
            "geo_redundant_backup": server.get("storageProfile", {}).get("geoRedundantBackup"),
            "ssl_enforcement": server.get("sslEnforcement"),
            "minimal_tls_version": server.get("minimalTlsVersion"),
            "public_network_access": server.get("publicNetworkAccess"),
            "tags": server.get("tags", {})
        }

        # Get databases
        databases = run_az_command(
            f"az mysql db list --subscription {subscription_id} "
            f"--resource-group {server.get('resourceGroup')} "
            f"--server-name {server.get('name')} --output json"
        )
        server_info["databases"] = [db.get("name") for db in databases]

        # Get firewall rules
        firewall_rules = run_az_command(
            f"az mysql server firewall-rule list --subscription {subscription_id} "
            f"--resource-group {server.get('resourceGroup')} "
            f"--server-name {server.get('name')} --output json"
        )
        server_info["firewall_rules"] = [
            {
                "name": rule.get("name"),
                "start_ip": rule.get("startIpAddress"),
                "end_ip": rule.get("endIpAddress")
            }
            for rule in firewall_rules
        ]

        database_data["mysql_servers"].append(server_info)

    # PostgreSQL Servers
    postgresql_servers = run_az_command(
        f"az postgres server list --subscription {subscription_id} --output json"
    )
    for server in postgresql_servers:
        server_info = {
            "name": server.get("name"),
            "id": server.get("id"),
            "location": server.get("location"),
            "resource_group": server.get("resourceGroup"),
            "fully_qualified_domain_name": server.get("fullyQualifiedDomainName"),
            "version": server.get("version"),
            "administrator_login": server.get("administratorLogin"),
            "user_visible_state": server.get("userVisibleState"),
            "sku": {
                "name": server.get("sku", {}).get("name"),
                "tier": server.get("sku", {}).get("tier"),
                "capacity": server.get("sku", {}).get("capacity"),
                "family": server.get("sku", {}).get("family")
            },
            "storage_mb": server.get("storageProfile", {}).get("storageMb"),
            "backup_retention_days": server.get("storageProfile", {}).get("backupRetentionDays"),
            "geo_redundant_backup": server.get("storageProfile", {}).get("geoRedundantBackup"),
            "ssl_enforcement": server.get("sslEnforcement"),
            "minimal_tls_version": server.get("minimalTlsVersion"),
            "public_network_access": server.get("publicNetworkAccess"),
            "tags": server.get("tags", {})
        }

        # Get databases
        databases = run_az_command(
            f"az postgres db list --subscription {subscription_id} "
            f"--resource-group {server.get('resourceGroup')} "
            f"--server-name {server.get('name')} --output json"
        )
        server_info["databases"] = [db.get("name") for db in databases]

        # Get firewall rules
        firewall_rules = run_az_command(
            f"az postgres server firewall-rule list --subscription {subscription_id} "
            f"--resource-group {server.get('resourceGroup')} "
            f"--server-name {server.get('name')} --output json"
        )
        server_info["firewall_rules"] = [
            {
                "name": rule.get("name"),
                "start_ip": rule.get("startIpAddress"),
                "end_ip": rule.get("endIpAddress")
            }
            for rule in firewall_rules
        ]

        database_data["postgresql_servers"].append(server_info)

    # CosmosDB Accounts
    cosmosdb_accounts = run_az_command(
        f"az cosmosdb list --subscription {subscription_id} --output json"
    )
    for account in cosmosdb_accounts:
        account_info = {
            "name": account.get("name"),
            "id": account.get("id"),
            "location": account.get("location"),
            "resource_group": account.get("resourceGroup"),
            "kind": account.get("kind"),
            "document_endpoint": account.get("documentEndpoint"),
            "provisioning_state": account.get("provisioningState"),
            "consistency_policy": {
                "default_consistency_level": account.get("consistencyPolicy", {}).get("defaultConsistencyLevel"),
                "max_staleness_prefix": account.get("consistencyPolicy", {}).get("maxStalenessPrefix"),
                "max_interval_seconds": account.get("consistencyPolicy", {}).get("maxIntervalInSeconds")
            },
            "locations": [
                {
                    "location": loc.get("locationName"),
                    "failover_priority": loc.get("failoverPriority"),
                    "is_zone_redundant": loc.get("isZoneRedundant")
                }
                for loc in account.get("locations", [])
            ],
            "enable_multiple_write_locations": account.get("enableMultipleWriteLocations"),
            "enable_automatic_failover": account.get("enableAutomaticFailover"),
            "capabilities": [
                cap.get("name") for cap in account.get("capabilities", [])
            ],
            "public_network_access": account.get("publicNetworkAccess"),
            "tags": account.get("tags", {})
        }

        # Get databases (SQL API)
        try:
            databases = run_az_command(
                f"az cosmosdb sql database list --subscription {subscription_id} "
                f"--resource-group {account.get('resourceGroup')} "
                f"--account-name {account.get('name')} --output json"
            )
            account_info["sql_databases"] = [db.get("name") for db in databases]
        except:
            account_info["sql_databases"] = []

        database_data["cosmosdb_accounts"].append(account_info)

    # Redis Caches
    redis_caches = run_az_command(
        f"az redis list --subscription {subscription_id} --output json"
    )
    for redis in redis_caches:
        redis_info = {
            "name": redis.get("name"),
            "id": redis.get("id"),
            "location": redis.get("location"),
            "resource_group": redis.get("resourceGroup"),
            "hostname": redis.get("hostName"),
            "port": redis.get("port"),
            "ssl_port": redis.get("sslPort"),
            "provisioning_state": redis.get("provisioningState"),
            "redis_version": redis.get("redisVersion"),
            "sku": {
                "name": redis.get("sku", {}).get("name"),
                "family": redis.get("sku", {}).get("family"),
                "capacity": redis.get("sku", {}).get("capacity")
            },
            "enable_non_ssl_port": redis.get("enableNonSslPort"),
            "minimum_tls_version": redis.get("minimumTlsVersion"),
            "public_network_access": redis.get("publicNetworkAccess"),
            "tags": redis.get("tags", {})
        }
        database_data["redis_caches"].append(redis_info)

    # MariaDB Servers
    mariadb_servers = run_az_command(
        f"az mariadb server list --subscription {subscription_id} --output json"
    )
    for server in mariadb_servers:
        server_info = {
            "name": server.get("name"),
            "id": server.get("id"),
            "location": server.get("location"),
            "resource_group": server.get("resourceGroup"),
            "fully_qualified_domain_name": server.get("fullyQualifiedDomainName"),
            "version": server.get("version"),
            "administrator_login": server.get("administratorLogin"),
            "user_visible_state": server.get("userVisibleState"),
            "sku": {
                "name": server.get("sku", {}).get("name"),
                "tier": server.get("sku", {}).get("tier"),
                "capacity": server.get("sku", {}).get("capacity"),
                "family": server.get("sku", {}).get("family")
            },
            "storage_mb": server.get("storageProfile", {}).get("storageMb"),
            "backup_retention_days": server.get("storageProfile", {}).get("backupRetentionDays"),
            "geo_redundant_backup": server.get("storageProfile", {}).get("geoRedundantBackup"),
            "ssl_enforcement": server.get("sslEnforcement"),
            "public_network_access": server.get("publicNetworkAccess"),
            "tags": server.get("tags", {})
        }
        database_data["mariadb_servers"].append(server_info)

    # Calculate summary
    database_data["summary"] = {
        "sql_servers": len(database_data["sql_servers"]),
        "sql_databases": len(database_data["sql_databases"]),
        "mysql": len(database_data["mysql_servers"]),
        "postgresql": len(database_data["postgresql_servers"]),
        "cosmosdb": len(database_data["cosmosdb_accounts"]),
        "redis": len(database_data["redis_caches"]),
        "mariadb": len(database_data["mariadb_servers"])
    }

    return database_data

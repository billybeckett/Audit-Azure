"""
Azure Compute Discovery Module
Discovers VMs, VM Scale Sets, App Services, Functions, Container Instances, AKS, etc.
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


def discover_compute(subscription_id):
    """
    Discover all compute resources in a subscription

    Args:
        subscription_id: Azure subscription ID

    Returns:
        dict: Dictionary containing all compute resources
    """
    compute_data = {
        "virtual_machines": [],
        "vm_scale_sets": [],
        "app_services": [],
        "app_service_plans": [],
        "function_apps": [],
        "container_instances": [],
        "kubernetes_services": [],
        "batch_accounts": [],
        "availability_sets": [],
        "summary": {}
    }

    # Virtual Machines
    vms = run_az_command(
        f"az vm list --subscription {subscription_id} --output json --show-details"
    )
    for vm in vms:
        vm_info = {
            "name": vm.get("name"),
            "id": vm.get("id"),
            "location": vm.get("location"),
            "resource_group": vm.get("resourceGroup"),
            "size": vm.get("hardwareProfile", {}).get("vmSize"),
            "os_type": vm.get("storageProfile", {}).get("osDisk", {}).get("osType"),
            "os_disk_size": vm.get("storageProfile", {}).get("osDisk", {}).get("diskSizeGb"),
            "image_reference": {
                "publisher": vm.get("storageProfile", {}).get("imageReference", {}).get("publisher"),
                "offer": vm.get("storageProfile", {}).get("imageReference", {}).get("offer"),
                "sku": vm.get("storageProfile", {}).get("imageReference", {}).get("sku"),
                "version": vm.get("storageProfile", {}).get("imageReference", {}).get("version")
            },
            "power_state": vm.get("powerState"),
            "provisioning_state": vm.get("provisioningState"),
            "private_ips": vm.get("privateIps"),
            "public_ips": vm.get("publicIps"),
            "fqdns": vm.get("fqdns"),
            "network_profile": [
                nic.get("id") for nic in vm.get("networkProfile", {}).get("networkInterfaces", [])
            ],
            "availability_set": vm.get("availabilitySet", {}).get("id"),
            "zones": vm.get("zones", []),
            "tags": vm.get("tags", {})
        }

        # Get VM extensions
        try:
            extensions = run_az_command(
                f"az vm extension list --subscription {subscription_id} "
                f"--resource-group {vm.get('resourceGroup')} "
                f"--vm-name {vm.get('name')} --output json"
            )
            vm_info["extensions"] = [
                {
                    "name": ext.get("name"),
                    "publisher": ext.get("publisher"),
                    "type": ext.get("typePropertiesType"),
                    "version": ext.get("typeHandlerVersion"),
                    "provisioning_state": ext.get("provisioningState")
                }
                for ext in extensions
            ]
        except:
            vm_info["extensions"] = []

        # Get diagnostics settings
        vm_info["boot_diagnostics_enabled"] = vm.get("diagnosticsProfile", {}).get(
            "bootDiagnostics", {}
        ).get("enabled", False)

        compute_data["virtual_machines"].append(vm_info)

    # VM Scale Sets
    vmss = run_az_command(
        f"az vmss list --subscription {subscription_id} --output json"
    )
    for vmss_item in vmss:
        vmss_info = {
            "name": vmss_item.get("name"),
            "id": vmss_item.get("id"),
            "location": vmss_item.get("location"),
            "resource_group": vmss_item.get("resourceGroup"),
            "sku": {
                "name": vmss_item.get("sku", {}).get("name"),
                "tier": vmss_item.get("sku", {}).get("tier"),
                "capacity": vmss_item.get("sku", {}).get("capacity")
            },
            "upgrade_policy": vmss_item.get("upgradePolicy", {}).get("mode"),
            "os_type": vmss_item.get("virtualMachineProfile", {}).get("storageProfile", {}).get(
                "osDisk", {}
            ).get("osType"),
            "overprovision": vmss_item.get("overprovision"),
            "single_placement_group": vmss_item.get("singlePlacementGroup"),
            "provisioning_state": vmss_item.get("provisioningState"),
            "zones": vmss_item.get("zones", []),
            "tags": vmss_item.get("tags", {})
        }

        # Get instance count
        try:
            instances = run_az_command(
                f"az vmss list-instances --subscription {subscription_id} "
                f"--resource-group {vmss_item.get('resourceGroup')} "
                f"--name {vmss_item.get('name')} --output json"
            )
            vmss_info["instance_count"] = len(instances)
        except:
            vmss_info["instance_count"] = 0

        compute_data["vm_scale_sets"].append(vmss_info)

    # App Service Plans
    app_plans = run_az_command(
        f"az appservice plan list --subscription {subscription_id} --output json"
    )
    for plan in app_plans:
        plan_info = {
            "name": plan.get("name"),
            "id": plan.get("id"),
            "location": plan.get("location"),
            "resource_group": plan.get("resourceGroup"),
            "sku": {
                "name": plan.get("sku", {}).get("name"),
                "tier": plan.get("sku", {}).get("tier"),
                "size": plan.get("sku", {}).get("size"),
                "family": plan.get("sku", {}).get("family"),
                "capacity": plan.get("sku", {}).get("capacity")
            },
            "kind": plan.get("kind"),
            "status": plan.get("status"),
            "number_of_sites": plan.get("numberOfSites"),
            "maximum_number_of_workers": plan.get("maximumNumberOfWorkers"),
            "reserved": plan.get("reserved"),  # Linux = True
            "is_spot": plan.get("isSpot"),
            "provisioning_state": plan.get("provisioningState"),
            "tags": plan.get("tags", {})
        }
        compute_data["app_service_plans"].append(plan_info)

    # App Services / Web Apps
    webapps = run_az_command(
        f"az webapp list --subscription {subscription_id} --output json"
    )
    for webapp in webapps:
        webapp_info = {
            "name": webapp.get("name"),
            "id": webapp.get("id"),
            "location": webapp.get("location"),
            "resource_group": webapp.get("resourceGroup"),
            "default_hostname": webapp.get("defaultHostName"),
            "enabled_hostnames": webapp.get("enabledHostNames", []),
            "state": webapp.get("state"),
            "app_service_plan": webapp.get("serverFarmId"),
            "kind": webapp.get("kind"),
            "repository_site_name": webapp.get("repositorySiteName"),
            "usage_state": webapp.get("usageState"),
            "https_only": webapp.get("httpsOnly"),
            "client_cert_enabled": webapp.get("clientCertEnabled"),
            "reserved": webapp.get("reserved"),  # Linux = True
            "availability_state": webapp.get("availabilityState"),
            "tags": webapp.get("tags", {})
        }

        # Get app settings (configuration)
        try:
            config = run_az_command(
                f"az webapp config show --subscription {subscription_id} "
                f"--resource-group {webapp.get('resourceGroup')} "
                f"--name {webapp.get('name')} --output json"
            )
            if isinstance(config, dict):
                webapp_info["runtime"] = {
                    "linux_fx_version": config.get("linuxFxVersion"),
                    "windows_fx_version": config.get("windowsFxVersion"),
                    "net_framework_version": config.get("netFrameworkVersion"),
                    "php_version": config.get("phpVersion"),
                    "python_version": config.get("pythonVersion"),
                    "node_version": config.get("nodeVersion"),
                    "java_version": config.get("javaVersion")
                }
                webapp_info["always_on"] = config.get("alwaysOn")
                webapp_info["http20_enabled"] = config.get("http20Enabled")
        except:
            webapp_info["runtime"] = {}

        compute_data["app_services"].append(webapp_info)

    # Function Apps
    function_apps = run_az_command(
        f"az functionapp list --subscription {subscription_id} --output json"
    )
    for func in function_apps:
        func_info = {
            "name": func.get("name"),
            "id": func.get("id"),
            "location": func.get("location"),
            "resource_group": func.get("resourceGroup"),
            "default_hostname": func.get("defaultHostName"),
            "state": func.get("state"),
            "app_service_plan": func.get("serverFarmId"),
            "kind": func.get("kind"),
            "runtime": func.get("kind"),
            "https_only": func.get("httpsOnly"),
            "reserved": func.get("reserved"),
            "tags": func.get("tags", {})
        }
        compute_data["function_apps"].append(func_info)

    # Container Instances
    container_groups = run_az_command(
        f"az container list --subscription {subscription_id} --output json"
    )
    for cg in container_groups:
        cg_info = {
            "name": cg.get("name"),
            "id": cg.get("id"),
            "location": cg.get("location"),
            "resource_group": cg.get("resourceGroup"),
            "os_type": cg.get("osType"),
            "provisioning_state": cg.get("provisioningState"),
            "restart_policy": cg.get("restartPolicy"),
            "ip_address": cg.get("ipAddress", {}).get("ip"),
            "fqdn": cg.get("ipAddress", {}).get("fqdn"),
            "ports": [
                port.get("port") for port in cg.get("ipAddress", {}).get("ports", [])
            ],
            "containers": [
                {
                    "name": c.get("name"),
                    "image": c.get("image"),
                    "cpu": c.get("resources", {}).get("requests", {}).get("cpu"),
                    "memory": c.get("resources", {}).get("requests", {}).get("memoryInGb"),
                    "ports": [
                        p.get("port") for p in c.get("ports", [])
                    ]
                }
                for c in cg.get("containers", [])
            ],
            "tags": cg.get("tags", {})
        }
        compute_data["container_instances"].append(cg_info)

    # Azure Kubernetes Service (AKS)
    aks_clusters = run_az_command(
        f"az aks list --subscription {subscription_id} --output json"
    )
    for aks in aks_clusters:
        aks_info = {
            "name": aks.get("name"),
            "id": aks.get("id"),
            "location": aks.get("location"),
            "resource_group": aks.get("resourceGroup"),
            "kubernetes_version": aks.get("kubernetesVersion"),
            "dns_prefix": aks.get("dnsPrefix"),
            "fqdn": aks.get("fqdn"),
            "provisioning_state": aks.get("provisioningState"),
            "power_state": aks.get("powerState", {}).get("code"),
            "node_resource_group": aks.get("nodeResourceGroup"),
            "enable_rbac": aks.get("enableRbac"),
            "network_profile": {
                "network_plugin": aks.get("networkProfile", {}).get("networkPlugin"),
                "network_policy": aks.get("networkProfile", {}).get("networkPolicy"),
                "service_cidr": aks.get("networkProfile", {}).get("serviceCidr"),
                "dns_service_ip": aks.get("networkProfile", {}).get("dnsServiceIp"),
                "load_balancer_sku": aks.get("networkProfile", {}).get("loadBalancerSku")
            },
            "agent_pools": [
                {
                    "name": pool.get("name"),
                    "count": pool.get("count"),
                    "vm_size": pool.get("vmSize"),
                    "os_type": pool.get("osType"),
                    "mode": pool.get("mode"),
                    "orchestrator_version": pool.get("orchestratorVersion"),
                    "max_pods": pool.get("maxPods"),
                    "availability_zones": pool.get("availabilityZones", [])
                }
                for pool in aks.get("agentPoolProfiles", [])
            ],
            "addon_profiles": aks.get("addonProfiles", {}),
            "tags": aks.get("tags", {})
        }
        compute_data["kubernetes_services"].append(aks_info)

    # Batch Accounts
    batch_accounts = run_az_command(
        f"az batch account list --subscription {subscription_id} --output json"
    )
    for batch in batch_accounts:
        batch_info = {
            "name": batch.get("name"),
            "id": batch.get("id"),
            "location": batch.get("location"),
            "resource_group": batch.get("resourceGroup"),
            "account_endpoint": batch.get("accountEndpoint"),
            "provisioning_state": batch.get("provisioningState"),
            "dedicated_core_quota": batch.get("dedicatedCoreQuota"),
            "low_priority_core_quota": batch.get("lowPriorityCoreQuota"),
            "pool_quota": batch.get("poolQuota"),
            "active_job_and_job_schedule_quota": batch.get("activeJobAndJobScheduleQuota"),
            "tags": batch.get("tags", {})
        }
        compute_data["batch_accounts"].append(batch_info)

    # Availability Sets
    avsets = run_az_command(
        f"az vm availability-set list --subscription {subscription_id} --output json"
    )
    for avset in avsets:
        avset_info = {
            "name": avset.get("name"),
            "id": avset.get("id"),
            "location": avset.get("location"),
            "resource_group": avset.get("resourceGroup"),
            "platform_fault_domain_count": avset.get("platformFaultDomainCount"),
            "platform_update_domain_count": avset.get("platformUpdateDomainCount"),
            "sku": avset.get("sku", {}).get("name"),
            "virtual_machines": [
                vm.get("id") for vm in avset.get("virtualMachines", [])
            ],
            "tags": avset.get("tags", {})
        }
        compute_data["availability_sets"].append(avset_info)

    # Calculate summary
    compute_data["summary"] = {
        "vms": len(compute_data["virtual_machines"]),
        "vmss": len(compute_data["vm_scale_sets"]),
        "app_services": len(compute_data["app_services"]),
        "app_service_plans": len(compute_data["app_service_plans"]),
        "functions": len(compute_data["function_apps"]),
        "containers": len(compute_data["container_instances"]),
        "aks_clusters": len(compute_data["kubernetes_services"]),
        "batch_accounts": len(compute_data["batch_accounts"]),
        "availability_sets": len(compute_data["availability_sets"])
    }

    return compute_data

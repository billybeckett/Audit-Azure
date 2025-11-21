# Resource Group Fix

## Issue Fixed

Some Azure CLI commands require the `--resource-group` argument and will fail with:
```
ERROR: the following arguments are required: --resource-group/-g
```

## Root Cause

Azure CLI commands fall into two categories:

### 1. Subscription-Level Commands (No --resource-group needed)
These work across the entire subscription:
```bash
az network vnet list --subscription {sub_id}
az network nsg list --subscription {sub_id}
az vm list --subscription {sub_id}
az storage account list --subscription {sub_id}
```

### 2. Resource-Group-Level Commands (--resource-group REQUIRED)
These must query each resource group:
```bash
az network vnet-gateway list --resource-group {rg} --subscription {sub_id}
```

## Solution Implemented

### Pattern

For commands requiring `--resource-group`:

```python
# 1. Get all resource groups first
resource_groups = run_az_command(
    f"az group list --subscription {subscription_id} --output json"
)
rg_names = [rg.get("name") for rg in resource_groups if rg.get("name")]

# 2. Iterate through each resource group
for rg_name in rg_names:
    resources = run_az_command(
        f"az COMMAND list --resource-group {rg_name} --subscription {subscription_id} --output json"
    )
    # Process resources...
```

## Commands Fixed

### networking_discovery.py

**Fixed:**
- ✅ `az network vnet-gateway list` - Now iterates through resource groups

**Already Correct:**
- ✅ `az network vnet peering list` - Already had --resource-group and --vnet-name
- ✅ `az network vnet list` - Works at subscription level
- ✅ `az network nsg list` - Works at subscription level
- ✅ `az network public-ip list` - Works at subscription level
- ✅ `az network lb list` - Works at subscription level
- ✅ `az network application-gateway list` - Works at subscription level
- ✅ `az network firewall list` - Works at subscription level
- ✅ `az network route-table list` - Works at subscription level
- ✅ `az network nic list` - Works at subscription level
- ✅ `az network vpn-gateway list` - Works at subscription level (Virtual WAN)

### compute_discovery.py

**Already Correct:**
- ✅ `az vm extension list` - Already had --resource-group and --vm-name
- ✅ `az vmss list-instances` - Already had --resource-group and --name
- ✅ All other commands work at subscription level

### database_discovery.py

**Already Correct:**
- ✅ `az sql db list` - Already had --resource-group and --server
- ✅ `az mysql db list` - Already had --resource-group and --server-name
- ✅ `az postgres db list` - Already had --resource-group and --server-name
- ✅ All server-level commands work at subscription level

### dns_discovery.py

**Already Correct:**
- ✅ `az network dns record-set list` - Already had --resource-group and --zone-name
- ✅ `az network private-dns record-set list` - Already had --resource-group and --zone-name
- ✅ `az network private-dns link vnet list` - Already had --resource-group and --zone-name
- ✅ Zone listing works at subscription level

### storage_discovery.py

**Already Correct:**
- ✅ All commands work at subscription level

### security_discovery.py

**Already Correct:**
- ✅ All commands work at subscription level

## How to Identify Commands That Need --resource-group

### Method 1: Check Azure CLI Documentation
```bash
az COMMAND list --help
```

Look for:
- `--resource-group` in the required parameters
- Error message: "the following arguments are required: --resource-group/-g"

### Method 2: Try Without --resource-group
If you get an error like:
```
ERROR: the following arguments are required: --resource-group/-g
```

Then you need to iterate through resource groups.

### Method 3: Common Patterns

**Usually require --resource-group:**
- Gateway resources (VNet Gateway, VPN Gateway)
- Some child resources (depends on the service)

**Usually work at subscription level:**
- Virtual Networks
- Network Security Groups
- Public IPs
- VMs
- Storage Accounts
- SQL Servers
- Most "list" operations

## Testing

To test if a command needs --resource-group:

```bash
# Test at subscription level
az COMMAND list --subscription YOUR_SUB_ID

# If it fails, try with resource group
az COMMAND list --resource-group YOUR_RG --subscription YOUR_SUB_ID
```

## Code Examples

### Before (BROKEN)
```python
vnet_gws = run_az_command(
    f"az network vnet-gateway list --subscription {subscription_id} --output json"
)
```

**Error:**
```
ERROR: the following arguments are required: --resource-group/-g
```

### After (FIXED)
```python
# Get resource groups
resource_groups = run_az_command(
    f"az group list --subscription {subscription_id} --output json"
)
rg_names = [rg.get("name") for rg in resource_groups if rg.get("name")]

# Iterate through each resource group
for rg_name in rg_names:
    vnet_gws = run_az_command(
        f"az network vnet-gateway list --resource-group {rg_name} --subscription {subscription_id} --output json"
    )
    for vgw in vnet_gws:
        # Process gateway...
```

## Performance Considerations

### Subscription-Level Queries (Preferred)
- ✅ **Fast** - Single API call
- ✅ **Efficient** - Gets all resources at once

### Resource-Group Iteration (Required for some)
- ⚠️ **Slower** - Multiple API calls (one per RG)
- ⚠️ **More requests** - Can hit rate limits in large environments
- ✅ **Necessary** - Some commands require it

**Optimization:**
- Only iterate through RGs when absolutely required
- Cache resource group list for reuse
- Use parallel requests if needed (future enhancement)

## Future Enhancements

Potential improvements:
1. **Parallel RG queries** - Query multiple RGs simultaneously
2. **Smart RG filtering** - Only query RGs that might have the resource
3. **Caching** - Cache RG list across discovery modules
4. **Error handling** - Better handling when RG access is denied

## Summary

- ✅ **Fixed:** `az network vnet-gateway list` now works correctly
- ✅ **Pattern:** Get RGs first, then iterate for commands that require it
- ✅ **Tested:** All other commands already correctly handle RG requirements
- ✅ **Documented:** Clear pattern for future additions

## Affected Files

- `scripts/discovery/networking_discovery.py` - Added RG iteration for vnet-gateway

All other files already had correct RG handling.

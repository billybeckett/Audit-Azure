# AWS vs Azure: Networking Comparison Guide

## Overview

This guide is designed for AWS professionals who need to understand Azure networking. While both platforms provide similar capabilities, their implementation approaches and terminology differ significantly. This document focuses on the networking services and provides practical examples using CLI tools.

## Table of Contents

1. [Core Networking Concepts](#core-networking-concepts)
2. [Service Mapping](#service-mapping)
3. [Key Differences](#key-differences)
4. [Practical Example: AWS Setup](#practical-example-aws-setup)
5. [Practical Example: Azure Equivalent](#practical-example-azure-equivalent)
6. [Cost Considerations](#cost-considerations)

---

## Core Networking Concepts

### Virtual Private Cloud/Network

| AWS | Azure | Notes |
|-----|-------|-------|
| **VPC (Virtual Private Cloud)** | **VNet (Virtual Network)** | Both provide isolated network environments |
| Region-specific | Region-specific | Cannot span multiple regions |
| Default VPC provided | No default VNet | Must create explicitly |
| CIDR block: /16 to /28 | Address space: /8 to /29 | Azure allows larger ranges |

**Key Similarity**: Both are software-defined networks that provide isolation, IP address management, and routing.

**Key Difference**: Azure VNets can have multiple non-contiguous address spaces, while AWS VPCs can have a primary CIDR and secondary CIDRs (up to 5).

---

### Subnets

| AWS | Azure | Notes |
|-----|-------|-------|
| **Subnet** | **Subnet** | Very similar concept |
| Availability Zone-specific | No AZ association | Azure subnets span all AZs in a region |
| /16 to /28 | /8 to /29 | Similar sizing |
| 5 reserved IPs | 5 reserved IPs | First 3 + last 2 IPs reserved |

**Key Similarity**: Both divide the parent network into smaller segments.

**Key Difference**: AWS subnets are tied to a specific Availability Zone, while Azure subnets automatically span all availability zones in a region.

---

### Routing

| AWS | Azure | Notes |
|-----|-------|-------|
| **Route Table** | **Route Table** | Similar function |
| Explicitly associated with subnets | Automatically applied to all subnets in VNet | Can be overridden per subnet |
| Main route table (default) | System routes (default) | Default routes handled differently |
| Static routes only | Static routes + BGP (with Virtual WAN) | Azure has more dynamic routing options |

**Key Similarity**: Both use route tables to direct traffic.

**Key Difference**: Azure has system-managed routes that are automatically created and can't be deleted (but can be overridden).

---

### Security

| AWS Concept | Azure Equivalent | Key Differences |
|-------------|------------------|-----------------|
| **Security Groups** | **Network Security Groups (NSG)** | Azure NSGs can attach to NICs or subnets |
| **Network ACLs** | **Network Security Groups** | Azure uses same NSG construct for both instance and subnet level |
| Stateful (Security Groups) | Stateful | Same behavior |
| Stateless (NACLs) | Stateful only | Azure doesn't have stateless option |

**Key Difference**: AWS has two layers (Security Groups + NACLs), while Azure uses NSGs at both NIC and subnet level, but they're always stateful.

---

### Internet Connectivity

| AWS | Azure | Notes |
|-----|-------|-------|
| **Internet Gateway (IGW)** | **Internet connectivity is default** | Azure VNets have internet outbound by default |
| **NAT Gateway** | **NAT Gateway** | Similar service, different pricing |
| Elastic IP | Public IP Address | Similar concept |
| Must attach IGW to VPC | No attachment needed | Fundamental difference |

**Key Difference**: In AWS, you must explicitly attach an IGW to enable internet access. In Azure, VNets have outbound internet by default; you need a Public IP or Load Balancer for inbound.

---

### VPN Connectivity

| AWS | Azure | Notes |
|-----|-------|-------|
| **Virtual Private Gateway (VGW)** | **VPN Gateway** | Both provide site-to-site VPN |
| **Customer Gateway** | **Local Network Gateway** | Represents on-premises VPN device |
| **VPN Connection** | **Connection** | Links the two gateways |
| BGP support optional | BGP support optional | Similar capabilities |

**Key Similarity**: Both provide IPsec VPN connectivity with similar features.

**Key Difference**: Azure VPN Gateways can take 30-45 minutes to deploy vs. AWS VGW which is typically faster.

---

### Transit/Hub Connectivity

| AWS | Azure | Notes |
|-----|-------|-------|
| **Transit Gateway (TGW)** | **Virtual WAN Hub** | Azure's answer to centralized routing |
| **Transit Gateway** | **VNet Peering** (alternative) | Simpler option for small deployments |
| Route table per attachment | Route table per hub | Similar routing control |
| Supports VPN, Direct Connect, VPC | Supports VPN, ExpressRoute, VNet | Parallel features |
| Cross-region peering | Cross-region (Global) | Both support inter-region |

**Key Similarity**: Both provide hub-and-spoke network topology with centralized routing.

**Key Difference**:
- AWS TGW is simpler to set up for basic hub-and-spoke
- Azure Virtual WAN is more complex but includes SD-WAN capabilities
- Azure also offers simple VNet Peering as a lighter alternative (mesh topology)

---

### Direct Connectivity

| AWS | Azure | Notes |
|-----|-------|-------|
| **Direct Connect** | **ExpressRoute** | Private connection to cloud |
| Direct Connect Gateway | ExpressRoute Gateway | Connects to virtual networks |
| 50 Mbps to 100 Gbps | 50 Mbps to 100 Gbps | Similar bandwidth options |

---

### Load Balancing

| AWS | Azure | Notes |
|-----|-------|-------|
| **Application Load Balancer** | **Application Gateway** | Layer 7 |
| **Network Load Balancer** | **Load Balancer** | Layer 4 |
| **Gateway Load Balancer** | **No direct equivalent** | Use NVAs with LB |
| Global Accelerator | Front Door / Traffic Manager | Global load balancing |

---

## Key Differences

### 1. Default Internet Access

**AWS**: VPCs are completely isolated by default. You must:
- Create and attach an Internet Gateway
- Add route to route table (0.0.0.0/0 → IGW)
- Assign public IPs or Elastic IPs

**Azure**: VNets have outbound internet access by default through system routes.

### 2. Subnet Availability

**AWS**: Subnets are tied to a single Availability Zone.

**Azure**: Subnets span all availability zones in a region automatically.

### 3. Security Model

**AWS**: Two-layer security (Security Groups + NACLs)

**Azure**: Single-layer NSGs that can be applied at NIC or subnet level

### 4. Resource Group Concept

**AWS**: Resource groups are tags/organizational units only

**Azure**: Resource groups are required containers for all resources, impact lifecycle management

### 5. Naming and Addressing

**AWS**:
- Resources often use IDs (vpc-xxxxx)
- DNS names auto-generated

**Azure**:
- You provide friendly names
- More explicit naming required

---

## Practical Example: AWS Setup

This example creates:
- 2 VPCs (10.1.0.0/16 and 10.2.0.0/16)
- 2 subnets per VPC (10.x.1.0/24 and 10.x.2.0/24)
- Transit Gateway connecting both VPCs
- VPN connection attached to the Transit Gateway

### Step 1: Create VPCs

```bash
# Create VPC 1
VPC1_ID=$(aws ec2 create-vpc \
  --cidr-block 10.1.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=VPC1}]' \
  --query 'Vpc.VpcId' \
  --output text)

echo "Created VPC1: $VPC1_ID"

# Create VPC 2
VPC2_ID=$(aws ec2 create-vpc \
  --cidr-block 10.2.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=VPC2}]' \
  --query 'Vpc.VpcId' \
  --output text)

echo "Created VPC2: $VPC2_ID"
```

### Step 2: Create Subnets

```bash
# VPC1 Subnets
SUBNET1_1=$(aws ec2 create-subnet \
  --vpc-id $VPC1_ID \
  --cidr-block 10.1.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=VPC1-Subnet1}]' \
  --query 'Subnet.SubnetId' \
  --output text)

SUBNET1_2=$(aws ec2 create-subnet \
  --vpc-id $VPC1_ID \
  --cidr-block 10.1.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=VPC1-Subnet2}]' \
  --query 'Subnet.SubnetId' \
  --output text)

# VPC2 Subnets
SUBNET2_1=$(aws ec2 create-subnet \
  --vpc-id $VPC2_ID \
  --cidr-block 10.2.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=VPC2-Subnet1}]' \
  --query 'Subnet.SubnetId' \
  --output text)

SUBNET2_2=$(aws ec2 create-subnet \
  --vpc-id $VPC2_ID \
  --cidr-block 10.2.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=VPC2-Subnet2}]' \
  --query 'Subnet.SubnetId' \
  --output text)

echo "Created subnets for VPC1: $SUBNET1_1, $SUBNET1_2"
echo "Created subnets for VPC2: $SUBNET2_1, $SUBNET2_2"
```

### Step 3: Create Transit Gateway

```bash
# Create Transit Gateway
TGW_ID=$(aws ec2 create-transit-gateway \
  --description "Transit Gateway for VPC interconnection" \
  --tag-specifications 'ResourceType=transit-gateway,Tags=[{Key=Name,Value=Main-TGW}]' \
  --query 'TransitGateway.TransitGatewayId' \
  --output text)

echo "Created Transit Gateway: $TGW_ID"

# Wait for Transit Gateway to become available
aws ec2 wait transit-gateway-available --transit-gateway-ids $TGW_ID
echo "Transit Gateway is now available"
```

### Step 4: Attach VPCs to Transit Gateway

```bash
# Attach VPC1 to TGW
TGW_ATTACH1=$(aws ec2 create-transit-gateway-vpc-attachment \
  --transit-gateway-id $TGW_ID \
  --vpc-id $VPC1_ID \
  --subnet-ids $SUBNET1_1 $SUBNET1_2 \
  --tag-specifications 'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=VPC1-TGW-Attachment}]' \
  --query 'TransitGatewayVpcAttachment.TransitGatewayAttachmentId' \
  --output text)

# Attach VPC2 to TGW
TGW_ATTACH2=$(aws ec2 create-transit-gateway-vpc-attachment \
  --transit-gateway-id $TGW_ID \
  --vpc-id $VPC2_ID \
  --subnet-ids $SUBNET2_1 $SUBNET2_2 \
  --tag-specifications 'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=VPC2-TGW-Attachment}]' \
  --query 'TransitGatewayVpcAttachment.TransitGatewayAttachmentId' \
  --output text)

echo "Created TGW attachments: $TGW_ATTACH1, $TGW_ATTACH2"
```

### Step 5: Update VPC Route Tables

```bash
# Get route table IDs
RT_VPC1=$(aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=$VPC1_ID" "Name=association.main,Values=true" \
  --query 'RouteTables[0].RouteTableId' \
  --output text)

RT_VPC2=$(aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=$VPC2_ID" "Name=association.main,Values=true" \
  --query 'RouteTables[0].RouteTableId' \
  --output text)

# Add routes to Transit Gateway
aws ec2 create-route \
  --route-table-id $RT_VPC1 \
  --destination-cidr-block 10.2.0.0/16 \
  --transit-gateway-id $TGW_ID

aws ec2 create-route \
  --route-table-id $RT_VPC2 \
  --destination-cidr-block 10.1.0.0/16 \
  --transit-gateway-id $TGW_ID

echo "Updated route tables with TGW routes"
```

### Step 6: Create Customer Gateway (On-Premises Side)

```bash
# Create Customer Gateway (represents your on-premises VPN device)
# Replace with your actual public IP
CGW_ID=$(aws ec2 create-customer-gateway \
  --type ipsec.1 \
  --public-ip 203.0.113.12 \
  --bgp-asn 65000 \
  --tag-specifications 'ResourceType=customer-gateway,Tags=[{Key=Name,Value=OnPrem-CGW}]' \
  --query 'CustomerGateway.CustomerGatewayId' \
  --output text)

echo "Created Customer Gateway: $CGW_ID"
```

### Step 7: Create VPN Attachment to Transit Gateway

```bash
# Create VPN attachment to Transit Gateway
VPN_ATTACH=$(aws ec2 create-vpn-connection \
  --type ipsec.1 \
  --customer-gateway-id $CGW_ID \
  --transit-gateway-id $TGW_ID \
  --tag-specifications 'ResourceType=vpn-connection,Tags=[{Key=Name,Value=TGW-VPN}]' \
  --query 'VpnConnection.VpnConnectionId' \
  --output text)

echo "Created VPN Connection: $VPN_ATTACH"
```

### Step 8: Enable Route Propagation (Optional)

```bash
# Get the Transit Gateway route table ID
TGW_RT_ID=$(aws ec2 describe-transit-gateway-route-tables \
  --filters "Name=transit-gateway-id,Values=$TGW_ID" \
  --query 'TransitGatewayRouteTables[0].TransitGatewayRouteTableId' \
  --output text)

# Enable route propagation for VPN
aws ec2 enable-transit-gateway-route-table-propagation \
  --transit-gateway-route-table-id $TGW_RT_ID \
  --transit-gateway-attachment-id $VPN_ATTACH

echo "Enabled route propagation for VPN"
```

### AWS Architecture Summary

```
                          ┌─────────────────────┐
                          │   Transit Gateway   │
                          │    (Hub for all)    │
                          └──────────┬──────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            │                        │                        │
            ▼                        ▼                        ▼
    ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
    │     VPC1      │       │     VPC2      │       │  VPN Gateway  │
    │  10.1.0.0/16  │       │  10.2.0.0/16  │       │  (On-Prem)    │
    └───────┬───────┘       └───────┬───────┘       └───────────────┘
            │                       │
       ┌────┴────┐             ┌────┴────┐
       ▼         ▼             ▼         ▼
   10.1.1.0/24  10.1.2.0/24  10.2.1.0/24  10.2.2.0/24
   (Subnet1)    (Subnet2)    (Subnet1)    (Subnet2)
```

---

## Practical Example: Azure Equivalent

This example creates the exact same architecture in Azure:
- 2 VNets (10.1.0.0/16 and 10.2.0.0/16)
- 2 subnets per VNet (10.x.1.0/24 and 10.x.2.0/24)
- Virtual WAN Hub (equivalent to Transit Gateway)
- VPN Gateway attached to the Virtual WAN Hub

### Important Azure Concepts

1. **Resource Group**: All Azure resources must be in a resource group
2. **Location**: Azure uses location (e.g., eastus) instead of region
3. **Virtual WAN**: Azure's equivalent to Transit Gateway (hub-and-spoke)

### Step 1: Create Resource Group

```bash
# Set variables
LOCATION="eastus"
RG_NAME="NetworkDemo-RG"

# Create Resource Group
az group create \
  --name $RG_NAME \
  --location $LOCATION

echo "Created Resource Group: $RG_NAME"
```

### Step 2: Create VNets

```bash
# Create VNet 1
az network vnet create \
  --resource-group $RG_NAME \
  --name VNet1 \
  --address-prefix 10.1.0.0/16 \
  --location $LOCATION

# Create VNet 2
az network vnet create \
  --resource-group $RG_NAME \
  --name VNet2 \
  --address-prefix 10.2.0.0/16 \
  --location $LOCATION

echo "Created VNets: VNet1 and VNet2"
```

### Step 3: Create Subnets

```bash
# VNet1 Subnets
az network vnet subnet create \
  --resource-group $RG_NAME \
  --vnet-name VNet1 \
  --name Subnet1 \
  --address-prefixes 10.1.1.0/24

az network vnet subnet create \
  --resource-group $RG_NAME \
  --vnet-name VNet1 \
  --name Subnet2 \
  --address-prefixes 10.1.2.0/24

# VNet2 Subnets
az network vnet subnet create \
  --resource-group $RG_NAME \
  --vnet-name VNet2 \
  --name Subnet1 \
  --address-prefixes 10.2.1.0/24

az network vnet subnet create \
  --resource-group $RG_NAME \
  --vnet-name VNet2 \
  --name Subnet2 \
  --address-prefixes 10.2.2.0/24

echo "Created subnets for both VNets"
```

### Step 4: Create Virtual WAN (Transit Hub)

```bash
# Create Virtual WAN (this is the hub architecture)
az network vwan create \
  --resource-group $RG_NAME \
  --name MainVWAN \
  --location $LOCATION \
  --type Standard

echo "Created Virtual WAN: MainVWAN"
```

### Step 5: Create Virtual Hub (Regional Hub)

```bash
# Create Virtual Hub in the region
# This is the equivalent of the Transit Gateway
az network vhub create \
  --resource-group $RG_NAME \
  --name Hub-EastUS \
  --vwan MainVWAN \
  --address-prefix 10.100.0.0/24 \
  --location $LOCATION

echo "Created Virtual Hub: Hub-EastUS"
echo "Note: Hub creation takes 10-30 minutes. Waiting..."

# Wait for hub to be provisioned
az network vhub wait \
  --resource-group $RG_NAME \
  --name Hub-EastUS \
  --created

echo "Virtual Hub is now ready"
```

### Step 6: Connect VNets to Virtual Hub

```bash
# Connect VNet1 to Virtual Hub
az network vhub connection create \
  --resource-group $RG_NAME \
  --vhub-name Hub-EastUS \
  --name VNet1-Connection \
  --remote-vnet VNet1

# Connect VNet2 to Virtual Hub
az network vhub connection create \
  --resource-group $RG_NAME \
  --vhub-name Hub-EastUS \
  --name VNet2-Connection \
  --remote-vnet VNet2

echo "Connected VNets to Virtual Hub"
echo "Note: Connections take 5-10 minutes to complete"
```

### Step 7: Create VPN Gateway in Virtual Hub

```bash
# Create VPN Gateway in the Virtual Hub
# This is equivalent to attaching a VPN to the Transit Gateway
az network vpn-gateway create \
  --resource-group $RG_NAME \
  --name Hub-VPNGateway \
  --vhub Hub-EastUS \
  --location $LOCATION \
  --scale-unit 1

echo "Created VPN Gateway in Virtual Hub"
echo "Note: VPN Gateway creation takes 30-45 minutes"

# Wait for VPN Gateway
az network vpn-gateway wait \
  --resource-group $RG_NAME \
  --name Hub-VPNGateway \
  --created

echo "VPN Gateway is now ready"
```

### Step 8: Create VPN Site (On-Premises Side)

```bash
# Create VPN Site (equivalent to Customer Gateway)
# Replace with your actual public IP
az network vpn-site create \
  --resource-group $RG_NAME \
  --name OnPrem-Site \
  --location $LOCATION \
  --virtual-wan MainVWAN \
  --ip-address 203.0.113.12 \
  --address-prefixes 192.168.0.0/16 \
  --device-vendor "Cisco" \
  --device-model "ISR" \
  --link-speed 100 \
  --asn 65000 \
  --bgp-peering-address 192.168.255.1

echo "Created VPN Site: OnPrem-Site"
```

### Step 9: Create VPN Connection

```bash
# Create VPN connection from VPN Gateway to VPN Site
az network vpn-gateway connection create \
  --resource-group $RG_NAME \
  --gateway-name Hub-VPNGateway \
  --name OnPrem-Connection \
  --remote-vpn-site OnPrem-Site \
  --shared-key "YourSharedKeyHere123!" \
  --enable-bgp true

echo "Created VPN Connection: OnPrem-Connection"
```

### Step 10: Verify Connectivity (Optional)

```bash
# View Virtual WAN configuration
az network vwan show \
  --resource-group $RG_NAME \
  --name MainVWAN

# View Virtual Hub configuration
az network vhub show \
  --resource-group $RG_NAME \
  --name Hub-EastUS

# List all VNet connections
az network vhub connection list \
  --resource-group $RG_NAME \
  --vhub-name Hub-EastUS \
  --output table

# View VPN Gateway status
az network vpn-gateway show \
  --resource-group $RG_NAME \
  --name Hub-VPNGateway

# View effective routes in Virtual Hub
az network vhub get-effective-routes \
  --resource-group $RG_NAME \
  --name Hub-EastUS \
  --resource-type VirtualNetworkConnection \
  --resource-id "/subscriptions/{subscription-id}/resourceGroups/$RG_NAME/providers/Microsoft.Network/virtualHubs/Hub-EastUS/hubVirtualNetworkConnections/VNet1-Connection"
```

### Azure Architecture Summary

```
                     ┌─────────────────────────────┐
                     │      Virtual WAN            │
                     │   (Global WAN Service)      │
                     └──────────┬──────────────────┘
                                │
                     ┌──────────▼──────────────┐
                     │    Virtual Hub          │
                     │   (Regional Hub)        │
                     │   10.100.0.0/24         │
                     └──────────┬──────────────┘
                                │
            ┌───────────────────┼──────────────────────┐
            │                   │                      │
            ▼                   ▼                      ▼
    ┌───────────────┐   ┌───────────────┐    ┌───────────────┐
    │    VNet1      │   │    VNet2      │    │  VPN Gateway  │
    │  10.1.0.0/16  │   │  10.2.0.0/16  │    │  (On-Prem)    │
    └───────┬───────┘   └───────┬───────┘    └───────────────┘
            │                   │
       ┌────┴────┐         ┌────┴────┐
       ▼         ▼         ▼         ▼
   10.1.1.0/24  10.1.2.0/24  10.2.1.0/24  10.2.2.0/24
   (Subnet1)    (Subnet2)    (Subnet1)    (Subnet2)
```

---

## Alternative Azure Approach: VNet Peering (Simpler Option)

If you don't need the advanced features of Virtual WAN, you can use VNet Peering:

```bash
# Create VNet Peering VNet1 → VNet2
az network vnet peering create \
  --resource-group $RG_NAME \
  --name VNet1-to-VNet2 \
  --vnet-name VNet1 \
  --remote-vnet VNet2 \
  --allow-vnet-access \
  --allow-forwarded-traffic \
  --allow-gateway-transit

# Create VNet Peering VNet2 → VNet1
az network vnet peering create \
  --resource-group $RG_NAME \
  --name VNet2-to-VNet1 \
  --vnet-name VNet2 \
  --remote-vnet VNet1 \
  --allow-vnet-access \
  --allow-forwarded-traffic \
  --use-remote-gateways

# For VPN, create a separate VPN Gateway in one VNet
az network vnet subnet create \
  --resource-group $RG_NAME \
  --vnet-name VNet1 \
  --name GatewaySubnet \
  --address-prefixes 10.1.255.0/27

az network public-ip create \
  --resource-group $RG_NAME \
  --name VNet1-VPN-PIP \
  --allocation-method Dynamic

az network vnet-gateway create \
  --resource-group $RG_NAME \
  --name VNet1-VPN-GW \
  --vnet VNet1 \
  --public-ip-address VNet1-VPN-PIP \
  --gateway-type Vpn \
  --vpn-type RouteBased \
  --sku VpnGw1 \
  --no-wait

echo "VNet Peering created. This creates a mesh topology instead of hub-and-spoke."
```

**VNet Peering vs Virtual WAN**:
- **VNet Peering**: Simpler, cheaper, mesh topology, good for < 10 VNets
- **Virtual WAN**: Complex, more expensive, hub-and-spoke, better for large scale deployments

---

## Comparison Summary Table

| Feature | AWS Command Pattern | Azure Command Pattern |
|---------|-------------------|---------------------|
| **Create Network** | `aws ec2 create-vpc` | `az network vnet create` |
| **Create Subnet** | `aws ec2 create-subnet` | `az network vnet subnet create` |
| **Create Transit Hub** | `aws ec2 create-transit-gateway` | `az network vwan create` + `az network vhub create` |
| **Attach Network to Hub** | `aws ec2 create-transit-gateway-vpc-attachment` | `az network vhub connection create` |
| **Create VPN Gateway** | `aws ec2 create-vpn-gateway` | `az network vpn-gateway create` |
| **On-Prem Device** | `aws ec2 create-customer-gateway` | `az network vpn-site create` |
| **VPN Connection** | `aws ec2 create-vpn-connection` | `az network vpn-gateway connection create` |
| **Route Table** | `aws ec2 create-route-table` | `az network route-table create` |
| **Network Peering** | `aws ec2 create-vpc-peering-connection` | `az network vnet peering create` |

---

## Cost Considerations

### AWS Costs
- **Transit Gateway**: $0.05/hour per attachment + data processing
- **VPN Connection**: $0.05/hour per connection
- **Data Transfer**: $0.02-$0.09/GB (varies by region and direction)

### Azure Costs
- **Virtual WAN**: Hub deployment ~$0.25/hour + connection units
- **VPN Gateway**: $0.04-$0.50/hour (depending on SKU)
- **VNet Peering**: $0.01/GB for intra-region, $0.035/GB for inter-region
- **Data Transfer**: $0.01-$0.087/GB (varies by region)

### Cost Comparison
For simple hub-and-spoke with 2-3 VNets:
- **VNet Peering** is usually cheaper than Virtual WAN in Azure
- **Transit Gateway** in AWS is cost-effective starting from 3+ VPCs

---

## Key Takeaways for AWS Users

1. **Mental Model**: Think of VNet as VPC, but with more flexibility in address space management
2. **Subnets**: Azure subnets span all AZs - no need to create per-AZ subnets
3. **Transit Hub**: Virtual WAN is more complex than TGW but offers SD-WAN features; consider VNet Peering for simple scenarios
4. **Security**: Azure uses NSGs everywhere (no separate NACL concept)
5. **Internet Access**: Azure VNets have outbound internet by default
6. **Deployment Time**: Azure networking resources (especially gateways) take longer to provision
7. **Resource Groups**: Everything must be in a resource group - use them for lifecycle management
8. **Naming**: Azure uses friendly names everywhere, plan your naming convention carefully

---

## Additional Resources

### AWS Documentation
- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [AWS Transit Gateway](https://docs.aws.amazon.com/vpc/latest/tgw/)

### Azure Documentation
- [Azure Virtual Network Documentation](https://docs.microsoft.com/azure/virtual-network/)
- [Azure Virtual WAN Documentation](https://docs.microsoft.com/azure/virtual-wan/)
- [Azure VNet Peering](https://docs.microsoft.com/azure/virtual-network/virtual-network-peering-overview)

### CLI Reference
- [AWS CLI EC2 Commands](https://docs.aws.amazon.com/cli/latest/reference/ec2/)
- [Azure CLI Network Commands](https://docs.microsoft.com/cli/azure/network)

---

## Cleanup Commands

### AWS Cleanup

```bash
# Delete VPN Connection
aws ec2 delete-vpn-connection --vpn-connection-id $VPN_ATTACH

# Delete Customer Gateway
aws ec2 delete-customer-gateway --customer-gateway-id $CGW_ID

# Delete TGW Attachments
aws ec2 delete-transit-gateway-vpc-attachment --transit-gateway-attachment-id $TGW_ATTACH1
aws ec2 delete-transit-gateway-vpc-attachment --transit-gateway-attachment-id $TGW_ATTACH2

# Wait for attachments to be deleted
sleep 60

# Delete Transit Gateway
aws ec2 delete-transit-gateway --transit-gateway-id $TGW_ID

# Delete Subnets
aws ec2 delete-subnet --subnet-id $SUBNET1_1
aws ec2 delete-subnet --subnet-id $SUBNET1_2
aws ec2 delete-subnet --subnet-id $SUBNET2_1
aws ec2 delete-subnet --subnet-id $SUBNET2_2

# Delete VPCs
aws ec2 delete-vpc --vpc-id $VPC1_ID
aws ec2 delete-vpc --vpc-id $VPC2_ID
```

### Azure Cleanup

```bash
# Delete entire resource group (deletes all resources)
az group delete \
  --name $RG_NAME \
  --yes \
  --no-wait

# This single command removes:
# - Virtual WAN
# - Virtual Hub
# - VPN Gateway
# - VPN Site
# - VNet Connections
# - VNets and Subnets
# - Everything else in the resource group
```

**Note**: Azure's resource group concept makes cleanup much simpler - delete the group and everything goes away.

---

*Document Version: 1.0*
*Last Updated: 2025-11-20*

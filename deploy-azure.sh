#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 NetworkBuster Azure Deployment${NC}"
echo "=================================="

# Configuration
RESOURCE_GROUP="networkbuster-rg"
REGISTRY_NAME=$(az deployment group show --resource-group $RESOURCE_GROUP --name main --query 'properties.outputs.containerRegistryLoginServer.value' -o tsv | cut -d'.' -f1)
REGISTRY_URL=$(az deployment group show --resource-group $RESOURCE_GROUP --name main --query 'properties.outputs.containerRegistryLoginServer.value' -o tsv)

echo -e "${GREEN}✓ Resource Group: $RESOURCE_GROUP${NC}"
echo -e "${GREEN}✓ Registry: $REGISTRY_URL${NC}"

# Login to Azure Container Registry
echo -e "${YELLOW}📦 Logging into Container Registry...${NC}"
az acr login --name $REGISTRY_NAME

# Build and push Main Server image
echo -e "${YELLOW}🔨 Building Main Server image...${NC}"
az acr build --registry $REGISTRY_NAME --image networkbuster-server:latest --image networkbuster-server:$(git rev-parse --short HEAD) .

# Build and push Overlay image
echo -e "${YELLOW}🔨 Building Overlay UI image...${NC}"
az acr build --registry $REGISTRY_NAME --image networkbuster-overlay:latest --image networkbuster-overlay:$(git rev-parse --short HEAD) challengerepo/real-time-overlay

# Build and push AI Defense image
echo -e "${YELLOW}🛡️ Building AI Defense Container image...${NC}"
az acr build --registry $REGISTRY_NAME --image networkbuster-ai-defense:latest --image networkbuster-ai-defense:$(git rev-parse --short HEAD) --file Dockerfile.ai-defense .

# Update Container Apps
echo -e "${YELLOW}🚀 Updating Container Apps...${NC}"
az containerapp update \
  --name networkbuster-server \
  --resource-group $RESOURCE_GROUP \
  --image $REGISTRY_URL/networkbuster-server:latest

az containerapp update \
  --name networkbuster-overlay \
  --resource-group $RESOURCE_GROUP \
  --image $REGISTRY_URL/networkbuster-overlay:latest

# Deploy AI Defense Container App (if it doesn't exist, create it)
echo -e "${YELLOW}🚀 Deploying AI Defense Container...${NC}"
if az containerapp show --name networkbuster-ai-defense --resource-group $RESOURCE_GROUP &>/dev/null; then
    az containerapp update \
      --name networkbuster-ai-defense \
      --resource-group $RESOURCE_GROUP \
      --image $REGISTRY_URL/networkbuster-ai-defense:latest
else
    az containerapp create \
      --name networkbuster-ai-defense \
      --resource-group $RESOURCE_GROUP \
      --environment networkbuster-env \
      --image $REGISTRY_URL/networkbuster-ai-defense:latest \
      --target-port 8000 \
      --ingress external \
      --cpu 1.0 \
      --memory 2.0Gi \
      --min-replicas 1 \
      --max-replicas 3 \
      --env-vars DEFENSE_LEVEL=maximum MONITORING_INTERVAL=30
fi

# Output URLs
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""
echo -e "${YELLOW}📊 Deployment URLs:${NC}"
echo "Main Server: $(az containerapp show --name networkbuster-server --resource-group $RESOURCE_GROUP --query 'properties.configuration.ingress.fqdn' -o tsv)"
echo "Overlay UI: $(az containerapp show --name networkbuster-overlay --resource-group $RESOURCE_GROUP --query 'properties.configuration.ingress.fqdn' -o tsv)"
echo "AI Defense: $(az containerapp show --name networkbuster-ai-defense --resource-group $RESOURCE_GROUP --query 'properties.configuration.ingress.fqdn' -o tsv)"

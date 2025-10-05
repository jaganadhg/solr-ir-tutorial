#!/bin/bash

# Solr Vector Search Setup Script
# This script sets up the complete Solr environment with proper configuration

set -e

echo "============================================================"
echo "Solr Vector Search Setup"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color


# Stop any existing containers
echo ""
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Remove old volumes if requested
read -p "Remove existing data volumes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing volumes...${NC}"
    docker-compose down -v
    echo -e "${GREEN}✓ Volumes removed${NC}"
fi

# Start Solr
echo ""
echo -e "${YELLOW}Starting Solr...${NC}"
docker-compose up -d

# Wait for Solr to be ready
echo ""
echo -e "${YELLOW}Waiting for Solr to start...${NC}"
sleep 10

max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s "http://localhost:8983/solr/admin/cores?action=STATUS" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Solr is running${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo -n "."
    sleep 2
done
echo ""

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}✗ Solr failed to start${NC}"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

# Create collection using API if it doesn't exist
echo ""
echo -e "${YELLOW}Setting up collection...${NC}"

# Copy config files into the container
echo "Copying configuration files..."
docker exec solr-vector-search-v1 mkdir -p /tmp/custom_configset/conf
docker cp configsets/conf/managed-schema.xml solr-vector-search-v1:/tmp/custom_configset/conf/
docker cp configsets/conf/solrconfig.xml solr-vector-search-v1:/tmp/custom_configset/conf/

# Copy default config files for missing items
docker exec solr-vector-search-v1 bash -c "cp /opt/solr/server/solr/configsets/_default/conf/stopwords.txt /tmp/custom_configset/conf/ 2>/dev/null || true"
docker exec solr-vector-search-v1 bash -c "cp /opt/solr/server/solr/configsets/_default/conf/synonyms.txt /tmp/custom_configset/conf/ 2>/dev/null || true"
docker exec solr-vector-search-v1 bash -c "cp /opt/solr/server/solr/configsets/_default/conf/protwords.txt /tmp/custom_configset/conf/ 2>/dev/null || true"
docker exec solr-vector-search-v1 bash -c "cp /opt/solr/server/solr/configsets/_default/conf/lang /tmp/custom_configset/conf/ -r 2>/dev/null || true"

# Delete collection if it exists
docker exec solr-vector-search-v1 curl -s "http://localhost:8983/solr/admin/cores?action=UNLOAD&core=vector_collection&deleteIndex=true&deleteDataDir=true&deleteInstanceDir=true" > /dev/null 2>&1 || true

# Create the collection
echo "Creating collection..."
docker exec solr-vector-search-v1 solr create -c vector_collection -d /tmp/custom_configset

# Verify collection was created
sleep 3
if curl -s "http://localhost:8983/solr/vector_collection/admin/ping" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Collection 'vector_collection' created successfully${NC}"
else
    echo -e "${RED}✗ Failed to create collection${NC}"
    echo "Check logs with: docker-compose logs"
    exit 1
fi


# Display final status
echo ""
echo "============================================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "============================================================"
echo ""
echo "Solr Admin UI: http://localhost:8983/solr"
echo "Collection: vector_collection"
echo ""
echo "Test the collection:"
echo "  curl 'http://localhost:8983/solr/vector_collection/select?q=*:*'"
echo ""
echo "Next steps:"
echo "  1. Run: python index_random_data.py"
echo "  2. Run: python example_usage.py"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
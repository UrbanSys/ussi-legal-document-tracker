#!/bin/bash
# Deploy USSI Backend to VM
# Usage: ./deploy.sh <vm-ip> <vm-user> [branch]

set -e

VM_IP=${1:-}
VM_USER=${2:-ubuntu}
BRANCH=${3:-main}
REPO_URL="https://github.com/UrbanSys/ussi-legal-document-tracker.git"
APP_DIR="/opt/ussi-legal-document-tracker"

if [ -z "$VM_IP" ]; then
    echo "Usage: ./deploy.sh <vm-ip> [vm-user] [branch]"
    echo "Example: ./deploy.sh 192.168.1.100 ubuntu main"
    exit 1
fi

echo "=========================================="
echo "Deploying USSI Backend to $VM_IP"
echo "=========================================="
echo ""

# Step 1: Install Docker if not present
echo "Step 1: Ensuring Docker is installed..."
ssh -o StrictHostKeyChecking=no "$VM_USER@$VM_IP" << 'EOF'
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    newgrp docker
    echo "Docker installed successfully"
else
    echo "Docker already installed"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed"
else
    echo "Docker Compose already installed"
fi
EOF

echo ""

# Step 2: Clone or update repository
echo "Step 2: Cloning/updating repository..."
ssh "$VM_USER@$VM_IP" << EOF
if [ -d "$APP_DIR" ]; then
    echo "Updating existing repository..."
    cd $APP_DIR
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
else
    echo "Cloning new repository..."
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
    git clone -b $BRANCH $REPO_URL $APP_DIR
fi
cd $APP_DIR
echo "Repository ready at $APP_DIR"
EOF

echo ""

# Step 3: Configure environment
echo "Step 3: Configuring environment..."
ssh "$VM_USER@$VM_IP" << EOF
cd $APP_DIR/backend

if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.docker .env
    echo "⚠️  Please edit .env with your database credentials:"
    echo "   - Set DATABASE_URL with your MSSQL connection"
    echo "   - Set SA_PASSWORD securely"
    echo "Then run: docker-compose up -d"
else
    echo ".env already exists, skipping..."
fi
EOF

echo ""

# Step 4: Build and start containers
echo "Step 4: Building Docker image and starting containers..."
ssh "$VM_USER@$VM_IP" << EOF
cd $APP_DIR/backend

echo "Building image..."
docker build -t ussi-backend:latest .

echo "Starting containers..."
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 10

echo "Container status:"
docker-compose ps

echo ""
echo "Checking health..."
docker exec ussi-backend curl -s http://localhost:8000/health || echo "Service still starting..."
EOF

echo ""

# Step 5: Verify deployment
echo "Step 5: Verifying deployment..."
echo ""
echo "Testing API connectivity..."
if curl -s "http://$VM_IP:8000/health" | grep -q "healthy"; then
    echo "✓ API is healthy!"
else
    echo "⚠️  API not yet responding (may still be starting)"
fi

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. SSH into VM: ssh $VM_USER@$VM_IP"
echo "2. Configure environment: cd $APP_DIR/backend && nano .env"
echo "3. View logs: docker-compose logs -f backend"
echo "4. Access API docs: http://$VM_IP:8000/docs"
echo ""
echo "Database setup:"
echo "1. Check container logs: docker-compose logs mssql"
echo "2. Connect to DB: docker exec -it ussi-mssql sqlcmd -S localhost -U sa"
echo ""

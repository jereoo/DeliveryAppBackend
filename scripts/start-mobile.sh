# CIO DIRECTIVE – PERMANENT FIX FOR DAILY NETWORK ERROR – NOV 20 2025
#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
BACKEND_PATH="../DeliveryAppBackend"
MOBILE_PATH="."

echo -e "${BLUE}🚀 CIO-APPROVED DELIVERYAPP STARTUP SEQUENCE${NC}"
echo -e "${BLUE}====================================================${NC}"

# Step 1: Check if Django backend is already running
echo -e "${YELLOW}📡 Checking Django backend status...${NC}"
if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Django backend already running${NC}"
else
    echo -e "${YELLOW}🔧 Starting Django backend...${NC}"
    
    # Navigate to backend and start server in background
    cd "$BACKEND_PATH"
    
    # Activate virtual environment if it exists
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    fi
    
    # Start Django server in background
    python manage.py runserver 0.0.0.0:8000 &
    DJANGO_PID=$!
    
    # Wait for Django to be ready
    echo -e "${YELLOW}⏳ Waiting for Django backend to be ready...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Django backend is ready!${NC}"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    if ! curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
        echo -e "${RED}❌ Django backend failed to start after 60 seconds${NC}"
        exit 1
    fi
    
    cd "$MOBILE_PATH"
fi

# Step 2: Clean Expo cache and start tunnel
echo -e "${YELLOW}🧹 Cleaning Expo cache...${NC}"
npx expo install --fix
rm -rf .expo node_modules/.cache

echo -e "${YELLOW}🌐 Starting Expo with tunnel...${NC}"

# Set environment variables
export EXPO_USE_TUNNEL=true

# Start Expo with tunnel in background and capture output
npx expo start --tunnel --clear &
EXPO_PID=$!

# Wait for tunnel URL to be generated
echo -e "${YELLOW}⏳ Waiting for Expo tunnel URL...${NC}"
sleep 10

# Try to extract tunnel URL from expo logs
TUNNEL_URL=""
for i in {1..20}; do
    # Check if expo generated a tunnel URL
    if pgrep -f "expo start" > /dev/null; then
        # Try to get tunnel URL from expo CLI output or metro bundler
        POTENTIAL_URL=$(curl -s http://localhost:19002/status 2>/dev/null | grep -o 'https://.*\.ngrok\.io' | head -1 || echo "")
        if [ ! -z "$POTENTIAL_URL" ]; then
            TUNNEL_URL="$POTENTIAL_URL"
            break
        fi
    fi
    echo -n "."
    sleep 2
done

# Update .env file with tunnel URL
if [ ! -z "$TUNNEL_URL" ]; then
    echo -e "${GREEN}🎯 Tunnel URL found: ${TUNNEL_URL}${NC}"
    
    # Update .env file
    cat > .env << EOF
# CIO DIRECTIVE – PERMANENT FIX FOR DAILY NETWORK ERROR – NOV 20 2025
EXPO_USE_TUNNEL=true
BACKEND_URL=${TUNNEL_URL}/api
EOF
    
    echo -e "${GREEN}✅ Updated .env with tunnel URL${NC}"
    
    # Copy to clipboard if available
    if command -v pbcopy > /dev/null; then
        echo "$TUNNEL_URL" | pbcopy
        echo -e "${GREEN}📋 Tunnel URL copied to clipboard${NC}"
    elif command -v xclip > /dev/null; then
        echo "$TUNNEL_URL" | xclip -selection clipboard
        echo -e "${GREEN}📋 Tunnel URL copied to clipboard${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Could not automatically detect tunnel URL${NC}"
    echo -e "${YELLOW}   Check the Expo CLI output above for the tunnel URL${NC}"
fi

# Step 3: Final instructions
echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}🎉 DELIVERYAPP STARTUP COMPLETE!${NC}"
echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}📱 Scan the QR code in Expo Go app${NC}"
echo -e "${GREEN}🌐 Django API: http://localhost:8000${NC}"
if [ ! -z "$TUNNEL_URL" ]; then
    echo -e "${GREEN}🔗 Mobile API: ${TUNNEL_URL}/api${NC}"
fi
echo -e "${GREEN}====================================================${NC}"

# Keep script running and show logs
echo -e "${BLUE}📊 Showing live logs (Ctrl+C to stop):${NC}"
wait
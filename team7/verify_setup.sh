#!/bin/bash
# Team 7 Quick Verification Script
# Verifies that all components are properly configured

echo "=============================================="
echo "Team 7 TOEFL Service - Setup Verification"
echo "=============================================="
echo ""

echo "📦 Checking Docker Containers..."
CORE_RUNNING=$(docker ps | grep -c "software-engineering-1404-01_g1-core")
GATEWAY_RUNNING=$(docker ps | grep -c "team7-gateway")

if [ "$CORE_RUNNING" -eq 1 ]; then
    echo "  ✓ Core service: Running"
else
    echo "  ✗ Core service: Not running"
fi

if [ "$GATEWAY_RUNNING" -eq 1 ]; then
    echo "  ✓ Team7 gateway: Running"  
else
    echo "  ✗ Team7 gateway: Not running"
fi

echo ""

echo "🔧 Checking Environment Configuration..."
if [ -f ".env" ]; then
    if grep -q "AI_GENERATOR_API_KEY=g4a-" .env; then
        echo "  ✓ .env file exists with API key configured"
    else
        echo "  ✗ .env file missing API key"
    fi
else
    echo "  ✗ .env file not found"
fi

echo ""

echo "Checking Database..."
if [ -f "team7/team7.sqlite3" ]; then
    echo "  ✓ Team7 database exists"
    
    # Count questions
    cd team7
    QUESTION_COUNT=$(python3 << EOF
import sqlite3
conn = sqlite3.connect('team7.sqlite3')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM team7_question')
print(cursor.fetchone()[0])
conn.close()
EOF
)
    echo "  ✓ Questions in database: $QUESTION_COUNT"
    cd ..
else
    echo "  ✗ Database file not found"
fi

echo ""

echo " Checking HTTP Endpoints..."
CORE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/team7/)
GATEWAY_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9131/team7/)

if [ "$CORE_RESPONSE" = "200" ]; then
    echo "  ✓ Core accessible at http://localhost:8000/team7/"
else
    echo "  ✗ Core not responding (HTTP $CORE_RESPONSE)"
fi

if [ "$GATEWAY_RESPONSE" = "200" ]; then
    echo "  ✓ Gateway accessible at http://localhost:9131/team7/"
else
    echo "  ✗ Gateway not responding (HTTP $GATEWAY_RESPONSE)"
fi

echo ""
echo "=============================================="
echo "✓ Setup verification complete!"
echo "=============================================="
echo ""
echo " For full details, see: team7/SETUP_COMPLETE.md"
echo ""
echo " Next steps:"
echo "   1. Open browser: http://localhost:9131/team7/"
echo "   2. Create a user account via core system"
echo "   3. Implement frontend JavaScript (Sprint 1, Task 5)"
echo ""

#!/bin/bash
# Health Check Script

API_URL="${API_URL:-http://localhost:8000}"
MAX_RETRIES="${MAX_RETRIES:-3}"
RETRY_INTERVAL="${RETRY_INTERVAL:-2}"

echo "🏥 Checking health of Accounting AI Assistant at ${API_URL}"

for i in $(seq 1 $MAX_RETRIES); do
    response=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/api/v1/health")
    
    if [ "$response" = "200" ]; then
        echo "✅ Service is healthy"
        
        # Get detailed health
        health_data=$(curl -s "${API_URL}/api/v1/health")
        echo "📊 Health details:"
        echo "$health_data" | python3 -m json.tool 2>/dev/null || echo "$health_data"
        
        exit 0
    else
        echo "⚠️  Attempt $i/$MAX_RETRIES: Health check failed (HTTP $response)"
        
        if [ $i -lt $MAX_RETRIES ]; then
            echo "Retrying in ${RETRY_INTERVAL} seconds..."
            sleep $RETRY_INTERVAL
        fi
    fi
done

echo "❌ Health check failed after $MAX_RETRIES attempts"
exit 1
#!/bin/bash

echo "--- STARTING AUTOMATED TEST SUITE ---"

# 1. Start Background Services
echo "[1/4] Starting Inventory Service..."
python ../inventory_consumer/main.py &
INVENTORY_PID=$!

echo "[2/4] Starting Analytics Service (Run 1)..."
# We redirect output to a file so we can check it later
python ../analytics_consumer/main.py > ../tests/run1_output.txt &
ANALYTICS_PID=$!

# 2. Produce Data
echo "[3/4] Producing 10k Events..."
python ../producer_order/main.py

# Wait for processing to finish (heuristic: wait 10 seconds)
sleep 10
kill $ANALYTICS_PID

# 3. Replay (Reset Offsets)
echo "[4/4] Resetting Offsets for Replay..."
docker-compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group analytics_group_v1 --topic InventoryEvents --reset-offsets --to-earliest --execute

echo "Starting Analytics Service (Run 2 - Replay)..."
python ../analytics_consumer/main.py > ../tests/run2_output.txt &
ANALYTICS_PID_2=$!

# Wait for replay
sleep 10
kill $ANALYTICS_PID_2
kill $INVENTORY_PID

echo "--- TEST SUITE COMPLETE ---"
echo "Check tests/run1_output.txt and tests/run2_output.txt for evidence."
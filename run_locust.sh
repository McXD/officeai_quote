#!/bin/bash

# Define test parameters
CONCURRENT_USERS=(1 10 50 100)  # User levels to test
RUN_TIMES=(1m 2m 3m 5m)  # Corresponding run times for each user level
SPAWN_RATE=5  # Users per second spawn rate
LOCUST_FILE="locustfile.py"  # Locust test file

# Loop through each concurrency level and run Locust
for i in "${!CONCURRENT_USERS[@]}"; do
    USERS="${CONCURRENT_USERS[i]}"
    RUN_TIME="${RUN_TIMES[i]}"
    export N_CU="$USERS"  # Set environment variable
    OUTPUT_FILE="benchmark_results"

    echo "Running Locust test with $USERS concurrent users for $RUN_TIME..."
    
    # Run Locust in headless mode and save results to CSV
    locust -f "$LOCUST_FILE" --headless -u "$USERS" -r "$SPAWN_RATE" --run-time "$RUN_TIME" --csv "$OUTPUT_FILE" > /dev/null 2>&1

    echo "Test with $USERS users completed"
    
    # Wait for 10 seconds before starting the next test
    sleep 3
    
    # Unset the environment variable to avoid unintended carry-over
    unset N_CU

done

echo "All tests completed!"

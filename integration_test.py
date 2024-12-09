import os
import subprocess
import time
from datetime import datetime
from client import TranslationClient
import requests
import sseclient

#Start the server
server_process = subprocess.Popen(["uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000"])
time.sleep(2)  #Wait for the server to start

try:
    client = TranslationClient("http://127.0.0.1:8000/status")

    #Step 1: Call get_status once (should return 'pending')
    print("\nStep 1: Testing get_status function:")
    status, timestamp = client.get_status()
    print(f"Initial Status: {status}, Timestamp: {timestamp}")
    assert status == "pending", "Initial status should be 'pending'"

    #Step 2: Monitor until 'completed' and calculate delay
    print("\nStep 2: Monitoring for status 'completed' and calculating delay:")

    #Use a dictionary to store timestamps
    timestamps = {"server_completed_time": None, "client_completed_time": None}

    def monitoring():
        response = requests.get(client.server_url, stream=True)
        client_sse = sseclient.SSEClient(response)

        for event in client_sse.events():
            event_data = eval(event.data)
            status = event_data["status"]
            timestamp = event_data["timestamp"]

            print(f"Monitoring Update: Status: {status}, Timestamp: {timestamp}")

            if status == "completed":
                timestamps["server_completed_time"] = timestamp  #Server's 'completed' timestamp
                timestamps["client_completed_time"] = time.time()  #Client's received time
                print("Processing completed!")
                break

    #Perform monitoring
    monitoring()

    #Calculate and display the delay
    server_completed_time = timestamps["server_completed_time"]
    client_completed_time = timestamps["client_completed_time"]

    print(f"Server 'completed' Timestamp: {server_completed_time}")
    print(f"Client Received 'completed' Timestamp: {client_completed_time}")
    delay = client_completed_time - server_completed_time
    print(f"Calculated Delay: {delay:.2f} seconds")

    #Step 3: Call get_status again (should return 'completed')
    print("\nStep 3: Testing get_status function after monitoring:")
    status, timestamp = client.get_status()
    print(f"Final Status: {status}, Timestamp: {timestamp}")
    assert status == "completed", "Final status should be 'completed'"

finally:
    #Stop the server
    server_process.terminate()
    server_process.wait()

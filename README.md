# Translation Client Library with SSE

## Overview

This solution assumes the server can be improved to use a **Server-Sent Events (SSE)** architecture, and the client library is designed for monitoring the real-time status of a simulated translation process.

The solution is designed to address the inefficiencies of traditional polling mechanisms while ensuring robust real-time communication.

---

## Features

1. **Real-Time Status Monitoring**:
The server streams status updates (`pending` and `completed`) to the client in real-time.

Each status includes a precise timestamp of when the status was generated.

2. **Easy Usage**:
The "monitor" API can keep monitoring the server and receive updates
with just one API call.

3. **Efficient Communication**:
The use of SSE ensures the client is notified of updates immediately without excessive resource usage.

4. **Thread-Safe Monitoring**:
The client can start real-time monitoring in a separate thread and terminate the monitoring process gracefully.

5. **Timestamp Comparison**:
The system tracks timestamps to calculate the delay between when the server sends the `"completed"` status and when the client processes it.

---

## Why Server-Sent Events (SSE)?

### Benefits of SSE:

1. **One-Way Updates**:
In this scenario, the server only needs to send updates to the client. SSE is ideal for such one-way communication, and for possible future extensions like video processing percentage updates.

2. **Real-Time Requirements**:
The client needs to know the status (`pending` or `completed`) as soon as it changes. SSE streams updates as they happen.

3. **Less Resource Usage**:
Unlike polling, which requires repeated HTTP requests, SSE keeps a single connection open and pushes updates when available, saving bandwidth and server resources.

4. **Built-In Reconnection**:
SSE automatically reconnects if the connection drops, ensuring reliable communication without additional effort.

---

## Why Use Timestamps?

The inclusion of timestamps allows us to:

1. **Track Event Timing**:
Measure the precise time when each status is generated and received.

2. **Calculate Latency**:
Understand the delay between server-side event generation and client-side processing.

3. **Debug Performance**:
Identify bottlenecks in real-time communication in future extensions.
---

## Setup Instructions

### Step 1: Create and Activate a Virtual Environment and install dependencies
1. Install Python 3.8+
2. Create a virtual environment: `python3 -m venv venv`
3. Activate virtual environment:
On Linux/Mac: `source venv/bin/activate`

On Windows: `venv\Scripts\activate`

4. Install dependencies with:
`pip install -r requirements.txt`

### Step 2: Start the Server
1. Run the server to simulate the translation process:
`uvicorn server:app`
    
The server exposes the following endpoint:
    
    GET /status
Streams status updates (pending or completed) with timestamps.
You can view the status updates in a browser by navigating to:
    
    http://127.0.0.1:8000/status

The server defaults to status `pending` at its start, and changes to `completed` after a pre configured period of time. The default configured time is 15 seconds.

## Client Library

### Overview

The TranslationClient class provides methods to interact with the server:

    get_status()

Fetches the current status (pending or completed) along with its timestamp without waiting for completion.

    monitor()
    
Starts monitoring the server in real time until the status changes to completed.

    stop_monitoring()
Stops the ongoing monitoring process.

### How to Use
Import and Initialize the Client

    from client import TranslationClient
    client = TranslationClient("http://127.0.0.1:8000/status")

Fetch Current Status

    status, timestamp = client.get_status()
    print(f"Status: {status}, Timestamp: {timestamp}")

Monitor Until Completion

    client.monitor()

Stop Monitoring

    client.stop_monitoring()


## Running the Tests

### How to Run

Run the integration test with:

    python integration_test.py

### What the Test Does

1. Initial Status Check:
Calls `get_status` once to confirm the initial status is pending.

2. Monitor the Translation Process:
Monitors the status in real time until it changes to `completed`.

3. Calculate the Delay:
Compares the timestamp provided by the server for the `"completed"` status with the client’s timestamp to calculate the delay.

4. Final Status Check:
Calls get_status again to confirm the final status is `completed`.

### Expected Output
You will see log messages for each step, including timestamps and calculated delays. For example:

    Step 1: Testing get_status function:
    INFO:     127.0.0.1:54933 - "GET /status HTTP/1.1" 200 OK
    Current Status: pending, Timestamp: 1733752895.6343958
    Initial Status: pending, Timestamp: 1733752895.6343958

    Step 2: Monitoring for status 'completed' and calculating delay:
    INFO:     127.0.0.1:54934 - "GET /status HTTP/1.1" 200 OK
    Monitoring Update: Status: pending, Timestamp: 1733752895.6343958
    Monitoring Update: Status: completed, Timestamp: 1733752910.6357088
    Processing completed!
    Server 'completed' Timestamp: 1733752910.6357088
    Client Received 'completed' Timestamp: 1733752910.636874
    Calculated Delay: 0.00 seconds

    Step 3: Testing get_status function after monitoring:
    INFO:     127.0.0.1:54940 - "GET /status HTTP/1.1" 200 OK
    Current Status: completed, Timestamp: 1733752910.6357088
    Final Status: completed, Timestamp: 1733752910.6357088

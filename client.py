import sseclient
import requests
import threading
import logging

logging.basicConfig(level=logging.INFO)


class TranslationClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.monitoring_thread = None
        self.stop_event = threading.Event()

    def get_status(self):
        #Fetch the current status from the server without waiting for completion.

        response = requests.get(self.server_url, stream=True)
        client = sseclient.SSEClient(response)

        for event in client.events():
            event_data = eval(event.data)  # Convert string to dictionary
            status = event_data["status"]
            timestamp = event_data["timestamp"]
            print(f"Current Status: {status}, Timestamp: {timestamp}")
            return status, timestamp

    def monitor(self):
        #Start monitoring the server until the status is 'completed'.
        #This runs in a separate thread and can be stopped with stop_monitoring.

        def monitoring():
            response = requests.get(self.server_url, stream=True)
            client = sseclient.SSEClient(response)

            for event in client.events():
                if self.stop_event.is_set():
                    print("Monitoring stopped.")
                    break

                event_data = eval(event.data)  # Convert string to dictionary
                status = event_data["status"]
                timestamp = event_data["timestamp"]
                print(f"Monitoring Update: Status: {status}, Timestamp: {timestamp}")

                if status == "completed":
                    print("Processing completed!")
                    break

        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=monitoring)
        self.monitoring_thread.start()

    def stop_monitoring(self):
        #Stop the ongoing monitoring process.

        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.stop_event.set()
            self.monitoring_thread.join()
            print("Monitoring has been successfully stopped.")

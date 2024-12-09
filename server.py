import os
import time
import asyncio
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse

app = FastAPI()

#Configurable delay before completion (seconds)
DELAY = 15

start_time = time.time()  #Track when the server started
status_start_time = start_time  #Track when the current status started


@app.get("/status")
async def get_status():
    #Serve the current status of the translation process with timestamps.
    #If still pending, hang the connection until the status is completed, using Server-Sent Events (SSE)

    async def event_generator():
        global status_start_time
        elapsed = time.time() - start_time
        if elapsed < DELAY:
            #Send the current status first
            yield {
                "event": "status",
                "data": {"status": "pending", "timestamp": status_start_time},
            }
            #Wait for the DELAY to complete
            await asyncio.sleep(DELAY - elapsed)
            status_start_time = time.time()
        #Once complete, send the updated status
        yield {
            "event": "status",
            "data": {"status": "completed", "timestamp": status_start_time},
        }

    return EventSourceResponse(event_generator())


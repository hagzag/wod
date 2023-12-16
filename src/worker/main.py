from fastapi import FastAPI, HTTPException, Query
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Global variable to store the current number of jobs (should init with 0)
current_job = 0

# Instrument the app
Instrumentator().instrument(app).expose(app)

@app.get("/")
async def health_check():
    # Simple health check endpoint
    return {"status": "OK"}

@app.get("/health")
async def health_check():
    # Simple health check endpoint
    return {"status": "healthy"}

@app.get("/jobs/get")
async def get_job():
    # Returns the current job status
    return {"current_job": current_job}

@app.post("/jobs/set")
async def set_job(count: int, action: str = Query(..., regex="^(set|increase)$")):
    global current_job
    if count < 0:
        raise HTTPException(status_code=400, detail="Count cannot be negative")

    if action == "set":
        current_job = count
    elif action == "increase":
        current_job += count

    return {"current_job": current_job}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")
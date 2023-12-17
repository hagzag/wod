# src/dp/main.py
from fastapi import FastAPI, HTTPException
from .kubernetes import check_readiness, get_kubernetes_deployments, scale_deployment
from starlette_prometheus import PrometheusMiddleware, metrics

app = FastAPI()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

@app.get("/liveness")
async def liveness():
    return {"status": "alive"}

@app.get("/readiness")
async def readiness():
    try:
        return check_readiness()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/workers/available")
# async def workers_available(label_selector: str = "unique-instance-id=worker-0"):

@app.get("/workers/list")
async def list_workers(label_selector: str = "unique-instance-id=worker-0"):
    try:
        return get_kubernetes_deployments(label_selector)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/worker/activate")
async def activate_worker(label_selector: str):
    return scale_deployment(label_selector, 1)

@app.post("/worker/deactivate")
async def deactivate_worker(label_selector: str):
    return scale_deployment(label_selector, 0)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")

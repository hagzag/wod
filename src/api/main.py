# src/dp/main.py
from fastapi import FastAPI, HTTPException
from .kubernetes import check_readiness, list_workers, scale_deployment
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

@app.get("/workers/available")
async def workers_available(label_selector: str = "app.kubernetes.io/instance=keda-po"):
    try:
        return list_workers(label_selector)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workers/{id}/activate")
async def activate_worker(id: str):
    try:
        return scale_deployment(id, 1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workers/{id}/deactivate")
async def deactivate_worker(id: str):
    try:
        return scale_deployment(id, 0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")

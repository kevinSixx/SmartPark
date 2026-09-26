from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="SmartPark AI Worker",
    version="1.0.0"
)


class DetectionRequest(BaseModel):
    device_id: str
    event: str
    distance_cm: float | None = None


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "smartpark-ai"
    }


@app.post("/process")
def process_detection(data: DetectionRequest):
    return {
        "status": "received",
        "message": "AI Worker listo para procesar el vehículo",
        "device_id": data.device_id,
        "event": data.event
    }
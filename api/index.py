from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import json
import numpy as np
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class Payload(BaseModel):
    regions: List[str]
    threshold_ms: int

# Load telemetry from JSON on start
here = os.path.dirname(__file__)
data_path = os.path.join(here, '..', 'q-vercel-latency.json')
with open(data_path, 'r') as f:
    data = json.load(f)

def calc_metrics(region_name, threshold):
    filtered = [x for x in data if x['region'] == region_name]
    if not filtered:
        return None
    latencies = [x['latency_ms'] for x in filtered]
    uptimes = [x['uptime_pct'] for x in filtered]
    breaches = sum(1 for x in latencies if x > threshold)
    return {
        'avg_latency': round(np.mean(latencies), 2),
        'p95_latency': round(np.percentile(latencies, 95), 2),
        'avg_uptime': round(np.mean(uptimes), 3),
        'breaches': breaches
    }

@app.post("/")
async def analytics(payload: Payload):
    metrics = {region: calc_metrics(region, payload.threshold_ms) for region in payload.regions}
    return metrics

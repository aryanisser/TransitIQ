import os
from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, atan2
from typing import Optional, List, Dict, Any
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None

MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "fleet-analytics-tracking-backend")

app = FastAPI(title="FleetIQ Python Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = None
db = None
if MongoClient and MONGODB_URI:
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        db = client[MONGODB_DB]
    except Exception:
        db = None

# fallback demo data, so app works even before MongoDB setup
memory_vehicles: List[Dict[str, Any]] = [
    {"id": "1", "reg": "BR01AB1234", "make": "Tata", "model": "Ace", "year": "2022", "owner": "Aryan Logistics", "status": "Active"},
    {"id": "2", "reg": "BR01CD5678", "make": "Mahindra", "model": "Bolero Pickup", "year": "2021", "owner": "Aryan Logistics", "status": "Active"},
    {"id": "3", "reg": "BR01EF9012", "make": "Ashok Leyland", "model": "Dost", "year": "2020", "owner": "Aryan Logistics", "status": "Maintenance"},
]
memory_locations: List[Dict[str, Any]] = [
    {"id": "l1", "reg": "BR01AB1234", "lat": 25.5941, "lon": 85.1376, "status": "Active", "timestamp": datetime.now(timezone.utc).isoformat(), "speed": 42.0, "alertMessage": None},
    {"id": "l2", "reg": "BR01CD5678", "lat": 25.6090, "lon": 85.1230, "status": "Active", "timestamp": datetime.now(timezone.utc).isoformat(), "speed": 64.0, "alertMessage": None},
    {"id": "l3", "reg": "BR01EF9012", "lat": 25.5810, "lon": 85.1600, "status": "Alert", "timestamp": datetime.now(timezone.utc).isoformat(), "speed": 82.0, "alertMessage": "Speeding detected"},
]

class Vehicle(BaseModel):
    id: Optional[str] = None
    reg: str
    make: str
    model: str
    year: str
    owner: str
    status: str = "Active"

class VehicleLocationRequest(BaseModel):
    reg: str
    lat: float
    lon: float
    status: str = "Active"
    speed: Optional[float] = None
    alertMessage: Optional[str] = None


def clean_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    if isinstance(doc.get("timestamp"), datetime):
        doc["timestamp"] = doc["timestamp"].isoformat()
    return doc


def collection(name: str):
    return db[name] if db is not None else None


def latest_by_reg(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    latest = {}
    for item in items:
        latest[item.get("reg")] = item
    return list(latest.values())


def distance_m(lat1, lon1, lat2, lon2):
    r = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2 * r * atan2(sqrt(a), sqrt(1-a))


def build_alert(lat: float, lon: float, speed: Optional[float]):
    alerts = []
    if speed is not None and speed > 75:
        alerts.append("Speeding detected")
    # demo restricted zone around Patna center
    if distance_m(lat, lon, 25.5941, 85.1376) < 700:
        alerts.append("Restricted zone proximity")
    return " | ".join(alerts) if alerts else None

@app.get("/")
def root():
    return {"message": "FleetIQ Python Backend is running", "database": "MongoDB" if db is not None else "Memory fallback"}

@app.get("/health")
def health():
    return {"status": "ok", "database_connected": db is not None}

@app.post("/api/v1/vehicle")
def add_vehicle(vehicle: Vehicle):
    data = vehicle.model_dump()
    data["id"] = data.get("id") or str(uuid4())
    col = collection("vehicles")
    if col is not None:
        if col.find_one({"reg": data["reg"]}):
            raise HTTPException(status_code=409, detail="Vehicle already exists")
        col.insert_one(data)
        return data
    if any(v["reg"] == data["reg"] for v in memory_vehicles):
        raise HTTPException(status_code=409, detail="Vehicle already exists")
    memory_vehicles.append(data)
    return data

@app.get("/api/v1/vehicle")
def get_all_vehicles():
    col = collection("vehicles")
    if col is not None:
        return [clean_doc(x) for x in col.find({})]
    return memory_vehicles

@app.get("/api/v1/vehicle/{reg}")
def get_vehicle_by_reg(reg: str):
    col = collection("vehicles")
    if col is not None:
        doc = col.find_one({"reg": reg})
        if not doc:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return clean_doc(doc)
    for v in memory_vehicles:
        if v["reg"] == reg:
            return v
    raise HTTPException(status_code=404, detail="Vehicle not found")

@app.delete("/api/v1/vehicle/{id}")
def delete_vehicle(id: str):
    col = collection("vehicles")
    if col is not None:
        col.delete_one({"id": id})
        return {"message": "Vehicle deleted"}
    global memory_vehicles
    memory_vehicles = [v for v in memory_vehicles if v.get("id") != id]
    return {"message": "Vehicle deleted"}

@app.post("/api/v1/vehicle/location")
def add_vehicle_location(req: VehicleLocationRequest):
    data = req.model_dump()
    data["id"] = str(uuid4())
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    if not data.get("alertMessage"):
        data["alertMessage"] = build_alert(data["lat"], data["lon"], data.get("speed"))
    if data["alertMessage"]:
        data["status"] = "Alert"

    col = collection("vehicle_tracking_data")
    if col is not None:
        col.insert_one(dict(data))
    else:
        memory_locations.append(data)
    return data

@app.get("/api/v1/vehicle/location")
def get_vehicle_locations():
    col = collection("vehicle_tracking_data")
    if col is not None:
        docs = [clean_doc(x) for x in col.find({}).sort("timestamp", 1)]
        return latest_by_reg(docs)
    return latest_by_reg(memory_locations)

@app.get("/api/v1/vehicle/location/history/{reg}")
def get_vehicle_location_history(reg: str):
    col = collection("vehicle_tracking_data")
    if col is not None:
        locs = [clean_doc(x) for x in col.find({"reg": reg}).sort("timestamp", 1)]
    else:
        locs = [x for x in memory_locations if x.get("reg") == reg]
    return {"reg": reg, "locations": locs}

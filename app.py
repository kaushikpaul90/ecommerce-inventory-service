from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import os
import httpx

app = FastAPI(title="Inventory Service")

# Base URL of the Database microservice
# DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://localhost:8000")
DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://192.168.105.2:30000")

# ---------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------
class Item(BaseModel):
    sku: str
    qty: int

class Reservation(BaseModel):
    id: str
    orderId: str
    items: List[Item]
    status: str

class Stock(BaseModel):
    sku: str
    quantity: int

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
async def db_request(method: str, path: str, json: Optional[dict] = None) -> dict:
    url = f"{DATABASE_SERVICE_URL}{path}"
    
    # Increase read timeout so slow-but-working DB calls won't fail fast.
    # Arguments: overall timeout, connect timeout
    # Adjust numbers if your environment needs more time.
    timeout = httpx.Timeout(30.0, connect=10.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.request(method, url, json=json)
    except httpx.ConnectTimeout:
        # Could not establish TCP connection within connect timeout
        raise HTTPException(status_code=504, detail=f"Timeout connecting to database service at {url}")
    except httpx.ReadTimeout:
        # Connected but server did not send response within read timeout
        raise HTTPException(status_code=504, detail=f"Timeout reading response from database service at {url}")
    except httpx.NetworkError as e:
        # Generic network error (DNS, resets, etc.)
        raise HTTPException(status_code=502, detail=f"Network error contacting database service at {url}: {e}")

    # Propagate HTTP errors from DB service with its details (400/404/500 etc.)
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    # Return parsed JSON or empty dict for no-content
    return resp.json() if resp.content else {}

# ---------------------------------------------------------------------
# Health & seed endpoints
# ---------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "Inventory Service"}

@app.post("/admin/seed")
async def seed():
    """Seed a few SKUs into the database"""
    sample_stock = [
        {"sku": "SKU-001", "quantity": 100},
        {"sku": "SKU-002", "quantity": 250},
        {"sku": "SKU-003", "quantity": 500},
    ]
    for s in sample_stock:
        await db_request("POST", "/inventory", json=s)
    return {"seeded": True, "stock": sample_stock}

# ---------------------------------------------------------------------
# Reservation flow
# ---------------------------------------------------------------------
@app.post("/reserve", response_model=Reservation)
async def reserve(payload: dict):
    """Reserve stock for an order."""
    order_id = payload.get("orderId")
    items = payload.get("items", [])
    if not items:
        raise HTTPException(400, detail="No items to reserve")

    # # Validate availability for each SKU
    # for it in items:
    #     sku, qty = it["sku"], int(it["qty"])
    #     try:
    #         inv = await db_request("GET", f"/inventory/{sku}")
    #     except HTTPException as e:
    #         if e.status_code == 404:
    #             raise HTTPException(409, detail=f"SKU {sku} not found")
    #         raise
    #     if inv["quantity"] < qty:
    #         raise HTTPException(409, detail=f"Insufficient stock for {sku}")

    # Create reservation in DB
    rid = str(uuid.uuid4())
    reservation = {
        "id": rid,
        "orderId": order_id,
        "items": items,
        "status": "reserved",
    }
    res = await db_request("POST", "/inventory/reserve", json=reservation)
    return {
        "id": res.get("id", rid),
        "orderId": res.get("orderId", order_id),
        "items": res.get("items", items),
        "status": res.get("status", "reserved")
    }

@app.post("/reservations/{rid}/commit")
async def commit(rid: str):
    """Commit reservation: decrement inventory and mark reservation completed."""
    # Fetch reservation from DB
    res = await db_request("GET", f"/inventory/reserve/{rid}")
    if not res:
        raise HTTPException(404, detail="Reservation not found")

    # # Decrement inventory
    # for it in res["items"]:
    #     sku, qty = it["sku"], int(it["qty"])
    #     inv = await db_request("GET", f"/inventory/{sku}")
    #     new_qty = max(inv["quantity"] - qty, 0)
    #     await db_request("PUT", f"/inventory/{sku}", json={"sku": sku, "quantity": new_qty})

    # Update reservation status
    res["status"] = "committed"
    await db_request("PUT", f"/inventory/reserve/{rid}", json=res)
    return {"committed": True, "reservation": rid}

@app.post("/reservations/{rid}/release")
async def release(rid: str):
    """Release a reservation (no inventory change)."""
    try:
        res = await db_request("GET", f"/inventory/reserve/{rid}")
    except HTTPException as e:
        if e.status_code == 404:
            return {"released": True, "idempotent": True}
        raise
    res["status"] = "released"
    await db_request("PUT", f"/inventory/reserve/{rid}", json=res)
    return {"released": True}

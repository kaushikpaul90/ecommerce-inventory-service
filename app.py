
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import uuid

app = FastAPI(title="Inventory Service")

class Stock(BaseModel):
    sku: str
    total: int

class Item(BaseModel):
    sku: str
    qty: int

class Reservation(BaseModel):
    id: str
    items: List[Item]
    orderId: str

STOCK: Dict[str, int] = {}
RESERVATIONS: Dict[str, Reservation] = {}

@app.get("/health")
def health():
    return {"status": "ok", "service": "Inventory Service"}

@app.post("/admin/seed")
def seed():
    STOCK["SKU-001"] = 10
    STOCK["SKU-002"] = 25
    return {"seeded": True, "stock": STOCK}

@app.post("/reserve", response_model=Reservation)
def reserve(payload: dict):
    order_id = payload.get("orderId")
    items = [Item(**it) for it in payload.get("items", [])]
    if not items:
        raise HTTPException(400, detail="No items to reserve")

    # Check availability considering current reservations
    # effective_available = total - sum(reserved for sku)
    reserved_by_sku: Dict[str, int] = {}
    for r in RESERVATIONS.values():
        for it in r.items:
            reserved_by_sku[it.sku] = reserved_by_sku.get(it.sku, 0) + it.qty

    for it in items:
        total = STOCK.get(it.sku, 0)
        reserved = reserved_by_sku.get(it.sku, 0)
        effective = total - reserved
        if effective < it.qty:
            raise HTTPException(409, detail=f"Insufficient stock for {it.sku}")

    rid = str(uuid.uuid4())
    res = Reservation(id=rid, items=items, orderId=order_id)
    RESERVATIONS[rid] = res
    return res

@app.post("/reservations/{rid}/commit")
def commit(rid: str):
    res = RESERVATIONS.get(rid)
    if not res:
        raise HTTPException(404, detail="Reservation not found")
    # Decrement stock and remove reservation
    for it in res.items:
        STOCK[it.sku] = STOCK.get(it.sku, 0) - it.qty
    RESERVATIONS.pop(rid, None)
    return {"committed": True}

@app.post("/reservations/{rid}/release")
def release(rid: str):
    res = RESERVATIONS.pop(rid, None)
    if not res:
        # idempotent
        return {"released": True, "idempotent": True}
    return {"released": True}

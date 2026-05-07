import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from classifier import classify_friction, should_intervene

app = FastAPI()

# Allow requests from Shopify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CheckoutEvent(BaseModel):
    cart: dict
    signals: dict

@app.post("/analyze")
async def analyze(event: CheckoutEvent):
    result = classify_friction(event.cart, event.signals)
    result["should_intervene"] = should_intervene(result)
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}
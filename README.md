# Checkout Recovery — AI-Assisted Checkout Intervention

**Kasparro Agentic Commerce Hackathon — Track 2**  
**Team:** Rohit Prasad  

---

## Demo Video
https://youtu.be/6A7PX_2dBaY

## Live Backend
https://checkout-recovery.onrender.com/docs

---

## What It Does

An AI system that silently observes buyer behavior on the checkout page, detects the specific reason they are hesitating, and delivers one targeted message to remove the blocker — before they abandon.

Cart abandonment costs Shopify merchants billions every year. 70% of buyers who start a checkout never complete it. Current solutions send a follow-up email hours after the buyer has already left. This system intervenes in real time — while the buyer is still on the page, still warm, still one good answer away from completing the purchase.

---

## How It Works
Buyer lands on checkout page
↓
Observer (widget.js) silently tracks behavior

Time on page
Which elements are hovered (shipping, total, payment, size)
Coupon field clicks
Back button usage
Payment section visibility
↓
Trigger condition met (45s idle / shipping hovered 2x / coupon clicked / etc.)
↓
Signals sent to FastAPI backend on Render
↓
Rule-based pre-filter checks signal strength
↓
LLM (Llama 3.3 70B) classifies friction type + generates intervention message
↓
If confidence > 0.6 → intervention card appears bottom-right
↓
Buyer reads message → friction resolved → purchase completed


---

## Friction Types Detected

| Type | Signal | Example Intervention |
|---|---|---|
| Shipping confusion | Hovered shipping cost 2+ times | "Standard delivery takes 3-5 days and costs $19.95. Orders above $100 ship free." |
| Price hesitation | Clicked coupon field / hovered total 2x | "This is our best price. Free returns within 30 days." |
| Trust gap | Reached payment section then hit back | "All payments secured with 256-bit encryption. Full refund within 30 days." |
| Variant uncertainty | Hovered size chart / removed items | "Not sure about the size? We offer free exchanges." |
| General confusion | Long idle time with no clear signal | "You're almost there — just fill in your shipping address." |

---

## Tech Stack

- **Frontend:** Vanilla JavaScript (widget.js) — zero dependencies
- **Backend:** Python, FastAPI, Uvicorn
- **AI:** Llama 3.3 70B via OpenRouter API
- **Hosting:** Render.com (backend), Shopify CDN (widget)
- **Store:** Shopify development store

---

## Project Structure
checkout-recovery/
├── backend/
│   ├── classifier.py      # Core AI friction classification
│   ├── main.py            # FastAPI API server
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── widget.js          # Observer + intervention widget
│   └── test.html          # Local checkout test page
├── docs/
│   ├── product-document.md
│   ├── technical-document.md
│   └── decision-log.md
└── README.md

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- An OpenRouter API key (free at openrouter.ai)

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` folder:
OPENROUTER_API_KEY=your_key_here

Start the server:
```bash
python -m uvicorn main:app --reload
```

Backend runs at `http://127.0.0.1:8000`  
API docs at `http://127.0.0.1:8000/docs`

### Frontend

```bash
cd frontend
python -m http.server 3000
```

Open `http://localhost:3000/test.html` in your browser.

Hover over the shipping cost twice to trigger the intervention.

---

## API Reference

### POST /analyze

**Request:**
```json
{
  "cart": {
    "items": [{"name": "Product Name", "price": 729.95, "quantity": 1}],
    "subtotal": 729.95,
    "shipping_cost": 19.95,
    "total": 749.90
  },
  "signals": {
    "time_on_page_seconds": 75,
    "hovered_on": ["shipping_cost", "shipping_cost", "total"],
    "payment_reached": false,
    "back_button_clicked": false,
    "coupon_field_clicked": false,
    "items_removed": false
  }
}
```

**Response:**
```json
{
  "friction_type": "shipping_confusion",
  "confidence": 0.85,
  "reasoning": "Buyer hovered over shipping cost twice indicating uncertainty about delivery cost",
  "intervention": "Standard delivery takes 3-5 days and costs $19.95. Orders above $100 ship free.",
  "should_intervene": true
}
```

### GET /health

Returns `{"status": "ok"}` — used for uptime monitoring.

---

## Key Design Decisions

**No chatbot.** One precise message removes friction faster than any conversation.

**Behavioral signals, not surveys.** We infer what the buyer is worried about from what they do, not what they say.

**Confidence threshold.** If confidence is below 0.6, nothing is shown. Wrong interventions are worse than no intervention.

**Fail silently.** If the backend is unavailable, the checkout continues unaffected. Nothing we build should ever interrupt the purchase flow.

---

## Documentation

- [Product Document](docs/product-document.md) — problem, target user, decisions, tradeoffs
- [Technical Document](docs/technical-document.md) — architecture, AI design, failure handling
- [Decision Log](docs/decision-log.md) — key decisions made during the build

---

## Contribution Note

group submission. Product thinking, architecture design, and engineering were done by Rohit Prasad and anushka arya together. Time split approximately 40% product thinking and documentation, 60% engineering and implementation.
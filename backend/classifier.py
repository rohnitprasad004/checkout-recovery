import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

SYSTEM_PROMPT = """
You are a checkout friction analyst for an ecommerce store.
A buyer is hesitating on the checkout page.
Analyze ALL signals together and identify the single most likely friction type.

FRICTION TYPE DECISION RULES:

1. trust_gap:
   - payment_reached=true AND back_button_clicked=true
   - Buyer got to payment, got scared, and retreated
   - This overrides everything else

2. price_hesitation:
   - coupon_field_clicked=true (looking for discount)
   - OR back_button_clicked=true AND hovered_on contains "total" or "price"
   - OR time_on_page_seconds > 100 AND hovered_on contains "total" multiple times

3. shipping_confusion:
   - hovered_on contains "shipping_cost" two or more times
   - AND payment_reached=false
   - AND coupon_field_clicked=false

4. variant_uncertainty:
   - items_removed=true OR hovered_on contains "size" or "color" or "variant"

5. general_confusion:
   - None of the above patterns match
   - High time on page with no clear signal

INTERVENTION RULES:
- trust_gap: reassure with return policy and security, do not ask a question
- price_hesitation: show value or mention free shipping threshold, do not offer discount
- shipping_confusion: give exact delivery estimate and cost, be specific to their cart
- variant_uncertainty: reassure about sizing or returns
- general_confusion: simplify with one clear next step

INTERVENTION STYLE:
- Sound human, not like a bot
- Be specific to the cart items and amounts
- One sentence or two max
- Never say "I" or "we" — speak as the store
- Never ask more than one question

Respond ONLY with valid JSON and nothing else. No backticks. No explanation outside the JSON.
{
  "friction_type": "one of the 5 types",
  "confidence": 0.0 to 1.0,
  "reasoning": "one sentence citing the specific signals that led to this classification",
  "intervention": "exact message to show the buyer"
}
"""

def extract_json(text: str) -> dict:
    text = text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    print(f"WARNING: Could not parse JSON from model output: {text[:200]}")
    return {
        "friction_type": "general_confusion",
        "confidence": 0.0,
        "reasoning": "Could not parse model response",
        "intervention": ""
    }


def classify_friction(cart: dict, signals: dict) -> dict:

    # Rule-based pre-filter — don't call AI if signals are too weak
    time_on_page = signals.get("time_on_page_seconds", 0)
    hovered = signals.get("hovered_on", [])
    back_clicked = signals.get("back_button_clicked", False)
    coupon_clicked = signals.get("coupon_field_clicked", False)
    payment_reached = signals.get("payment_reached", False)
    items_removed = signals.get("items_removed", False)

    has_strong_signal = (
        time_on_page > 45 or
        len(hovered) >= 2 or
        back_clicked or
        coupon_clicked or
        payment_reached or
        items_removed
    )

    if not has_strong_signal:
        return {
            "friction_type": "general_confusion",
            "confidence": 0.0,
            "reasoning": "Insufficient signals to classify friction",
            "intervention": ""
        }

    prompt = f"""
Cart contents:
{json.dumps(cart, indent=2)}

Buyer behavior signals:
{json.dumps(signals, indent=2)}

Classify the friction type and generate the intervention message.
"""

    try:
        response = client.chat.completions.create(
            model="liquid/lfm-2.5-1.2b-instruct:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        text = response.choices[0].message.content
        result = extract_json(text)

        # Validate required fields
        required = ["friction_type", "confidence", "reasoning", "intervention"]
        for field in required:
            if field not in result:
                result[field] = "" if field != "confidence" else 0.0

        # Validate friction type
        valid_types = [
            "shipping_confusion", "price_hesitation",
            "trust_gap", "variant_uncertainty", "general_confusion"
        ]
        if result["friction_type"] not in valid_types:
            result["friction_type"] = "general_confusion"

        # Validate confidence is a float
        try:
            result["confidence"] = float(result["confidence"])
        except (ValueError, TypeError):
            result["confidence"] = 0.0

        return result

    except Exception as e:
        print(f"ERROR calling model: {e}")
        return {
            "friction_type": "general_confusion",
            "confidence": 0.0,
            "reasoning": f"Model error: {str(e)}",
            "intervention": ""
        }


def should_intervene(result: dict, threshold: float = 0.6) -> bool:
    return (
        result["confidence"] >= threshold and
        result["intervention"] != "" and
        result["friction_type"] != "general_confusion"
    )


if __name__ == "__main__":

    test_cases = [
        {
            "name": "Test 1 - Shipping confusion",
            "cart": {
                "items": [{"name": "Running Shoes", "price": 2499, "quantity": 1}],
                "subtotal": 2499,
                "shipping_cost": 199,
                "total": 2698
            },
            "signals": {
                "time_on_page_seconds": 75,
                "hovered_on": ["shipping_cost", "shipping_cost", "total"],
                "payment_reached": False,
                "back_button_clicked": False,
                "coupon_field_clicked": False,
                "items_removed": False
            }
        },
        {
            "name": "Test 2 - Price hesitation",
            "cart": {
                "items": [{"name": "Wireless Headphones", "price": 4999, "quantity": 1}],
                "subtotal": 4999,
                "shipping_cost": 0,
                "total": 4999
            },
            "signals": {
                "time_on_page_seconds": 120,
                "hovered_on": ["total", "total", "price"],
                "payment_reached": False,
                "back_button_clicked": True,
                "coupon_field_clicked": True,
                "items_removed": False
            }
        },
        {
            "name": "Test 3 - Trust gap",
            "cart": {
                "items": [{"name": "Leather Wallet", "price": 1299, "quantity": 1}],
                "subtotal": 1299,
                "shipping_cost": 99,
                "total": 1398
            },
            "signals": {
                "time_on_page_seconds": 90,
                "hovered_on": ["payment_section", "security_badge"],
                "payment_reached": True,
                "back_button_clicked": True,
                "coupon_field_clicked": False,
                "items_removed": False
            }
        },
        {
            "name": "Test 4 - Variant uncertainty",
            "cart": {
                "items": [{"name": "Cotton T-Shirt", "price": 799, "quantity": 1, "variant": "M"}],
                "subtotal": 799,
                "shipping_cost": 99,
                "total": 898
            },
            "signals": {
                "time_on_page_seconds": 60,
                "hovered_on": ["size_chart", "variant", "color"],
                "payment_reached": False,
                "back_button_clicked": False,
                "coupon_field_clicked": False,
                "items_removed": True
            }
        },
        {
            "name": "Test 5 - Low confidence (should NOT intervene)",
            "cart": {
                "items": [{"name": "Book", "price": 299, "quantity": 1}],
                "subtotal": 299,
                "shipping_cost": 49,
                "total": 348
            },
            "signals": {
                "time_on_page_seconds": 20,
                "hovered_on": [],
                "payment_reached": False,
                "back_button_clicked": False,
                "coupon_field_clicked": False,
                "items_removed": False
            }
        }
    ]

    for test in test_cases:
        print(f"\n{test['name']}:")
        result = classify_friction(test["cart"], test["signals"])
        print(json.dumps(result, indent=2))
        intervene = should_intervene(result)
        print(f"→ Should intervene: {intervene}")
        if intervene:
            print(f"→ Show message: \"{result['intervention']}\"")
        print("-" * 50)
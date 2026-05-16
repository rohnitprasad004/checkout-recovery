Technical Document - AI-Assisted Checkout Recovery
Project: AI-Assisted Checkout Recovery
Track: Track 2 - Kasparro Agentic Commerce Hackathon
Team: Rohit Prasad
Date: May 2026

1. System Architecture
1.1 High-Level Overview
The system has three components working together to detect buyer hesitation and deliver targeted interventions in real time.
The buyer browser runs widget.js which silently observes behavior and sends signals to the backend. The backend runs on Render.com as a FastAPI service - it applies a rule-based pre-filter, calls the LLM via OpenRouter, and returns a classified friction type with an intervention message. The LLM (Llama 3.3 70B) receives cart context and behavioral signals, classifies friction, generates the intervention message, and returns structured JSON.
1.2 Component Breakdown
ComponentTechnologyHostingPurposewidget.jsVanilla JavaScriptShopify CDNObserver and Intervenermain.pyFastAPI PythonRender.comAPI gatewayclassifier.pyPython and OpenAI SDKRender.comFriction classificationLLMLlama 3.3 70BOpenRouter cloudAI inferenceStoreShopifyShopify cloudEcommerce platformCodeGitGitHubVersion control
1.3 Data Flow
Step 1: Buyer lands on checkout or cart page.
Step 2: widget.js loads, observer starts silently tracking signals.
Step 3: Buyer behavior detected - hover, click, idle time, back button usage.
Step 4: Trigger condition met - widget sends POST to /analyze with cart and signals.
Step 5: FastAPI receives request, calls classify_friction().
Step 6: Pre-filter checks signal strength - if weak, returns early with confidence 0.0, no LLM called.
Step 7: LLM prompt constructed with cart contents and behavioral signals.
Step 8: OpenRouter API called, Llama 3.3 70B responds with structured JSON.
Step 9: Response parsed, validated, returned to widget.
Step 10: Widget checks confidence threshold - if below 0.6, nothing shown.
Step 11: If confidence above 0.6, showWidget() renders the intervention card.
Step 12: Card appears bottom-right, auto-dismisses after 10 seconds.

2. Frontend: widget.js
2.1 Architecture
The widget is a self-executing IIFE (Immediately Invoked Function Expression) that encapsulates all state and logic. It injects no global variables and does not interfere with Shopify own JavaScript or third-party scripts on the page.
This containment pattern is critical for a Shopify theme script - it must not conflict with anything Shopify or the merchant has already loaded.
2.2 Signal Collection
Time on page: A counter incremented every second using setInterval. Used to detect idle hesitation and as context for the LLM.
Element hover tracking: Multiple CSS selectors target shipping cost, total price, payment section, coupon field, size chart, and variant selector across common Shopify theme patterns. When the cursor enters any matching element, its label is pushed to the hoveredElements array. This gives the classifier a record of exactly what the buyer was looking at.
Coupon field click: A direct click event listener on the discount input. Clicking this field is a strong price hesitation signal - the buyer is actively looking for a way to pay less. This triggers immediate analysis without waiting for the 45-second timer.
Back button detection: The browser popstate event fires when the buyer navigates backward. When combined with paymentReached being true, this is the strongest trust gap signal in our system - the buyer reached payment and retreated.
Payment section visibility: An IntersectionObserver fires when the payment section enters the viewport. This passively sets a flag. The back button event is what triggers analysis.
Cart item removal: The itemsRemoved flag is set when cart manipulation events are detected, indicating the buyer is uncertain about their product choice.
2.3 Trigger Logic
Analysis fires immediately on strong signals: coupon field clicked, back button clicked after payment viewed, or shipping cost hovered two or more times.
Analysis fires on the 45-second timer for buyers who are quietly hesitating without obvious behavioral signals.
The widgetShown flag prevents multiple interventions per session. Once set to true, all subsequent trigger conditions are ignored. One intervention per checkout session, maximum.
2.4 Failure Handling
The entire fetch call is wrapped in try-catch. Network errors, backend timeouts, CORS issues, rate limit responses - all fall into the catch block, which logs a console warning and returns silently. No error UI is shown. The checkout continues as if our widget does not exist.
The checkout page is where the merchant revenue is collected. Nothing we build should ever interrupt that flow.
2.5 Intervention Card
The card is injected with inline styles to ensure correct rendering regardless of page CSS. Position fixed means it appears regardless of scroll position. It includes a friction-type icon, the AI-generated message, and a dismiss button. Auto-dismiss fires after 10 seconds.

3. Backend: FastAPI and Classifier
3.1 API Endpoints
POST /analyze receives cart and signals, runs classify_friction(), and returns friction_type, confidence, reasoning, intervention, and should_intervene.
GET /health returns status ok. Used for deployment verification and uptime monitoring.
3.2 CORS Configuration
CORS is set to allow all origins because the widget runs on Shopify domain, which differs from our Render backend domain. The browser same-origin policy would block the widget fetch call without CORS headers. In production this would be restricted to known Shopify store domains.
3.3 The Classifier: Three Stages
Stage 1: Rule-based pre-filter
Before any LLM API call, the classifier evaluates signal strength:
has_strong_signal is true when time on page exceeds 45 seconds, OR hovered elements count is 2 or more, OR back button was clicked, OR coupon was clicked, OR payment was reached, OR items were removed.
If no strong signal, return immediately with confidence 0.0. No LLM call is made. This saves API cost and prevents false positives.
Stage 2: LLM Classification
The system prompt provides an explicit decision tree rather than vague instructions. This is critical for models that default to one output without guidance:
trust_gap fires when payment was reached AND back button was clicked - this overrides everything else.
price_hesitation fires when coupon was clicked, or back button with price/total hover signals.
shipping_confusion fires when shipping cost was hovered multiple times without payment reached.
variant_uncertainty fires when items were removed or size/variant elements were hovered.
general_confusion is the fallback when no pattern matches clearly.
Temperature is set to 0.3 for consistent structured outputs.
Stage 3: Output Validation
Every field is validated. Invalid friction types default to general_confusion. Non-float confidence values default to 0.0. Required fields are defaulted if missing. The API always returns a valid predictable response regardless of LLM output.
3.4 JSON Extraction Robustness
LLMs sometimes wrap JSON in markdown code blocks despite instructions. extract_json() first strips markdown fences and attempts direct parsing. If that fails, regex finds any JSON object in the text. If both fail, a safe fallback with confidence 0.0 is returned.
3.5 should_intervene() Logic
Three conditions must all be true: confidence at or above 0.6, non-empty intervention message, and friction type is not general_confusion.
We explicitly exclude general_confusion even at high confidence - messages for that type are too vague to be genuinely helpful. Better silent than generic.

4. AI Design Decisions
4.1 Where AI Draws the Line
Clear boundary between AI decisions and deterministic code decisions.
AI decides: which friction type best matches the signals, what specific message to show, and how confident it is.
Deterministic code decides: whether signals are strong enough to call AI, whether to show the intervention based on the confidence threshold, how long to display the card, and whether to allow another intervention this session.
LLMs are probabilistic and can be confidently wrong. Binary decisions with clear correct answers belong in code. Decisions requiring language understanding and contextual reasoning belong in the LLM.
4.2 Prompt Engineering Principles
Explicit rules over implicit reasoning: we give the model a decision tree mapping signal combinations to friction types, not a vague instruction to figure out what is wrong. This makes outputs predictable, auditable, and correctable.
JSON-first output: the model is instructed to respond only with valid JSON. We strip markdown fences as a safety net. Structured output is non-negotiable.
Encoded product judgment: the prompt instructs the model not to offer discounts for price hesitation (this trains buyers to abandon deliberately), not to ask more than one question, and to sound like a helpful store rather than a bot. Product decisions encoded into AI behavior.
4.3 Model Choice: Llama 3.3 70B
Chosen because it is the largest freely available model on OpenRouter at build time, follows structured output instructions reliably, and is instruction-tuned making it responsive to explicit decision rules.
Smaller models (3B, 8B) were tested and rejected. They defaulted to shipping_confusion regardless of signals and could not reliably follow the decision tree. The 70B model could.
The openai Python SDK is used because OpenRouter is OpenAI API-compatible. Switching to GPT-4o or Claude requires changing one environment variable and one model string, no code changes.
4.4 Failure Mode Handling
LLM API timeout: exception caught, safe fallback returned, no intervention shown.
Malformed JSON response: extract_json() regex fallback, then safe fallback with confidence 0.0.
Invalid friction type in response: validation step defaults to general_confusion.
Backend unreachable from widget: fetch exception caught, console warning logged, no UI change.
Backend cold start slow response: widget does not block - if buyer navigates away before response, nothing shown.
OpenRouter rate limit: exception caught in classifier, safe fallback returned.

5. Infrastructure and Deployment
5.1 Backend on Render.com
Runtime: Python 3. Root directory: backend/. Build command: pip install -r requirements.txt. Start command: uvicorn main:app --host 0.0.0.0 --port . Instance type: free tier, 512MB RAM, 0.1 CPU.
Known limitation: Free tier spins down after 15 minutes of inactivity. First request after cold start takes 30-50 seconds. Production would use paid tier at /month.
5.2 Frontend on Shopify Theme
widget.js is uploaded to the theme assets folder and served from Shopify CDN. A script tag is added to layout/theme.liquid just before the closing body tag.
Known limitation: Shopify native checkout runs on a separate Shopify-controlled domain. Theme-injected scripts cannot observe behavior or inject UI there. The widget works on cart and product pages. Native checkout integration requires Shopify Checkout UI Extensions API, which requires a full public app with OAuth and app review.
5.3 Dependencies
Backend: fastapi, uvicorn, python-dotenv, openai, pydantic. No database, no cache, no message queue. Stateless by design.
Frontend: zero dependencies. Vanilla JavaScript only. Single self-contained file, loads in any browser.
5.4 Repository Structure

6. Security
API key management: All keys stored as environment variables, never hardcoded. .env is gitignored. Production keys stored in Render encrypted environment variable storage, never exposed in logs or responses.
Data handling: The system stores no buyer data. Every call is stateless. No personal information - name, email, address, payment data - is ever sent to our backend. Only cart contents (product names and prices) and behavioral signals (hover counts, time on page, boolean flags) are processed.
Checkout safety: All backend calls are async and non-blocking. All errors caught silently. The widget adds no required steps to checkout. Can be removed by deleting one script tag from theme.liquid.
CORS: Currently open to all origins for development. Production deployment restricts to known Shopify domains.

7. Testing
7.1 Classifier Unit Tests (5 Scenarios)
Shipping confusion - hovered shipping 2x, 75s on page: classified correctly, confidence 0.85, should intervene true.
Price hesitation - coupon clicked, back button, 120s: classified correctly, confidence 0.95, should intervene true.
Trust gap - payment reached, back button clicked: classified correctly, confidence 0.95, should intervene true.
Variant uncertainty - items removed, hovered size chart: classified correctly, confidence 0.85, should intervene true.
Low signal - 20s on page, no interactions: pre-filter triggered, confidence 0.0, should intervene false, no LLM call made.
7.2 API Integration Testing
Tested via FastAPI auto-generated documentation at /docs with valid inputs, invalid inputs, and edge cases to verify error handling and response structure.
7.3 End-to-End Testing
Full flow tested using frontend/test.html with labeled interactive elements and a real-time signal log. Confirmed: observer correctly detects hover events, backend receives and processes signals, widget appears with correct friction type icon and message, widget auto-dismisses after 10 seconds, widget cannot appear more than once per session, and backend unavailability does not affect page behavior.

8. What We Would Improve With More Time
Shopify Checkout UI Extensions: Implementing native checkout integration is the single highest-impact improvement. It would allow observing buyer behavior on the actual payment page where highest-value hesitation occurs.
Per-merchant configuration: Each store has different products, shipping rates, and return policies. Intervention messages would be more accurate and specific if they referenced actual store data via the Admin API.
Logging and feedback loop: Currently no logging of whether interventions lead to completed purchases. A production system would track every intervention outcome and use that data to improve classification accuracy.
Model upgrade: Production would use GPT-4o or Claude 3.5 Sonnet with a paid API for improved classification accuracy and message quality.
A/B testing infrastructure: Measuring actual impact on conversion rates requires session tracking, persistent storage, and statistical analysis. Natural next step after validating the core intervention logic.
Multi-merchant support: Production requires Shopify OAuth for merchant onboarding, per-merchant configuration, and multi-tenant data isolation in the backend.
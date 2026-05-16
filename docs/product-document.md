# Product Document — AI-Assisted Checkout Recovery

**Project:** AI-Assisted Checkout Recovery  
**Track:** Track 2 — Kasparro Agentic Commerce Hackathon  
**Team:** Rohit Prasad  
**Date:** May 2026

---

## 1. The Problem

### 1.1 Cart Abandonment is Ecommerce's Biggest Unsolved Problem

Cart abandonment is not a niche edge case. It is the default outcome of most checkout attempts. Industry data consistently shows that approximately 70% of buyers who initiate a checkout never complete it. For every 10 people who add a product to their cart and start the checkout process, 7 leave without buying.

This is not a small inconvenience. For a Shopify merchant doing $10,000 per month in completed revenue, the math looks like this:

- Completed revenue: $10,000
- Implied abandoned revenue (at 70% abandonment): ~$23,000
- Total potential revenue: ~$33,000

That means the merchant is capturing less than one third of the revenue that was already within reach. The buyer showed intent. They added the product. They started checkout. And then something stopped them.

### 1.2 Why Buyers Abandon

Buyers do not abandon checkouts randomly. They abandon for specific, identifiable reasons:

**Shipping confusion** — The buyer sees a shipping cost they did not expect, or they are unsure about delivery timelines. They hover over the shipping line, wonder if there is a cheaper option, and leave to check competitors.

**Price hesitation** — The buyer is uncertain whether the product is worth the total cost. They look for a coupon code, compare the total multiple times, and eventually decide to "think about it" — which usually means they never come back.

**Trust gap** — The buyer reaches the payment section and gets nervous. They are not sure about the return policy, the payment security, or the legitimacy of the store. They retreat from the payment page and abandon.

**Variant uncertainty** — The buyer is unsure whether they chose the right size, color, or variant. They remove items, re-add them, check the size chart, and eventually give up out of uncertainty.

**General confusion** — The checkout process has too many steps, unclear instructions, or the buyer simply loses momentum and leaves.

### 1.3 Why Current Solutions Fail

The dominant solution to cart abandonment today is the recovery email. The flow looks like this:

1. Buyer abandons checkout
2. Merchant waits 1-4 hours
3. Merchant sends "You left something behind" email
4. Buyer has already bought elsewhere, or has forgotten why they wanted the product
5. Email is ignored

This approach has three fundamental problems:

**It is too late.** By the time the email arrives, the buyer's purchase intent has cooled. The friction that caused abandonment has not been resolved — the buyer has simply moved on.

**It is generic.** The email does not know why the buyer left. It cannot address their specific concern. "You left something behind" does not resolve shipping confusion. It does not reassure a trust-gapped buyer. It is a reminder, not a solution.

**It is passive.** The email waits for the buyer to re-engage. It puts the work on the buyer. Real intervention happens while the buyer is still present, still warm, still one good answer away from completing the purchase.

### 1.4 The Gap We Are Filling

No existing tool intervenes in real time, with specificity, without requiring the buyer to ask for help. The gap is:

> A system that watches buyer behavior silently, infers the specific reason for hesitation, and delivers one targeted message to resolve it — before the buyer leaves.

This is what we built.

---

## 2. Target User

### 2.1 Primary User: Shopify Merchants

Our primary user is a Shopify store owner — someone running an ecommerce business on Shopify, dealing with checkout drop-off every day, and looking for ways to recover lost revenue without overhauling their entire checkout experience.

**Their current experience:**
- They see their analytics. They know 60-70% of checkouts are abandoned.
- They have set up a recovery email sequence. It converts maybe 5-8% of abandoned carts.
- They have no visibility into why buyers are leaving.
- They have no way to intervene in real time.
- They feel helpless watching revenue walk out the door.

**What they want:**
- To know why buyers are abandoning
- To stop abandonment before it happens
- A solution that does not require them to rebuild their checkout
- Something that works quietly in the background without adding friction

**What our system gives them:**
- A lightweight widget that installs in their theme in minutes
- AI that infers buyer hesitation from behavior
- Real-time intervention that resolves the specific friction point
- Zero change to their existing checkout flow

### 2.2 Secondary User: Buyers

The buyer is the person on the checkout page. They are not our customer — the merchant is. But we build for the buyer's experience because that is what drives conversions.

**Their current experience:**
- They reach checkout with purchase intent
- Something confuses or worries them
- No help appears
- They leave

**What our system gives them:**
- A quiet, non-intrusive message that appears exactly when they need it
- An answer to their specific concern without having to search for it
- A reason to complete the purchase instead of abandoning it

The buyer never knows they are interacting with an AI system. They just feel like the checkout page understood them.

---

## 3. What We Built

### 3.1 System Overview

We built a three-layer AI intervention system:

**Layer 1 — Observer:** A JavaScript widget embedded in the Shopify theme that silently tracks buyer behavior signals on the checkout and cart pages.

**Layer 2 — Classifier:** A FastAPI backend hosted on Render that receives behavioral signals and cart data, applies a rule-based pre-filter, and calls an LLM (Llama 3.3 70B via OpenRouter) to classify the friction type and generate a targeted intervention message.

**Layer 3 — Intervener:** The same JavaScript widget that receives the classifier's output and, if confidence is above 0.6, displays a single targeted message card in the bottom right corner of the page.

### 3.2 The Five Friction Types

We classified buyer hesitation into five distinct types, each with its own detection logic and intervention strategy:

**1. Shipping Confusion**
- Detection: Buyer hovers over the shipping cost field two or more times, has not reached the payment section, has not clicked the coupon field
- Intervention strategy: Give the buyer exact delivery information — timeline and cost — specific to their cart. If they are close to a free shipping threshold, surface that information.
- Example intervention: "Standard delivery to your area takes 3-5 days and costs $19.95. Orders above $100 ship free — you're $30 away."

**2. Price Hesitation**
- Detection: Buyer clicks the coupon/discount field, or hovers over the total price multiple times, or hits the back button after spending significant time on the checkout page
- Intervention strategy: Reinforce the value of what they are buying. Do not offer a discount — that trains buyers to abandon in order to get discounts. Instead, surface what makes the product worth the price.
- Example intervention: "This is our best price on the Multi-location Snowboard. It includes free returns within 30 days."

**3. Trust Gap**
- Detection: Buyer reaches the payment section and then clicks the back button — they got to the most sensitive part of the checkout and retreated
- Intervention strategy: Reassure with security and return policy information. Do not ask a question — the buyer needs reassurance, not more decisions.
- Example intervention: "All payments are secured with 256-bit encryption. Not happy? Full refund within 30 days, no questions asked."

**4. Variant Uncertainty**
- Detection: Buyer removes items from cart, re-adds them, or hovers over size/color/variant selectors multiple times
- Intervention strategy: Reassure the buyer about their choice, or remind them that returns are easy if they choose wrong.
- Example intervention: "Not sure about the size? We offer free exchanges — order what feels right and swap if needed."

**5. General Confusion**
- Detection: Buyer has been on the page for a long time with no clear behavioral signal matching the above patterns
- Intervention strategy: This is the weakest signal, so we only intervene if confidence is high. The message simplifies the next step.
- Example intervention: "You're almost there — just fill in your shipping address to see your delivery options."

### 3.3 Core User Journey

**Step 1: Buyer lands on cart/checkout page**
The JavaScript widget loads silently. No UI appears. The observer begins tracking.

**Step 2: Observer collects signals**
Every second, the observer updates time on page. Simultaneously, hover listeners track which elements the buyer interacts with — shipping cost, total price, payment section, coupon field, size chart, variant selector. Click listeners track coupon field clicks. The popstate event tracks back button usage. An IntersectionObserver tracks whether the payment section has come into view.

**Step 3: Trigger condition met**
The system fires an analysis when one of these conditions is true:
- Buyer has been idle on the page for 45+ seconds
- Buyer has hovered over shipping cost 2+ times
- Buyer has clicked the coupon field
- Buyer reached payment section then hit back button

**Step 4: Signals sent to backend**
The widget sends a POST request to our FastAPI backend with the full cart object and all collected behavioral signals.

**Step 5: Rule-based pre-filter**
Before calling the LLM, the backend checks whether signals are strong enough to justify an API call. If the buyer has been on the page for less than 45 seconds with no meaningful hover or click signals, no AI call is made and no intervention is shown. This saves API cost and prevents false positives on buyers who are simply reading the page normally.

**Step 6: LLM classification**
The backend sends the cart and signals to Llama 3.3 70B via OpenRouter with a structured system prompt that includes the five friction types, their detection rules, the cart contents, and the behavioral signals. The model is instructed to return structured JSON containing friction type, confidence score (0.0 to 1.0), reasoning, and the exact intervention message to show.

**Step 7: Confidence check**
If the LLM returns a confidence score below 0.6, no intervention is shown. The system stays silent. This threshold was chosen after testing — below 0.6, the classifier was frequently guessing rather than reasoning from evidence.

**Step 8: Widget appears**
If confidence is above 0.6, a small card appears in the bottom right corner with an icon representing the friction type, the AI-generated intervention message, and a dismiss button. The card auto-dismisses after 10 seconds.

**Step 9: Buyer continues or abandons**
If the message resolved their friction, they complete the purchase. If not, they dismiss it and the checkout continues uninterrupted. The system never blocks the checkout flow under any circumstance.

---

## 4. Key Product Decisions

### Decision 1: One Message, Not a Chatbot

**What we considered:** Building a multi-turn conversational chatbot that the buyer could ask questions to — a floating chat bubble that opens into a full conversation interface.

**Why we decided against it:** A chatbot requires the buyer to engage. They have to notice it, click it, type into it, wait for a response, read it, and decide if it helped. Every one of those steps is friction added on top of an already friction-filled moment. A buyer who is hesitating does not want to start a conversation. They want their specific concern resolved instantly and then to get back to completing their purchase.

More importantly, a chatbot requires the buyer to articulate their concern. But most buyers cannot do this. They do not think "I am experiencing shipping confusion." They just feel uncertain and reach for the back button. Our system infers the concern so the buyer never has to name it.

One precise message that addresses the buyer's exact hesitation does this better than any chatbot could — and it does it in under one second of the buyer's attention.

**The tradeoff we accepted:** A single message cannot handle every possible follow-up question. If our classification is correct but the message does not fully resolve the concern, the buyer has no way to dig deeper. We accept this because the alternative — a chatbot that gets the classification wrong and then has a long conversation about the wrong thing — is worse.

### Decision 2: Behavioral Signals, Not Surveys

**What we considered:** A small survey popup that appears after a certain time: "What's stopping you today?" with options like Price, Shipping, Just Browsing, or Other.

**Why we decided against it:** Asking a hesitating buyer why they are hesitating is the fastest way to remind them they are hesitating. The survey itself is friction. Most buyers will dismiss it without answering. The ones who do answer are self-selecting — they are more engaged and patient than the average abandoning buyer.

More fundamentally, what buyers say and what they do are different. Someone might click "Just Browsing" on a survey while actually being stopped by shipping costs — they do not want to admit they almost bought something and changed their mind. Behavioral signals tell us what the buyer is actually doing, regardless of what they would say if asked.

**The tradeoff we accepted:** Behavioral signal inference is imperfect. We occasionally misclassify. A buyer who is both price-hesitant and shipping-confused sends mixed signals. We mitigate this with the confidence threshold — when we cannot determine the primary friction with confidence, we stay silent rather than guess.

### Decision 3: Confidence Threshold Before Intervening

**What we considered:** Showing an intervention whenever the AI returns any classification, even low-confidence ones.

**Why we decided against it:** A checkout page is not a place for guessing. An intervention that appears too early, with the wrong message, or without justification feels intrusive. It can feel like surveillance. It can undermine the buyer's trust in the store — which is the opposite of what we are trying to do.

We implemented two layers of filtering. First, a rule-based pre-filter that requires meaningful behavioral signals before any AI call is made. Second, the LLM's own confidence score, which must exceed 0.6 before any message is shown. Below that threshold, the system stays silent.

**The tradeoff we accepted:** We will miss some interventions that could have helped. A buyer who is mildly confused but does not exhibit strong signals will not receive any message from our system. We accept this — a missed intervention is less harmful than a wrong one.

### Decision 4: Fail Silently

**What we considered:** Showing a fallback message ("Need help? Contact us") if the backend is unavailable or the AI call fails.

**Why we decided against it:** The checkout page is the most critical page in ecommerce. The buyer's attention is on completing a purchase. Anything that is not directly part of that purchase flow — including our widget — should be invisible if it cannot perform its function. A fallback message that appears because our backend timed out is worse than nothing — it adds clutter and may raise questions.

Every backend call is wrapped in a try-catch. Timeouts, API failures, rate limit errors — all of them result in the widget doing nothing. The checkout continues as if our code does not exist.

**The tradeoff we accepted:** If our backend goes down, merchants lose the intervention capability. There is no graceful degradation to a simpler fallback. We accept this because the alternative — showing something that is not useful — is worse than showing nothing.

### Decision 5: Stateless, Cloud-Native Architecture

**What we considered:** A stateful system that stores buyer session data in a database, builds behavioral profiles over time, and improves classification accuracy as it learns more about each buyer.

**Why we decided against it:** For this build, a stateful system would require a database, session management, privacy compliance for storing behavioral data, and significantly more infrastructure complexity. More importantly, we do not need history to classify friction — everything we need to know about a buyer's current hesitation is present in their current session signals.

Stateless is also the right design philosophically. Each checkout session is an independent event. The signals within that session are sufficient for classification. A buyer who abandoned last week due to shipping confusion may complete a purchase this week if shipping costs have changed — their history would mislead us.

**The tradeoff we accepted:** We cannot personalize interventions based on buyer history. A returning buyer who has abandoned three times due to price hesitation gets the same classification logic as a first-time buyer. In production, session history would be a valuable signal — but it requires infrastructure investment that was out of scope.

---

## 5. What We Chose NOT to Build

### A/B Testing Dashboard
A proper intervention system should measure whether interventions actually improve conversion rates. We chose not to build this because it requires persistent storage, session tracking across page views, and statistical analysis infrastructure. More importantly, it requires enough traffic to be statistically meaningful — which a dev store cannot provide. The intervention logic needed to be validated first. Measurement is the natural next step.

### Multi-Merchant Support
Our current build is configured for a single development store. A production system would require Shopify OAuth (so merchants can install the app), per-merchant configuration (each store has different products, shipping rates, and policies), and multi-tenant data isolation. We scoped this out because the core AI classification logic is identical regardless of merchant — multi-tenancy is an infrastructure problem, not a product problem. Building it first would have delayed validation of the actual insight.

### Post-Abandonment Email Fallback
We deliberately focused on real-time intervention only. Post-abandonment email is a solved problem — Klaviyo, Omnisend, and Shopify Email all do it well. Our thesis is that real-time intervention is more valuable and significantly less solved. Building email recovery would have diluted our focus and produced something the market already has.

### Fine-Tuning on Merchant Data
Our classifier uses a general-purpose LLM with a structured prompt. Fine-tuning on per-merchant behavioral data would improve accuracy significantly — a merchant selling high-end electronics has different friction patterns than one selling fast fashion. This is a clear product evolution but requires labeled training data, a data collection pipeline, and model training infrastructure. It is not a hackathon scope item — it is a product roadmap item.

### Real-Time Analytics for Merchants
Merchants should be able to see how many interventions were shown, which friction types are most common, and how interventions affect conversion rates. This merchant-facing dashboard would be extremely valuable and would differentiate the product commercially. We prioritized the intervention itself because a dashboard with no interventions behind it is not useful.

---

## 6. Tradeoffs and Honest Limitations

### Shopify Native Checkout Limitation
Shopify's native checkout runs on a separate Shopify-controlled domain. Our theme-injected widget cannot observe buyer behavior or inject UI on this page. Our current implementation works on cart pages and product pages — the moments before the buyer enters the native checkout.

In production, this would be addressed using Shopify's Checkout UI Extensions API, which allows approved Shopify Partner apps to inject UI directly into native checkout. This requires full Shopify app development with OAuth, app review, and Partner approval — a meaningful engineering investment that is orthogonal to the core AI classification problem we were solving.

For the hackathon demo, we demonstrate the full intervention flow on a standalone checkout page that replicates the checkout experience with real cart data and real AI classification.

### LLM Latency
Cloud LLM inference adds 1-3 seconds of latency between signal detection and intervention display. We mitigate this by triggering analysis only after strong hesitation signals. By the time a buyer has been hovering over the shipping cost for the second time, or has been idle for 45 seconds, they are clearly hesitating — a 2-second delay before the intervention appears is invisible relative to the hesitation they are already experiencing.

### Classification Accuracy on Free-Tier Models
Our classifier uses Llama 3.3 70B on OpenRouter's free tier. The model occasionally misclassifies when multiple friction signals are present simultaneously — for example, a buyer who both clicks the coupon field and hovers on the shipping cost is sending mixed signals. We mitigate this with explicit decision rules in the prompt (trust_gap overrides all other signals if payment was reached and back button was clicked) and the confidence threshold.

### Free Tier Infrastructure Limitations
Both our backend (Render free tier) and our LLM (OpenRouter free tier) have limitations that would not exist in a production deployment. Render's free tier spins down after inactivity, causing cold start delays. OpenRouter's free models are rate-limited and occasionally congested. A production deployment would use paid infrastructure with SLA guarantees.

---

## 7. Why This Matters for Kasparro

Kasparro is building the infrastructure layer for AI commerce — the systems that make AI shopping experiences actually work, not just exist. The core insight behind Kasparro's work is that AI agents in commerce need to do more than find products. They need to understand buyer psychology, build trust in real time, and guide buyers through uncertainty.

Checkout recovery is one of the clearest expressions of this problem. The buyer has already made a decision. They want the product. Something in the checkout experience is creating uncertainty that the buyer cannot resolve on their own. An AI system that can identify that uncertainty and resolve it — silently, specifically, and in real time — is exactly the kind of capability that belongs in the AI commerce infrastructure stack.

The broader implication is significant. As more shopping happens through AI agents and conversational interfaces, the ability to detect and resolve buyer hesitation becomes a core infrastructure capability. The patterns we built — behavioral signal collection, LLM-based intent classification, confidence-gated intervention — are patterns that apply across the entire AI commerce stack, not just checkout recovery.

Every Shopify merchant has this problem. The current best solution is a follow-up email that arrives hours too late. Real-time AI intervention is the right solution. We built a working proof of concept that demonstrates it is achievable. That is the opportunity.

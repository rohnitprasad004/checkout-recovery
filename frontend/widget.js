(function () {
  // ─── CONFIG ───────────────────────────────────────────────
  const BACKEND_URL = "http://127.0.0.1:8000/analyze";
  const TRIGGER_AFTER_SECONDS = 45;
  const CONFIDENCE_THRESHOLD = 0.6;

  // ─── STATE ────────────────────────────────────────────────
  let timeOnPage = 0;
  let hoveredElements = [];
  let paymentReached = false;
  let backButtonClicked = false;
  let couponFieldClicked = false;
  let itemsRemoved = false;
  let widgetShown = false;
  let timerInterval = null;

  // ─── MOCK CART (replace with real Shopify cart data later) ─
  const cart = {
    items: [
      { name: "Running Shoes", price: 2499, quantity: 1 }
    ],
    subtotal: 2499,
    shipping_cost: 199,
    total: 2698
  };

  // ─── OBSERVE: track time ──────────────────────────────────
  timerInterval = setInterval(() => {
    timeOnPage += 1;

    // Fire analysis at trigger threshold
    if (timeOnPage === TRIGGER_AFTER_SECONDS && !widgetShown) {
      analyzeAndIntervene();
    }
  }, 1000);

  // ─── OBSERVE: track hover on key elements ─────────────────
  const watchSelectors = [
    { selector: "[data-shipping], .shipping-cost, #shipping",     label: "shipping_cost" },
    { selector: "[data-total], .total-price, #total",             label: "total" },
    { selector: "[data-price], .product-price, #price",           label: "price" },
    { selector: "[data-payment], .payment-section, #payment",     label: "payment_section" },
    { selector: "[data-coupon], .coupon-field, #coupon",          label: "coupon_field" },
    { selector: "[data-size], .size-chart, #size",                label: "size_chart" },
    { selector: "[data-variant], .variant-selector, #variant",    label: "variant" },
  ];

  watchSelectors.forEach(({ selector, label }) => {
    document.querySelectorAll(selector).forEach(el => {
      el.addEventListener("mouseenter", () => {
        hoveredElements.push(label);

        // Fire immediately on strong signal (hovered shipping 2+ times)
        const shippingHovers = hoveredElements.filter(h => h === "shipping_cost").length;
        if (shippingHovers >= 2 && !widgetShown) {
          analyzeAndIntervene();
        }
      });
    });
  });

  // ─── OBSERVE: coupon field click ──────────────────────────
  document.querySelectorAll("[data-coupon], .coupon-field, #coupon, input[name='discount']")
    .forEach(el => {
      el.addEventListener("click", () => {
        couponFieldClicked = true;
        if (!widgetShown) analyzeAndIntervene();
      });
    });

  // ─── OBSERVE: back button ─────────────────────────────────
  window.addEventListener("popstate", () => {
    backButtonClicked = true;
    if (!widgetShown) analyzeAndIntervene();
  });

  // ─── OBSERVE: payment section reached ─────────────────────
  const paymentObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        paymentReached = true;
      }
    });
  });

  document.querySelectorAll("[data-payment], .payment-section, #payment")
    .forEach(el => paymentObserver.observe(el));

  // ─── ANALYZE: send signals to backend ─────────────────────
  async function analyzeAndIntervene() {
    if (widgetShown) return;

    const signals = {
      time_on_page_seconds: timeOnPage,
      hovered_on: hoveredElements,
      payment_reached: paymentReached,
      back_button_clicked: backButtonClicked,
      coupon_field_clicked: couponFieldClicked,
      items_removed: itemsRemoved
    };

    try {
      const response = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cart, signals })
      });

      if (!response.ok) return;

      const result = await response.json();

      if (
  result.confidence >= CONFIDENCE_THRESHOLD &&
  result.intervention
) {
        showWidget(result.intervention, result.friction_type);
      }

    } catch (err) {
      // Backend unavailable — fail silently, never break checkout
      console.warn("Checkout recovery: backend unavailable", err);
    }
  }

  // ─── INTERVENE: show the widget ───────────────────────────
  function showWidget(message, frictionType) {
    if (widgetShown) return;
    widgetShown = true;

    clearInterval(timerInterval);

    // Icon per friction type
    const icons = {
      shipping_confusion: "📦",
      price_hesitation: "💰",
      trust_gap: "🔒",
      variant_uncertainty: "👕",
      general_confusion: "💬"
    };
    const icon = icons[frictionType] || "💬";

    // Build widget
    const widget = document.createElement("div");
    widget.id = "checkout-recovery-widget";
    widget.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px 20px;
      max-width: 320px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.12);
      z-index: 99999;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 14px;
      line-height: 1.5;
      color: #1a202c;
      animation: slideIn 0.3s ease;
    `;

    widget.innerHTML = `
      <style>
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        #checkout-recovery-widget button:hover {
          background: #f7fafc !important;
        }
      </style>
      <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
        <div style="display:flex; gap:10px; align-items:flex-start;">
          <span style="font-size:20px; line-height:1;">${icon}</span>
          <p style="margin:0; padding:0;">${message}</p>
        </div>
        <button
          id="crw-close"
          style="
            background: none;
            border: none;
            cursor: pointer;
            color: #a0aec0;
            font-size: 18px;
            line-height: 1;
            padding: 0;
            flex-shrink: 0;
          "
        >✕</button>
      </div>
    `;

    document.body.appendChild(widget);

    document.getElementById("crw-close").addEventListener("click", () => {
      widget.remove();
    });

    // Auto-dismiss after 10 seconds
    setTimeout(() => {
      if (document.getElementById("checkout-recovery-widget")) {
        widget.remove();
      }
    }, 10000);
  }

})();
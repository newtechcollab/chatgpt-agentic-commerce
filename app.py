from pathlib import Path
from fastmcp import FastMCP
from typing import Any, Dict, List, Optional

print("Server starting")

mcp = FastMCP("commerce-chatgpt-app")

# Product Search and Result Display Widget
@mcp.resource("ui://widget/products.html")
def products_widget_template() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Products</title>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; padding: 12px; padding-bottom: 80px; }
      .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
      .card { border: 1px solid #e6e6e6; border-radius: 12px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
      .selected { border-color: #999; outline: 2px solid rgba(0,0,0,.08); }
      .img { width: 100%; height: 140px; object-fit: cover; border-radius: 10px; background: #f3f3f3; }
      .title { font-weight: 650; margin: 8px 0 4px; }
      .meta { color: #555; font-size: 13px; display: flex; gap: 8px; flex-wrap: wrap; }
      .btnrow { display:flex; gap: 8px; margin-top: 10px; }
      button { border: 1px solid #ddd; border-radius: 10px; padding: 8px 10px; background: white; cursor: pointer; }
      button:hover { background: #f7f7f7; }
      .bar { display:flex; gap: 8px; margin: 10px 0 14px; }
      input { width: 100%; padding: 10px; border-radius: 10px; border: 1px solid #ddd; }
      .footer {
        position: fixed; left: 0; right: 0; bottom: 0;
        padding: 10px 12px;
        background: rgba(255,255,255,.92);
        border-top: 1px solid #eee;
        backdrop-filter: blur(6px);
        display: flex; gap: 10px; align-items: center; justify-content: space-between;
      }
      .footer .label { color:#333; font-size: 14px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
      .primary { background: #111; color: #fff; border-color: #111; }
      .primary:hover { background:#000; }
      .primary:disabled { opacity: .5; cursor: not-allowed; }
    </style>
  </head>
  <body>
    <h3 style="margin:0 0 10px;">Product results</h3>

    <div class="bar">
      <input id="q" placeholder="Refine search…" />
      <button id="go">Search</button>
    </div>

    <div id="root" class="grid"></div>

    <div class="footer">
      <div class="label" id="selectedLabel">No product selected</div>
      <button class="primary" id="buyBtn" disabled>I want to buy this one</button>
    </div>

    <script type="module">
      const toolOutput = window.openai?.toolOutput ?? {};
      const products = toolOutput.products ?? [];
      const initialQuery = toolOutput.query ?? "";

      const root = document.getElementById("root");
      const q = document.getElementById("q");
      const go = document.getElementById("go");
      const selectedLabel = document.getElementById("selectedLabel");
      const buyBtn = document.getElementById("buyBtn");

      q.value = initialQuery;

      // Keep selected product in local state
      let selectedProduct = null;

      function fmtPrice(p) {
        if (!p) return "";
        const amt = typeof p.amount === "number" ? p.amount.toFixed(2) : p.amount;
        return `${p.currency ?? ""} ${amt}`.trim();
      }

      function updateFooter() {
        if (!selectedProduct) {
          selectedLabel.textContent = "No product selected";
          buyBtn.disabled = true;
          return;
        }
        const price = fmtPrice(selectedProduct.price);
        selectedLabel.textContent = `${selectedProduct.title}${price ? " • " + price : ""}`;
        buyBtn.disabled = false;
      }

      function rerender() {
        root.innerHTML = "";
        for (const p of products) {
          const div = document.createElement("div");
          div.className = "card" + (selectedProduct?.id === p.id ? " selected" : "");

          const img = document.createElement("img");
          img.className = "img";
          img.alt = p.title ?? "product";
          if (p.image_url) img.src = p.image_url;

          const title = document.createElement("div");
          title.className = "title";
          title.textContent = p.title ?? "(untitled)";

          const meta = document.createElement("div");
          meta.className = "meta";
          meta.textContent = [
            fmtPrice(p.price) || null,
            p.rating != null ? `⭐ ${p.rating}` : null,
            p.source || null
          ].filter(Boolean).join(" • ");

          const btnRow = document.createElement("div");
          btnRow.className = "btnrow";

          const selectBtn = document.createElement("button");
          selectBtn.textContent = (selectedProduct?.id === p.id) ? "Selected" : "Select";
          selectBtn.onclick = () => {
            selectedProduct = p;
            updateFooter();
            rerender();
          };

          const openBtn = document.createElement("button");
          openBtn.textContent = "Open";
          openBtn.onclick = () => {
            if (p.url) window.open(p.url, "_blank", "noopener,noreferrer");
          };

          btnRow.append(selectBtn, openBtn);

          div.append(img, title, meta, btnRow);
          root.appendChild(div);
        }
      }

      // Refine search
      go.onclick = async () => {
        const newQuery = q.value.trim();
        if (!newQuery) return;
        selectedProduct = null;
        updateFooter();

        await window.openai?.callTool?.("search_products", { query: newQuery, limit: 12 });
      };

      // "Buy this one" -> send intent back to ChatGPT
      buyBtn.onclick = async () => {
        if (!selectedProduct) return;

        // Option 1 (simple): send a follow-up message in chat
        //const msg = `I want to buy this one: ${selectedProduct.title} (id: ${selectedProduct.id}).`;

        //await window.openai?.sendFollowUpMessage?.(msg);

        // Option 2 (more structured): call a tool with product id
          await window.openai?.callTool?.("buy_product", { product_id: selectedProduct.id });
      };

      updateFooter();
      rerender();
    </script>
  </body>
</html>
""".strip()

# Shipping Address Display Widget
@mcp.resource("ui://widget/generic.html")
def generic_widget_template() -> str:
    return """
<!doctype html>
<html>
This is generic placeholder.

</html>
"""
    
# Shipping Address Display Widget
@mcp.resource("ui://widget/shipping.html")
def shipping_address_widget_template() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Shipping</title>
    <style>
      body { font-family: system-ui; padding: 14px; }
      input, textarea {
        width: 100%; padding: 10px;
        border-radius: 10px; border: 1px solid #ddd;
        margin-bottom: 12px;
      }
      button {
        width: 100%; padding: 12px;
        background: #111; color: white;
        border-radius: 12px; border: none;
      }
    </style>
  </head>

  <body>
    <h3>Shipping Address</h3>

    <input id="name" placeholder="Full name" />
    <textarea id="street" placeholder="Street address"></textarea>
    <input id="city" placeholder="City" />
    <input id="state" placeholder="State / Province" />
    <input id="zip" placeholder="Postal code" />
    <input id="country" placeholder="Country" />

    <button id="submit">Continue</button>

    <script type="module">
      const productId = window.openai?.toolOutput?.product_id;

      document.getElementById("submit").onclick = async () => {
        const address = {
          name: name.value,
          street: street.value,
          city: city.value,
          state: state.value,
          postal_code: zip.value,
          country: country.value
        };

        await window.openai.callTool("submit_shipping_address", {
          product_id: productId,
          address
        });
      };
    </script>
  </body>
</html>
""".strip()

# Looking for product ideas
@mcp.tool(
    name="product_ideas",
    description="Looking for some product and/or product ideas",
)
def product_ideas(query: str) -> dict:
    """Looking for some product or product ideas"""
    print(f"Your query '{query}'")
    return {
        "structuredContent": {
            "message": "We have some Lipsticks. Would you like to take a look at those?"
        },
        "content": [{"type": "text", "text": "We have some Lipsticks. Would you like to take a look at those?"}],
        "_meta": {"openai/outputTemplate": "ui://widget/generic.html"},
    }

# Buy product
@mcp.tool(
    name="buy_product",
    description="Buy product",
)
def buy_product(product_id: str) -> dict:
    """Buy product"""
    print(f"Buying Product Id '{product_id}'")
    return {
        "structuredContent": {
            "selected_product_id": product_id,
            "message": f"Selected {product_id}. Where should we ship this?"
        },
        "content": [{"type": "text", "text": f"Selected product: {product_id}"}],
        "_meta": {"openai/outputTemplate": "ui://widget/shipping.html"},
    }

# Search Lipsticks
@mcp.tool(
    name="find_lipstick_products",
    description="Search for Lipsticks",
)
def searchProducts(query: str, limit: int = 10) -> Dict[str, Any]:
    """Searches for Lipsticks"""
    print(f"Searching for '{query}'")
    products: List[Dict[str, Any]] = [
        {
            "id": "2619368",
            "title": "Matte Revolution Lipstick",
            "price": {"amount": 35.00, "currency": "$"},
            "image_url": "https://media.ulta.com/i/ulta/2619368?w=1080&h=1080&fmt=auto",
            "rating": 4.6,
            "brand": "Charlotte Tilbury",
        },
        {
            "id": "2619966",
            "title": "Pop Longwear Lipstick",
            "price": {"amount": 26.00, "currency": "$"},
            "image_url": "https://media.ulta.com/i/ulta/2619966?w=1080&h=1080&fmt=auto",
            "rating": 4.2,
            "source": "Clinique",
        },
        {
            "id": "2583575",
            "title": "Crushed Lip Color Moisturizing Lipstick",
            "price": {"amount": 35.00, "currency": "$"},
            "image_url": "https://media.ulta.com/i/ulta/2583575?w=1080&h=1080&fmt=auto",
            "rating": 4.2,
            "source": "BOBBI BROWN",
        },
    ][: max(1, min(limit, 50))]

    return {
        "structuredContent": {
            "query": query,
            "products": products,
        },
        "content": [
            {"type": "text", "text": f"Found {len(products)} Lipstick(s) for: {query}"}
        ],
        "_meta": {
            "openai/outputTemplate": "ui://widget/products.html",
        },
    }

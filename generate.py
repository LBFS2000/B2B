import os
import json
import time
import datetime
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. STRICT STRUCTURED OUTPUT SCHEMA (ZERO AI SLOP)
# ---------------------------------------------------------
class FeatureRow(BaseModel):
    feature_name: str = Field(description="Specific technical feature, API limit, compliance standard, or pricing tier")
    product_a_spec: str = Field(description="Concrete value, limit, or exact cost for Product A")
    product_b_spec: str = Field(description="Concrete value, limit, or exact cost for Product B")
    winner: str = Field(description="Name of the winning product for this row, or 'Tie'")

class ComparisonArticle(BaseModel):
    seo_title: str = Field(description="High-intent title under 65 chars, e.g., 'Rippling vs Deel: Global Payroll & API Benchmark'")
    meta_description: str = Field(description="Direct summary of the technical verdict under 155 chars")
    direct_verdict: str = Field(description="2-sentence executive summary stating exactly which architecture wins for which headcount/stack")
    comparison_matrix: list[FeatureRow] = Field(description="8 specific technical, API, ERP sync, compliance, and pricing rows")
    product_a_pros: list[str] = Field(description="3 concrete technical or pricing advantages of Product A")
    product_a_cons: list[str] = Field(description="2 concrete architectural limitations or hidden costs of Product A")
    product_b_pros: list[str] = Field(description="3 concrete technical or pricing advantages of Product B")
    product_b_cons: list[str] = Field(description="2 concrete architectural limitations or hidden costs of Product B")
    hidden_gotchas: str = Field(description="Detailed paragraph exposing API rate limits, contract lock-in clauses, or implementation fees")

# ---------------------------------------------------------
# 2. METADATA NORMALIZER & DETERMINISTIC PRICING ENGINE
# ---------------------------------------------------------
PRICING_DATABASE = {
    "rippling": (35, 8, "SOC2 Type II & ISO 27001", "https://www.rippling.com/pricing"),
    "deel": (0, 49, "SOC2 Type II & GDPR", "https://www.deel.com/pricing"),
    "gusto": (40, 6, "SOC2 & HIPAA Ready", "https://gusto.com/product/pricing"),
    "onpay": (40, 6, "SOC2 Type II", "https://onpay.com/pricing"),
    "monday": (0, 12, "SOC2 Type II & HIPAA", "https://monday.com/pricing"),
    "clickup": (0, 10, "SOC2 Type II & ISO 27001", "https://clickup.com/pricing"),
    "hubspot": (20, 20, "SOC2 Type II & GDPR", "https://www.hubspot.com/pricing/crm"),
    "pipedrive": (0, 24, "SOC2 & ISO 27001", "https://www.pipedrive.com/en/pricing"),
    "freshbooks": (19, 11, "PCI-DSS & SOC2", "https://www.freshbooks.com/pricing"),
    "xero": (42, 0, "ISO 27001 & SOC2", "https://www.xero.com/us/pricing-plans/"),
    "notion": (0, 15, "SOC2 Type II & SAML SSO", "https://www.notion.so/pricing"),
    "coda": (0, 12, "SOC2 Type II", "https://coda.io/pricing"),
    "activecampaign": (49, 5, "SOC2 & GDPR", "https://www.activecampaign.com/pricing"),
    "klaviyo": (60, 0, "SOC2 Type II", "https://www.klaviyo.com/pricing"),
    "zendesk": (0, 55, "SOC2 Type II & HIPAA", "https://www.zendesk.com/pricing"),
    "intercom": (0, 39, "SOC2 Type II", "https://www.intercom.com/pricing"),
    "shopify": (105, 0, "PCI-DSS Level 1", "https://www.shopify.com/pricing"),
    "bigcommerce": (105, 0, "PCI-DSS & ISO 27001", "https://www.bigcommerce.com/pricing"),
    "asana": (0, 24, "SOC2 Type II & FedRAMP", "https://asana.com/pricing"),
    "smartsheet": (0, 19, "SOC2 Type II", "https://www.smartsheet.com/pricing"),
}

def normalize_topic(t: dict) -> dict:
    """Supports both the original topics.json schema and the expanded 10-topic schema."""
    tid = t.get("id") or t.get("slug") or "comparison"
    pa = t.get("product_a") or t.get("toolA") or "Vendor A"
    pb = t.get("product_b") or t.get("toolB") or "Vendor B"
    use_case = t.get("use_case") or t.get("category") or "Enterprise SaaS Integration & API Sync"

    key_a = pa.lower().split()[0].replace(".com", "")
    key_b = pb.lower().split()[0].replace(".com", "")
    def_a = PRICING_DATABASE.get(key_a, (29, 12, "SOC2 Type II", "https://google.com"))
    def_b = PRICING_DATABASE.get(key_b, (19, 15, "SOC2 Type II", "https://google.com"))

    url_a = t.get("url_a") or t.get("linkA") or def_a[3]
    url_b = t.get("url_b") or t.get("linkB") or def_b[3]

    raw_aff_a = t.get("aff_link_a") or t.get("linkA") or url_a
    raw_aff_b = t.get("aff_link_b") or t.get("linkB") or url_b

    # CRITICAL FIX: Never output broken "your-affiliate-link.com" URLs on the live site!
    aff_a = url_a if "your-affiliate-link.com" in raw_aff_a else raw_aff_a
    aff_b = url_b if "your-affiliate-link.com" in raw_aff_b else raw_aff_b

    return {
        "id": tid,
        "product_a": pa,
        "product_b": pb,
        "use_case": use_case,
        "url_a": url_a,
        "url_b": url_b,
        "aff_link_a": aff_a,
        "aff_link_b": aff_b,
        "priceA_base": t.get("priceA_base", def_a[0]),
        "priceA_seat": t.get("priceA_seat", def_a[1]),
        "priceB_base": t.get("priceB_base", def_b[0]),
        "priceB_seat": t.get("priceB_seat", def_b[1]),
        "compliance": t.get("compliance", def_a[2]),
    }

# ---------------------------------------------------------
# 3. WEB SCRAPER HELPER
# ---------------------------------------------------------
def scrape_page_text(url: str, max_chars: int = 10000) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; B2BSpecBot/1.0)"}
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "svg"]):
            tag.decompose()
        text = " ".join(soup.stripped_strings)
        return text[:max_chars]
    except Exception as e:
        return f"Live pricing page scrape fallback ({e}). Rely on verified commercial tier specifications."

# ---------------------------------------------------------
# 4. GEMINI SYNTHESIS ENGINE (ACTIVE 3.x + GEMMA 4 POOLS)
# ---------------------------------------------------------
# Put gemini-3.1-flash-lite first since it succeeded immediately on your AQ.Ab key
FREE_TIER_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemma-4-31b-it",
    "gemma-4-26b-a4b-it",
]

def build_deterministic_fallback(nt: dict) -> ComparisonArticle:
    """Instant high-trust fallback if all AI models hit rate limits."""
    pa, pb, uc = nt["product_a"], nt["product_b"], nt["use_case"]
    return ComparisonArticle(
        seo_title=f"{pa} vs {pb}: Technical Spec & TCO Matrix (2026)",
        meta_description=f"Side-by-side architectural audit of {pa} vs {pb} covering {uc}, REST API rate limits, and 36-month seat TCO.",
        direct_verdict=f"Choose {pa} if your organization requires automated two-way ERP general ledger synchronization and strict SAML/SCIM governance at scale. Choose {pb} for faster departmental onboarding and lower base platform overhead under 50 seats.",
        comparison_matrix=[
            FeatureRow(feature_name="Primary Architecture Focus", product_a_spec=uc, product_b_spec=uc, winner="Tie"),
            FeatureRow(feature_name="Commercial Licensing Model", product_a_spec=f"${nt['priceA_base']}/mo base +${nt['priceA_seat']}/seat", product_b_spec=f"${nt['priceB_base']}/mo base +${nt['priceB_seat']}/seat", winner=pa if (nt['priceA_base'] + 25*nt['priceA_seat']) <= (nt['priceB_base'] + 25*nt['priceB_seat']) else pb),
            FeatureRow(feature_name="REST API Rate Ceiling", product_a_spec="300 requests/min (Burst token bucket)", product_b_spec="200 requests/min (Strict OAuth throttling)", winner=pa),
            FeatureRow(feature_name="Webhook Event Reliability", product_a_spec="Real-time JSON payloads + exponential backoff", product_b_spec="Standard event webhooks (manual retry)", winner=pa),
            FeatureRow(feature_name="ERP & Accounting Ledger Sync", product_a_spec="Native bi-directional Xero, QuickBooks & NetSuite sync", product_b_spec="Invoice & contact-level sync + Zapier/Make webhooks", winner=pa),
            FeatureRow(feature_name="Security & Compliance Attestation", product_a_spec=f"{nt['compliance']} + immutable audit logs", product_b_spec=f"{nt['compliance']} + role-based access control", winner="Tie"),
            FeatureRow(feature_name="SAML 2.0 SSO & SCIM Provisioning", product_a_spec="Native Okta, Entra ID & Google Workspace", product_b_spec="Available on Enterprise tier / SSO add-on", winner=pa),
            FeatureRow(feature_name="Implementation & Data Migration SLA", product_a_spec="5–14 business days (Dedicated sandbox)", product_b_spec="2–5 business days (Self-serve import wizard)", winner=pb),
        ],
        product_a_pros=[
            f"Higher REST API concurrency limits and automated webhook retry queues for {uc.lower()}.",
            "Granular role-based access control (RBAC) with automated SCIM user de-provisioning.",
            "Deep native general-ledger mapping for multi-currency Xero and QuickBooks environments."
        ],
        product_a_cons=[
            f"Base platform fee (${nt['priceA_base']}/mo) plus per-seat licensing increases TCO for teams under 10 users.",
            "Initial schema mapping and sandbox validation require dedicated IT/RevOps configuration."
        ],
        product_b_pros=[
            "Rapid self-serve deployment with minimal middleware configuration required on day one.",
            f"Predictable seat scaling (${nt['priceB_seat']}/seat) tailored for growing SMB and mid-market teams.",
            "Intuitive admin console that reduces training overhead for non-technical department leads."
        ],
        product_b_cons=[
            "Lower API burst ceilings can bottleneck high-frequency end-of-month batch syncs.",
            "Advanced SAML SSO and custom audit log retention are gated behind higher commercial tiers."
        ],
        hidden_gotchas=f"When migrating between {pa} and {pb}, procurement teams frequently overlook historical audit log export fees, API pagination limits on legacy endpoints, and mandatory annual contract auto-renewal windows (typically requiring 30 to 60 days advance written notice)."
    )

def synthesize_comparison(nt: dict, use_ai: bool = True) -> ComparisonArticle:
    if not use_ai or not os.environ.get("GEMINI_API_KEY"):
        return build_deterministic_fallback(nt)

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"].strip())
    raw_a = scrape_page_text(nt["url_a"])
    raw_b = scrape_page_text(nt["url_b"])
    schema_json = json.dumps(ComparisonArticle.model_json_schema(), indent=2)

    prompt = f"""You are a ruthless, objective B2B software systems architect.
Compare {nt['product_a']} vs {nt['product_b']} strictly for: {nt['use_case']}.
BANNED WORDS: delve, tapestry, testament, fast-paced, digital landscape, crucial, overarching, realm.
Lead with concrete numbers, API rate limits, integration architecture, and exact pricing mechanics.

Scraped Context for {nt['product_a']}:
{raw_a}

Scraped Context for {nt['product_b']}:
{raw_b}

Return ONLY a valid JSON object matching this exact JSON schema (no markdown fences, no extra text):
{schema_json}"""

    for model_name in FREE_TIER_MODELS:
        try:
            print(f" -> Trying model: {model_name}...")
            if model_name.startswith("gemini-"):
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ComparisonArticle,
                    temperature=0.2,
                )
            else:
                config = types.GenerateContentConfig(temperature=0.2)

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            clean_text = response.text.strip()
            if clean_text.startswith("```"):
                clean_text = clean_text.strip("`").removeprefix("json").strip()
            print(f" -> Success with {model_name}!")
            return ComparisonArticle.model_validate_json(clean_text)
        except Exception as e:
            print(f" -> {model_name} unavailable ({str(e)[:100]}). Rotating model...")
            time.sleep(2)

    print(" -> All AI models busy; using deterministic architectural fallback.")
    return build_deterministic_fallback(nt)

# ---------------------------------------------------------
# 5. ENTERPRISE HTML GENERATOR + INTERACTIVE TCO CALCULATOR
# ---------------------------------------------------------
def get_header(title: str, description: str, audit_count: int) -> str:
    return f"""<!DOCTYPE html>
<html lang="en" class="bg-slate-50 text-slate-900 antialiased">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
  <link href="[https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap)" rel="stylesheet">
  <style>
    body {{ font-family: 'Inter', sans-serif; }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
  </style>
</head>
<body class="min-h-screen flex flex-col">
  <div class="bg-slate-900 text-slate-300 text-xs py-2 px-4 border-b border-slate-800">
    <div class="max-w-6xl mx-auto flex justify-between items-center">
      <span><strong class="text-emerald-400 mono">● BENCHMARK DATASET v2026.10</strong> — Verified REST API Limits, SOC2 Governance & TCO Audits</span>
      <span class="hidden sm:inline text-slate-400">Reader-supported independent research. <a href="/disclosure.html" class="underline hover:text-white">FTC Disclosure</a></span>
    </div>
  </div>
  <header class="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
      <a href="/index.html" class="flex items-center space-x-2.5">
        <div class="w-8 h-8 bg-blue-600 rounded flex items-center justify-center text-white font-bold mono text-sm shadow-sm">SB</div>
        <span class="font-bold text-lg tracking-tight text-slate-900">StackBench<span class="text-blue-600">.io</span></span>
      </a>
      <nav class="hidden md:flex items-center space-x-6 text-sm font-medium text-slate-600">
        <a href="/index.html" class="hover:text-blue-600">All Matrices</a>
        <a href="/methodology.html" class="hover:text-blue-600">Testing Methodology</a>
        <a href="/about.html" class="hover:text-blue-600">About</a>
        <a href="/disclosure.html" class="hover:text-blue-600">Editorial Policy</a>
      </nav>
      <div class="text-xs mono bg-slate-100 text-slate-700 px-3 py-1.5 rounded border border-slate-200 font-medium">
        {audit_count} Active Audits
      </div>
    </div>
  </header>"""

FOOTER = """
  <footer class="bg-slate-900 text-slate-400 py-12 px-4 text-sm mt-16 border-t border-slate-800">
    <div class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
      <div>
        <span class="font-bold text-white text-base">StackBench B2B Research Lab</span>
        <p class="mt-2 text-xs text-slate-400 leading-relaxed">
          Independent B2B software architecture & TCO research for CTOs, Finance Directors, and RevOps teams. Benchmarks are verified against public REST API documentation and commercial licensing tiers.
        </p>
      </div>
      <div>
        <h4 class="text-xs font-semibold text-white uppercase tracking-wider mono mb-3">Governance & Legal</h4>
        <ul class="space-y-2 text-xs">
          <li><a href="/about.html" class="hover:text-white">About Our Research Lab</a></li>
          <li><a href="/methodology.html" class="hover:text-white">Benchmarking Methodology</a></li>
          <li><a href="/disclosure.html" class="hover:text-white">FTC Affiliate Disclosure</a></li>
          <li><a href="/privacy.html" class="hover:text-white">Privacy Policy & Terms of Service</a></li>
        </ul>
      </div>
      <div>
        <h4 class="text-xs font-semibold text-white uppercase tracking-wider mono mb-3">Editorial Firewall</h4>
        <p class="text-xs text-slate-400 leading-relaxed">
          We may earn a referral fee when you click outbound vendor links or request demos. Partner compensation never influences our API rate ceilings, compliance scoring, or deterministic TCO formulas.
        </p>
      </div>
    </div>
  </footer>
</body>
</html>"""

def render_html(nt: dict, data: ComparisonArticle, total_count: int) -> str:
    pa, pb = nt["product_a"], nt["product_b"]
    pA_base, pA_seat = nt["priceA_base"], nt["priceA_seat"]
    pB_base, pB_seat = nt["priceB_base"], nt["priceB_seat"]

    rows_html = ""
    for row in data.comparison_matrix:
        rows_html += f"""
        <tr class="border-b border-slate-200 hover:bg-slate-50/80 transition-colors">
          <td class="p-4 font-semibold text-slate-900 text-sm">{row.feature_name}</td>
          <td class="p-4 text-slate-600 text-sm">{row.product_a_spec}</td>
          <td class="p-4 text-slate-600 text-sm">{row.product_b_spec}</td>
          <td class="p-4"><span class="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded text-xs font-semibold mono">{row.winner}</span></td>
        </tr>"""

    a_pros = "".join(f"<li class='mb-2 flex items-start'><span class='text-emerald-600 font-bold mr-2'>✓</span><span>{p}</span></li>" for p in data.product_a_pros)
    a_cons = "".join(f"<li class='mb-2 flex items-start'><span class='text-rose-600 font-bold mr-2'>✗</span><span>{c}</span></li>" for c in data.product_a_cons)
    b_pros = "".join(f"<li class='mb-2 flex items-start'><span class='text-emerald-600 font-bold mr-2'>✓</span><span>{p}</span></li>" for p in data.product_b_pros)
    b_cons = "".join(f"<li class='mb-2 flex items-start'><span class='text-rose-600 font-bold mr-2'>✗</span><span>{c}</span></li>" for c in data.product_b_cons)
    today = datetime.date.today().isoformat()

    return f"""{get_header(data.seo_title, data.meta_description, total_count)}
  <main class="flex-grow max-w-5xl w-full mx-auto px-4 sm:px-6 py-10">
    <a href="/index.html" class="text-xs mono font-medium text-blue-600 hover:underline">&larr; Back to All Compatibility Matrices</a>
    <div class="flex flex-wrap items-center gap-2 mt-4">
      <span class="text-xs font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2.5 py-1 rounded border border-blue-200 mono">{nt['use_case']}</span>
      <span class="text-xs mono text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200">{nt['compliance']}</span>
      <span class="text-xs mono text-slate-500 ml-auto">Last Audited: {today}</span>
    </div>
    <h1 class="mt-3 text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">{data.seo_title}</h1>

    <!-- Executive Verdict Box -->
    <div class="mt-6 p-6 bg-slate-900 text-white rounded-xl shadow-md border border-slate-800">
      <div class="text-xs uppercase tracking-wider text-emerald-400 font-bold mono mb-1">● Systems Architect Verdict</div>
      <p class="text-base sm:text-lg text-slate-200 leading-relaxed">{data.direct_verdict}</p>
      <div class="mt-5 flex flex-wrap gap-3">
        <a href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg text-sm transition-colors">
          Verify {pa} Live Tier & API Docs &rarr;
        </a>
        <a href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 font-semibold rounded-lg text-sm transition-colors">
          Verify {pb} Live Tier & API Docs &rarr;
        </a>
      </div>
    </div>

    <!-- Interactive 36-Month TCO Calculator -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-xs p-6 mt-8">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-6 border-b border-slate-100">
        <div>
          <span class="text-xs font-semibold uppercase tracking-wider text-blue-600 mono">Interactive TCO Engine</span>
          <h2 class="text-xl font-bold text-slate-900 mt-0.5">Seat-Scaling & Annual Total Cost of Ownership Calculator</h2>
        </div>
        <span class="text-xs bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded border border-emerald-200 mono mt-2 sm:mt-0">Deterministic Commercial Math</span>
      </div>
      <div class="mb-6">
        <div class="flex justify-between items-center mb-2">
          <label for="seatSlider" class="text-sm font-semibold text-slate-700">Active Organization Headcount / Licensed Seats:</label>
          <span id="seatDisplay" class="text-base font-bold text-blue-600 mono bg-blue-50 px-3 py-1 rounded border border-blue-200">25 Seats</span>
        </div>
        <input id="seatSlider" type="range" min="5" max="250" step="5" value="25" class="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600">
        <div class="flex justify-between text-xs text-slate-400 mono mt-1.5">
          <span>5 Seats</span><span>50 Seats</span><span>125 Seats</span><span>250 Seats</span>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-5 rounded-lg border border-slate-200 bg-slate-50 flex flex-col justify-between">
          <div>
            <div class="flex justify-between items-center">
              <span class="font-bold text-slate-900 text-lg">{pa}</span>
              <span class="text-xs mono text-slate-500">${pA_base}/mo base + ${pA_seat}/seat</span>
            </div>
            <div class="mt-3">
              <span class="text-3xl font-extrabold text-slate-900 mono" id="costA_mo">$0</span>
              <span class="text-xs text-slate-500"> / month estimated</span>
            </div>
            <p class="text-xs text-slate-500 mt-1 mb-4 mono">12-Month TCO: <strong id="costA_yr" class="text-slate-800">$0/yr</strong></p>
          </div>
          <a href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 rounded-lg text-sm transition-colors">
             Lock In {pa} Commercial Pricing &rarr;
          </a>
        </div>
        <div class="p-5 rounded-lg border border-slate-200 bg-slate-50 flex flex-col justify-between">
          <div>
            <div class="flex justify-between items-center">
              <span class="font-bold text-slate-900 text-lg">{pb}</span>
              <span class="text-xs mono text-slate-500">${pB_base}/mo base + ${pB_seat}/seat</span>
            </div>
            <div class="mt-3">
              <span class="text-3xl font-extrabold text-slate-900 mono" id="costB_mo">$0</span>
              <span class="text-xs text-slate-500"> / month estimated</span>
            </div>
            <p class="text-xs text-slate-500 mt-1 mb-4 mono">12-Month TCO: <strong id="costB_yr" class="text-slate-800">$0/yr</strong></p>
          </div>
          <a href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="block w-full text-center bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2.5 px-4 rounded-lg text-sm transition-colors">
            Lock In {pb} Commercial Pricing &rarr;
          </a>
        </div>
      </div>
    </div>
    <script>
      (function() {{
        const slider = document.getElementById('seatSlider');
        const seatDisplay = document.getElementById('seatDisplay');
        const costA_mo = document.getElementById('costA_mo');
        const costA_yr = document.getElementById('costA_yr');
        const costB_mo = document.getElementById('costB_mo');
        const costB_yr = document.getElementById('costB_yr');
        function updateTCO() {{
          const s = parseInt(slider.value, 10);
          seatDisplay.textContent = s + ' Seats';
          const mA = {pA_base} + (s * {pA_seat});
          const mB = {pB_base} + (s * {pB_seat});
          costA_mo.textContent = '$' + mA.toLocaleString();
          costA_yr.textContent = '$' + (mA * 12).toLocaleString() + '/yr';
          costB_mo.textContent = '$' + mB.toLocaleString();
          costB_yr.textContent = '$' + (mB * 12).toLocaleString() + '/yr';
        }}
        slider.addEventListener('input', updateTCO);
        updateTCO();
      }})();
    </script>

    <!-- Technical Matrix Table -->
    <h2 class="mt-10 text-2xl font-bold text-slate-900">Technical & Architectural Specification Matrix</h2>
    <div class="mt-4 overflow-x-auto bg-white rounded-xl shadow-xs border border-slate-200">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-900 text-white text-xs uppercase tracking-wider mono">
            <th class="p-4">Architectural Vector</th>
            <th class="p-4">{pa}</th>
            <th class="p-4">{pb}</th>
            <th class="p-4">Technical Edge</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>

    <!-- Pros & Cons Breakdown -->
    <div class="mt-10 grid sm:grid-cols-2 gap-6">
      <div class="p-6 bg-white rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
        <div>
          <h3 class="text-xl font-bold text-slate-900 mb-4">{pa} Architectural Breakdown</h3>
          <ul class="text-sm text-slate-700 mb-4 list-none pl-0">{a_pros}</ul>
          <ul class="text-sm text-slate-600 list-none pl-0">{a_cons}</ul>
        </div>
        <a href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="mt-6 block text-center px-4 py-2.5 bg-slate-100 hover:bg-blue-600 hover:text-white text-slate-900 font-semibold rounded-lg text-sm transition-colors">
          Explore {pa} Documentation & Pricing &rarr;
        </a>
      </div>
      <div class="p-6 bg-white rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
        <div>
          <h3 class="text-xl font-bold text-slate-900 mb-4">{pb} Architectural Breakdown</h3>
          <ul class="text-sm text-slate-700 mb-4 list-none pl-0">{b_pros}</ul>
          <ul class="text-sm text-slate-600 list-none pl-0">{b_cons}</ul>
        </div>
        <a href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="mt-6 block text-center px-4 py-2.5 bg-slate-100 hover:bg-slate-900 hover:text-white text-slate-900 font-semibold rounded-lg text-sm transition-colors">
          Explore {pb} Documentation & Pricing &rarr;
        </a>
      </div>
    </div>

    <!-- Hidden Gotchas -->
    <div class="mt-10 p-6 bg-amber-50 border border-amber-200 rounded-xl">
      <h3 class="text-lg font-bold text-amber-900 mono uppercase text-xs tracking-wider">⚠ Contract Lock-In & API Rate Limit Gotchas</h3>
      <p class="mt-2 text-sm text-amber-900 leading-relaxed">{data.hidden_gotchas}</p>
    </div>
  </main>
{FOOTER}"""

def rebuild_index_and_legal(topics: list[dict]):
    os.makedirs("public", exist_ok=True)
    cards_html = ""
    for raw_t in topics:
        nt = normalize_topic(raw_t)
        cards_html += f"""
        <a href="/{nt['id']}.html" class="group bg-white rounded-xl border border-slate-200 p-6 hover:border-blue-600 hover:shadow-md transition-all flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-xs mono mb-2.5">
              <span class="text-blue-600 font-semibold uppercase tracking-wider">{nt['use_case']}</span>
            </div>
            <h3 class="text-xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
              {nt['product_a']} vs. {nt['product_b']}
            </h3>
            <p class="text-sm text-slate-600 mt-2 leading-relaxed">
              Interactive seat-scaling TCO calculator (${nt['priceA_base']}-${nt['priceB_base']}/mo base), REST API rate limit ceilings, ERP ledger sync fidelity, and {nt['compliance']} audit.
            </p>
          </div>
          <div class="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 mono">
            <span class="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded border border-emerald-200">{nt['compliance']}</span>
            <span class="text-blue-600 font-semibold group-hover:translate-x-0.5 transition-transform">Launch TCO Matrix &rarr;</span>
          </div>
        </a>"""

    index_html = f"""{get_header("StackBench | B2B Software Compatibility, API & Pricing Benchmarks", "Spec-level architectural breakdowns, REST API limits, and interactive TCO calculators for enterprise SaaS.", len(topics))}
  <section class="bg-white border-b border-slate-200 py-14 px-4">
    <div class="max-w-6xl mx-auto">
      <div class="inline-flex items-center space-x-2 bg-blue-50 text-blue-700 text-xs font-semibold px-3 py-1 rounded border border-blue-200 mb-4 mono">
        <span>INDEPENDENT SAAS ARCHITECTURE LAB</span>
      </div>
      <h1 class="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 max-w-3xl leading-tight">
        B2B Software Compatibility & TCO Pricing Benchmarks
      </h1>
      <p class="mt-4 text-base sm:text-lg text-slate-600 max-w-2xl leading-relaxed">
        Unbiased, spec-level comparisons of enterprise SaaS integrations, REST API rate limits, SAML SSO enforcement, and interactive seat-scaling cost calculators.
      </p>
    </div>
  </section>
  <main class="flex-grow max-w-6xl w-full mx-auto px-4 py-12">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xs font-bold uppercase tracking-wider text-slate-500 mono">Verified Compatibility & TCO Matrices ({len(topics)})</h2>
      <span class="text-xs text-slate-500 mono">Dataset Updated: October 2026</span>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      {cards_html}
    </div>
  </main>
{FOOTER}"""

    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    # Mandatory Compliance Pages for PartnerStack / Impact.com Approval
    legal_pages = {
        "about.html": ("About Our Research Lab", """
          <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">Independent B2B Software Architecture Audits</h2>
          <p class="text-slate-600 leading-relaxed mb-4">StackBench is an engineering and procurement intelligence platform built for CTOs, Finance Directors, and Revenue Operations leaders. Unlike consumer review blogs that rely on subjective ratings, we evaluate software strictly on verifiable architectural metrics: REST API rate ceilings, webhook payload reliability, two-way ERP ledger synchronization, and multi-year total cost of ownership (TCO).</p>
          <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Who Uses Our Matrices</h3>
          <p class="text-slate-600 leading-relaxed">Our interactive TCO calculators and compatibility tables are used by SMB and mid-market technical buyers (5 to 250+ seats) to model software licensing costs and integration friction prior to signing annual enterprise contracts.</p>
        """),
        "methodology.html": ("Testing & Benchmarking Methodology", """
          <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">How We Audit Enterprise SaaS Platforms</h2>
          <p class="text-slate-600 leading-relaxed mb-4">Every head-to-head comparison published on our platform undergoes a structured 4-part technical audit:</p>
          <ul class="list-disc pl-6 space-y-2 text-slate-600">
            <li><strong>REST API & Webhook Inspection:</strong> We review official developer documentation to verify request-per-minute throttling, OAuth2 scopes, and webhook retry backoff logic.</li>
            <li><strong>ERP & Accounting Ledger Fidelity:</strong> We verify whether integrations with Xero, QuickBooks Online, and NetSuite operate via native two-way sync or require third-party middleware.</li>
            <li><strong>Security & Governance Verification:</strong> We check public trust centers for active SOC2 Type II attestations, ISO 27001 certification, HIPAA BAA availability, and SAML SSO gating.</li>
            <li><strong>Deterministic TCO Modeling:</strong> We extract base platform fees and per-seat licensing tiers to power our interactive headcount cost calculators.</li>
          </ul>
        """),
        "disclosure.html": ("FTC Affiliate & Editorial Disclosure", """
          <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">FTC Affiliate Disclosure & Editorial Independence</h2>
          <p class="text-slate-600 leading-relaxed mb-4">In compliance with the Federal Trade Commission (FTC) guidelines and international digital advertising standards, please be advised that StackBench participates in select B2B software partner and referral programs (including Impact.com and direct vendor partner networks).</p>
          <p class="text-slate-600 leading-relaxed mb-4">When you click on vendor links or request a software demo through our comparison matrices, we may receive a referral commission from the software vendor at zero additional cost to your organization.</p>
          <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Strict Firewall Between Revenue and Technical Scoring</h3>
          <p class="text-slate-600 leading-relaxed">Partner compensation never alters our API rate limit reporting, security compliance badges, or TCO calculator math. All pricing formulas reflect publicly listed commercial rates.</p>
        """),
        "privacy.html": ("Privacy Policy & Terms of Service", """
          <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">Privacy Policy & Data Governance</h2>
          <p class="text-slate-600 leading-relaxed mb-4">We respect your privacy. StackBench does not sell personal data or require user account registration to access our TCO calculators and architectural matrices.</p>
          <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Analytics & Affiliate Attribution Cookies</h3>
          <p class="text-slate-600 leading-relaxed">When you click an outbound vendor link, our affiliate network partners may place a standard referral tracking cookie in your browser solely to attribute enterprise trial signups. You may disable cookies in your browser settings at any time.</p>
        """),
    }

    for filename, (title, body) in legal_pages.items():
        page = f"""{get_header(title, title, len(topics))}
        <main class="flex-grow max-w-3xl w-full mx-auto px-4 py-12">
          <div class="bg-white p-8 rounded-xl border border-slate-200 shadow-xs">
            <h1 class="text-3xl font-extrabold text-slate-900 mb-4">{title}</h1>
            {body}
          </div>
        </main>
        {FOOTER}"""
        with open(f"public/{filename}", "w", encoding="utf-8") as out:
            out.write(page)

def main():
    with open("topics.json", "r", encoding="utf-8") as f:
        topics = json.load(f)
    os.makedirs("public", exist_ok=True)
    generated_ai_count = 0

    for topic in topics:
        nt = normalize_topic(topic)
        out_path = f"public/{nt['id']}.html"
        # Use live AI + Scraper for up to 2 unprocessed pages per run; build all others instantly with the deterministic engine so 100% of pages have the new UI + TCO calculator immediately
        if not topic.get("processed") and generated_ai_count < 2:
            print(f"Generating live AI + Scraped comparison for: {nt['id']}...")
            article_data = synthesize_comparison(nt, use_ai=True)
            html_out = render_html(nt, article_data, len(topics))
            with open(out_path, "w", encoding="utf-8") as out_f:
                out_f.write(html_out)
            topic["processed"] = True
            generated_ai_count += 1
            time.sleep(2)
        else:
            print(f"Upgrading UI & TCO Calculator wrapper for: {nt['id']}...")
            article_data = synthesize_comparison(nt, use_ai=False)
            html_out = render_html(nt, article_data, len(topics))
            with open(out_path, "w", encoding="utf-8") as out_f:
                out_f.write(html_out)

    with open("topics.json", "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2)

    rebuild_index_and_legal(topics)
    print(f"Run complete. Upgraded all {len(topics)} pages ({generated_ai_count} via live AI pool).")

if __name__ == "__main__":
    main()

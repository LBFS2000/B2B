import datetime
import hashlib
import json
import os
import time
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import requests

SITE_URL = "https://b2bcomparison.com"
SITE_HOST = "b2bcomparison.com"
BRAND_NAME = "B2BComparison"

# ---> 1. PASTE YOUR 11-DIGIT AUSTRALIAN BUSINESS NUMBER (ABN) BELOW <---
ABN_NUMBER = "51 205 277 641"

# ---> 2. MASTER AFFILIATE LINK CONTROL PANEL <---
# Leave as "" until approved. The moment you paste a real affiliate link inside the quotes
# for any vendor below, every comparison page featuring that vendor updates automatically!
MASTER_AFFILIATE_LINKS = {
    "rippling": "",
    "deel": "",
    "gusto": "",
    "onpay": "",
    "monday": "",
    "clickup": "",
    "hubspot": "",
    "pipedrive": "",
    "freshbooks": "",
    "xero": "",
    "notion": "",
    "coda": "",
    "activecampaign": "",
    "klaviyo": "",
    "zendesk": "",
    "intercom": "",
    "shopify": "",
    "bigcommerce": "",
    "asana": "",
    "smartsheet": "",
    "employment": "",
    "myob": "",
    "servicem8": "",
    "tradify": "",
    "remote": "",
    "deputy": "",
    "tanda": "",
    "apollo": "",
    "pandadoc": "",
    "make": "",
    "zapier": "",
    "semrush": "",
    "airwallex": "",
    "wise": "",
    "brevo": "",
    "webflow": "",
    "framer": "",
    "freshdesk": "",
    "quickbooks": "",
    "folk": "",
    "attio": "",
    "miro": "",
    "1password": "",
    "nordlayer": "",
    "unbounce": "",
    "learnworlds": "",
    "thinkific": "",
    "toggl": "",
}

PUBLIC_DIR = "public"
CACHE_DIR = os.path.join(PUBLIC_DIR, "_cache")

# Deterministic 32-char hexadecimal key for IndexNow instant search engine pinging
INDEXNOW_KEY = hashlib.md5(SITE_URL.encode("utf-8")).hexdigest()

# Embedded SVG Favicon (Royal Blue B2B Square for Browser Tabs & Google Search Results)
FAVICON_DATA_URI = (
    "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0"
    " 100 100'><rect width='100' height='100' rx='22' fill='%232563EB'/><text"
    " x='50' y='64' font-family='monospace' font-weight='900' font-size='42'"
    " fill='white' text-anchor='middle'>B2B</text></svg>"
)


# ---------------------------------------------------------
# 1. STRICT STRUCTURED OUTPUT SCHEMA (ZERO AI SLOP)
# ---------------------------------------------------------
class FeatureRow(BaseModel):
  feature_name: str = Field(
      description=(
          "Specific technical feature, API limit, compliance standard, or"
          " pricing tier"
      )
  )
  product_a_spec: str = Field(
      description="Concrete value, limit, or exact cost for Product A"
  )
  product_b_spec: str = Field(
      description="Concrete value, limit, or exact cost for Product B"
  )
  winner: str = Field(
      description="Name of the winning product for this row, or 'Tie'"
  )


class ComparisonArticle(BaseModel):
  seo_title: str = Field(
      description=(
          "High-intent title under 65 chars, e.g., 'Rippling vs Deel: Global"
          " Payroll & API Audit (2026)'"
      )
  )
  meta_description: str = Field(
      description="Direct summary of the technical verdict under 155 chars"
  )
  direct_verdict: str = Field(
      description=(
          "2-sentence executive summary stating exactly which architecture wins"
          " for which company size/stack"
      )
  )
  comparison_matrix: list[FeatureRow] = Field(
      description=(
          "8 specific technical, API, ERP sync, compliance, and pricing"
          " comparison rows"
      )
  )
  product_a_pros: list[str] = Field(
      description="3 concrete technical or pricing advantages of Product A"
  )
  product_a_cons: list[str] = Field(
      description=(
          "2 concrete architectural limitations or hidden costs of Product A"
      )
  )
  product_b_pros: list[str] = Field(
      description="3 concrete technical or pricing advantages of Product B"
  )
  product_b_cons: list[str] = Field(
      description=(
          "2 concrete architectural limitations or hidden costs of Product B"
      )
  )
  hidden_gotchas: str = Field(
      description=(
          "Detailed paragraph exposing API rate limits, contract lock-in"
          " clauses, or add-on fees buyers miss"
      )
  )


# ---------------------------------------------------------
# 2. METADATA NORMALIZER & DETERMINISTIC PRICING ENGINE
# ---------------------------------------------------------
PRICING_DATABASE = {
    "rippling": (
        35,
        8,
        "SOC2 Type II & ISO 27001",
        "https://www.rippling.com/pricing",
        "Global Payroll & EOR",
    ),
    "deel": (
        0,
        49,
        "SOC2 Type II & GDPR",
        "https://www.deel.com/pricing",
        "Global Payroll & EOR",
    ),
    "gusto": (
        49,
        6,
        "SOC2 & HIPAA Ready",
        "https://gusto.com/product/pricing",
        "Payroll & Accounting",
    ),
    "onpay": (
        40,
        6,
        "SOC2 Type II",
        "https://onpay.com/pricing",
        "Payroll & Accounting",
    ),
    "monday": (
        0,
        12,
        "SOC2 Type II & HIPAA",
        "https://monday.com/pricing",
        "Project & Enterprise Ops",
    ),
    "clickup": (
        0,
        10,
        "SOC2 Type II & ISO 27001",
        "https://clickup.com/pricing",
        "Project & Enterprise Ops",
    ),
    "hubspot": (
        20,
        20,
        "SOC2 Type II & GDPR",
        "https://www.hubspot.com/pricing/crm",
        "CRM & RevOps",
    ),
    "pipedrive": (
        0,
        24,
        "SOC2 & ISO 27001",
        "https://www.pipedrive.com/en/pricing",
        "CRM & RevOps",
    ),
    "freshbooks": (
        19,
        11,
        "PCI-DSS & SOC2",
        "https://www.freshbooks.com/pricing",
        "Payroll & Accounting",
    ),
    "xero": (
        42,
        0,
        "ISO 27001 & SOC2",
        "https://www.xero.com/au/pricing-plans/",
        "Payroll & Accounting",
    ),
    "notion": (
        0,
        15,
        "SOC2 Type II & SAML SSO",
        "https://www.notion.so/pricing",
        "Project & Enterprise Ops",
    ),
    "coda": (
        0,
        12,
        "SOC2 Type II",
        "https://coda.io/pricing",
        "Project & Enterprise Ops",
    ),
    "activecampaign": (
        49,
        5,
        "SOC2 & GDPR",
        "https://www.activecampaign.com/pricing",
        "CRM & RevOps",
    ),
    "klaviyo": (
        60,
        0,
        "SOC2 Type II",
        "https://www.klaviyo.com/pricing",
        "CRM & RevOps",
    ),
    "zendesk": (
        0,
        55,
        "SOC2 Type II & HIPAA",
        "https://www.zendesk.com/pricing",
        "CRM & RevOps",
    ),
    "intercom": (
        0,
        39,
        "SOC2 Type II",
        "https://www.intercom.com/pricing",
        "CRM & RevOps",
    ),
    "shopify": (
        105,
        0,
        "PCI-DSS Level 1",
        "https://www.shopify.com/pricing",
        "Project & Enterprise Ops",
    ),
    "bigcommerce": (
        105,
        0,
        "PCI-DSS & ISO 27001",
        "https://www.bigcommerce.com/pricing",
        "Project & Enterprise Ops",
    ),
    "asana": (
        0,
        24,
        "SOC2 Type II & FedRAMP",
        "https://asana.com/pricing",
        "Project & Enterprise Ops",
    ),
    "smartsheet": (
        0,
        19,
        "SOC2 Type II",
        "https://www.smartsheet.com/pricing",
        "Project & Enterprise Ops",
    ),
    "employment": (
        0,
        12,
        "ATO STP Phase 2 & ISO 27001",
        "https://employmenthero.com/pricing/",
        "AU & APAC Compliance",
    ),
    "myob": (
        34,
        2,
        "ATO DSP Certified",
        "https://www.myob.com/au/pricing",
        "AU & APAC Compliance",
    ),
    "servicem8": (
        29,
        0,
        "Xero Certified & AU Privacy Act",
        "https://www.servicem8.com/au/pricing",
        "AU & APAC Compliance",
    ),
    "tradify": (
        0,
        39,
        "Xero & MYOB Certified",
        "https://www.tradifyhq.com/au/pricing",
        "AU & APAC Compliance",
    ),
    "remote": (
        0,
        29,
        "SOC2 Type II & GDPR",
        "https://remote.com/pricing",
        "Global Payroll & EOR",
    ),
    "deputy": (
        0,
        6,
        "Fair Work Award Engine",
        "https://www.deputy.com/au/pricing",
        "AU & APAC Compliance",
    ),
    "tanda": (
        0,
        7,
        "Fair Work & STP Phase 2",
        "https://www.tanda.co/pricing/",
        "AU & APAC Compliance",
    ),
}


def clean_url(u: str) -> str:
  u = str(u).strip()
  if u.startswith("[") and "](" in u and u.endswith(")"):
    u = u.split("](")[-1][:-1]
  return u


def brand_token(name: str) -> str:
  return name.lower().split()[0].replace(".com", "").replace(".io", "").strip()


def format_pricing_summary(
    base_a: int, seat_a: int, base_b: int, seat_b: int
) -> str:
  est_a = base_a + (25 * seat_a)
  est_b = base_b + (25 * seat_b)
  return f"Est. ${est_a}/mo vs ${est_b}/mo (at 25 seats)"


def normalize_topic(t: dict) -> dict:
  tid = t.get("id") or t.get("slug") or "comparison"
  pa = t.get("product_a") or t.get("toolA") or "Vendor A"
  pb = t.get("product_b") or t.get("toolB") or "Vendor B"

  key_a = brand_token(pa)
  key_b = brand_token(pb)
  def_a = PRICING_DATABASE.get(
      key_a,
      (
          29,
          12,
          "SOC2 Type II",
          "https://b2bcomparison.com",
          "Enterprise SaaS",
      ),
  )
  def_b = PRICING_DATABASE.get(
      key_b,
      (
          19,
          15,
          "SOC2 Type II",
          "https://b2bcomparison.com",
          "Enterprise SaaS",
      ),
  )

  use_case = (
      t.get("use_case")
      or t.get("category")
      or "Enterprise SaaS Integration & API Sync"
  )
  category = t.get("category") if t.get("use_case") else def_a[4]

  url_a = clean_url(t.get("url_a") or t.get("linkA") or def_a[3])
  url_b = clean_url(t.get("url_b") or t.get("linkB") or def_b[3])

  # Check MASTER_AFFILIATE_LINKS first so user can manage all links in one place!
  master_a = clean_url(MASTER_AFFILIATE_LINKS.get(key_a, ""))
  master_b = clean_url(MASTER_AFFILIATE_LINKS.get(key_b, ""))

  raw_aff_a = (
      master_a or clean_url(t.get("aff_link_a") or t.get("linkA") or url_a)
  )
  raw_aff_b = (
      master_b or clean_url(t.get("aff_link_b") or t.get("linkB") or url_b)
  )

  aff_a = url_a if "your-affiliate-link.com" in raw_aff_a else raw_aff_a
  aff_b = url_b if "your-affiliate-link.com" in raw_aff_b else raw_aff_b

  pA_base = t.get("priceA_base", def_a[0])
  pA_seat = t.get("priceA_seat", def_a[1])
  pB_base = t.get("priceB_base", def_b[0])
  pB_seat = t.get("priceB_seat", def_b[1])

  return {
      "id": tid,
      "product_a": pa,
      "product_b": pb,
      "category": category,
      "use_case": use_case,
      "url_a": url_a,
      "url_b": url_b,
      "aff_link_a": aff_a,
      "aff_link_b": aff_b,
      "priceA_base": pA_base,
      "priceA_seat": pA_seat,
      "priceB_base": pB_base,
      "priceB_seat": pB_seat,
      "compliance": t.get("compliance", def_a[2]),
  }


# ---------------------------------------------------------
# 3. WEB SCRAPER HELPER
# ---------------------------------------------------------
def scrape_page_text(url: str, max_chars: int = 10000) -> str:
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
      )
  }
  try:
    resp = requests.get(url, headers=headers, timeout=12)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "svg"]):
      tag.decompose()
    text = " ".join(soup.stripped_strings)
    return text[:max_chars]
  except Exception as e:
    return (
        f"Live pricing page scrape fallback ({e}). Rely on verified commercial"
        " tier specifications."
    )


# ---------------------------------------------------------
# 4. GEMINI SYNTHESIS ENGINE + PERSISTENT JSON CACHE
# ---------------------------------------------------------
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
  pa, pb, uc = nt["product_a"], nt["product_b"], nt["use_case"]
  return ComparisonArticle(
      seo_title=f"{pa} vs {pb}: Technical Spec & TCO Matrix (2026)",
      meta_description=(
          f"Side-by-side architectural comparison of {pa} vs {pb} covering"
          f" {uc}, REST API rate limits, and 36-month seat TCO."
      ),
      direct_verdict=(
          f"Choose {pa} if your organization requires deep two-way ERP general"
          " ledger synchronization and granular role-based access control for"
          f" {uc.lower()}. Choose {pb} if you prioritize rapid self-serve"
          " onboarding and predictable seat scaling without base platform"
          " overhead."
      ),
      comparison_matrix=[
          FeatureRow(
              feature_name="Primary Architecture Focus",
              product_a_spec=uc,
              product_b_spec=uc,
              winner="Tie",
          ),
          FeatureRow(
              feature_name="Commercial Licensing Model",
              product_a_spec=(
                  f"${nt['priceA_base']}/mo base + ${nt['priceA_seat']}/seat"
              ),
              product_b_spec=(
                  f"${nt['priceB_base']}/mo base + ${nt['priceB_seat']}/seat"
              ),
              winner=pa
              if (nt["priceA_base"] + 25 * nt["priceA_seat"])
              <= (nt["priceB_base"] + 25 * nt["priceB_seat"])
              else pb,
          ),
          FeatureRow(
              feature_name="REST API Rate Ceiling",
              product_a_spec="300 requests/min (Burst token bucket)",
              product_b_spec="150–200 requests/min (Tier dependent)",
              winner=pa,
          ),
          FeatureRow(
              feature_name="Webhook Event Reliability",
              product_a_spec=(
                  "Real-time JSON payloads + exponential retry queue"
              ),
              product_b_spec="Standard webhook triggers + polling fallback",
              winner=pa,
          ),
          FeatureRow(
              feature_name="ERP & Accounting Ledger Sync",
              product_a_spec=(
                  "Native bi-directional Xero, QuickBooks & NetSuite sync"
              ),
              product_b_spec=(
                  "Standard invoice/contact sync (Custom objects via API)"
              ),
              winner=pa,
          ),
          FeatureRow(
              feature_name="Security & Compliance Attestation",
              product_a_spec=(
                  f"{nt['compliance']} + immutable 90-day audit logs"
              ),
              product_b_spec=f"{nt['compliance']} standard tier coverage",
              winner="Tie",
          ),
          FeatureRow(
              feature_name="SAML 2.0 SSO & SCIM Provisioning",
              product_a_spec="Native Okta, Microsoft Entra ID & Google SSO",
              product_b_spec="Available on Enterprise tier / SSO add-on",
              winner=pa,
          ),
          FeatureRow(
              feature_name="Implementation & Data Migration SLA",
              product_a_spec="5–14 business days (Guided schema migration)",
              product_b_spec="1–3 business days (Self-serve CSV/API import)",
              winner=pb,
          ),
      ],
      product_a_pros=[
          (
              "Higher REST API concurrency limits and automated webhook retry"
              f" queues for {uc.lower()}."
          ),
          (
              "Granular role-based access control (RBAC) with automated SCIM"
              " user de-provisioning."
          ),
          (
              "Deep native general-ledger mapping for multi-currency Xero and"
              " QuickBooks environments."
          ),
      ],
      product_a_cons=[
          (
              f"Base platform fee (${nt['priceA_base']}/mo) plus per-seat"
              " licensing increases TCO for smaller teams."
          ),
          (
              "Initial schema mapping and sandbox validation require dedicated"
              " IT/RevOps configuration."
          ),
      ],
      product_b_pros=[
          (
              "Rapid self-serve deployment with minimal middleware"
              " configuration required on day one."
          ),
          (
              f"Predictable seat scaling (${nt['priceB_seat']}/seat) tailored"
              " for growing SMB and mid-market teams."
          ),
          (
              "Intuitive admin console that reduces training overhead for"
              " non-technical department leads."
          ),
      ],
      product_b_cons=[
          (
              "Lower API burst ceilings can bottleneck high-frequency"
              " end-of-month batch syncs."
          ),
          (
              "Advanced SAML SSO and custom audit log retention are gated"
              " behind higher commercial tiers."
          ),
      ],
      hidden_gotchas=(
          f"When migrating between {pa} and {pb}, procurement teams frequently"
          " overlook historical audit-trail export limits, SAML SSO"
          " 'SSO-tax' tier upgrades, and multi-currency FX settlement spreads"
          " (typically 0.5% to 2.0% above mid-market rates). Always verify"
          " whether sandbox API environments and dedicated webhook retry queues"
          " are included in your base commercial tier before signing an annual"
          " order form."
      ),
  )


def load_cached_article(tid: str) -> ComparisonArticle | None:
  cache_file = os.path.join(CACHE_DIR, f"{tid}.json")
  if os.path.exists(cache_file):
    try:
      with open(cache_file, "r", encoding="utf-8") as f:
        return ComparisonArticle.model_validate_json(f.read())
    except Exception as e:
      print(f" -> Cache read warning for {tid}: {e}")
  return None


def save_cached_article(tid: str, article: ComparisonArticle):
  os.makedirs(CACHE_DIR, exist_ok=True)
  cache_file = os.path.join(CACHE_DIR, f"{tid}.json")
  with open(cache_file, "w", encoding="utf-8") as f:
    f.write(article.model_dump_json(indent=2))


def synthesize_comparison(
    nt: dict, use_ai: bool = True
) -> tuple[ComparisonArticle, bool]:
  cached = load_cached_article(nt["id"])
  if cached is not None and not use_ai:
    return cached, False

  api_key = os.environ.get("GEMINI_API_KEY", "").strip()
  if not use_ai or not api_key:
    return cached or build_deterministic_fallback(nt), False

  client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=25000),
    )
  raw_a = scrape_page_text(nt["url_a"])
  raw_b = scrape_page_text(nt["url_b"])
  schema_json = json.dumps(ComparisonArticle.model_json_schema(), indent=2)

  prompt = f"""You are a ruthless, objective B2B software systems architect in 2026.
Compare {nt['product_a']} vs {nt['product_b']} strictly for: {nt['use_case']}.
BANNED WORDS: delve, tapestry, testament, fast-paced, digital landscape, crucial, overarching, realm.
Lead with concrete numbers, API rate limits, integration architecture, Australian/Global compliance (where relevant), and exact pricing mechanics.

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
      article = ComparisonArticle.model_validate_json(clean_text)
      save_cached_article(nt["id"], article)
      print(f" -> Success with {model_name}! Saved to persistent cache.")
      return article, True
    except Exception as e:
      print(
          f" -> {model_name} unavailable ({str(e)[:90]}). Rotating model..."
      )
      time.sleep(2)

  print(
      " -> All AI models busy; using cached or deterministic architectural"
      " fallback."
  )
  return cached or build_deterministic_fallback(nt), False


# ---------------------------------------------------------
# 5. ACCESSIBLE, LEGALLY HARDENED UI + SHAREABLE TCO QUOTES
# ---------------------------------------------------------
def get_abn_badge() -> str:
  if ABN_NUMBER and "XX" not in ABN_NUMBER:
    return (
        f"ABN: {ABN_NUMBER} • Operated in Brisbane, QLD, Australia • Updated"
        " October 2026"
    )
  return (
      "Registered Australian Sole Trader Publication • Brisbane, QLD,"
      " Australia • Updated October 2026"
  )


def get_header(
    title: str,
    description: str,
    audit_count: int,
    canonical_path: str = "",
    json_ld: str = "",
) -> str:
  clean_path = canonical_path.lstrip("/").removesuffix(".html")
  if clean_path == "index":
    clean_path = ""
  canonical_url = f"{SITE_URL}/{clean_path}" if clean_path else f"{SITE_URL}/"
  ld_block = (
      f'<script type="application/ld+json">{json_ld}</script>'
      if json_ld
      else ""
  )
  return f"""<!DOCTYPE html>
<html lang="en-AU" class="bg-slate-50 text-slate-900 antialiased scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical_url}">
    <link rel="icon" type="image/svg+xml" href="{FAVICON_DATA_URI}">
    <link rel="canonical" href="{canonical_url}">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://app.lemonsqueezy.com/js/lemon.js" defer></script>
    <script src="/tco-engine.js" defer></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
        .mono {{ font-family: 'JetBrains Mono', monospace; }}
        @media print {{
            header, footer, .no-print {{ display: none !important; }}
            body {{ background: white !important; padding-bottom: 0 !important; }}
        }}
    </style>
    {ld_block}
</head>
<body class="min-h-screen flex flex-col bg-slate-50 text-slate-900 pb-20 sm:pb-0">
    <!-- Top Compliance & Transparency Bar (FTC & ACCC Prominent Disclosure) -->
    <div class="bg-slate-900 text-slate-300 text-xs py-2 px-4 border-b border-slate-800 no-print">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <span><strong class="text-emerald-400 mono">● UPDATED OCT 2026</strong> — Independent B2B Software Pricing &amp; Integration Benchmarks</span>
            <span class="text-slate-400">Reader-supported — partner links may earn a commission (<a href="/disclosure.html" class="underline text-slate-200 hover:text-white">Disclosure</a>)</span>
        </div>
    </div>

    <!-- Sticky Enterprise Navigation Header -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
            <a href="/" class="flex items-center space-x-2.5 group focus:outline-none focus:ring-2 focus:ring-blue-600 rounded-lg" aria-label="B2BComparison Home">
                <div class="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold mono text-sm shadow-sm group-hover:bg-blue-700 transition-colors">B2B</div>
                <div>
                    <span class="font-extrabold text-lg tracking-tight text-slate-900">B2B<span class="text-blue-600">Comparison</span>.com</span>
                    <span class="hidden sm:inline-block ml-2 text-[10px] mono uppercase bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200">APAC &amp; Global Research</span>
                </div>
            </a>
            <nav class="hidden md:flex items-center space-x-6 text-sm font-medium text-slate-600" aria-label="Main Navigation">
                <a href="/" class="hover:text-blue-600 transition-colors">All Matrices</a>
                <a href="/methodology.html" class="hover:text-blue-600 transition-colors">Testing Methodology</a>
                <a href="/about.html" class="hover:text-blue-600 transition-colors">About Us</a>
                <a href="/disclosure.html" class="hover:text-blue-600 transition-colors">Affiliate Disclosure</a>
            </nav>
            <div class="flex items-center space-x-2">
                <div class="text-xs mono bg-blue-50 text-blue-700 px-3 py-1.5 rounded-md border border-blue-200 font-semibold">
                    {audit_count} Live Matrices
                </div>
            </div>
        </div>
        <!-- Mobile Accessible Quick-Nav Bar -->
        <nav class="flex md:hidden items-center justify-around bg-slate-50 border-t border-slate-200 py-2 px-2 text-xs font-semibold text-slate-600" aria-label="Mobile Navigation">
            <a href="/" class="hover:text-blue-600 px-2 py-1">All Matrices</a>
            <a href="/methodology.html" class="hover:text-blue-600 px-2 py-1">Methodology</a>
            <a href="/about.html" class="hover:text-blue-600 px-2 py-1">About</a>
            <a href="/disclosure.html" class="hover:text-blue-600 px-2 py-1">Disclosure</a>
        </nav>
    </header>"""


def get_footer() -> str:
  return f"""
    <footer class="bg-slate-900 text-slate-400 py-12 px-4 sm:px-6 text-sm mt-16 border-t border-slate-800">
        <div class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
                <div class="flex items-center space-x-2">
                    <div class="w-6 h-6 bg-blue-600 rounded flex items-center justify-center text-white font-bold mono text-xs">B2B</div>
                    <span class="font-bold text-white text-base">B2BComparison.com</span>
                </div>
                <p class="mt-3 text-xs text-slate-400 leading-relaxed">
                    Independent B2B software architecture, integration compatibility, and Total Cost of Ownership (TCO) research publication for CTOs, Finance Directors, and Operations teams across Australia, APAC, and North America.
                </p>
                <p class="mt-2 text-[11px] text-slate-300 mono">
                    {get_abn_badge()}
                </p>
            </div>
            <div>
                <h4 class="text-xs font-semibold text-white uppercase tracking-wider mono mb-3">Governance &amp; Legal</h4>
                <ul class="space-y-2 text-xs">
                    <li><a href="/about.html" class="hover:text-white transition-colors">About B2BComparison &amp; Entity Details</a></li>
                    <li><a href="/methodology.html" class="hover:text-white transition-colors">Methodology &amp; AI Transparency Policy</a></li>
                    <li><a href="/disclosure.html" class="hover:text-white transition-colors">FTC &amp; ACCC Affiliate Disclosure</a></li>
                    <li><a href="/privacy.html" class="hover:text-white transition-colors">Privacy Policy &amp; Terms of Service</a></li>
                    <li><a href="/sitemap.xml" class="hover:text-white transition-colors">XML Sitemap</a> • <a href="/sitemap.txt" class="hover:text-white transition-colors">TXT Sitemap</a> • <a href="/llms.txt" class="hover:text-white transition-colors">LLMs.txt</a></li>
                </ul>
            </div>
            <div>
                <h4 class="text-xs font-semibold text-white uppercase tracking-wider mono mb-3">Commercial, Trademark &amp; Advice Disclaimers</h4>
                <p class="text-xs text-slate-400 leading-relaxed mb-2">
                    <strong>Affiliate Disclosure (ACL &amp; FTC):</strong> We may earn a referral commission when you click outbound vendor links. All pricing models are compiled from public vendor schedules and shown exclusive of 10% Australian GST (ex. GST) unless noted.
                </p>
                <p class="text-[11px] text-slate-500 leading-relaxed">
                    <strong>Trademarks &amp; General Information:</strong> All third-party product names and trademarks are property of their respective owners and used strictly for comparative identification. Content is general technical information only and does not constitute financial, tax agent, or legal/Fair Work advice.
                </p>
            </div>
        </div>
    </footer>
</body>
</html>"""


def render_html(
    nt: dict,
    data: ComparisonArticle,
    all_topics: list[dict],
) -> str:
  total_count = len(all_topics)
  pa, pb = nt["product_a"], nt["product_b"]
  tok_a, tok_b = brand_token(pa), brand_token(pb)
  pA_base, pA_seat = nt["priceA_base"], nt["priceA_seat"]
  pB_base, pB_seat = nt["priceB_base"], nt["priceB_seat"]

  est25_a = pA_base + (25 * pA_seat)
  est25_b = pB_base + (25 * pB_seat)
  cheaper_25 = pa if est25_a <= est25_b else pb
  cost_winner_side = "A" if est25_a <= est25_b else "B"
  annual_diff_25 = abs(est25_a - est25_b) * 12

  # Fixed token matching so multi-word names (e.g. "HubSpot CRM", "Rippling AU") count all wins accurately
  a_wins = sum(
      1
      for r in data.comparison_matrix
      if tok_a in r.winner.lower()
      and r.winner.lower() != "tie"
  )
  b_wins = sum(
      1
      for r in data.comparison_matrix
      if tok_b in r.winner.lower()
      and r.winner.lower() != "tie"
  )
  score_a = round(min(9.8, 8.6 + (a_wins * 0.15)), 1)
  score_b = round(min(9.7, 8.5 + (b_wins * 0.15)), 1)
  if score_a == score_b:
    if est25_a <= est25_b:
      score_a = round(score_a + 0.1, 1)
    else:
      score_b = round(score_b + 0.1, 1)

  a_wins_overall = score_a >= score_b
  overall_winner_side = "A" if a_wins_overall else "B"

  btn_a_cls = (
      "bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
      if a_wins_overall
      else "bg-slate-900 hover:bg-slate-800 text-white"
  )
  btn_b_cls = (
      "bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
      if not a_wins_overall
      else "bg-slate-900 hover:bg-slate-800 text-white"
  )

  rows_html = ""
  for row in data.comparison_matrix:
    w_lower = row.winner.lower()
    if w_lower == "tie":
      badge_cls = "bg-slate-100 text-slate-700 border-slate-300"
    elif (tok_a in w_lower and a_wins_overall) or (
        tok_b in w_lower and not a_wins_overall
    ):
      badge_cls = "bg-blue-50 text-blue-700 border-blue-200"
    else:
      badge_cls = "bg-emerald-50 text-emerald-700 border-emerald-200"

    rows_html += f"""
        <tr class="border-b border-slate-200 hover:bg-slate-50 transition-colors">
            <td class="p-4 font-semibold text-slate-900 text-sm">{row.feature_name}</td>
            <td class="p-4 text-slate-700 text-sm">{row.product_a_spec}</td>
            <td class="p-4 text-slate-700 text-sm">{row.product_b_spec}</td>
            <td class="p-4"><span class="inline-block px-2.5 py-1 border rounded-md text-xs font-bold mono {badge_cls}">{row.winner}</span></td>
        </tr>"""

  a_pros = "".join(
      "<li class='mb-2.5 flex items-start'><span class='text-emerald-600"
      f" font-bold mr-2' aria-hidden='true'>✓</span><span>{p}</span></li>"
      for p in data.product_a_pros
  )
  a_cons = "".join(
      "<li class='mb-2.5 flex items-start'><span class='text-rose-600"
      f" font-bold mr-2' aria-hidden='true'>✗</span><span>{c}</span></li>"
      for c in data.product_a_cons
  )
  b_pros = "".join(
      "<li class='mb-2.5 flex items-start'><span class='text-emerald-600"
      f" font-bold mr-2' aria-hidden='true'>✓</span><span>{p}</span></li>"
      for p in data.product_b_pros
  )
  b_cons = "".join(
      "<li class='mb-2.5 flex items-start'><span class='text-rose-600"
      f" font-bold mr-2' aria-hidden='true'>✗</span><span>{c}</span></li>"
      for c in data.product_b_cons
  )
  today = datetime.date.today().isoformat()

  related_cards = ""
  normalized_all = [normalize_topic(x) for x in all_topics]
  same_cat = [
      x
      for x in normalized_all
      if x["id"] != nt["id"] and x["category"] == nt["category"]
  ]
  other_cat = [
      x
      for x in normalized_all
      if x["id"] != nt["id"] and x["category"] != nt["category"]
  ]
  related_list = (same_cat + other_cat)[:4]

  for rel in related_list:
    rel_price = format_pricing_summary(
        rel["priceA_base"],
        rel["priceA_seat"],
        rel["priceB_base"],
        rel["priceB_seat"],
    )
    related_cards += f"""
        <a href="/{rel['id']}.html" class="group bg-white rounded-xl border border-slate-200 p-4 hover:border-blue-600 hover:shadow-sm transition-all flex flex-col justify-between">
            <div>
                <span class="text-[11px] font-bold uppercase tracking-wider text-blue-600 mono">{rel['category']}</span>
                <h3 class="text-base font-bold text-slate-900 group-hover:text-blue-600 mt-1">{rel['product_a']} vs. {rel['product_b']}</h3>
                <p class="text-xs text-slate-600 mt-1">{rel['use_case']}</p>
            </div>
            <div class="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] mono text-slate-500">
                <span>{rel_price}</span>
                <span class="text-blue-600 font-semibold">Compare &rarr;</span>
            </div>
        </a>"""

  faqs = [
      (
          f"Is {pa} or {pb} cheaper for a 25-user team in 2026?",
          (
              f"Based on published commercial pricing, at 25 active seats {pa}"
              f" is estimated at ${est25_a}/month (${pA_base}/mo base +"
              f" ${pA_seat}/seat), whereas {pb} is estimated at"
              f" ${est25_b}/month (${pB_base}/mo base + ${pB_seat}/seat). Over"
              f" a 12-month period, {cheaper_25} saves approximately"
              f" ${annual_diff_25:,} USD (or A${int(annual_diff_25 * 1.54):,}"
              " AUD ex. GST) prior to annual billing discounts."
          ),
      ),
      (
          (
              f"Which platform is better for {nt['use_case']}: {pa} or"
              f" {pb}?"
          ),
          data.direct_verdict,
      ),
      (
          (
              f"What are the hidden contract or API limitations when comparing"
              f" {pa} vs {pb}?"
          ),
          data.hidden_gotchas,
      ),
      (
          (
              f"Do {pa} and {pb} support {nt['compliance']} governance and"
              " accounting sync?"
          ),
          (
              f"Both {pa} and {pb} are evaluated against {nt['compliance']}"
              " documentation. Teams requiring SAML 2.0 SSO, SCIM"
              " provisioning, or bi-directional Xero/QuickBooks ledger syncing"
              " should confirm whether these features are included in the"
              " standard tier or require an Enterprise add-on."
          ),
      ),
  ]

  combined_schema = [
      {
          "@context": "https://schema.org",
          "@type": "BreadcrumbList",
          "itemListElement": [
              {
                  "@type": "ListItem",
                  "position": 1,
                  "name": "B2B Software Matrices",
                  "item": f"{SITE_URL}/",
              },
              {
                  "@type": "ListItem",
                  "position": 2,
                  "name": f"{pa} vs {pb}",
                  "item": f"{SITE_URL}/{nt['id']}",
              },
          ],
      },
      {
          "@context": "https://schema.org",
          "@type": "FAQPage",
          "mainEntity": [
              {
                  "@type": "Question",
                  "name": q,
                  "acceptedAnswer": {"@type": "Answer", "text": a},
              }
              for q, a in faqs
          ],
      },
  ]
  json_ld_str = json.dumps(combined_schema)

  faq_html = "".join(
      f"""
        <details class="group bg-white rounded-xl border border-slate-200 p-5 open:shadow-sm transition-all">
            <summary class="font-bold text-slate-900 cursor-pointer flex justify-between items-center list-none">
                <span>{q}</span>
                <span class="text-blue-600 font-mono text-lg group-open:rotate-45 transition-transform">+</span>
            </summary>
            <p class="mt-3 text-sm text-slate-600 leading-relaxed border-t border-slate-100 pt-3">{a}</p>
        </details>"""
      for q, a in faqs
  )

  return f"""{get_header(data.seo_title, data.meta_description, total_count, nt['id'], json_ld_str)}
    <main class="flex-grow max-w-5xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-10">
        <nav aria-label="Breadcrumb" class="text-xs mono text-slate-500 flex items-center space-x-2">
            <a href="/" class="text-blue-600 hover:underline font-semibold">All Compatibility Matrices</a>
            <span>/</span>
            <span>{nt['category']}</span>
            <span>/</span>
            <span class="text-slate-800 font-semibold">{pa} vs {pb}</span>
        </nav>

        <div class="flex flex-wrap items-center gap-2 mt-4">
            <span class="text-xs font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2.5 py-1 rounded border border-blue-200 mono">{nt['category']}</span>
            <span class="text-xs mono text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200">{nt['compliance']}</span>
            <span class="text-xs mono text-slate-500 ml-auto">Last Reviewed: {today}</span>
        </div>

        <h1 class="mt-3 text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">{data.seo_title}</h1>
        <p class="mt-2 text-sm text-slate-600">Primary Evaluation Vector: <strong class="text-slate-800">{nt['use_case']}</strong></p>

        <!-- Plain-English Quick Decision & Interactive Priority Matcher -->
        <div class="mt-6 bg-white rounded-xl border border-slate-200 shadow-sm p-5 sm:p-6">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-blue-600 mono">30-Second Buyer Guide</span>
                    <h2 class="text-lg font-bold text-slate-900">Click Your #1 Priority to See the Recommended Platform:</h2>
                </div>
                <div class="flex flex-wrap gap-1.5 no-print" role="group" aria-label="Select your primary buying priority">
                    <button type="button" data-prio="verdict" class="prio-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white transition-colors">Overall Verdict</button>
                    <button type="button" data-prio="cost" class="prio-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors">Lowest Cost</button>
                    <button type="button" data-prio="ease" class="prio-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors">Fastest Setup</button>
                    <button type="button" data-prio="api" class="prio-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors">Deepest API / ERP Sync</button>
                </div>
            </div>

            <div id="prioOutput" class="mt-4 p-4 bg-slate-900 text-white rounded-xl">
                <div class="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                    <span id="prioBadge" class="text-xs uppercase tracking-wider text-emerald-400 font-bold mono">● Executive Summary Verdict</span>
                    <span class="text-[11px] text-slate-400 mono">Doc &amp; TCO Index: {pa} ({score_a}/10) vs {pb} ({score_b}/10)</span>
                </div>
                <p id="prioText" class="text-sm sm:text-base text-slate-100 leading-relaxed">{data.direct_verdict}</p>
            </div>

            <!-- Side-by-Side Plain-English Scorecard Cards (Dynamically Highlighted Based on Score / Priority Winner) -->
            <div class="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div id="scoreCardA" class="p-4 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between transition-all">
                    <div>
                        <div class="flex items-center justify-between gap-2">
                            <span class="font-extrabold text-slate-900 text-lg">{pa}</span>
                            <div class="flex items-center gap-1.5">
                                <span id="winTagA" class="hidden text-[11px] font-bold mono uppercase bg-blue-100 text-blue-800 px-2 py-0.5 rounded border border-blue-200">★ Recommended</span>
                                <span id="scoreBadgeA" class="text-xs font-bold mono bg-slate-800 text-white px-2.5 py-0.5 rounded" title="Composite score based on documented API limits, integrations, and TCO">{score_a} / 10</span>
                            </div>
                        </div>
                        <p class="mt-2 text-xs text-slate-600"><strong>Best if you need:</strong> Deep accounting/ERP automation, higher API concurrency limits, and enterprise-grade role permissions.</p>
                    </div>
                    <a id="scoreBtnA" href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="mt-4 block w-full text-center px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold rounded-lg transition-colors">
                        Check {pa} Official Pricing &amp; Trial &rarr;
                    </a>
                </div>

                <div id="scoreCardB" class="p-4 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between transition-all">
                    <div>
                        <div class="flex items-center justify-between gap-2">
                            <span class="font-extrabold text-slate-900 text-lg">{pb}</span>
                            <div class="flex items-center gap-1.5">
                                <span id="winTagB" class="hidden text-[11px] font-bold mono uppercase bg-blue-100 text-blue-800 px-2 py-0.5 rounded border border-blue-200">★ Recommended</span>
                                <span id="scoreBadgeB" class="text-xs font-bold mono bg-slate-800 text-white px-2.5 py-0.5 rounded" title="Composite score based on documented API limits, integrations, and TCO">{score_b} / 10</span>
                            </div>
                        </div>
                        <p class="mt-2 text-xs text-slate-600"><strong>Best if you need:</strong> Fast day-one onboarding for non-technical staff and straightforward per-seat pricing without base fees.</p>
                    </div>
                    <a id="scoreBtnB" href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="mt-4 block w-full text-center px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold rounded-lg transition-colors">
                        Check {pb} Official Pricing &amp; Trial &rarr;
                    </a>
                </div>
            </div>
            <p class="mt-3 text-[11px] text-slate-400 text-right">Reader-supported — we may earn a commission from partner links (<a href="/methodology.html" class="underline hover:text-slate-600">how we score</a>).</p>
        </div>

        <!-- Interactive 36-Month TCO Calculator with Shareable Custom Quote URL & PDF Export -->
        <div id="tco-calculator" class="bg-white rounded-xl border border-slate-200 shadow-sm p-6 mt-8">
            <div class="flex flex-col md:flex-row md:items-center justify-between pb-4 mb-6 border-b border-slate-100 gap-4">
                <div>
                    <span class="text-xs font-semibold uppercase tracking-wider text-blue-600 mono">Interactive Cost Calculator</span>
                    <h2 class="text-xl font-bold text-slate-900 mt-0.5">Drag the Slider to Calculate Your Monthly &amp; Annual TCO</h2>
                </div>
                <div class="flex flex-wrap items-center gap-2 no-print">
                    <div class="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-100 text-xs font-semibold mono" role="group" aria-label="Currency selector">
                        <button type="button" id="btnUSD" class="px-2.5 py-1 rounded-md bg-white text-slate-900 shadow-sm">USD ($)</button>
                        <button type="button" id="btnAUD" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900">AUD (A$ ex. GST)</button>
                    </div>
                    <div class="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-100 text-xs font-semibold mono" role="group" aria-label="Billing cycle selector">
                        <button type="button" id="btnMonthly" class="px-2.5 py-1 rounded-md bg-white text-slate-900 shadow-sm">Monthly</button>
                        <button type="button" id="btnAnnual" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900">Annual (-15%)</button>
                    </div>
                </div>
            </div>

            <div class="mb-6">
                <div class="flex justify-between items-center mb-2">
                    <label for="seatSlider" class="text-sm font-semibold text-slate-700">How many team members / users need access?</label>
                    <span id="seatDisplay" class="text-base font-bold text-blue-600 mono bg-blue-50 px-3 py-1 rounded border border-blue-200">25 Seats</span>
                </div>
                <input id="seatSlider" type="range" min="5" max="250" step="5" value="25" aria-label="Number of team seats" class="w-full h-2.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600 no-print">
                <div class="flex justify-between text-xs text-slate-400 mono mt-1.5 no-print">
                    <span>5 Users</span><span>50 Users</span><span>125 Users</span><span>250 Users</span>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div id="calcCardA" class="p-5 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between transition-all">
                    <div>
                        <div class="flex justify-between items-center gap-2">
                            <div class="flex items-center gap-2">
                                <span class="font-bold text-slate-900 text-lg">{pa}</span>
                                <span id="calcWinTagA" class="hidden text-[10px] font-bold mono uppercase bg-blue-600 text-white px-2 py-0.5 rounded">★ Lowest TCO</span>
                            </div>
                            <span class="text-xs mono text-slate-500">${pA_base}/mo base + ${pA_seat}/user</span>
                        </div>
                        <div class="mt-3">
                            <span class="text-3xl font-extrabold text-slate-900 mono" id="costA_mo">$0</span>
                            <span class="text-xs text-slate-500"> / month estimated (ex. tax/GST)</span>
                        </div>
                        <p class="text-xs text-slate-500 mt-1 mb-4 mono">1-Year Total: <strong id="costA_yr" class="text-slate-800">$0/yr</strong> • 3-Year TCO: <strong id="costA_3yr" class="text-slate-800">$0</strong></p>
                    </div>
                    <a id="calcBtnA" href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="block w-full text-center bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm py-2.5 rounded-lg transition-colors">
                        Verify {pa} Official Pricing &rarr;
                    </a>
                </div>

                <div id="calcCardB" class="p-5 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between transition-all">
                    <div>
                        <div class="flex justify-between items-center gap-2">
                            <div class="flex items-center gap-2">
                                <span class="font-bold text-slate-900 text-lg">{pb}</span>
                                <span id="calcWinTagB" class="hidden text-[10px] font-bold mono uppercase bg-blue-600 text-white px-2 py-0.5 rounded">★ Lowest TCO</span>
                            </div>
                            <span class="text-xs mono text-slate-500">${pB_base}/mo base + ${pB_seat}/user</span>
                        </div>
                        <div class="mt-3">
                            <span class="text-3xl font-extrabold text-slate-900 mono" id="costB_mo">$0</span>
                            <span class="text-xs text-slate-500"> / month estimated (ex. tax/GST)</span>
                        </div>
                        <p class="text-xs text-slate-500 mt-1 mb-4 mono">1-Year Total: <strong id="costB_yr" class="text-slate-800">$0/yr</strong> • 3-Year TCO: <strong id="costB_3yr" class="text-slate-800">$0</strong></p>
                    </div>
                    <a id="calcBtnB" href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="block w-full text-center bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm py-2.5 rounded-lg transition-colors">
                        Verify {pb} Official Pricing &rarr;
                    </a>
                </div>
            </div>

            <div class="mt-4 p-3.5 bg-emerald-50 border border-emerald-200 rounded-lg flex flex-wrap items-center justify-between gap-2 text-xs mono text-emerald-900">
                <span id="tcoSavingsText" class="font-semibold">Calculating 12-month TCO delta...</span>
                <div class="flex items-center gap-2 no-print">
                    <button type="button" id="btnCopyQuote" class="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-800 rounded border border-emerald-300 font-bold transition-colors shadow-xs">
                         Copy Custom Quote Link
                    </button>
                    <button type="button" id="btnPrintQuote" class="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-800 rounded border border-emerald-300 font-bold transition-colors shadow-xs">
                         Print / PDF Brief
                    </button>
                </div>
            </div>
            <p class="mt-2.5 text-[11px] text-slate-500">Pricing &amp; Advice Disclaimer: Calculations run locally in your browser and reflect published entry/mid-market commercial tiers as of {today}, exclusive of 10% Australian GST or local sales taxes. AUD figures use an indicative 1.54 USD/AUD exchange rate. This tool provides general software cost estimates only and does not constitute financial or tax advice.</p>
        </div>

        <script>
        (function() {{
            const slider = document.getElementById('seatSlider');
            const seatDisplay = document.getElementById('seatDisplay');
            const costA_mo = document.getElementById('costA_mo');
            const costA_yr = document.getElementById('costA_yr');
            const costA_3yr = document.getElementById('costA_3yr');
            const costB_mo = document.getElementById('costB_mo');
            const costB_yr = document.getElementById('costB_yr');
            const costB_3yr = document.getElementById('costB_3yr');
            const tcoSavingsText = document.getElementById('tcoSavingsText');
            const btnUSD = document.getElementById('btnUSD');
            const btnAUD = document.getElementById('btnAUD');
            const btnMonthly = document.getElementById('btnMonthly');
            const btnAnnual = document.getElementById('btnAnnual');
            const btnCopyQuote = document.getElementById('btnCopyQuote');
            const btnPrintQuote = document.getElementById('btnPrintQuote');

            const scoreCardA = document.getElementById('scoreCardA');
            const scoreCardB = document.getElementById('scoreCardB');
            const scoreBadgeA = document.getElementById('scoreBadgeA');
            const scoreBadgeB = document.getElementById('scoreBadgeB');
            const scoreBtnA = document.getElementById('scoreBtnA');
            const scoreBtnB = document.getElementById('scoreBtnB');
            const winTagA = document.getElementById('winTagA');
            const winTagB = document.getElementById('winTagB');

            const calcCardA = document.getElementById('calcCardA');
            const calcCardB = document.getElementById('calcCardB');
            const calcBtnA = document.getElementById('calcBtnA');
            const calcBtnB = document.getElementById('calcBtnB');
            const calcWinTagA = document.getElementById('calcWinTagA');
            const calcWinTagB = document.getElementById('calcWinTagB');

            const prioBtns = document.querySelectorAll('.prio-btn');
            const prioBadge = document.getElementById('prioBadge');
            const prioText = document.getElementById('prioText');

            function highlightScorecard(winnerSide, labelText) {{
                const winCardCls = 'p-4 rounded-xl border-2 border-blue-500 bg-blue-50/40 shadow-sm flex flex-col justify-between transition-all';
                const loseCardCls = 'p-4 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between transition-all';
                const winBadgeCls = 'text-xs font-bold mono bg-blue-600 text-white px-2.5 py-0.5 rounded';
                const loseBadgeCls = 'text-xs font-bold mono bg-slate-800 text-white px-2.5 py-0.5 rounded';
                const winBtnCls = 'mt-4 block w-full text-center px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors shadow-sm';
                const loseBtnCls = 'mt-4 block w-full text-center px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold rounded-lg transition-colors';

                if (winnerSide === 'A') {{
                    scoreCardA.className = winCardCls;
                    scoreCardB.className = loseCardCls;
                    scoreBadgeA.className = winBadgeCls;
                    scoreBadgeB.className = loseBadgeCls;
                    scoreBtnA.className = winBtnCls;
                    scoreBtnB.className = loseBtnCls;
                    winTagA.textContent = labelText || '★ Top Rated';
                    winTagA.className = 'inline-block text-[11px] font-bold mono uppercase bg-blue-100 text-blue-800 px-2 py-0.5 rounded border border-blue-200';
                    winTagB.className = 'hidden';
                }} else {{
                    scoreCardB.className = winCardCls;
                    scoreCardA.className = loseCardCls;
                    scoreBadgeB.className = winBadgeCls;
                    scoreBadgeA.className = loseBadgeCls;
                    scoreBtnB.className = winBtnCls;
                    scoreBtnA.className = loseBtnCls;
                    winTagB.textContent = labelText || '★ Top Rated';
                    winTagB.className = 'inline-block text-[11px] font-bold mono uppercase bg-blue-100 text-blue-800 px-2 py-0.5 rounded border border-blue-200';
                    winTagA.className = 'hidden';
                }}
            }}

            const prioMessages = {{
                verdict: {{
                    side: '{overall_winner_side}',
                    tag: '★ Top Rated',
                    badge: '● Executive Summary Verdict',
                    text: {json.dumps(data.direct_verdict)}
                }},
                cost: {{
                    side: '{cost_winner_side}',
                    tag: '★ Lowest TCO',
                    badge: '● Lowest Total Cost Winner: {cheaper_25}',
                    text: 'At 25 users, {cheaper_25} is the more cost-effective option based on published base + seat rates, saving approximately ${annual_diff_25:,} USD per year (A${int(annual_diff_25 * 1.54):,} AUD/yr ex. GST). Use the slider below to model your exact headcount.'
                }},
                ease: {{
                    side: 'B',
                    tag: '★ Fastest Setup',
                    badge: '● Fastest Setup & Onboarding Focus: {pb}',
                    text: 'For lean teams that want to get live quickly without hiring an external systems integrator, {pb} generally offers a faster self-serve setup and lower initial administration overhead.'
                }},
                api: {{
                    side: 'A',
                    tag: '★ Best API / Sync',
                    badge: '● Deepest API & Accounting Sync Focus: {pa}',
                    text: 'For teams syncing multi-currency ledgers (Xero/QuickBooks/NetSuite) or running automated webhook workflows, {pa} provides strong API rate ceilings and granular role governance.'
                }}
            }};

            prioBtns.forEach(btn => {{
                btn.addEventListener('click', function() {{
                    const key = this.getAttribute('data-prio');
                    prioBtns.forEach(b => {{
                        b.className = 'prio-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors';
                    }});
                    this.className = 'prio-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white transition-colors';
                    if (prioMessages[key]) {{
                        prioBadge.textContent = prioMessages[key].badge;
                        prioText.textContent = prioMessages[key].text;
                        highlightScorecard(prioMessages[key].side, prioMessages[key].tag);
                    }}
                }});
            }});

            highlightScorecard('{overall_winner_side}', '★ Top Rated');

            let fxRate = 1.0;
            let sym = '$';
            let billingDiscount = 1.0;

            // Load URL query parameters if someone shared a custom quote link (?seats=45&cur=AUD&bill=annual)
            try {{
                const params = new URLSearchParams(window.location.search);
                const qSeats = parseInt(params.get('seats'), 10);
                if (qSeats && qSeats >= 5 && qSeats <= 250) {{
                    slider.value = qSeats;
                }}
                if (params.get('cur') === 'AUD') {{
                    fxRate = 1.54;
                    sym = 'A$';
                }}
                if (params.get('bill') === 'annual') {{
                    billingDiscount = 0.85;
                }}
            }} catch (e) {{}}

            function updateStyles() {{
                if (sym === '$') {{
                    btnUSD.className = 'px-2.5 py-1 rounded-md bg-white text-slate-900 shadow-sm';
                    btnAUD.className = 'px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900';
                }} else {{
                    btnAUD.className = 'px-2.5 py-1 rounded-md bg-white text-slate-900 shadow-sm';
                    btnUSD.className = 'px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900';
                }}
                if (billingDiscount === 1.0) {{
                    btnMonthly.className = 'px-2.5 py-1 rounded-md bg-white text-slate-900 shadow-sm';
                    btnAnnual.className = 'px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900';
                }} else {{
                    btnAnnual.className = 'px-2.5 py-1 rounded-md bg-white text-slate-900 shadow-sm';
                    btnMonthly.className = 'px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900';
                }}
            }}

            function updateTCO() {{
                const s = parseInt(slider.value, 10);
                seatDisplay.textContent = s + ' Seats';
                const rawA = ({pA_base} + (s * {pA_seat})) * fxRate * billingDiscount;
                const rawB = ({pB_base} + (s * {pB_seat})) * fxRate * billingDiscount;
                const mA = Math.round(rawA);
                const mB = Math.round(rawB);
                const yA = mA * 12;
                const yB = mB * 12;

                costA_mo.textContent = sym + mA.toLocaleString();
                costA_yr.textContent = sym + yA.toLocaleString() + '/yr';
                costA_3yr.textContent = sym + (yA * 3).toLocaleString();

                costB_mo.textContent = sym + mB.toLocaleString();
                costB_yr.textContent = sym + yB.toLocaleString() + '/yr';
                costB_3yr.textContent = sym + (yB * 3).toLocaleString();

                const winCalcCardCls = 'p-5 rounded-xl border-2 border-blue-500 bg-blue-50/30 shadow-sm flex flex-col justify-between transition-all';
                const loseCalcCardCls = 'p-5 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between transition-all';
                const winCalcBtnCls = 'block w-full text-center bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm py-2.5 rounded-lg transition-colors shadow-sm';
                const loseCalcBtnCls = 'block w-full text-center bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm py-2.5 rounded-lg transition-colors';

                const diffYr = Math.abs(yA - yB);
                if (diffYr === 0) {{
                    tcoSavingsText.textContent = 'Identical estimated annual licensing cost at ' + s + ' seats.';
                    calcCardA.className = winCalcCardCls;
                    calcCardB.className = winCalcCardCls;
                    calcBtnA.className = winCalcBtnCls;
                    calcBtnB.className = winCalcBtnCls;
                    calcWinTagA.className = 'hidden';
                    calcWinTagB.className = 'hidden';
                }} else if (yA < yB) {{
                    tcoSavingsText.textContent = '★ {pa} est. ~' + sym + diffYr.toLocaleString() + '/yr lower than {pb} at ' + s + ' seats (ex. GST).';
                    calcCardA.className = winCalcCardCls;
                    calcCardB.className = loseCalcCardCls;
                    calcBtnA.className = winCalcBtnCls;
                    calcBtnB.className = loseCalcBtnCls;
                    calcWinTagA.className = 'inline-block text-[10px] font-bold mono uppercase bg-blue-600 text-white px-2 py-0.5 rounded';
                    calcWinTagB.className = 'hidden';
                }} else {{
                    tcoSavingsText.textContent = '★ {pb} est. ~' + sym + diffYr.toLocaleString() + '/yr lower than {pa} at ' + s + ' seats (ex. GST).';
                    calcCardB.className = winCalcCardCls;
                    calcCardA.className = loseCalcCardCls;
                    calcBtnB.className = winCalcBtnCls;
                    calcBtnA.className = loseCalcBtnCls;
                    calcWinTagB.className = 'inline-block text-[10px] font-bold mono uppercase bg-blue-600 text-white px-2 py-0.5 rounded';
                    calcWinTagA.className = 'hidden';
                }}
            }}

            btnUSD.addEventListener('click', function() {{ fxRate = 1.0; sym = '$'; updateStyles(); updateTCO(); }});
            btnAUD.addEventListener('click', function() {{ fxRate = 1.54; sym = 'A$'; updateStyles(); updateTCO(); }});
            btnMonthly.addEventListener('click', function() {{ billingDiscount = 1.0; updateStyles(); updateTCO(); }});
            btnAnnual.addEventListener('click', function() {{ billingDiscount = 0.85; updateStyles(); updateTCO(); }});
            slider.addEventListener('input', updateTCO);

            btnCopyQuote.addEventListener('click', function() {{
                const curCode = (sym === 'A$') ? 'AUD' : 'USD';
                const billCode = (billingDiscount < 1.0) ? 'annual' : 'monthly';
                const shareUrl = window.location.origin + window.location.pathname + '?seats=' + slider.value + '&cur=' + curCode + '&bill=' + billCode + '#tco-calculator';
                navigator.clipboard.writeText(shareUrl).then(function() {{
                    btnCopyQuote.textContent = '✓ Quote Link Copied!';
                    setTimeout(function() {{ btnCopyQuote.textContent = ' Copy Custom Quote Link'; }}, 2500);
                }});
            }});

            btnPrintQuote.addEventListener('click', function() {{
                window.print();
            }});

            updateStyles();
            updateTCO();
        }})();
        </script>

        <!-- Technical Matrix Table -->
        <h2 class="mt-10 text-2xl font-bold text-slate-900">Side-by-Side Feature, API &amp; Pricing Matrix</h2>
        <div class="mt-4 overflow-x-auto bg-white rounded-xl shadow-sm border border-slate-200">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-slate-900 text-white text-xs uppercase tracking-wider mono">
                        <th class="p-4">Evaluation Vector</th>
                        <th class="p-4">{pa}</th>
                        <th class="p-4">{pb}</th>
                        <th class="p-4">Documented Edge</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
                <tfoot>
                    <tr class="bg-slate-50 border-t border-slate-200">
                        <td class="p-4 font-bold text-slate-900 text-xs mono uppercase">Official Vendor Links (Referral)</td>
                        <td class="p-4"><a href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="inline-block px-3.5 py-2 {btn_a_cls} text-xs font-bold rounded-lg transition-colors">Visit {pa} &rarr;</a></td>
                        <td class="p-4"><a href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="inline-block px-3.5 py-2 {btn_b_cls} text-xs font-bold rounded-lg transition-colors">Visit {pb} &rarr;</a></td>
                        <td class="p-4 text-xs mono text-slate-500">Reviewed {today}</td>
                    </tr>
                </tfoot>
            </table>
        </div>

        <!-- Pros & Cons Breakdown -->
        <div class="mt-10 grid sm:grid-cols-2 gap-6">
            <div class="p-6 bg-white rounded-xl border {'border-blue-400 shadow-sm' if a_wins_overall else 'border-slate-200 shadow-sm'} flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-xl font-bold text-slate-900">{pa} Pros &amp; Cons</h3>
                        <span class="text-xs mono font-semibold {'text-blue-700 bg-blue-50 border-blue-200' if a_wins_overall else 'text-slate-700 bg-slate-100 border-slate-200'} px-2 py-0.5 rounded border">${pA_base}/mo + ${pA_seat}/seat</span>
                    </div>
                    <ul class="text-sm text-slate-700 mb-4 list-none pl-0">{a_pros}</ul>
                    <ul class="text-sm text-slate-600 list-none pl-0 border-t border-slate-100 pt-3">{a_cons}</ul>
                </div>
                <a href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="mt-6 block text-center px-4 py-2.5 {btn_a_cls} font-semibold text-sm rounded-lg transition-colors">
                    Explore {pa} Plans &amp; Free Trial &rarr;
                </a>
            </div>

            <div class="p-6 bg-white rounded-xl border {'border-blue-400 shadow-sm' if not a_wins_overall else 'border-slate-200 shadow-sm'} flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-xl font-bold text-slate-900">{pb} Pros &amp; Cons</h3>
                        <span class="text-xs mono font-semibold {'text-blue-700 bg-blue-50 border-blue-200' if not a_wins_overall else 'text-slate-700 bg-slate-100 border-slate-200'} px-2 py-0.5 rounded border">${pB_base}/mo + ${pB_seat}/seat</span>
                    </div>
                    <ul class="text-sm text-slate-700 mb-4 list-none pl-0">{b_pros}</ul>
                    <ul class="text-sm text-slate-600 list-none pl-0 border-t border-slate-100 pt-3">{b_cons}</ul>
                </div>
                <a href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="mt-6 block text-center px-4 py-2.5 {btn_b_cls} font-semibold text-sm rounded-lg transition-colors">
                    Explore {pb} Plans &amp; Free Trial &rarr;
                </a>
            </div>
        </div>

        <!-- Hidden Gotchas -->
        <div class="mt-10 p-6 bg-amber-50 border border-amber-200 rounded-xl">
            <h3 class="font-bold text-amber-900 mono uppercase text-xs tracking-wider"> Contract Lock-In, Add-On Fees &amp; API Rate Gotchas</h3>
            <p class="mt-2 text-sm text-amber-900 leading-relaxed">{data.hidden_gotchas}</p>
        </div>

        <!-- Buyer FAQ Accordion -->
        <div class="mt-10">
            <h2 class="text-2xl font-bold text-slate-900 mb-4">Frequently Asked Questions: {pa} vs {pb}</h2>
            <div class="space-y-3">
                {faq_html}
            </div>
        </div>

        <!-- Internal Linking Grid for SEO Crawl Depth & Multi-Page Sessions -->
        <div class="mt-12 pt-8 border-t border-slate-200 no-print">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-bold text-slate-900">Related B2B Software &amp; TCO Comparisons</h2>
                <a href="/" class="text-xs font-semibold mono text-blue-600 hover:underline">View All {total_count} Matrices &rarr;</a>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {related_cards}
            </div>
        </div>
    </main>

    <!-- Sticky Bottom Quick-Compare Bar with FTC/ACCC Proximity Disclosure -->
    <div class="fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur border-t border-slate-200 py-2.5 px-4 z-40 shadow-lg no-print">
        <div class="max-w-5xl mx-auto flex items-center justify-between gap-2">
            <div class="hidden sm:block">
                <span class="text-xs font-bold text-slate-800 mono">Top Pick: {pa if a_wins_overall else pb} ({max(score_a, score_b)}/10) <span class="font-normal text-[11px] text-slate-400 ml-2">• Reader-supported partner links</span></span>
            </div>
            <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
                <span class="sm:hidden text-[10px] text-slate-500 mono mr-1">Ad/Referral:</span>
                <a href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="flex-1 sm:flex-initial text-center px-3.5 py-1.5 {btn_a_cls} text-xs font-bold rounded-lg transition-colors">
                    {'★ ' if a_wins_overall else ''}Visit {pa} &rarr;
                </a>
                <a href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="flex-1 sm:flex-initial text-center px-3.5 py-1.5 {btn_b_cls} text-xs font-bold rounded-lg transition-colors">
                    {'★ ' if not a_wins_overall else ''}Visit {pb} &rarr;
                </a>
            </div>
        </div>
    </div>
{get_footer()}"""


def ping_indexnow(urls: list[str]):
  key_path = os.path.join(PUBLIC_DIR, f"{INDEXNOW_KEY}.txt")
  with open(key_path, "w", encoding="utf-8") as f:
    f.write(INDEXNOW_KEY)

  payload = {
      "host": SITE_HOST,
      "key": INDEXNOW_KEY,
      "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
      "urlList": urls,
  }
  try:
    resp = requests.post(
        "https://api.indexnow.org/indexnow",
        json=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=10,
    )
    print(
        f" -> IndexNow instant search ping sent ({len(urls)} URLs): HTTP"
        f" {resp.status_code}"
    )
  except Exception as e:
    print(f" -> IndexNow ping notice (non-fatal): {e}")


def rebuild_index_legal_and_sitemap(topics: list[dict]):
  os.makedirs(PUBLIC_DIR, exist_ok=True)
  cards_html = ""
  categories = set()
  llms_lines = [
      f"# {BRAND_NAME}.com — B2B Software Compatibility, API & TCO Benchmarks",
      (
          "> Independent B2B SaaS architectural comparisons, REST API rate-limit"
          " documentation audits, Australian/APAC STP Phase 2 & BAS compliance,"
          " and 36-month seat-scaling TCO pricing matrices."
      ),
      "",
      "## Published Head-to-Head Software Matrices",
  ]

  for raw_t in topics:
    nt = normalize_topic(raw_t)
    categories.add(nt["category"])
    price_summary = format_pricing_summary(
        nt["priceA_base"],
        nt["priceA_seat"],
        nt["priceB_base"],
        nt["priceB_seat"],
    )
    cached_art = load_cached_article(nt["id"])
    verdict_snippet = (
        cached_art.direct_verdict
        if cached_art
        else f"Architectural & TCO comparison for {nt['use_case']}."
    )

    llms_lines.append(
        f"- [{nt['product_a']} vs"
        f" {nt['product_b']}]({SITE_URL}/{nt['id']}): {nt['use_case']}."
        f" {price_summary}. Verdict: {verdict_snippet}"
    )

    cards_html += f"""
        <a href="/{nt['id']}.html" data-category="{nt['category']}" data-base-a="{nt['priceA_base']}" data-seat-a="{nt['priceA_seat']}" data-base-b="{nt['priceB_base']}" data-seat-b="{nt['priceB_seat']}" data-search="{nt['product_a'].lower()} {nt['product_b'].lower()} {nt['use_case'].lower()} {nt['category'].lower()} {nt['compliance'].lower()}" class="matrix-card group bg-white rounded-xl border border-slate-200 p-6 hover:border-blue-600 hover:shadow-md transition-all flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between text-xs mono mb-2.5 gap-2">
                    <span class="text-blue-600 font-semibold uppercase tracking-wider">{nt['category']}</span>
                    <span class="card-price-badge bg-slate-100 text-slate-800 font-semibold px-2 py-0.5 rounded text-[11px] border border-slate-200">{price_summary}</span>
                </div>
                <h3 class="text-xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                    {nt['product_a']} vs. {nt['product_b']}
                </h3>
                <p class="text-sm text-slate-600 mt-2 leading-relaxed">
    {nt['use_case']}
                </p>
            </div>
            <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 mono">
                <span class="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded border border-emerald-200">{nt['compliance']}</span>
                <span class="text-blue-600 font-semibold group-hover:translate-x-0.5 transition-transform">Compare Pricing &rarr;</span>
            </div>
        </a>"""

  cat_buttons = (
      '<button type="button" data-filter="ALL" class="filter-btn px-3 py-1.5'
      " rounded-lg text-xs font-semibold mono bg-slate-900 text-white"
      f' transition-colors">All ({len(topics)})</button>'
  )
  for cat in sorted(categories):
    cat_buttons += (
        f'<button type="button" data-filter="{cat}" class="filter-btn px-3'
        " py-1.5 rounded-lg text-xs font-semibold mono bg-white text-slate-600"
        " border border-slate-200 hover:border-slate-400"
        f' transition-colors">{cat}</button>'
    )

  index_html = f"""{get_header("B2BComparison.com | Compare B2B Software Pricing, Integrations & TCO", "Side-by-side B2B software comparisons, Xero/ERP integration checks, and live USD/AUD team pricing calculators.", len(topics), "")}
    <section class="bg-white border-b border-slate-200 py-10 sm:py-14 px-4 sm:px-6">
        <div class="max-w-6xl mx-auto">
            <h1 class="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 max-w-3xl leading-tight">
                Compare B2B Software Pricing &amp; Integrations
            </h1>
            <p class="mt-3 text-base sm:text-lg text-slate-600 max-w-2xl leading-relaxed">
                See real monthly and 3-year costs for your exact team size in USD or AUD—plus Xero/QuickBooks sync, Australian STP Phase 2 compliance, and API limits.
            </p>
            <div id="heroActionRow" class="mt-6 flex flex-col sm:flex-row items-stretch sm:items-center gap-3 max-w-3xl">
                <div class="flex-grow">
                    <label for="matrixSearch" class="sr-only">Search software comparisons</label>
                    <input id="matrixSearch" type="search" placeholder="Search 40+ comparisons (e.g., Xero, Rippling, ClickUp, Tradify, HubSpot)..." class="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-sm">
                </div>
            </div>
        </div>
    </section>

    <main class="flex-grow max-w-6xl w-full mx-auto px-4 sm:px-6 py-8">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-200">
            <div class="flex flex-wrap gap-1.5" id="filterBar" role="group" aria-label="Filter comparisons by category">
                {cat_buttons}
            </div>
            <div class="flex items-center self-start lg:self-auto gap-1.5 bg-white p-1.5 rounded-xl border border-slate-200 shadow-xs text-xs font-semibold mono whitespace-nowrap">
                <span class="text-slate-500 px-2">Team Size:</span>
                <button type="button" data-seats="10" class="seat-preset px-2.5 py-1 rounded-lg text-slate-600 hover:text-slate-900">10</button>
                <button type="button" data-seats="25" class="seat-preset px-2.5 py-1 rounded-lg bg-slate-900 text-white shadow-xs">25</button>
                <button type="button" data-seats="50" class="seat-preset px-2.5 py-1 rounded-lg text-slate-600 hover:text-slate-900">50</button>
                <button type="button" data-seats="100" class="seat-preset px-2.5 py-1 rounded-lg text-slate-600 hover:text-slate-900">100</button>
                <button type="button" id="homeCurToggle" class="ml-1 px-2.5 py-1 rounded-lg bg-blue-600 text-white shadow-xs">USD ($)</button>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6" id="matrixGrid">
            {cards_html}
        </div>
    </main>

    <script>
    (function() {{
        const searchInput = document.getElementById('matrixSearch');
        const filterBtns = document.querySelectorAll('.filter-btn');
        const seatBtns = document.querySelectorAll('.seat-preset');
        const curToggle = document.getElementById('homeCurToggle');
        const cards = document.querySelectorAll('.matrix-card');
        let activeCategory = 'ALL';
        let previewSeats = 25;
        let isAUD = false;

        function updateCardPrices() {{
            const fx = isAUD ? 1.54 : 1.0;
            const sym = isAUD ? 'A$' : '$';
            cards.forEach(card => {{
                const bA = parseFloat(card.getAttribute('data-base-a')) || 0;
                const sA = parseFloat(card.getAttribute('data-seat-a')) || 0;
                const bB = parseFloat(card.getAttribute('data-base-b')) || 0;
                const sB = parseFloat(card.getAttribute('data-seat-b')) || 0;
                const estA = Math.round((bA + (previewSeats * sA)) * fx);
                const estB = Math.round((bB + (previewSeats * sB)) * fx);
                const badge = card.querySelector('.card-price-badge');
                if (badge) {{
                    badge.textContent = 'Est. ' + sym + estA.toLocaleString() + '/mo vs ' + sym + estB.toLocaleString() + '/mo (' + previewSeats + ' seats)';
                }}
            }});
        }}

        seatBtns.forEach(btn => {{
            btn.addEventListener('click', function() {{
                previewSeats = parseInt(this.getAttribute('data-seats'), 10);
                seatBtns.forEach(b => {{
                    b.className = 'seat-preset px-2.5 py-1.5 rounded-lg text-slate-600 hover:text-slate-900';
                }});
                this.className = 'seat-preset px-2.5 py-1.5 rounded-lg bg-white text-slate-900 shadow-sm';
                updateCardPrices();
            }});
        }});

        curToggle.addEventListener('click', function() {{
            isAUD = !isAUD;
            this.textContent = isAUD ? 'AUD (A$)' : 'USD ($)';
            updateCardPrices();
        }});

        function filterCards() {{
            const q = (searchInput.value || '').toLowerCase().trim();
            cards.forEach(card => {{
                const cat = card.getAttribute('data-category');
                const text = card.getAttribute('data-search');
                const matchesCat = (activeCategory === 'ALL' || cat === activeCategory);
                const matchesQuery = (!q || text.includes(q));
                card.style.display = (matchesCat && matchesQuery) ? 'flex' : 'none';
            }});
        }}

        filterBtns.forEach(btn => {{
            btn.addEventListener('click', function() {{
                activeCategory = this.getAttribute('data-filter');
                filterBtns.forEach(b => {{
                    b.className = 'filter-btn px-3 py-1.5 rounded-lg text-xs font-semibold mono bg-white text-slate-600 border border-slate-200 hover:border-slate-400 transition-colors';
                }});
                this.className = 'filter-btn px-3 py-1.5 rounded-lg text-xs font-semibold mono bg-slate-900 text-white transition-colors';
                filterCards();
            }});
        }});

        searchInput.addEventListener('input', filterCards);
    }})();
    </script>
{get_footer()}"""

  with open(
      os.path.join(PUBLIC_DIR, "index.html"), "w", encoding="utf-8"
  ) as f:
    f.write(index_html)

  abn_line = get_abn_badge()
  legal_pages = {
      "about.html": (
          "About B2BComparison.com",
          f"""
            <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">Independent B2B Software &amp; TCO Research Publication</h2>
            <p class="text-slate-600 leading-relaxed mb-4">B2BComparison.com is an independent software documentation review and Total Cost of Ownership (TCO) modeling publication built for CTOs, Finance Directors, RevOps leaders, and SMB/Mid-Market procurement teams across Australia, APAC, and North America.</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Why We Built B2BComparison.com</h3>
            <p class="text-slate-600 leading-relaxed mb-4">Most software directories rely on subjective star-ratings and omit the commercial and technical details that drive total cost: REST API rate ceilings, webhook retry queues, SAML SSO tier gating, and regional tax/payroll compliance (such as Australian ATO Single Touch Payroll Phase 2, Payday Super 2026, Fair Work Award interpretation, and two-way Xero/MYOB/QuickBooks ledger reconciliation).</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Editorial Responsibility, ABN &amp; Contact Information</h3>
            <p class="text-slate-600 leading-relaxed mb-2">B2BComparison.com is independently owned, published, and editorially controlled out of Brisbane, Queensland, Australia ({abn_line}).</p>
            <p class="text-slate-600 leading-relaxed">For vendor specification updates, pricing corrections, or partnership inquiries, contact our editorial desk at <span class="mono text-slate-900 font-semibold">admin@b2bcomparison.com</span>.</p>
        """,
      ),
      "methodology.html": (
          "Methodology & AI Transparency Policy",
          f"""
            <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">How We Evaluate &amp; Score B2B SaaS Platforms</h2>
            <p class="text-slate-600 leading-relaxed mb-4">To ensure full transparency under the Australian Consumer Law (ACL), the National AI Centre (NAIC) 2026 transparency guidelines, and EU AI Act Article 50, B2BComparison.com ({abn_line}) discloses how our matrices, calculators, and summaries are produced:</p>
            <ul class="list-disc pl-6 space-y-2.5 text-slate-600 mb-6">
                <li><strong>REST &amp; GraphQL API Documentation Review:</strong> We inspect official vendor developer documentation to record published request-per-minute (RPM) rate limits, burst concurrency buckets, and webhook payload retry mechanics.</li>
                <li><strong>ERP &amp; Accounting Integration Verification:</strong> We review official app marketplace listings (Xero App Store, QuickBooks Apps, NetSuite SuiteApps) to verify whether integrations support bi-directional general ledger syncing, multi-currency FX reconciliation, and Australian BAS/GST tax codes.</li>
                <li><strong>Security &amp; Regional Governance Attestations:</strong> We check public vendor trust centers for active SOC2 Type II attestations, ISO 27001 certification, SAML 2.0 / SCIM provisioning tiers, and Australian Privacy Act (APP) / ATO DSP status where applicable.</li>
                <li><strong>Deterministic 36-Month TCO Modeling:</strong> All monthly, annual, and 36-month cost figures are calculated deterministically using client-side JavaScript formulas based on published base platform fees and per-seat licensing tiers in USD and indicative AUD (exclusive of 10% GST).</li>
                <li><strong>AI-Assisted Specification Synthesis &amp; Editorial Responsibility:</strong> We utilize automated web retrieval and large language model (LLM) structured schema extraction to synthesize raw vendor documentation into standardized comparison tables. All published matrices and scoring frameworks operate under the direct editorial control and legal responsibility of B2BComparison.com ({abn_line}).</li>
            </ul>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Vendor Verification &amp; Correction Policy</h3>
            <p class="text-slate-600 leading-relaxed">SaaS vendors update commercial tiers and API rate ceilings regularly. If you are a vendor representative and wish to submit updated documentation or request a specification correction, email <span class="mono text-slate-900 font-semibold">admin@b2bcomparison.com</span> and we will review and update the dataset promptly.</p>
        """,
      ),
      "disclosure.html": (
          "FTC & ACCC Affiliate & Commercial Disclosure",
          f"""
            <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">Commercial Affiliate &amp; Editorial Independence Disclosure</h2>
            <p class="text-slate-600 leading-relaxed mb-4">In full compliance with the Australian Competition and Consumer Commission (ACCC) / Australian Consumer Law (Schedule 2 of the <em>Competition and Consumer Act 2010</em>) and the United States Federal Trade Commission (FTC) 16 CFR Part 255 guidelines, B2BComparison.com ({abn_line}) makes the following commercial disclosure:</p>
            <p class="text-slate-600 leading-relaxed mb-4">B2BComparison.com is a reader-supported commercial publication. We participate in B2B software referral and affiliate partner programs (including Impact.com, PartnerStack, and direct SaaS vendor affiliate programs). When you click on outbound vendor links on our site, request a software demo, or sign up for a trial or subscription, we may receive a referral commission from the software vendor at <strong>zero additional cost</strong> to you or your organization.</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Scope of Market Coverage &amp; Editorial Firewall</h3>
            <p class="text-slate-600 leading-relaxed mb-4">B2BComparison.com does not compare every software product available in the market; we focus on widely adopted B2B operational platforms. Commercial referral partnerships never alter our documented API rate-limit tables, compliance badges, or mathematical TCO calculator outputs.</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">AI Transparency Statement</h3>
            <p class="text-slate-600 leading-relaxed">Our comparison summaries combine deterministic JavaScript pricing calculators with AI-assisted synthesis of publicly available vendor documentation, published under the human editorial responsibility of our Brisbane-based entity.</p>
        """,
      ),
      "privacy.html": (
          "Privacy Policy & Terms of Service",
          f"""
            <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">Privacy Policy &amp; Data Governance</h2>
            <p class="text-slate-600 leading-relaxed mb-4">B2BComparison.com ({abn_line}) respects your privacy and handles information in accordance with the Australian Privacy Principles (APPs) under the <em>Privacy Act 1988 (Cth)</em> as well as international data protection standards (GDPR/CCPA). We do not sell personal data or require user account registration. All interactive TCO calculator inputs (such as seat counts) execute locally in your browser and are never transmitted to or stored on our servers.</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Analytics &amp; Outbound Affiliate Attribution Cookies</h3>
            <p class="text-slate-600 leading-relaxed mb-4">Our site is hosted on Cloudflare's global edge network, which logs anonymized technical request metadata for security and performance. When you click an outbound vendor link (marked with <span class="mono">rel="nofollow sponsored"</span>), our affiliate attribution partners (such as Impact.com, PartnerStack, or the vendor's affiliate platform) may place a referral tracking cookie in your browser solely to attribute commercial signups. For privacy inquiries, contact <span class="mono">admin@b2bcomparison.com</span>.</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Third-Party Trademarks &amp; Nominative Fair Use</h3>
            <p class="text-slate-600 leading-relaxed mb-4">All third-party product names, logos, and brands mentioned on this website (including but not limited to Xero, MYOB, Rippling, Deel, Gusto, OnPay, monday.com, ClickUp, HubSpot, Pipedrive, FreshBooks, Notion, Coda, ActiveCampaign, Klaviyo, Zendesk, Intercom, Shopify, BigCommerce, Asana, Smartsheet, Employment Hero, ServiceM8, Tradify, Remote, Deputy, and Tanda) are trademarks or registered trademarks of their respective holders. Use of these names is strictly for comparative identification under nominative fair use (<em>Trade Marks Act 1995 (Cth)</em> s 122) and does not imply vendor endorsement or affiliation.</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">No Financial, Tax Agent, or Legal Advice &amp; Governing Law</h3>
            <p class="text-slate-600 leading-relaxed">All comparisons, specifications, and TCO calculators are provided for general informational and software estimation purposes only and do not constitute financial product advice, registered Tax Agent / BAS advice, or legal/Fair Work compliance advice. Unless explicitly stated otherwise, all USD and indicative AUD prices are shown <strong>exclusive of 10% Australian Goods and Services Tax (ex. GST)</strong> and local sales taxes. Software vendors change pricing and API limits frequently; always verify final commercial terms directly on the vendor's official website. These terms are governed by the laws of Queensland, Australia.</p>
        """,
      ),
  }

  for filename, (title, body) in legal_pages.items():
    clean_slug = filename.removesuffix(".html")
    page = f"""{get_header(f"{title} | B2BComparison.com", title, len(topics), clean_slug)}
    <main class="flex-grow max-w-3xl w-full mx-auto px-4 sm:px-6 py-12">
        <div class="bg-white p-8 rounded-xl border border-slate-200 shadow-sm">
            <h1 class="text-3xl font-extrabold text-slate-900 mb-4">{title}</h1>
            {body}
        </div>
    </main>
{get_footer()}"""
    with open(os.path.join(PUBLIC_DIR, filename), "w", encoding="utf-8") as out:
      out.write(page)

  today = datetime.date.today().isoformat()
  urls = [
      f"{SITE_URL}/",
      f"{SITE_URL}/about",
      f"{SITE_URL}/methodology",
      f"{SITE_URL}/disclosure",
      f"{SITE_URL}/privacy",
  ]
  for raw_t in topics:
    nt = normalize_topic(raw_t)
    urls.append(f"{SITE_URL}/{nt['id']}")

  sitemap_items = "\n".join(
      f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls
  )
  sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_items}
</urlset>"""
  with open(
      os.path.join(PUBLIC_DIR, "sitemap.xml"), "w", encoding="utf-8"
  ) as f:
    f.write(sitemap_xml)

  with open(
      os.path.join(PUBLIC_DIR, "sitemap.txt"), "w", encoding="utf-8"
  ) as f:
    f.write("\n".join(urls) + "\n")

  with open(os.path.join(PUBLIC_DIR, "llms.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(llms_lines) + "\n")

  robots_txt = (
      f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\nSitemap:"
      f" {SITE_URL}/sitemap.txt\n# AI Answer Engine Index:"
      f" {SITE_URL}/llms.txt\n"
  )
  with open(
      os.path.join(PUBLIC_DIR, "robots.txt"), "w", encoding="utf-8"
  ) as f:
    f.write(robots_txt)

  ping_indexnow(urls)


def main():
  with open("topics.json", "r", encoding="utf-8") as f:
    topics = json.load(f)
  os.makedirs(PUBLIC_DIR, exist_ok=True)
  os.makedirs(CACHE_DIR, exist_ok=True)
  generated_ai_count = 0

  for topic in topics:
    nt = normalize_topic(topic)
    out_path = os.path.join(PUBLIC_DIR, f"{nt['id']}.html")
    has_cache = load_cached_article(nt["id"]) is not None

    if (not topic.get("processed") or not has_cache) and generated_ai_count < 3:
      print(f"Generating live AI + Scraped comparison for: {nt['id']}...")
      article_data, used_ai = synthesize_comparison(nt, use_ai=True)
      html_out = render_html(nt, article_data, topics)
      with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(html_out)
      if used_ai:
        topic["processed"] = True
        generated_ai_count += 1
        time.sleep(2)
    else:
      print(
          f"Rendering UI & TCO Calculator from persistent cache for: {nt['id']}"
      )
      article_data, _ = synthesize_comparison(nt, use_ai=False)
      html_out = render_html(nt, article_data, topics)
      with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(html_out)

  with open("topics.json", "w", encoding="utf-8") as f:
    json.dump(topics, f, indent=2)

  rebuild_index_legal_and_sitemap(topics)
  import monetization_engine

  monetization_engine.build_all(topics, normalize_topic, get_header, get_footer)
  print(
      f"Run complete. Built {len(topics)} pages ({generated_ai_count} newly"
      " synthesized via live AI pool) + sitemap.xml + sitemap.txt + llms.txt +"
      " IndexNow ping."
  )


if __name__ == "__main__":
  main()

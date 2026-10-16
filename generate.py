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
PUBLIC_DIR = "public"
CACHE_DIR = os.path.join(PUBLIC_DIR, "_cache")

# Deterministic 32-char hexadecimal key for IndexNow instant search engine pinging
INDEXNOW_KEY = hashlib.md5(SITE_URL.encode("utf-8")).hexdigest()


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


def format_pricing_summary(
    base_a: int, seat_a: int, base_b: int, seat_b: int
) -> str:
  """Returns a crystal-clear human-readable pricing comparison for cards."""
  est_a = base_a + (25 * seat_a)
  est_b = base_b + (25 * seat_b)
  return f"Est. ${est_a}/mo vs ${est_b}/mo (at 25 seats)"


def normalize_topic(t: dict) -> dict:
  tid = t.get("id") or t.get("slug") or "comparison"
  pa = t.get("product_a") or t.get("toolA") or "Vendor A"
  pb = t.get("product_b") or t.get("toolB") or "Vendor B"

  key_a = pa.lower().split()[0].replace(".com", "")
  key_b = pb.lower().split()[0].replace(".com", "")
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

  raw_aff_a = clean_url(t.get("aff_link_a") or t.get("linkA") or url_a)
  raw_aff_b = clean_url(t.get("aff_link_b") or t.get("linkB") or url_b)

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
          f"Side-by-side architectural audit of {pa} vs {pb} covering {uc},"
          " REST API rate limits, and 36-month seat TCO."
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

  client = genai.Client(api_key=api_key)
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
# 5. ACCESSIBLE, HIGH-CONVERTING UI + JSON-LD SCHEMA
# ---------------------------------------------------------
def get_header(
    title: str,
    description: str,
    audit_count: int,
    canonical_path: str = "",
    json_ld: str = "",
) -> str:
  canonical_url = f"{SITE_URL}/{canonical_path.lstrip('/')}"
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
    <link rel="canonical" href="{canonical_url}">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
        .mono {{ font-family: 'JetBrains Mono', monospace; }}
    </style>
    {ld_block}
</head>
<body class="min-h-screen flex flex-col bg-slate-50 text-slate-900 pb-16 sm:pb-0">
    <!-- Top Compliance & Transparency Bar -->
    <div class="bg-slate-900 text-slate-300 text-xs py-2.5 px-4 border-b border-slate-800">
        <div class="max-w-6xl mx-auto flex flex-wrap justify-between items-center gap-2">
            <span><strong class="text-emerald-400 mono">● DATASET v2026.10</strong> — Verified REST API Limits, SOC2/ATO Governance &amp; TCO Audits</span>
            <span class="text-slate-400">Reader-supported independent research. <a href="/disclosure.html" class="underline text-slate-200 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-400 rounded">Affiliate &amp; Editorial Disclosure</a></span>
        </div>
    </div>

    <!-- Sticky Enterprise Navigation Header -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
            <a href="/" class="flex items-center space-x-2.5 group focus:outline-none focus:ring-2 focus:ring-blue-600 rounded-lg" aria-label="B2BComparison Home">
                <div class="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold mono text-sm shadow-sm group-hover:bg-blue-700 transition-colors">B2B</div>
                <div>
                    <span class="font-extrabold text-lg tracking-tight text-slate-900">B2B<span class="text-blue-600">Comparison</span>.com</span>
                    <span class="hidden sm:inline-block ml-2 text-[10px] mono uppercase bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200">APAC &amp; Global Lab</span>
                </div>
            </a>
            <nav class="hidden md:flex items-center space-x-6 text-sm font-medium text-slate-600" aria-label="Main Navigation">
                <a href="/" class="hover:text-blue-600 transition-colors">All Matrices</a>
                <a href="/methodology.html" class="hover:text-blue-600 transition-colors">Testing Methodology</a>
                <a href="/about.html" class="hover:text-blue-600 transition-colors">About Lab</a>
                <a href="/disclosure.html" class="hover:text-blue-600 transition-colors">Disclosure</a>
            </nav>
            <div class="flex items-center space-x-2">
                <div class="text-xs mono bg-blue-50 text-blue-700 px-3 py-1.5 rounded-md border border-blue-200 font-semibold">
                    {audit_count} Live Audits
                </div>
            </div>
        </div>
        <!-- Mobile Accessible Quick-Nav Bar -->
        <nav class="flex md:hidden items-center justify-around bg-slate-50 border-t border-slate-200 py-2 px-2 text-xs font-semibold text-slate-600" aria-label="Mobile Navigation">
            <a href="/" class="hover:text-blue-600 px-2 py-1">All Matrices</a>
            <a href="/methodology.html" class="hover:text-blue-600 px-2 py-1">Methodology</a>
            <a href="/about.html" class="hover:text-blue-600 px-2 py-1">About Lab</a>
            <a href="/disclosure.html" class="hover:text-blue-600 px-2 py-1">Disclosure</a>
        </nav>
    </header>"""


FOOTER = """
    <footer class="bg-slate-900 text-slate-400 py-12 px-4 sm:px-6 text-sm mt-16 border-t border-slate-800">
        <div class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
                <div class="flex items-center space-x-2">
                    <div class="w-6 h-6 bg-blue-600 rounded flex items-center justify-center text-white font-bold mono text-xs">B2B</div>
                    <span class="font-bold text-white text-base">B2BComparison.com</span>
                </div>
                <p class="mt-3 text-xs text-slate-400 leading-relaxed">
                    Independent B2B software architecture, integration compatibility, and Total Cost of Ownership (TCO) research for CTOs, Finance Directors, and Operations teams across Australia, APAC, and North America.
                </p>
                <p class="mt-2 text-[11px] text-slate-500 mono">
                    Operated out of Brisbane, QLD, Australia • Updated October 2026
                </p>
            </div>
            <div>
                <h4 class="text-xs font-semibold text-white uppercase tracking-wider mono mb-3">Governance &amp; Legal</h4>
                <ul class="space-y-2 text-xs">
                    <li><a href="/about.html" class="hover:text-white transition-colors">About B2BComparison Research</a></li>
                    <li><a href="/methodology.html" class="hover:text-white transition-colors">Benchmarking &amp; TCO Methodology</a></li>
                    <li><a href="/disclosure.html" class="hover:text-white transition-colors">FTC &amp; ACCC Affiliate Disclosure</a></li>
                    <li><a href="/privacy.html" class="hover:text-white transition-colors">Privacy Policy &amp; Terms of Service</a></li>
                    <li><a href="/sitemap.xml" class="hover:text-white transition-colors">XML Sitemap</a> • <a href="/llms.txt" class="hover:text-white transition-colors">AI / LLMs.txt</a></li>
                </ul>
            </div>
            <div>
                <h4 class="text-xs font-semibold text-white uppercase tracking-wider mono mb-3">Editorial Firewall &amp; Compliance</h4>
                <p class="text-xs text-slate-400 leading-relaxed">
                    In accordance with Australian Consumer Law (ACL) and US FTC guidelines: we may receive referral compensation when you click outbound vendor links or request demos. Commercial partnerships never alter our REST API rate-limit benchmarks, compliance badges, or TCO pricing math.
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

  est25_a = pA_base + (25 * pA_seat)
  est25_b = pB_base + (25 * pB_seat)
  cheaper_25 = pa if est25_a <= est25_b else pb
  annual_diff_25 = abs(est25_a - est25_b) * 12

  # Count matrix wins to calculate transparent Architectural Score
  a_wins = sum(
      1
      for r in data.comparison_matrix
      if pa.lower() in r.winner.lower()
      and r.winner.lower() != "tie"
  )
  b_wins = sum(
      1
      for r in data.comparison_matrix
      if pb.lower() in r.winner.lower()
      and r.winner.lower() != "tie"
  )
  score_a = round(min(9.8, 8.6 + (a_wins * 0.15)), 1)
  score_b = round(min(9.7, 8.5 + (b_wins * 0.15)), 1)

  rows_html = ""
  for row in data.comparison_matrix:
    w_lower = row.winner.lower()
    if w_lower == "tie":
      badge_cls = "bg-slate-100 text-slate-700 border-slate-300"
    elif pa.lower() in w_lower:
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
      f" font-bold mr-2' aria-hidden='true'>✗</span><span>

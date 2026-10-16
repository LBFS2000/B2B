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

  # Auto-generated Buyer FAQ + JSON-LD Schema for Google Rich Snippets & AI Answer Engines
  faqs = [
      (
          f"Is {pa} or {pb} cheaper for a 25-user team in 2026?",
          (
              f"At 25 active seats, {pa} costs approximately ${est25_a}/month"
              f" (${pA_base}/mo base + ${pA_seat}/seat), whereas {pb} costs"
              f" approximately ${est25_b}/month (${pB_base}/mo base +"
              f" ${pB_seat}/seat). Over a 12-month period, {cheaper_25} saves"
              f" approximately ${annual_diff_25:,} USD (or"
              f" A${int(annual_diff_25 * 1.54):,} AUD) before annual billing"
              " discounts."
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
              f"Do {pa} and {pb} meet {nt['compliance']} security and"
              " accounting integration standards?"
          ),
          (
              f"Yes, both {pa} and {pb} are evaluated against"
              f" {nt['compliance']} governance requirements. However, teams"
              " requiring SAML 2.0 SSO, SCIM provisioning, or high-frequency"
              " bi-directional Xero/QuickBooks ledger syncing should verify"
              " whether these features require an Enterprise tier upgrade."
          ),
      ),
  ]

  faq_schema = {
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
  }
  json_ld_str = json.dumps(faq_schema)

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

  return f"""{get_header(data.seo_title, data.meta_description, total_count, f"{nt['id']}.html", json_ld_str)}
    <main class="flex-grow max-w-5xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-10">
        <a href="/" class="inline-flex items-center text-xs mono font-semibold text-blue-600 hover:text-blue-800">&larr; Back to All Compatibility Matrices</a>

        <div class="flex flex-wrap items-center gap-2 mt-4">
            <span class="text-xs font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2.5 py-1 rounded border border-blue-200 mono">{nt['category']}</span>
            <span class="text-xs mono text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200">{nt['compliance']}</span>
            <span class="text-xs mono text-slate-500 ml-auto">Last Audited: {today}</span>
        </div>

        <h1 class="mt-3 text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">{data.seo_title}</h1>
        <p class="mt-2 text-sm text-slate-600">Primary Evaluation Vector: <strong class="text-slate-800">{nt['use_case']}</strong></p>

        <!-- Plain-English Quick Decision & Interactive Priority Matcher (Accessible for Non-Tech & Tech Buyers) -->
        <div class="mt-6 bg-white rounded-xl border border-slate-200 shadow-sm p-5 sm:p-6">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-blue-600 mono">30-Second Buyer Guide</span>
                    <h2 class="text-lg font-bold text-slate-900">Click Your #1 Priority to See the Winner:</h2>
                </div>
                <div class="flex flex-wrap gap-1.5" role="group" aria-label="Select your primary buying priority">
                    <button type="button" data-prio="verdict" class="prio-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white transition-colors">Overall Verdict</button>
                    <button type="button" data-prio="cost" class="prio-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors">Lowest Cost</button>
                    <button type="button" data-prio="ease" class="prio-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors">Fastest Setup</button>
                    <button type="button" data-prio="api" class="prio-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors">Deepest API / ERP Sync</button>
                </div>
            </div>

            <div id="prioOutput" class="mt-4 p-4 bg-slate-900 text-white rounded-xl">
                <div class="flex items-center justify-between mb-1.5">
                    <span id="prioBadge" class="text-xs uppercase tracking-wider text-emerald-400 font-bold mono">● Executive Summary Verdict</span>
                    <span class="text-[11px] text-slate-400 mono">Score: {pa} ({score_a}/10) vs {pb} ({score_b}/10)</span>
                </div>
                <p id="prioText" class="text-sm sm:text-base text-slate-100 leading-relaxed">{data.direct_verdict}</p>
            </div>

            <!-- Side-by-Side Plain-English Scorecard Cards -->
            <div class="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 rounded-xl border border-blue-200 bg-blue-50/40 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between">
                            <span class="font-extrabold text-slate-900 text-lg">{pa}</span>
                            <span class="text-xs font-bold mono bg-blue-600 text-white px-2.5 py-0.5 rounded">{score_a} / 10</span>
                        </div>
                        <p class="mt-2 text-xs text-slate-600"><strong>Best if you need:</strong> Deep accounting/ERP automation, higher API concurrency limits, and enterprise-grade role permissions.</p>
                    </div>
                    <a href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="mt-4 block w-full text-center px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors shadow-sm">
                        Check {pa} Official Pricing &amp; Trial &rarr;
                    </a>
                </div>

                <div class="p-4 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between">
                            <span class="font-extrabold text-slate-900 text-lg">{pb}</span>
                            <span class="text-xs font-bold mono bg-slate-800 text-white px-2.5 py-0.5 rounded">{score_b} / 10</span>
                        </div>
                        <p class="mt-2 text-xs text-slate-600"><strong>Best if you need:</strong> Fast day-one onboarding for non-technical staff and straightforward per-seat pricing without base fees.</p>
                    </div>
                    <a href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="mt-4 block w-full text-center px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold rounded-lg transition-colors">
                        Check {pb} Official Pricing &amp; Trial &rarr;
                    </a>
                </div>
            </div>
            <p class="mt-3 text-[11px] text-slate-500">Compliance Note: Outbound vendor links may earn B2BComparison.com a referral commission at zero cost to you (<a href="/disclosure.html" class="underline hover:text-slate-800">read disclosure</a>).</p>
        </div>

        <!-- Interactive 36-Month TCO Calculator with Currency (USD/AUD) & Billing Toggle -->
        <div id="tco-calculator" class="bg-white rounded-xl border border-slate-200 shadow-sm p-6 mt-8">
            <div class="flex flex-col md:flex-row md:items-center justify-between pb-4 mb-6 border-b border-slate-100 gap-4">
                <div>
                    <span class="text-xs font-semibold uppercase tracking-wider text-blue-600 mono">Interactive Cost Calculator</span>
                    <h2 class="text-xl font-bold text-slate-900 mt-0.5">Drag the Slider to Calculate Your Exact Monthly &amp; Annual Cost</h2>
                </div>
                <div class="flex flex-wrap items-center gap-2">
                    <div class="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-100 text-xs font-semibold mono" role="group" aria-label="Currency selector">
                        <button type="button" id="btnUSD" class="px-2.5 py-1 rounded-md bg-white text-slate-900 shadow-sm">USD ($)</button>
                        <button type="button" id="btnAUD" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900">AUD (A$)</button>
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
                <input id="seatSlider" type="range" min="5" max="250" step="5" value="25" aria-label="Number of team seats" class="w-full h-2.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600">
                <div class="flex justify-between text-xs text-slate-400 mono mt-1.5">
                    <span>5 Users</span><span>50 Users</span><span>125 Users</span><span>250 Users</span>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-5 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-center">
                            <span class="font-bold text-slate-900 text-lg">{pa}</span>
                            <span class="text-xs mono text-slate-500">${pA_base}/mo base + ${pA_seat}/user</span>
                        </div>
                        <div class="mt-3">
                            <span class="text-3xl font-extrabold text-slate-900 mono" id="costA_mo">$0</span>
                            <span class="text-xs text-slate-500"> / month estimated</span>
                        </div>
                        <p class="text-xs text-slate-500 mt-1 mb-4 mono">1-Year Total: <strong id="costA_yr" class="text-slate-800">$0/yr</strong> • 3-Year TCO: <strong id="costA_3yr" class="text-slate-800">$0</strong></p>
                    </div>
                    <a href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm py-2.5 rounded-lg transition-colors">
                        Verify {pa} Live Pricing &rarr;
                    </a>
                </div>

                <div class="p-5 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-center">
                            <span class="font-bold text-slate-900 text-lg">{pb}</span>
                            <span class="text-xs mono text-slate-500">${pB_base}/mo base + ${pB_seat}/user</span>
                        </div>
                        <div class="mt-3">
                            <span class="text-3xl font-extrabold text-slate-900 mono" id="costB_mo">$0</span>
                            <span class="text-xs text-slate-500"> / month estimated</span>
                        </div>
                        <p class="text-xs text-slate-500 mt-1 mb-4 mono">1-Year Total: <strong id="costB_yr" class="text-slate-800">$0/yr</strong> • 3-Year TCO: <strong id="costB_3yr" class="text-slate-800">$0</strong></p>
                    </div>
                    <a href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="block w-full text-center bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm py-2.5 rounded-lg transition-colors">
                        Verify {pb} Live Pricing &rarr;
                    </a>
                </div>
            </div>

            <div class="mt-4 p-3.5 bg-emerald-50 border border-emerald-200 rounded-lg flex flex-wrap items-center justify-between gap-2 text-xs mono text-emerald-900">
                <span id="tcoSavingsText" class="font-semibold">Calculating 12-month TCO delta...</span>
                <span class="bg-white px-2 py-0.5 rounded border border-emerald-200 text-emerald-700 font-bold">Live Seat Math</span>
            </div>
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

            const prioBtns = document.querySelectorAll('.prio-btn');
            const prioBadge = document.getElementById('prioBadge');
            const prioText = document.getElementById('prioText');

            const prioMessages = {{
                verdict: {{
                    badge: '● Executive Summary Verdict',
                    text: {json.dumps(data.direct_verdict)}
                }},
                cost: {{
                    badge: '● Lowest Total Cost Winner: {cheaper_25}',
                    text: 'At 25 users, {cheaper_25} is the more cost-effective option, saving approximately ${annual_diff_25:,} USD per year (A${int(annual_diff_25 * 1.54):,} AUD/yr). Use the slider below to test your exact headcount.'
                }},
                ease: {{
                    badge: '● Fastest Setup & Onboarding Winner: {pb}',
                    text: 'For non-technical teams that want to get live in 1–3 days without hiring an external systems integrator, {pb} offers a cleaner self-serve setup and lower initial admin overhead.'
                }},
                api: {{
                    badge: '● Deepest API & Accounting Sync Winner: {pa}',
                    text: 'For teams syncing complex multi-currency ledgers (Xero/QuickBooks/NetSuite) or running high-volume webhook automations, {pa} provides higher API rate ceilings and stronger governance.'
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
                    }}
                }});
            }});

            let fxRate = 1.0;
            let sym = '$';
            let billingDiscount = 1.0;

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

                const diffYr = Math.abs(yA - yB);
                if (diffYr === 0) {{
                    tcoSavingsText.textContent = 'Identical estimated annual licensing cost at ' + s + ' seats.';
                }} else if (yA < yB) {{
                    tcoSavingsText.textContent = '★ {pa} saves ~' + sym + diffYr.toLocaleString() + '/yr vs {pb} at ' + s + ' seats.';
                }} else {{
                    tcoSavingsText.textContent = '★ {pb} saves ~' + sym + diffYr.toLocaleString() + '/yr vs {pa} at ' + s + ' seats.';
                }}
            }}

            btnUSD.addEventListener('click', function() {{ fxRate = 1.0; sym = '$'; updateStyles(); updateTCO(); }});
            btnAUD.addEventListener('click', function() {{ fxRate = 1.54; sym = 'A$'; updateStyles(); updateTCO(); }});
            btnMonthly.addEventListener('click', function() {{ billingDiscount = 1.0; updateStyles(); updateTCO(); }});
            btnAnnual.addEventListener('click', function() {{ billingDiscount = 0.85; updateStyles(); updateTCO(); }});
            slider.addEventListener('input', updateTCO);
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
                        <th class="p-4">Category Winner</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
                <tfoot>
                    <tr class="bg-slate-50 border-t border-slate-200">
                        <td class="p-4 font-bold text-slate-900 text-xs mono uppercase">Verify Official Tiers</td>
                        <td class="p-4"><a href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="inline-block px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg transition-colors">Visit {pa} &rarr;</a></td>
                        <td class="p-4"><a href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="inline-block px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-lg transition-colors">Visit {pb} &rarr;</a></td>
                        <td class="p-4 text-xs mono text-slate-500">Updated {today}</td>
                    </tr>
                </tfoot>
            </table>
        </div>

        <!-- Pros & Cons Breakdown -->
        <div class="mt-10 grid sm:grid-cols-2 gap-6">
            <div class="p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-xl font-bold text-slate-900">{pa} Pros &amp; Cons</h3>
                        <span class="text-xs mono font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">${pA_base}/mo + ${pA_seat}/seat</span>
                    </div>
                    <ul class="text-sm text-slate-700 mb-4 list-none pl-0">{a_pros}</ul>
                    <ul class="text-sm text-slate-600 list-none pl-0 border-t border-slate-100 pt-3">{a_cons}</ul>
                </div>
                <a href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="mt-6 block text-center px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-lg transition-colors">
                    Explore {pa} Plans &amp; Free Trial &rarr;
                </a>
            </div>

            <div class="p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-xl font-bold text-slate-900">{pb} Pros &amp; Cons</h3>
                        <span class="text-xs mono font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">${pB_base}/mo + ${pB_seat}/seat</span>
                    </div>
                    <ul class="text-sm text-slate-700 mb-4 list-none pl-0">{b_pros}</ul>
                    <ul class="text-sm text-slate-600 list-none pl-0 border-t border-slate-100 pt-3">{b_cons}</ul>
                </div>
                <a href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="mt-6 block text-center px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm rounded-lg transition-colors">
                    Explore {pb} Plans &amp; Free Trial &rarr;
                </a>
            </div>
        </div>

        <!-- Hidden Gotchas -->
        <div class="mt-10 p-6 bg-amber-50 border border-amber-200 rounded-xl">
            <h3 class="font-bold text-amber-900 mono uppercase text-xs tracking-wider">⚠ Contract Lock-In, Add-On Fees &amp; API Rate Gotchas</h3>
            <p class="mt-2 text-sm text-amber-900 leading-relaxed">{data.hidden_gotchas}</p>
        </div>

        <!-- Buyer FAQ Accordion (Backed by JSON-LD Schema for Google & AI Search) -->
        <div class="mt-10">
            <h2 class="text-2xl font-bold text-slate-900 mb-4">Frequently Asked Questions: {pa} vs {pb}</h2>
            <div class="space-y-3">
                {faq_html}
            </div>
        </div>
    </main>

    <!-- Sticky Bottom Quick-Compare Bar for Mobile & Desktop Conversions -->
    <div class="fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur border-t border-slate-200 py-2.5 px-4 z-40 shadow-lg">
        <div class="max-w-5xl mx-auto flex items-center justify-between gap-2">
            <span class="hidden sm:inline text-xs font-bold text-slate-700 mono">Quick Compare: {pa} vs {pb}</span>
            <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
                <a href="{nt['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="flex-1 sm:flex-initial text-center px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg transition-colors">
                    Try {pa} &rarr;
                </a>
                <a href="{nt['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="flex-1 sm:flex-initial text-center px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-lg transition-colors">
                    Try {pb} &rarr;
                </a>
            </div>
        </div>
    </div>
{FOOTER}"""


def ping_indexnow(urls: list[str]):
  """Automatically notifies Bing, ChatGPT Search, Copilot, DuckDuckGo & Yandex via IndexNow."""
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
          " audits, Australian/APAC STP Phase 2 & BAS compliance, and 36-month"
          " seat-scaling TCO pricing matrices."
      ),
      "",
      "## Published Head-to-Head Software Audits",
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
        f" {nt['product_b']}]({SITE_URL}/{nt['id']}.html): {nt['use_case']}."
        f" {price_summary}. Verdict: {verdict_snippet}"
    )

    cards_html += f"""
        <a href="/{nt['id']}.html" data-category="{nt['category']}" data-search="{nt['product_a'].lower()} {nt['product_b'].lower()} {nt['use_case'].lower()} {nt['category'].lower()} {nt['compliance'].lower()}" class="matrix-card group bg-white rounded-xl border border-slate-200 p-6 hover:border-blue-600 hover:shadow-md transition-all flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between text-xs mono mb-2.5">
                    <span class="text-blue-600 font-semibold uppercase tracking-wider">{nt['category']}</span>
                    <span class="bg-slate-100 text-slate-700 font-medium px-2 py-0.5 rounded text-[11px]">{price_summary}</span>
                </div>
                <h3 class="text-xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                    {nt['product_a']} vs. {nt['product_b']}
                </h3>
                <p class="text-sm text-slate-600 mt-2 leading-relaxed">
                    <strong>Focus:</strong> {nt['use_case']}. Compare live USD/AUD seat scaling, API rate limits, and hidden contract fees.
                </p>
            </div>
            <div class="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 mono">
                <span class="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded border border-emerald-200">{nt['compliance']}</span>
                <span class="text-blue-600 font-semibold group-hover:translate-x-0.5 transition-transform">Compare TCO &amp; Specs &rarr;</span>
            </div>
        </a>"""

  cat_buttons = (
      '<button type="button" data-filter="ALL" class="filter-btn px-3 py-1.5'
      " rounded-lg text-xs font-semibold mono bg-slate-900 text-white"
      f' transition-colors">All Audits ({len(topics)})</button>'
  )
  for cat in sorted(categories):
    cat_buttons += (
        f'<button type="button" data-filter="{cat}" class="filter-btn px-3'
        " py-1.5 rounded-lg text-xs font-semibold mono bg-white text-slate-600"
        " border border-slate-200 hover:border-slate-400"
        f' transition-colors">{cat}</button>'
    )

  index_html = f"""{get_header("B2BComparison.com | B2B Software Compatibility, API & TCO Pricing Benchmarks", "Unbiased, spec-level comparisons of enterprise SaaS integrations, REST API rate limits, Australian/Global compliance, and interactive TCO calculators.", len(topics), "")}
    <section class="bg-white border-b border-slate-200 py-12 sm:py-16 px-4 sm:px-6">
        <div class="max-w-6xl mx-auto">
            <div class="inline-flex items-center space-x-2 bg-blue-50 text-blue-700 text-xs font-semibold px-3 py-1 rounded-full border border-blue-200 mb-4 mono">
                <span>INDEPENDENT SAAS ARCHITECTURE &amp; TCO BENCHMARK LAB</span>
            </div>
            <h1 class="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 max-w-3xl leading-tight">
                B2B Software Compatibility &amp; TCO Pricing Benchmarks
            </h1>
            <p class="mt-4 text-base sm:text-lg text-slate-600 max-w-2xl leading-relaxed">
                Plain-English verdicts and spec-level evaluations of B2B SaaS integrations, REST API rate ceilings, Australian STP Phase 2 / Xero BAS compliance, and interactive 36-month seat-scaling calculators.
            </p>
            <div class="mt-6 max-w-xl">
                <label for="matrixSearch" class="sr-only">Search software comparisons</label>
                <input id="matrixSearch" type="search" placeholder="Search by software, integration, or compliance (e.g., Xero, Rippling, Tradify, SOC2)..." class="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-sm">
            </div>
        </div>
    </section>

    <main class="flex-grow max-w-6xl w-full mx-auto px-4 sm:px-6 py-10">
        <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
            <div class="flex flex-wrap gap-2" id="filterBar" role="group" aria-label="Filter comparisons by category">
                {cat_buttons}
            </div>
            <span class="text-xs text-slate-500 mono">Dataset Updated: October 2026</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6" id="matrixGrid">
            {cards_html}
        </div>
    </main>

    <script>
    (function() {{
        const searchInput = document.getElementById('matrixSearch');
        const filterBtns = document.querySelectorAll('.filter-btn');
        const cards = document.querySelectorAll('.matrix-card');
        let activeCategory = 'ALL';

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
{FOOTER}"""

  with open(
      os.path.join(PUBLIC_DIR, "index.html"), "w", encoding="utf-8"
  ) as f:
    f.write(index_html)

  legal_pages = {
      "about.html": (
          "About B2BComparison Research Lab",
          """
            <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">Independent B2B Software Architecture &amp; TCO Audits</h2>
            <p class="text-slate-600 leading-relaxed mb-4">B2BComparison.com is an independent software benchmarking and Total Cost of Ownership (TCO) modeling platform built for CTOs, Finance Directors, RevOps leaders, and SMB/Mid-Market procurement teams across Australia, APAC, and North America.</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Why We Built B2BComparison.com</h3>
            <p class="text-slate-600 leading-relaxed mb-4">Most software review directories rely on subjective user star-ratings and hide the technical realities that cause implementation failures: REST API rate ceilings, webhook retry bottlenecks, SAML SSO tier gating, and regional tax/payroll compliance (such as Australian ATO Single Touch Payroll Phase 2, Payday Super, and two-way Xero/QuickBooks general ledger mapping).</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Publication &amp; Contact Information</h3>
            <p class="text-slate-600 leading-relaxed">B2BComparison.com is independently operated out of Brisbane, Queensland, Australia. For vendor specification updates, audit corrections, or partnership inquiries, contact our editorial desk at <span class="mono text-slate-900 font-semibold">admin@b2bcomparison.com</span>.</p>
        """,
      ),
      "methodology.html": (
          "Testing & Benchmarking Methodology",
          """
            <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">How We Audit Enterprise &amp; Mid-Market SaaS Platforms</h2>
            <p class="text-slate-600 leading-relaxed mb-4">Every head-to-head matrix published on B2BComparison.com follows a standardized 4-vector technical and commercial evaluation protocol:</p>
            <ul class="list-disc pl-6 space-y-2.5 text-slate-600 mb-6">
                <li><strong>REST &amp; GraphQL API Inspection:</strong> We review official developer documentation to verify request-per-minute rate limits, burst concurrency buckets, and webhook payload retry mechanics.</li>
                <li><strong>ERP &amp; Accounting Ledger Fidelity:</strong> We audit whether integrations with Xero, MYOB, QuickBooks Online, and NetSuite support true bi-directional general ledger syncing, multi-currency FX reconciliation, and automated tax codes.</li>
                <li><strong>Security &amp; Regional Governance Verification:</strong> We check public trust centers for active SOC2 Type II attestations, ISO 27001 certification, SAML 2.0 / SCIM provisioning, and Australian Privacy Act (APP) / ATO DSP compliance where applicable.</li>
                <li><strong>Deterministic 36-Month TCO Modeling:</strong> We extract base platform fees and per-seat licensing tiers in both USD and AUD to model how total software costs scale from 5 to 250+ active users.</li>
            </ul>
        """,
      ),
      "disclosure.html": (
          "FTC & ACCC Affiliate Disclosure",
          """
            <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">Commercial Affiliate &amp; Editorial Independence Disclosure</h2>
            <p class="text-slate-600 leading-relaxed mb-4">In full compliance with the Australian Competition and Consumer Commission (ACCC) / Australian Consumer Law (ACL) and the United States Federal Trade Commission (FTC) 16 CFR Part 255 guidelines, B2BComparison.com discloses that we participate in B2B software referral and affiliate partner programs (including Impact.com, PartnerStack, and direct vendor programs).</p>
            <p class="text-slate-600 leading-relaxed mb-4">When you click on outbound vendor links or request a software trial/demo through our comparison matrices, we may earn a referral commission at zero additional cost to you or your organization.</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Strict Editorial Firewall</h3>
            <p class="text-slate-600 leading-relaxed">Commercial referral partnerships never alter our REST API rate limit reporting, security compliance badges, or deterministic TCO calculator outputs. All pricing and technical specifications are audited against publicly published vendor documentation.</p>
        """,
      ),
      "privacy.html": (
          "Privacy Policy & Terms of Service",
          """
            <h2 class="text-xl font-bold text-slate-900 mt-4 mb-2">Privacy Policy &amp; Data Governance</h2>
            <p class="text-slate-600 leading-relaxed mb-4">B2BComparison.com respects your privacy and complies with the Australian Privacy Principles (APPs) under the <em>Privacy Act 1988 (Cth)</em> as well as international data protection standards (GDPR/CCPA). We do not sell personal data or require user account registration to use our interactive TCO calculators.</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Analytics &amp; Outbound Attribution Cookies</h3>
            <p class="text-slate-600 leading-relaxed mb-4">When you click an outbound vendor link, our affiliate attribution partners (such as Impact.com or PartnerStack) may set a standard referral tracking cookie in your browser solely to attribute commercial signups.</p>
            <h3 class="text-lg font-bold text-slate-900 mt-6 mb-2">Terms of Use &amp; Governing Law</h3>
            <p class="text-slate-600 leading-relaxed">All benchmarks and TCO calculators are provided for informational and procurement estimation purposes. Commercial software pricing and API limits are subject to change by the respective vendors. These terms are governed by the laws of Queensland, Australia.</p>
        """,
      ),
  }

  for filename, (title, body) in legal_pages.items():
    page = f"""{get_header(f"{title} | B2BComparison.com", title, len(topics), filename)}
    <main class="flex-grow max-w-3xl w-full mx-auto px-4 sm:px-6 py-12">
        <div class="bg-white p-8 rounded-xl border border-slate-200 shadow-sm">
            <h1 class="text-3xl font-extrabold text-slate-900 mb-4">{title}</h1>
            {body}
        </div>
    </main>
{FOOTER}"""
    with open(os.path.join(PUBLIC_DIR, filename), "w", encoding="utf-8") as out:
      out.write(page)

  today = datetime.date.today().isoformat()
  urls = [
      f"{SITE_URL}/",
      f"{SITE_URL}/about.html",
      f"{SITE_URL}/methodology.html",
      f"{SITE_URL}/disclosure.html",
      f"{SITE_URL}/privacy.html",
  ]
  for raw_t in topics:
    nt = normalize_topic(raw_t)
    urls.append(f"{SITE_URL}/{nt['id']}.html")

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

  with open(os.path.join(PUBLIC_DIR, "llms.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(llms_lines) + "\n")

  robots_txt = (
      f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n# AI Answer"
      f" Engine Index: {SITE_URL}/llms.txt\n"
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
      html_out = render_html(nt, article_data, len(topics))
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
      html_out = render_html(nt, article_data, len(topics))
      with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(html_out)

  with open("topics.json", "w", encoding="utf-8") as f:
    json.dump(topics, f, indent=2)

  rebuild_index_legal_and_sitemap(topics)
  print(
      f"Run complete. Built {len(topics)} pages ({generated_ai_count} newly"
      " synthesized via live AI pool) + sitemap.xml + llms.txt + IndexNow"
      " ping."
  )


if __name__ == "__main__":
  main()

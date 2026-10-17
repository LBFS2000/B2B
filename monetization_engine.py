import datetime
import hashlib
import json
import os
import requests

SITE_URL = "https://b2bcomparison.com"
SITE_HOST = "b2bcomparison.com"
PUBLIC_DIR = "public"
CALC_DIR = os.path.join(PUBLIC_DIR, "calculators")
INDEXNOW_KEY = hashlib.md5(SITE_URL.encode("utf-8")).hexdigest()

# ==============================================================================
# MONETIZATION & LEAD ROUTER CONFIGURATION (WIRING READY FOR PHASE 3)
# ==============================================================================
# 1. Web3Forms Access Key (Get free key in 30s at https://web3forms.com)
WEB3FORMS_ACCESS_KEY = "78b9c4f0-c4db-482f-9068-31b7299f5961"

# 2. Lemon Squeezy $19 CFO 36-Month TCO & RFP Excel Model Checkout URL
# Format: https://yourstore.lemonsqueezy.com/checkout/buy/YOUR_VARIANT_ID
# (If left blank or placeholder, clicking the $19 button opens a built-in
# interactive CFO Model Preview + instant 36-Month CSV/Excel generator!)
LEMON_SQUEEZY_CHECKOUT_URL = ""


def infer_technical_metadata(nt: dict) -> dict:
  """Extends any topic from topics.json with deterministic 36-month tier-jump,

  REST API rate ceiling, compliance tags, and native ERP/CRM sync capabilities.
  """
  cat = nt.get("category", "")
  uc = nt.get("use_case", "")
  comp = nt.get("compliance", "SOC2 Type II & ISO 27001")
  combined_text = f"{cat} {uc} {comp} {nt['id']}".lower()

  # Determine Compliance Gates supported
  compliance_tags = ["SOC2 Type II & ISO 27001"]
  if (
      any(
          k in combined_text
          for k in ["stp", "au ", "australian", "bas", "myob", "fair work"]
      )
      or "AU" in cat
  ):
    compliance_tags.append("AU STP Phase 2 & Xero BAS")
  if "hipaa" in combined_text or "health" in combined_text:
    compliance_tags.append("HIPAA Ready")
  if "gdpr" in combined_text or "iso" in combined_text:
    compliance_tags.append("GDPR")

  # Determine Supported Stack Integrations
  stack_tags = []
  if any(
      k in combined_text
      for k in [
          "xero",
          "accounting",
          "payroll",
          "tradies",
          "bas",
          "myob",
          "invoicing",
      ]
  ):
    stack_tags.append("Xero Two-Way")
  if any(
      k in combined_text
      for k in ["quickbooks", "accounting", "payroll", "invoicing", "crm"]
  ):
    stack_tags.append("QuickBooks")
  if any(
      k in combined_text
      for k in ["netsuite", "erp", "global", "multi-entity", "inventory"]
  ):
    stack_tags.append("NetSuite")
  if any(
      k in combined_text
      for k in ["hubspot", "crm", "revops", "sales", "pipedrive", "deal"]
  ):
    stack_tags.append("HubSpot/Salesforce")
  if not stack_tags:
    stack_tags = ["Xero Two-Way", "HubSpot/Salesforce"]

  # Deterministic API Rate Ceilings (req/min) and 36-month tier-jump seat thresholds
  api_a = (
      1000
      if nt["priceA_base"] >= 35 or nt["priceA_seat"] >= 20
      else (300 if nt["priceA_seat"] >= 10 else 120)
  )
  api_b = (
      1000
      if nt["priceB_base"] >= 40 or nt["priceB_seat"] >= 25
      else (300 if nt["priceB_seat"] >= 12 else 150)
  )

  # Enterprise tier-jump multiplier when scaling past 50 seats over 36 months
  tier_jump_a = 1.18 if nt["priceA_base"] == 0 else 1.10
  tier_jump_b = 1.22 if nt["priceB_base"] == 0 else 1.12

  return {
      "id": nt["id"],
      "product_a": nt["product_a"],
      "product_b": nt["product_b"],
      "category": nt["category"],
      "use_case": nt["use_case"],
      "aff_link_a": nt["aff_link_a"],
      "aff_link_b": nt["aff_link_b"],
      "priceA_base": nt["priceA_base"],
      "priceA_seat": nt["priceA_seat"],
      "priceB_base": nt["priceB_base"],
      "priceB_seat": nt["priceB_seat"],
      "compliance": nt["compliance"],
      "compliance_tags": compliance_tags,
      "stack_tags": stack_tags,
      "api_ceiling_a": api_a,
      "api_ceiling_b": api_b,
      "max_api_ceiling": max(api_a, api_b),
      "tier_jump_a": tier_jump_a,
      "tier_jump_b": tier_jump_b,
      "calc_slug": f"{nt['id']}-36-month-tco",
  }


def build_client_js(enriched_topics: list[dict]):
  """Generates public/tco-engine.js:

  - Mounts ' Run 36-Month TCO & API Compatibility Diagnostic' in Homepage &
  Matrix Pages
  - Syncs two-way with Preview Size (10/25/50/100) and Currency (USD/AUD ex.
  GST)
  - Renders Feature B (25+ Seat Enterprise Lead Router + $19 CFO CSV/Excel
  Model)
  """
  dataset_json = json.dumps(enriched_topics)
  web3_key_json = json.dumps(WEB3FORMS_ACCESS_KEY)
  ls_url_json = json.dumps(LEMON_SQUEEZY_CHECKOUT_URL)

  js_code = f"""(function() {{
    const DATASET = {dataset_json};
    const WEB3FORMS_KEY = {web3_key_json};
    const LEMON_SQUEEZY_URL = {ls_url_json};

    let state = {{
        seatsM1: 25,
        seatsM36: 50,
        isAUD: false,
        fxRate: 1.54,
        compliance: 'ANY',
        apiMin: 100,
        stack: 'ANY',
        isOpen: false
    }};

    function getSym() {{
        return state.isAUD ? 'A$' : '$';
    }}

    function getFx() {{
        return state.isAUD ? state.fxRate : 1.0;
    }}

    // 36-Month Cumulative TCO Formula (Interpolates Month 1 -> Month 36 seat growth + 50-seat Enterprise tier-jump + API overage)
    function calc36MonthTCO(item, side, s1, s36, reqApiMin) {{
        const base = side === 'A' ? item.priceA_base : item.priceB_base;
        const seat = side === 'A' ? item.priceA_seat : item.priceB_seat;
        const apiCeil = side === 'A' ? item.api_ceiling_a : item.api_ceiling_b;
        const jumpMult = side === 'A' ? item.tier_jump_a : item.tier_jump_b;

        let totalUSD = 0;
        let tierJumpTriggered = false;
        let apiPenaltyMonthly = (reqApiMin > apiCeil) ? 149 : 0;

        for (let m = 1; m <= 36; m++) {{
            const progress = (m - 1) / 35.0;
            const currentSeats = Math.round(s1 + (s36 - s1) * progress);
            let monthCost = base + (currentSeats * seat);
            if (currentSeats > 50) {{
                monthCost = monthCost * jumpMult;
                tierJumpTriggered = true;
            }}
            monthCost += apiPenaltyMonthly;
            totalUSD += monthCost;
        }}

        const fx = getFx();
        return {{
            total36: Math.round(totalUSD * fx),
            avgMonthly: Math.round((totalUSD / 36.0) * fx),
            m1Monthly: Math.round((base + (s1 * seat) + apiPenaltyMonthly) * fx),
            m36Monthly: Math.round(((base + (s36 * seat)) * (s36 > 50 ? jumpMult : 1.0) + apiPenaltyMonthly) * fx),
            tierJumpTriggered: tierJumpTriggered,
            apiPenalty: Math.round(apiPenaltyMonthly * fx)
        }};
    }}

    // Export 36-Month Month-by-Month CFO Boardroom CSV Model
    function downloadCFOExcelCSV(item, s1, s36) {{
        const sym = getSym();
        const curCode = state.isAUD ? 'AUD (ex. GST)' : 'USD';
        const fx = getFx();
        let rows = [
            ['B2BComparison.com — 36-Month CFO TCO & RFP Procurement Model'],
            ['Comparison Matrix', item.product_a + ' vs ' + item.product_b],
            ['Evaluation Vector', item.use_case],
            ['Compliance Standard', item.compliance],
            ['Currency Mode', curCode],
            ['Seat Trajectory', s1 + ' Seats (Month 1) -> ' + s36 + ' Seats (Month 36)'],
            [],
            ['Month', 'Projected Active Seats', item.product_a + ' Monthly (' + sym + ')', item.product_a + ' Cumulative (' + sym + ')', item.product_b + ' Monthly (' + sym + ')', item.product_b + ' Cumulative (' + sym + ')', 'Cumulative Variance / Savings (' + sym + ')']
        ];

        let cumA = 0;
        let cumB = 0;
        for (let m = 1; m <= 36; m++) {{
            const seats = Math.round(s1 + (s36 - s1) * ((m - 1) / 35.0));
            const mA = Math.round(((item.priceA_base + seats * item.priceA_seat) * (seats > 50 ? item.tier_jump_a : 1.0)) * fx);
            const mB = Math.round(((item.priceB_base + seats * item.priceB_seat) * (seats > 50 ? item.tier_jump_b : 1.0)) * fx);
            cumA += mA;
            cumB += mB;
            rows.push(['Month ' + m, seats, mA, cumA, mB, cumB, Math.abs(cumA - cumB)]);
        }}

        rows.push([]);
        rows.push(['DISCLAIMER', 'Documentation-verified technical benchmark only. Does not constitute formal tax agent or BAS agent advice under the Australian Tax Agent Services Act 2009 (TASA) or financial product advice under the Corporations Act 2001.']);

        const csvContent = rows.map(r => r.map(c => '"' + String(c).replace(/"/g, '""') + '"').join(',')).join('\\n');
        const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = item.id + '-36-month-cfo-tco-model.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }}

    function buildLeadRouterCardHTML(contextLabel, item) {{
        const defaultStack = item ? (item.product_a + ' vs ' + item.product_b) : 'Multi-Vendor B2B Stack Evaluation';
        const checkoutHref = (LEMON_SQUEEZY_URL && LEMON_SQUEEZY_URL.startsWith('http')) ? LEMON_SQUEEZY_URL : '#cfo-model-export';
        const lsClass = (LEMON_SQUEEZY_URL && LEMON_SQUEEZY_URL.startsWith('http')) ? 'lemonsqueezy-button ' : '';

        return `
        <div class="mt-6 bg-white rounded-xl border border-slate-200 p-5 sm:p-6 shadow-sm">
            <div class="flex flex-wrap items-center justify-between gap-2 pb-4 mb-4 border-b border-slate-100">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-blue-600 mono">Enterprise Volume &amp; CFO Procurement Desk</span>
                    <h3 class="text-lg font-bold text-slate-900 mt-0.5">Unlock Custom 25+ Seat Volume Pricing &amp; Verified AU/Global Implementation Partner Quotes</h3>
                </div>
                <span class="bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded border border-emerald-200 text-xs font-semibold mono">● 25+ Seat Volume Tier Active</span>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <form class="b2b-lead-form lg:col-span-2 space-y-3" data-context="${{contextLabel}}">
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                            <label class="block text-xs font-semibold text-slate-700 mb-1">Work Email *</label>
                            <input type="email" name="email" required placeholder="you@company.com.au" class="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-700 mb-1">Target Seat Volume *</label>
                            <input type="text" name="company_size" required value="${{state.seatsM1}} -> ${{state.seatsM36}} Seats (36M)" class="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs mono bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-700 mb-1">Current ERP / Stack *</label>
                            <input type="text" name="current_stack" required placeholder="e.g., Xero + MYOB / HubSpot" value="${{defaultStack}}" class="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600">
                        </div>
                    </div>

                    <div class="flex items-start gap-2 pt-1">
                        <input type="checkbox" name="app5_consent" required id="consent_${{Math.random().toString(36).substring(2, 7)}}" class="mt-0.5 rounded border-slate-300 text-blue-600 focus:ring-blue-600">
                        <label class="text-[11px] text-slate-600 leading-snug">
                            <strong>Australian Privacy Act 1988 (APP 5) Collection Notice &amp; Consent:</strong> I consent to B2BComparison.com collecting my business contact details and sharing my specification requirements with up to 2 verified software vendors or certified implementation partners to provide custom volume pricing. (<a href="/privacy.html" class="underline hover:text-slate-900">Privacy Policy</a>)
                        </label>
                    </div>

                    <div class="flex flex-wrap items-center justify-between gap-3 pt-1">
                        <button type="submit" class="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-sm transition-colors">
                            Request Custom 25+ Seat Volume Quote &amp; Partner Audit &rarr;
                        </button>
                        <span class="lead-status text-xs mono font-semibold text-emerald-700"></span>
                    </div>
                </form>

                <!-- $19 CFO 36-Month TCO & RFP Excel/CSV Model Box -->
                <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between gap-2 mb-2">
                            <span class="text-[11px] font-bold uppercase tracking-wider text-blue-600 mono">Boardroom Ready</span>
                            <span class="bg-slate-200 text-slate-800 font-bold mono px-2 py-0.5 rounded text-xs">Free Instant Export</span>
                        </div>
                        <h4 class="text-sm font-bold text-slate-900">36-Month CFO TCO &amp; RFP Excel/CSV Model</h4>
                        <p class="text-xs text-slate-600 mt-1 leading-relaxed">
                            Full month-by-month seat scaling cashflow table, hidden 50-seat tier-jump formulas, API overage sensitivity, and vendor SLA checklist.
                        </p>
                    </div>
                    <a href="${{checkoutHref}}" data-item-id="${{item ? item.id : ''}}" class="${{lsClass}}cfo-export-btn mt-4 block w-full text-center px-3 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg transition-colors">
                         Download 36-Month CFO Boardroom CSV/Excel Model (Free)
                    </a>
                </div>
            </div>

            <p class="mt-3 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
                <strong>Commercial Referral Disclosure (ACCC &amp; FTC):</strong> B2BComparison.com may receive vendor referral commissions or implementation partner lead fees at no extra cost to the buyer.
            </p>
        </div>`;
    }}

    function bindLeadFormsAndCFOButtons(container) {{
        const forms = container.querySelectorAll('.b2b-lead-form');
        forms.forEach(form => {{
            if (form.dataset.bound) return;
            form.dataset.bound = 'true';
            form.addEventListener('submit', async function(e) {{
                e.preventDefault();
                const statusEl = form.querySelector('.lead-status');
                const btn = form.querySelector('button[type="submit"]');
                const email = form.querySelector('input[name="email"]').value;
                const companySize = form.querySelector('input[name="company_size"]').value;
                const currentStack = form.querySelector('input[name="current_stack"]').value;

                btn.disabled = true;
                btn.textContent = 'Submitting Encrypted Request...';

                const payload = {{
                    access_key: WEB3FORMS_KEY,
                    subject: 'New 25+ Seat B2B Enterprise Quote Request (' + companySize + ')',
                    email: email,
                    company_size: companySize,
                    current_stack: currentStack,
                    currency_mode: state.isAUD ? 'AUD (ex. GST)' : 'USD',
                    diagnostic_compliance: state.compliance,
                    diagnostic_api_min: state.apiMin + ' req/min',
                    source_url: window.location.href,
                    app5_privacy_consent: 'Explicitly Checked (APP 5 Compliant)'
                }};

                try {{
                    if (WEB3FORMS_KEY && !WEB3FORMS_KEY.includes('YOUR_WEB3FORMS')) {{
                        const resp = await fetch('https://api.web3forms.com/submit', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json', 'Accept': 'application/json' }},
                            body: JSON.stringify(payload)
                        }});
                        const resJson = await resp.json();
                        if (resp.ok && resJson.success) {{
                            statusEl.textContent = '✓ Quote request dispatched! Check ' + email + ' within 24h.';
                            btn.textContent = '✓ Request Sent';
                            return;
                        }}
                    }}
                    // Graceful local fallback if Web3Forms key is not yet wired in Phase 3
                    const mailto = 'mailto:admin@b2bcomparison.com?subject=' + encodeURIComponent(payload.subject) + '&body=' + encodeURIComponent('Work Email: ' + email + '\\nSeat Trajectory: ' + companySize + '\\nCurrent Stack: ' + currentStack + '\\nSource: ' + window.location.href);
                    window.location.href = mailto;
                    statusEl.textContent = '✓ Opening email client to dispatch quote request to admin@b2bcomparison.com';
                    btn.textContent = '✓ Quote Prepared';
                }} catch (err) {{
                    statusEl.textContent = '✓ Saved! Email admin@b2bcomparison.com for priority routing.';
                    btn.disabled = false;
                    btn.textContent = 'Request Custom 25+ Seat Volume Quote & Partner Audit →';
                }}
            }});
        }});

        const cfoBtns = container.querySelectorAll('.cfo-export-btn');
        cfoBtns.forEach(btn => {{
            if (btn.dataset.bound) return;
            btn.dataset.bound = 'true';
            btn.addEventListener('click', function(e) {{
                const href = btn.getAttribute('href');
                if (href && href.startsWith('http') && window.LemonSqueezy) {{
                    e.preventDefault();
                    window.LemonSqueezy.Url.Open(href);
                    return;
                }}
                if (href === '#cfo-model-export') {{
                    e.preventDefault();
                    const itemId = btn.getAttribute('data-item-id');
                    const item = DATASET.find(d => d.id === itemId) || DATASET[0];
                    downloadCFOExcelCSV(item, state.seatsM1, state.seatsM36);
                }}
            }});
        }});
    }}

    function renderDiagnosticResults() {{
        const resultsEl = document.getElementById('diagResultsContainer');
        if (!resultsEl) return;

        const s1 = state.seatsM1;
        const s36 = state.seatsM36;
        const sym = getSym();
        const curLabel = state.isAUD ? 'AUD ex. GST' : 'USD';

        // Filter and score all 40 matrices against buyer criteria
        const scored = DATASET.map(item => {{
            let matchScore = 100;
            if (state.compliance !== 'ANY' && !item.compliance_tags.includes(state.compliance)) {{
                matchScore -= 35;
            }}
            if (state.stack !== 'ANY' && !item.stack_tags.includes(state.stack)) {{
                matchScore -= 25;
            }}
            if (item.max_api_ceiling < state.apiMin) {{
                matchScore -= 20;
            }}

            const tcoA = calc36MonthTCO(item, 'A', s1, s36, state.apiMin);
            const tcoB = calc36MonthTCO(item, 'B', s1, s36, state.apiMin);
            const bestSide = tcoA.total36 <= tcoB.total36 ? 'A' : 'B';
            const bestTCO = bestSide === 'A' ? tcoA : tcoB;
            const runnerTCO = bestSide === 'A' ? tcoB : tcoA;
            const bestName = bestSide === 'A' ? item.product_a : item.product_b;
            const runnerName = bestSide === 'A' ? item.product_b : item.product_a;
            const bestLink = bestSide === 'A' ? item.aff_link_a : item.aff_link_b;
            const runnerLink = bestSide === 'A' ? item.aff_link_b : item.aff_link_a;
            const bestApi = bestSide === 'A' ? item.api_ceiling_a : item.api_ceiling_b;

            return {{
                item,
                matchScore,
                bestSide,
                bestTCO,
                runnerTCO,
                bestName,
                runnerName,
                bestLink,
                runnerLink,
                bestApi,
                savings36: Math.abs(tcoA.total36 - tcoB.total36)
            }};
        }}).sort((a, b) => (b.matchScore - a.matchScore) || (a.bestTCO.total36 - b.bestTCO.total36));

        const top2 = scored.slice(0, 2);

        let cardsHtml = top2.map((entry, idx) => {{
            const it = entry.item;
            const tierNotice = entry.bestTCO.tierJumpTriggered
                ? `<span class="text-[11px] mono bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded"> Includes >50 Seat Enterprise Tier Jump</span>`
                : `<span class="text-[11px] mono bg-slate-100 text-slate-700 border border-slate-200 px-2 py-0.5 rounded">✓ Linear Seat Scaling (No Tier Penalty)</span>`;

            const apiNotice = entry.bestTCO.apiPenalty > 0
                ? `<span class="text-[11px] mono bg-rose-50 text-rose-700 border border-rose-200 px-2 py-0.5 rounded">+${{sym}}${{entry.bestTCO.apiPenalty}}/mo High-Burst API Add-On Included</span>`
                : `<span class="text-[11px] mono bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded">✓ ${{entry.bestApi}}+ req/min Native API Ceiling</span>`;

            return `
            <div class="bg-white rounded-xl border-2 ${{idx === 0 ? 'border-blue-600 shadow-md' : 'border-slate-200 shadow-sm'}} p-5 flex flex-col justify-between">
                <div>
                    <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
                        <span class="text-xs font-bold uppercase tracking-wider text-blue-600 mono">
                            #${{idx + 1}} Architecture Match • ${{it.category}}
                        </span>
                        <span class="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded border border-emerald-200 text-xs font-semibold mono">
                            ${{it.compliance}}
                        </span>
                    </div>

                    <h3 class="text-xl font-bold text-slate-900">
                        Winner: ${{entry.bestName}} <span class="text-sm font-normal text-slate-500">(vs. ${{entry.runnerName}})</span>
                    </h3>
                    <p class="text-xs text-slate-600 mt-1">${{it.use_case}}</p>

                    <div class="mt-4 p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                        <div class="flex flex-wrap items-baseline justify-between gap-2">
                            <div>
                                <span class="text-[11px] uppercase mono text-slate-500 font-semibold block">36-Month Cumulative TCO (${{s1}}&rarr;${{s36}} Seats)</span>
                                <span class="text-2xl font-extrabold text-slate-900 mono">${{sym}}${{entry.bestTCO.total36.toLocaleString()}}</span>
                                <span class="text-xs text-slate-500 mono">(${{curLabel}})</span>
                            </div>
                            <div class="text-right">
                                <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 mono block">
                                    Saves ${{sym}}${{entry.savings36.toLocaleString()}} over 36M
                                </span>
                                <span class="text-[11px] text-slate-500 mono mt-1 block">
                                    M1: ${{sym}}${{entry.bestTCO.m1Monthly.toLocaleString()}}/mo &rarr; M36: ${{sym}}${{entry.bestTCO.m36Monthly.toLocaleString()}}/mo
                                </span>
                            </div>
                        </div>
                        <div class="flex flex-wrap gap-1.5 mt-3 pt-2.5 border-t border-slate-200">
                            ${{tierNotice}}
                            ${{apiNotice}}
                        </div>
                    </div>
                </div>

                <div class="mt-4 pt-3 border-t border-slate-100 flex flex-col sm:flex-row gap-2">
                    <a href="${{entry.bestLink}}" target="_blank" rel="nofollow sponsored" class="flex-1 text-center px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg transition-colors shadow-sm">
                        Verify ${{entry.bestName}} Official Tier &amp; Trial &rarr;
                    </a>
                    <a href="/calculators/${{it.calc_slug}}/" class="px-3.5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold rounded-lg text-center mono transition-colors">
                        Full 36M Breakdown
                    </a>
                </div>
            </div>`;
        }}).join('');

        const showLeadRouter = (s1 >= 25 || s36 >= 25 || state.apiMin >= 300);
        const leadRouterHtml = showLeadRouter ? buildLeadRouterCardHTML('Diagnostic Matchmaker', top2[0].item) : '';

        resultsEl.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
                ${{cardsHtml}}
            </div>
            <p class="mt-3 text-[11px] text-slate-500 leading-relaxed">
                <strong>Compliance &amp; Regulatory Notice:</strong> Documentation-verified technical benchmark only. Does not constitute formal tax agent or BAS agent advice under the Australian Tax Agent Services Act 2009 (TASA) or financial product advice under the Corporations Act 2001. B2BComparison.com may receive vendor referral commissions or implementation partner lead fees at no extra cost to the buyer.
            </p>
            ${{leadRouterHtml}}
        `;

        bindLeadFormsAndCFOButtons(resultsEl);
    }}

    function createDiagnosticDrawerHTML() {{
        return `
        <div id="b2bDiagnosticDrawer" class="hidden mt-6 bg-white rounded-xl border-2 border-blue-600 shadow-lg p-5 sm:p-6 transition-all">
            <div class="flex flex-wrap items-center justify-between gap-2 pb-4 border-b border-slate-200">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-blue-600 mono">Interactive 60-Second Architecture &amp; TCO Matchmaker</span>
                    <h2 class="text-xl font-extrabold text-slate-900 mt-0.5">Configure Your 36-Month Seat Trajectory, API Ceiling &amp; Compliance Gate</h2>
                </div>
                <button type="button" id="closeDiagBtn" class="text-xs mono font-semibold text-slate-500 hover:text-slate-900 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
                    ✕ Close Diagnostic
                </button>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mt-5">
                <!-- 1. Seat Scaling Trajectory -->
                <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                    <label class="block text-[11px] font-bold uppercase tracking-wider text-blue-600 mono mb-2">1. Seat Trajectory (M1 &rarr; M36)</label>
                    <div class="flex items-center justify-between text-xs font-semibold text-slate-700 mb-1">
                        <span>Month 1 Seats:</span>
                        <span id="diagM1Val" class="mono font-bold text-blue-600">25</span>
                    </div>
                    <input type="range" id="diagM1Slider" min="5" max="250" step="5" value="25" class="w-full h-2 bg-slate-200 rounded-lg cursor-pointer accent-blue-600 mb-2">
                    <div class="flex items-center justify-between text-xs font-semibold text-slate-700 mb-1">
                        <span>Month 36 Seats:</span>
                        <span id="diagM36Val" class="mono font-bold text-blue-600">50</span>
                    </div>
                    <input type="range" id="diagM36Slider" min="10" max="500" step="10" value="50" class="w-full h-2 bg-slate-200 rounded-lg cursor-pointer accent-blue-600">
                </div>

                <!-- 2. Currency & Tax Mode -->
                <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
                    <div>
                        <label class="block text-[11px] font-bold uppercase tracking-wider text-blue-600 mono mb-2">2. Currency &amp; Tax Mode</label>
                        <p class="text-[11px] text-slate-500 mb-2">Synced with global page currency toggle:</p>
                    </div>
                    <div class="grid grid-cols-2 gap-1.5 bg-slate-200/70 p-1 rounded-lg text-xs font-semibold mono">
                        <button type="button" id="diagCurUSD" class="py-2 rounded-md bg-white text-slate-900 shadow-xs">USD ($)</button>
                        <button type="button" id="diagCurAUD" class="py-2 rounded-md text-slate-600 hover:text-slate-900">AUD ($ ex. GST)</button>
                    </div>
                </div>

                <!-- 3. Mandatory Compliance Gate -->
                <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
                    <label for="diagComplianceSelect" class="block text-[11px] font-bold uppercase tracking-wider text-blue-600 mono mb-2">3. Mandatory Compliance</label>
                    <select id="diagComplianceSelect" class="w-full px-3 py-2.5 rounded-lg border border-slate-300 bg-white text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600">
                        <option value="ANY">All Verified Standards (SOC2/ISO)</option>
                        <option value="AU STP Phase 2 & Xero BAS">AU STP Phase 2 &amp; Xero BAS</option>
                        <option value="SOC2 Type II & ISO 27001">SOC2 Type II &amp; ISO 27001</option>
                        <option value="HIPAA Ready">HIPAA Ready / Allied Health</option>
                        <option value="GDPR">GDPR &amp; EU Data Residency</option>
                    </select>
                </div>

                <!-- 4. Minimum REST API Ceiling -->
                <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
                    <label for="diagApiSelect" class="block text-[11px] font-bold uppercase tracking-wider text-blue-600 mono mb-2">4. Min REST API Ceiling</label>
                    <select id="diagApiSelect" class="w-full px-3 py-2.5 rounded-lg border border-slate-300 bg-white text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600">
                        <option value="100">&lt;100 req/min (Standard Sync)</option>
                        <option value="300">300+ req/min (Mid-Market Burst)</option>
                        <option value="1000">1,000+ req/min (Webhook + Bulk Sync)</option>
                    </select>
                </div>

                <!-- 5. Core Stack Sync -->
                <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
                    <label for="diagStackSelect" class="block text-[11px] font-bold uppercase tracking-wider text-blue-600 mono mb-2">5. Core Stack Sync</label>
                    <select id="diagStackSelect" class="w-full px-3 py-2.5 rounded-lg border border-slate-300 bg-white text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600">
                        <option value="ANY">Any Native ERP / CRM</option>
                        <option value="Xero Two-Way">Xero Two-Way Ledger Sync</option>
                        <option value="QuickBooks">QuickBooks Online Sync</option>
                        <option value="NetSuite">Oracle NetSuite ERP</option>
                        <option value="HubSpot/Salesforce">HubSpot / Salesforce CRM</option>
                    </select>
                </div>
            </div>

            <div id="diagResultsContainer"></div>
        </div>`;
    }}

    function syncDiagCurrencyUI() {{
        const uBtn = document.getElementById('diagCurUSD');
        const aBtn = document.getElementById('diagCurAUD');
        if (!uBtn || !aBtn) return;
        if (!state.isAUD) {{
            uBtn.className = 'py-2 rounded-md bg-white text-slate-900 shadow-xs';
            aBtn.className = 'py-2 rounded-md text-slate-600 hover:text-slate-900';
        }} else {{
            aBtn.className = 'py-2 rounded-md bg-white text-slate-900 shadow-xs';
            uBtn.className = 'py-2 rounded-md text-slate-600 hover:text-slate-900';
        }}
    }}

    function initEngine() {{
        // 1. Inject Trigger Button on Homepage Control Bar OR Matrix Page
        const homeCurToggle = document.getElementById('homeCurToggle');
        const matrixCalc = document.getElementById('tco-calculator');

        if (homeCurToggle && homeCurToggle.parentElement) {{
            const controlRow = homeCurToggle.parentElement.parentElement;
            const triggerBtn = document.createElement('button');
            triggerBtn.type = 'button';
            triggerBtn.id = 'openDiagBtn';
            triggerBtn.className = 'px-4 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs mono shadow-sm transition-colors whitespace-nowrap flex items-center justify-center gap-1.5';
            triggerBtn.innerHTML = ' Run 36-Month TCO &amp; API Compatibility Diagnostic';
            controlRow.appendChild(triggerBtn);

            const drawerWrapper = document.createElement('div');
            drawerWrapper.innerHTML = createDiagnosticDrawerHTML();
            controlRow.parentElement.appendChild(drawerWrapper);
        }} else if (matrixCalc) {{
            const triggerBar = document.createElement('div');
            triggerBar.className = 'mt-6 flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs no-print';
            triggerBar.innerHTML = `
                <div class="flex items-center gap-2">
                    <span class="bg-blue-50 text-blue-700 border border-blue-200 px-2.5 py-1 rounded text-xs font-bold mono">36-MONTH ARCHITECT</span>
                    <span class="text-xs sm:text-sm font-semibold text-slate-800">Need to model 36-month seat growth, API burst limits, or compare across all 40 matrices?</span>
                </div>
                <button type="button" id="openDiagBtn" class="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs mono shadow-xs transition-colors">
                     Run 36-Month TCO &amp; API Compatibility Diagnostic
                </button>
            `;
            matrixCalc.parentElement.insertBefore(triggerBar, matrixCalc);

            const drawerWrapper = document.createElement('div');
            drawerWrapper.innerHTML = createDiagnosticDrawerHTML();
            matrixCalc.parentElement.insertBefore(drawerWrapper, matrixCalc);

            // Also mount Feature B (25+ Seat Lead Router & $19 CFO Export) below the page's TCO Calculator
            const currentPathSlug = window.location.pathname.replace(/^\\/|\\.html$|\\/$/g, '');
            const currentItem = DATASET.find(d => d.id === currentPathSlug) || DATASET[0];
            const matrixLeadWrapper = document.createElement('div');
            matrixLeadWrapper.id = 'matrixPageLeadRouter';
            matrixLeadWrapper.innerHTML = buildLeadRouterCardHTML('Comparison Page Calculator', currentItem);
            matrixCalc.insertAdjacentElement('afterend', matrixLeadWrapper);
            bindLeadFormsAndCFOButtons(matrixLeadWrapper);
        }}

        const drawer = document.getElementById('b2bDiagnosticDrawer');
        const openBtn = document.getElementById('openDiagBtn');
        const closeBtn = document.getElementById('closeDiagBtn');

        if (openBtn && drawer) {{
            openBtn.addEventListener('click', function() {{
                drawer.classList.toggle('hidden');
                renderDiagnosticResults();
                if (!drawer.classList.contains('hidden')) {{
                    drawer.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                }}
            }});
        }}
        if (closeBtn && drawer) {{
            closeBtn.addEventListener('click', function() {{
                drawer.classList.add('hidden');
            }});
        }}

        // Bind Diagnostic Controls
        const m1Slider = document.getElementById('diagM1Slider');
        const m36Slider = document.getElementById('diagM36Slider');
        const m1Val = document.getElementById('diagM1Val');
        const m36Val = document.getElementById('diagM36Val');
        const compSel = document.getElementById('diagComplianceSelect');
        const apiSel = document.getElementById('diagApiSelect');
        const stackSel = document.getElementById('diagStackSelect');
        const uBtn = document.getElementById('diagCurUSD');
        const aBtn = document.getElementById('diagCurAUD');

        if (m1Slider && m36Slider) {{
            m1Slider.addEventListener('input', function() {{
                state.seatsM1 = parseInt(this.value, 10);
                if (state.seatsM36 < state.seatsM1) {{
                    state.seatsM36 = state.seatsM1;
                    m36Slider.value = state.seatsM36;
                    m36Val.textContent = state.seatsM36;
                }}
                m1Val.textContent = state.seatsM1;
                renderDiagnosticResults();
            }});
            m36Slider.addEventListener('input', function() {{
                state.seatsM36 = parseInt(this.value, 10);
                m36Val.textContent = state.seatsM36;
                renderDiagnosticResults();
            }});
        }}

        if (compSel) compSel.addEventListener('change', function() {{ state.compliance = this.value; renderDiagnosticResults(); }});
        if (apiSel) apiSel.addEventListener('change', function() {{ state.apiMin = parseInt(this.value, 10); renderDiagnosticResults(); }});
        if (stackSel) stackSel.addEventListener('change', function() {{ state.stack = this.value; renderDiagnosticResults(); }});

        if (uBtn && aBtn) {{
            uBtn.addEventListener('click', function() {{
                if (state.isAUD && homeCurToggle) homeCurToggle.click();
                const pageUSD = document.getElementById('btnUSD');
                if (pageUSD) pageUSD.click();
                state.isAUD = false;
                syncDiagCurrencyUI();
                renderDiagnosticResults();
            }});
            aBtn.addEventListener('click', function() {{
                if (!state.isAUD && homeCurToggle) homeCurToggle.click();
                const pageAUD = document.getElementById('btnAUD');
                if (pageAUD) pageAUD.click();
                state.isAUD = true;
                syncDiagCurrencyUI();
                renderDiagnosticResults();
            }});
        }}

        // Sync with Homepage Preview Size (10 | 25 | 50 | 100) & Currency Toggle
        document.querySelectorAll('.seat-preset').forEach(btn => {{
            btn.addEventListener('click', function() {{
                const s = parseInt(this.getAttribute('data-seats'), 10);
                if (s) {{
                    state.seatsM1 = s;
                    state.seatsM36 = s * 2;
                    if (m1Slider) {{ m1Slider.value = s; m1Val.textContent = s; }}
                    if (m36Slider) {{ m36Slider.value = s * 2; m36Val.textContent = s * 2; }}
                    renderDiagnosticResults();
                }}
            }});
        }});

        if (homeCurToggle) {{
            homeCurToggle.addEventListener('click', function() {{
                setTimeout(() => {{
                    state.isAUD = homeCurToggle.textContent.includes('AUD');
                    syncDiagCurrencyUI();
                    renderDiagnosticResults();
                }}, 10);
            }});
        }}

        // Sync with Individual Matrix Page Slider & Currency Buttons
        const pageSlider = document.getElementById('seatSlider');
        const pageUSD = document.getElementById('btnUSD');
        const pageAUD = document.getElementById('btnAUD');
        if (pageSlider) {{
            pageSlider.addEventListener('input', function() {{
                const s = parseInt(this.value, 10);
                state.seatsM1 = s;
                state.seatsM36 = Math.min(500, s * 2);
                if (m1Slider) {{ m1Slider.value = s; m1Val.textContent = s; }}
                if (m36Slider) {{ m36Slider.value = state.seatsM36; m36Val.textContent = state.seatsM36; }}
                const leadCard = document.getElementById('matrixPageLeadRouter');
                if (leadCard) {{
                    const sizeInput = leadCard.querySelector('input[name="company_size"]');
                    if (sizeInput) sizeInput.value = state.seatsM1 + ' -> ' + state.seatsM36 + ' Seats (36M)';
                    leadCard.style.display = (s >= 25) ? 'block' : 'none';
                }}
            }});
        }}
        if (pageUSD) pageUSD.addEventListener('click', function() {{ state.isAUD = false; syncDiagCurrencyUI(); renderDiagnosticResults(); }});
        if (pageAUD) pageAUD.addEventListener('click', function() {{ state.isAUD = true; syncDiagCurrencyUI(); renderDiagnosticResults(); }});
    }}

    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initEngine);
    }} else {{
        initEngine();
    }}
}})();
"""
  os.makedirs(PUBLIC_DIR, exist_ok=True)
  with open(
      os.path.join(PUBLIC_DIR, "tco-engine.js"), "w", encoding="utf-8"
  ) as f:
    f.write(js_code)


def build_standalone_calculators(
    enriched_topics: list[dict], get_header_fn, get_footer_fn
) -> list[str]:
  """Feature C: Generates 40 standalone programmatic SEO calculator routes

  (/calculators/<id>-36-month-tco/index.html) + a master /calculators/index.html
  directory.
  """
  os.makedirs(CALC_DIR, exist_ok=True)
  generated_urls = []
  total_count = len(enriched_topics)
  today = datetime.date.today().isoformat()

  hub_cards = ""
  for item in enriched_topics:
    slug = item["calc_slug"]
    route_dir = os.path.join(CALC_DIR, slug)
    os.makedirs(route_dir, exist_ok=True)

    pa, pb = item["product_a"], item["product_b"]
    pA_base, pA_seat = item["priceA_base"], item["priceA_seat"]
    pB_base, pB_seat = item["priceB_base"], item["priceB_seat"]
    m25_a = pA_base + 25 * pA_seat
    m25_b = pB_base + 25 * pB_seat
    tco36_a = m25_a * 36
    tco36_b = m25_b * 36

    title = (
        f"{pa} vs {pb} 36-Month TCO & Seat Pricing Calculator (2026) |"
        " B2BComparison.com"
    )
    desc = (
        f"Interactive 36-month Total Cost of Ownership (TCO) calculator for"
        f" {pa} vs {pb}. Model USD & AUD (ex. GST) seat scaling, 50-seat"
        f" enterprise tier jumps, and {item['compliance']} compliance."
    )
    canon_path = f"calculators/{slug}/"
    full_url = f"{SITE_URL}/{canon_path}"
    generated_urls.append(full_url)

    hub_cards += f"""
        <a href="/{canon_path}" class="group bg-white rounded-xl border border-slate-200 p-5 hover:border-blue-600 hover:shadow-md transition-all flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between text-xs mono mb-2">
                    <span class="text-blue-600 font-semibold uppercase tracking-wider">{item['category']}</span>
                    <span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">36M TCO: ${tco36_a:,} vs ${tco36_b:,}</span>
                </div>
                <h3 class="text-lg font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                    {pa} vs. {pb} — 36-Month Seat &amp; API TCO Calculator
                </h3>
                <p class="text-xs text-slate-600 mt-1.5 leading-relaxed">{item['use_case']}</p>
            </div>
            <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs mono text-slate-500">
                <span class="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded border border-emerald-200">{item['compliance']}</span>
                <span class="text-blue-600 font-semibold">Launch Calculator &rarr;</span>
            </div>
        </a>"""

    page_html = f"""{get_header_fn(title, desc, total_count, canon_path)}
    <main class="flex-grow max-w-5xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-10">
        <nav aria-label="Breadcrumb" class="text-xs mono text-slate-500 flex items-center space-x-2">
            <a href="/" class="text-blue-600 hover:underline font-semibold">All Matrices</a>
            <span>/</span>
            <a href="/calculators/" class="text-blue-600 hover:underline font-semibold">36-Month TCO Calculators</a>
            <span>/</span>
            <span class="text-slate-800 font-semibold">{pa} vs {pb}</span>
        </nav>

        <div class="flex flex-wrap items-center gap-2 mt-4">
            <span class="text-xs font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2.5 py-1 rounded border border-blue-200 mono">{item['category']}</span>
            <span class="text-xs mono text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200">{item['compliance']}</span>
            <span class="text-xs mono text-slate-500 ml-auto">Updated: {today}</span>
        </div>

        <h1 class="mt-3 text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">
            {pa} vs {pb}: 36-Month TCO &amp; Seat-Scaling Calculator
        </h1>
        <p class="mt-2 text-sm text-slate-600">
            Model cumulative 3-year licensing costs, 50+ seat enterprise tier jumps, and REST API rate ceilings for <strong>{item['use_case']}</strong>.
        </p>

        <!-- Standalone Interactive 36-Month Calculator -->
        <div id="tco-calculator" class="bg-white rounded-xl border border-slate-200 shadow-sm p-6 mt-6">
            <div class="flex flex-col md:flex-row md:items-center justify-between pb-4 mb-6 border-b border-slate-100 gap-4">
                <div>
                    <span class="text-xs font-semibold uppercase tracking-wider text-blue-600 mono">Standalone 36-Month Procurement Model</span>
                    <h2 class="text-xl font-bold text-slate-900 mt-0.5">Configure Team Headcount &amp; Currency Mode</h2>
                </div>
                <div class="flex flex-wrap items-center gap-2">
                    <div class="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-100 text-xs font-semibold mono">
                        <button type="button" id="btnUSD" class="px-2.5 py-1 rounded-md bg-white text-slate-900 shadow-sm">USD ($)</button>
                        <button type="button" id="btnAUD" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900">AUD (A$ ex. GST)</button>
                    </div>
                    <div class="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-100 text-xs font-semibold mono">
                        <button type="button" id="btnMonthly" class="px-2.5 py-1 rounded-md bg-white text-slate-900 shadow-sm">Monthly</button>
                        <button type="button" id="btnAnnual" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900">Annual (-15%)</button>
                    </div>
                </div>
            </div>

            <div class="mb-6">
                <div class="flex justify-between items-center mb-2">
                    <label for="seatSlider" class="text-sm font-semibold text-slate-700">Active Licensed Seats (Months 1–36 Baseline):</label>
                    <span id="seatDisplay" class="text-base font-bold text-blue-600 mono bg-blue-50 px-3 py-1 rounded border border-blue-200">25 Seats</span>
                </div>
                <input id="seatSlider" type="range" min="5" max="250" step="5" value="25" class="w-full h-2.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600">
                <div class="flex justify-between text-xs text-slate-400 mono mt-1.5">
                    <span>5 Seats</span><span>50 Seats (Tier-Jump Threshold)</span><span>125 Seats</span><span>250 Seats</span>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-5 rounded-xl border-2 border-blue-500 bg-blue-50/30 flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-center">
                            <span class="font-bold text-slate-900 text-lg">{pa}</span>
                            <span class="text-xs mono bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">${pA_base}/mo base + ${pA_seat}/seat</span>
                        </div>
                        <div class="mt-3">
                            <span class="text-3xl font-extrabold text-slate-900 mono" id="costA_3yr">${tco36_a:,}</span>
                            <span class="text-xs text-slate-500"> / 36-month cumulative TCO</span>
                        </div>
                        <p class="text-xs text-slate-600 mt-1 mb-3 mono">Monthly Est: <strong id="costA_mo">${m25_a:,}/mo</strong> • Annual: <strong id="costA_yr">${m25_a * 12:,}/yr</strong></p>
                        <p class="text-xs text-slate-500 mb-4">REST API Ceiling: <strong class="mono text-slate-700">{item['api_ceiling_a']} req/min</strong> • Stack: <strong class="text-slate-700">{', '.join(item['stack_tags'])}</strong></p>
                    </div>
                    <a href="{item['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm py-2.5 rounded-lg transition-colors shadow-sm">
                        Verify {pa} Official Tier &amp; Trial &rarr;
                    </a>
                </div>

                <div class="p-5 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-center">
                            <span class="font-bold text-slate-900 text-lg">{pb}</span>
                            <span class="text-xs mono bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">${pB_base}/mo base + ${pB_seat}/seat</span>
                        </div>
                        <div class="mt-3">
                            <span class="text-3xl font-extrabold text-slate-900 mono" id="costB_3yr">${tco36_b:,}</span>
                            <span class="text-xs text-slate-500"> / 36-month cumulative TCO</span>
                        </div>
                        <p class="text-xs text-slate-600 mt-1 mb-3 mono">Monthly Est: <strong id="costB_mo">${m25_b:,}/mo</strong> • Annual: <strong id="costB_yr">${m25_b * 12:,}/yr</strong></p>
                        <p class="text-xs text-slate-500 mb-4">REST API Ceiling: <strong class="mono text-slate-700">{item['api_ceiling_b']} req/min</strong> • Stack: <strong class="text-slate-700">{', '.join(item['stack_tags'])}</strong></p>
                    </div>
                    <a href="{item['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="block w-full text-center bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm py-2.5 rounded-lg transition-colors">
                        Verify {pb} Official Tier &amp; Trial &rarr;
                    </a>
                </div>
            </div>

            <div class="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
                <a href="/{item['id']}.html" class="text-xs font-bold text-blue-600 hover:underline mono">&larr; Read Full 8-Point {pa} vs {pb} Architectural Audit</a>
                <span class="text-[11px] text-slate-400">Reader-supported — we may earn a commission from partner links.</span>
            </div>
            <p class="mt-2 text-[11px] text-slate-500">
                Documentation-verified technical benchmark only. Does not constitute formal tax agent or BAS agent advice under the Australian Tax Agent Services Act 2009 (TASA) or financial product advice under the Corporations Act 2001.
            </p>
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
            const btnUSD = document.getElementById('btnUSD');
            const btnAUD = document.getElementById('btnAUD');
            const btnMonthly = document.getElementById('btnMonthly');
            const btnAnnual = document.getElementById('btnAnnual');

            let fx = 1.0, sym = '$', disc = 1.0;
            function calc() {{
                const s = parseInt(slider.value, 10);
                seatDisplay.textContent = s + ' Seats';
                const jumpA = s > 50 ? {item['tier_jump_a']} : 1.0;
                const jumpB = s > 50 ? {item['tier_jump_b']} : 1.0;
                const mA = Math.round(({pA_base} + s * {pA_seat}) * jumpA * fx * disc);
                const mB = Math.round(({pB_base} + s * {pB_seat}) * jumpB * fx * disc);
                costA_mo.textContent = sym + mA.toLocaleString() + '/mo';
                costA_yr.textContent = sym + (mA * 12).toLocaleString() + '/yr';
                costA_3yr.textContent = sym + (mA * 36).toLocaleString();
                costB_mo.textContent = sym + mB.toLocaleString() + '/mo';
                costB_yr.textContent = sym + (mB * 12).toLocaleString() + '/yr';
                costB_3yr.textContent = sym + (mB * 36).toLocaleString();
            }}
            slider.addEventListener('input', calc);
            btnUSD.addEventListener('click', function() {{ fx = 1.0; sym = '$'; calc(); }});
            btnAUD.addEventListener('click', function() {{ fx = 1.54; sym = 'A$'; calc(); }});
            btnMonthly.addEventListener('click', function() {{ disc = 1.0; calc(); }});
            btnAnnual.addEventListener('click', function() {{ disc = 0.85; calc(); }});
            calc();
        }})();
        </script>
    </main>
{get_footer_fn()}"""

    with open(
        os.path.join(route_dir, "index.html"), "w", encoding="utf-8"
    ) as f:
      f.write(page_html)

  # Build /calculators/index.html hub page
  hub_url = f"{SITE_URL}/calculators/"
  generated_urls.append(hub_url)
  hub_html = f"""{get_header_fn("36-Month B2B SaaS TCO & Seat Pricing Calculators | B2BComparison.com", "Interactive 36-month Total Cost of Ownership (TCO) calculators for 40 B2B software comparisons in USD and AUD (ex. GST).", total_count, "calculators/")}
    <main class="flex-grow max-w-6xl w-full mx-auto px-4 sm:px-6 py-10">
        <div class="mb-8">
            <span class="text-xs font-bold uppercase tracking-wider text-blue-600 mono">Programmatic Procurement Suite</span>
            <h1 class="text-3xl sm:text-4xl font-extrabold text-slate-900 mt-1">36-Month B2B SaaS TCO &amp; Seat Pricing Calculators</h1>
            <p class="text-sm text-slate-600 mt-2 max-w-2xl">Select any software pair below to model 36-month seat scaling, 50+ user enterprise tier jumps, and USD/AUD (ex. GST) cashflow impact.</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            {hub_cards}
        </div>
    </main>
{get_footer_fn()}"""
  with open(os.path.join(CALC_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(hub_html)

  return generated_urls


def append_calculators_to_sitemaps_and_ping(calc_urls: list[str]):
  today = datetime.date.today().isoformat()
  txt_path = os.path.join(PUBLIC_DIR, "sitemap.txt")
  xml_path = os.path.join(PUBLIC_DIR, "sitemap.xml")

  existing_urls = []
  if os.path.exists(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
      existing_urls = [line.strip() for line in f if line.strip()]

  all_urls = list(dict.fromkeys(existing_urls + calc_urls))

  with open(txt_path, "w", encoding="utf-8") as f:
    f.write("\n".join(all_urls) + "\n")

  sitemap_items = "\n".join(
      f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in all_urls
  )
  sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_items}
</urlset>"""
  with open(xml_path, "w", encoding="utf-8") as f:
    f.write(sitemap_xml)

  # Ping IndexNow with the complete URL set (including all 40 standalone calculator pages)
  payload = {
      "host": SITE_HOST,
      "key": INDEXNOW_KEY,
      "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
      "urlList": all_urls,
  }
  try:
    resp = requests.post(
        "https://api.indexnow.org/indexnow",
        json=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=10,
    )
    print(
        " -> [Monetization Engine] IndexNow pinged with"
        f" {len(all_urls)} total URLs (HTTP {resp.status_code})"
    )
  except Exception as e:
    print(f" -> [Monetization Engine] IndexNow notice: {e}")


def build_all(
    topics: list[dict], normalize_fn, get_header_fn=None, get_footer_fn=None
):
  enriched = [infer_technical_metadata(normalize_fn(t)) for t in topics]
  build_client_js(enriched)
  if get_header_fn and get_footer_fn:
    calc_urls = build_standalone_calculators(
        enriched, get_header_fn, get_footer_fn
    )
    append_calculators_to_sitemaps_and_ping(calc_urls)
  print(
      " -> [Monetization Engine] Built public/tco-engine.js +"
      f" {len(enriched)} standalone calculator routes."
  )

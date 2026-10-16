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
    feature_name: str = Field(description="Specific technical feature, limit, or pricing tier")
    product_a_spec: str = Field(description="Concrete value, limit, or cost for Product A")
    product_b_spec: str = Field(description="Concrete value, limit, or cost for Product B")
    winner: str = Field(description="Name of the winning product for this row, or 'Tie'")

class ComparisonArticle(BaseModel):
    seo_title: str = Field(description="High-intent title under 60 chars, e.g., 'Rippling vs Deel: Global Payroll Specs'")
    meta_description: str = Field(description="Direct summary of the verdict under 155 chars")
    direct_verdict: str = Field(description="2-sentence executive summary stating exactly who should buy Product A vs Product B.")
    comparison_matrix: list[FeatureRow] = Field(description="6 to 8 specific technical and pricing comparison rows")
    product_a_pros: list[str] = Field(description="3 concrete technical advantages of Product A")
    product_a_cons: list[str] = Field(description="2 concrete limitations or hidden costs of Product A")
    product_b_pros: list[str] = Field(description="3 concrete technical advantages of Product B")
    product_b_cons: list[str] = Field(description="2 concrete limitations or hidden costs of Product B")
    hidden_gotchas: str = Field(description="Paragraph detailing API limits, lock-in clauses, or add-on fees buyers miss.")

# ---------------------------------------------------------
# 2. WEB SCRAPER HELPER
# ---------------------------------------------------------
def scrape_page_text(url: str, max_chars: int = 12000) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; B2BSpecBot/1.0)"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "svg"]):
            tag.decompose()
        text = " ".join(soup.stripped_strings)
        return text[:max_chars]
    except Exception as e:
        return f"Could not scrape live URL ({e}). Rely on verified technical specifications."

# ---------------------------------------------------------
# 3. GEMINI SYNTHESIS ENGINE (WITH AUTO-FALLBACK)
# ---------------------------------------------------------
FREE_TIER_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-2.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash-lite",
]

def synthesize_comparison(topic: dict) -> ComparisonArticle:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    raw_a = scrape_page_text(topic["url_a"])
    raw_b = scrape_page_text(topic["url_b"])

    system_instruction = (
        "You are a ruthless, objective B2B software systems architect. "
        "Compare the two products strictly for the specified use case using the scraped context. "
        "BANNED WORDS: delve, tapestry, testament, fast-paced, digital landscape, crucial, overarching, realm. "
        "Lead with concrete numbers, API rate limits, integration architecture, and exact pricing mechanics."
    )

    prompt = f"""
    Compare {topic['product_a']} vs {topic['product_b']} specifically for: {topic['use_case']}.
    
    Scraped Context for {topic['product_a']}:
    {raw_a}
    
    Scraped Context for {topic['product_b']}:
    {raw_b}
    """

    last_error = None
    for model_name in FREE_TIER_MODELS:
        try:
            print(f"  -> Trying model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=ComparisonArticle,
                    temperature=0.2,
                ),
            )
            print(f"  -> Success with {model_name}!")
            return ComparisonArticle.model_validate_json(response.text)
        except Exception as e:
            print(f"  -> {model_name} busy or rate-limited ({e}). Switching to backup model in 4s...")
            last_error = e
            time.sleep(4)

    raise RuntimeError(f"All free-tier models were temporarily busy. Last error: {last_error}")

# ---------------------------------------------------------
# 4. ZERO-DEPENDENCY STATIC HTML GENERATOR
# ---------------------------------------------------------
def render_html(topic: dict, data: ComparisonArticle) -> str:
    rows_html = ""
    for row in data.comparison_matrix:
        rows_html += f"""
        <tr class="border-b border-slate-200">
            <td class="p-4 font-semibold text-slate-800">{row.feature_name}</td>
            <td class="p-4 text-slate-600">{row.product_a_spec}</td>
            <td class="p-4 text-slate-600">{row.product_b_spec}</td>
            <td class="p-4"><span class="px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold">{row.winner}</span></td>
        </tr>"""

    a_pros = "".join(f"<li class='mb-1'>✅ {p}</li>" for p in data.product_a_pros)
    a_cons = "".join(f"<li class='mb-1'>❌ {c}</li>" for c in data.product_a_cons)
    b_pros = "".join(f"<li class='mb-1'>✅ {p}</li>" for p in data.product_b_pros)
    b_cons = "".join(f"<li class='mb-1'>❌ {c}</li>" for c in data.product_b_cons)

    today = datetime.date.today().isoformat()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data.seo_title}</title>
    <meta name="description" content="{data.meta_description}">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900 antialiased">
    <main class="max-w-4xl mx-auto px-6 py-12">
        <a href="index.html" class="text-sm font-medium text-indigo-600 hover:underline">&larr; All B2B Architecture Comparisons</a>
        <div class="mt-4 text-xs uppercase tracking-wider text-slate-500 font-semibold">Updated: {today} &bull; {topic['use_case']}</div>
        <h1 class="mt-2 text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">{data.seo_title}</h1>
        
        <div class="mt-6 p-6 bg-indigo-950 text-white rounded-xl shadow-md">
            <div class="text-xs uppercase tracking-wider text-indigo-300 font-bold mb-1">Executive Verdict</div>
            <p class="text-lg leading-relaxed">{data.direct_verdict}</p>
            <div class="mt-6 flex flex-wrap gap-4">
                <a href="{topic['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-lg transition">Check {topic['product_a']} Pricing &rarr;</a>
                <a href="{topic['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="px-5 py-2.5 bg-white hover:bg-slate-100 text-slate-900 font-bold rounded-lg transition">Check {topic['product_b']} Pricing &rarr;</a>
            </div>
        </div>

        <h2 class="mt-10 text-2xl font-bold">Technical & Pricing Matrix</h2>
        <div class="mt-4 overflow-x-auto bg-white rounded-xl shadow-sm border border-slate-200">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-slate-100 border-b border-slate-200 text-xs uppercase text-slate-600">
                        <th class="p-4">Specification</th>
                        <th class="p-4">{topic['product_a']}</th>
                        <th class="p-4">{topic['product_b']}</th>
                        <th class="p-4">Edge</th>
                    </tr>
                </thead>
                <tbody class="text-sm">{rows_html}</tbody>
            </table>
        </div>

        <div class="mt-10 grid sm:grid-cols-2 gap-6">
            <div class="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
                <h3 class="text-xl font-bold mb-4">{topic['product_a']} Breakdown</h3>
                <ul class="text-sm text-slate-700 mb-4">{a_pros}</ul>
                <ul class="text-sm text-slate-600">{a_cons}</ul>
                <a href="{topic['aff_link_a']}" target="_blank" rel="nofollow sponsored" class="mt-6 block text-center w-full py-2.5 bg-slate-900 text-white font-semibold rounded-lg hover:bg-slate-800">Try {topic['product_a']} Free</a>
            </div>
            <div class="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
                <h3 class="text-xl font-bold mb-4">{topic['product_b']} Breakdown</h3>
                <ul class="text-sm text-slate-700 mb-4">{b_pros}</ul>
                <ul class="text-sm text-slate-600">{b_cons}</ul>
                <a href="{topic['aff_link_b']}" target="_blank" rel="nofollow sponsored" class="mt-6 block text-center w-full py-2.5 bg-slate-900 text-white font-semibold rounded-lg hover:bg-slate-800">Try {topic['product_b']} Free</a>
            </div>
        </div>

        <div class="mt-10 p-6 bg-amber-50 border border-amber-200 rounded-xl">
            <h3 class="text-lg font-bold text-amber-900">⚠️ Hidden Gotchas & Integration Limits</h3>
            <p class="mt-2 text-sm text-amber-800 leading-relaxed">{data.hidden_gotchas}</p>
        </div>
    </main>
</body>
</html>"""

def rebuild_index(topics: list[dict]):
    os.makedirs("public", exist_ok=True)
    links = ""
    for t in topics:
        if t.get("processed"):
            links += f"""
            <a href="{t['id']}.html" class="block p-5 bg-white rounded-xl border border-slate-200 hover:border-indigo-500 shadow-sm transition">
                <div class="text-xs font-bold text-indigo-600 uppercase">{t['use_case']}</div>
                <div class="mt-1 text-lg font-bold text-slate-900">{t['product_a']} vs {t['product_b']}</div>
            </a>"""
    
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B2B Stack Integration & Pricing Matrix</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900">
    <main class="max-w-4xl mx-auto px-6 py-12">
        <h1 class="text-3xl font-extrabold">B2B Software Compatibility & Pricing Benchmarks</h1>
        <p class="mt-2 text-slate-600">Unbiased, spec-level comparisons of enterprise SaaS integrations, API limits, and total cost of ownership.</p>
        <div class="mt-8 grid gap-4">{links}</div>
    </main>
</body>
</html>"""
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

def main():
    with open("topics.json", "r", encoding="utf-8") as f:
        topics = json.load(f)

    os.makedirs("public", exist_ok=True)
    generated_count = 0

    # Process up to 2 new pages per daily run to maintain natural SEO velocity
    for topic in topics:
        if not topic.get("processed") and generated_count < 2:
            print(f"Generating comparison for: {topic['id']}...")
            article_data = synthesize_comparison(topic)
            html_out = render_html(topic, article_data)
            
            with open(f"public/{topic['id']}.html", "w", encoding="utf-8") as out_f:
                out_f.write(html_out)
            
            topic["processed"] = True
            generated_count += 1
            time.sleep(3)

    with open("topics.json", "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2)

    rebuild_index(topics)
    print(f"Run complete. Generated {generated_count} new pages.")

if __name__ == "__main__":
    main()

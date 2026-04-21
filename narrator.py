import anthropic
import os
from dotenv import load_dotenv
 
load_dotenv()
 
# ── System prompt ──────────────────────────────────────────────────────────────
 
SYSTEM_PROMPT = """You are Perceiv, an AI data analyst assistant. Your job is to help users understand their datasets through clear, specific, plain-English analysis.
 
When writing your initial analysis:
- Be specific — always reference actual column names, real numbers from the data, and concrete percentages
- Structure your response with 3–4 short paragraphs: (1) dataset overview, (2) data quality issues, (3) notable patterns or distributions, (4) what the user should investigate first
- Flag skewed distributions by name (e.g. "revenue is right-skewed — median $187 vs mean $342, suggesting a small number of high-value outliers")
- Call out datetime columns and what time range they cover
- Mention dominance in categorical columns (e.g. "West accounts for 52% of region values")
- Be direct and specific — avoid generic phrases like "this dataset appears to contain"
- Keep a professional but approachable tone — you're a senior analyst explaining to a capable colleague, not writing an academic report
 
When answering follow-up questions:
- Answer the specific question first, then add one relevant insight the user may not have thought to ask
- If you can give a number, give it — don't just describe trends
- If the question requires a calculation you weren't given, say what you'd need and suggest how to get it
- Keep follow-up responses concise — 3–6 sentences unless the question is complex"""
 
 
# ── Prompt builders ────────────────────────────────────────────────────────────
 
def build_initial_prompt(summary, missing_report, col_stats):
    rows = summary.get("rows")
    cols = summary.get("columns")
    missing_pct = summary.get("missing_pct")
    numeric_cols = summary.get("numeric_cols")
    text_cols = summary.get("text_cols")
    datetime_cols = summary.get("datetime_cols", 0)
    datetime_names = summary.get("datetime_col_names", [])
 
    prompt = f"Dataset: {rows} rows × {cols} columns\n"
    prompt += f"Column types: {numeric_cols} numeric, {text_cols} text, {datetime_cols} datetime\n"
    prompt += f"Overall missing: {missing_pct}%\n"
 
    if datetime_names:
        prompt += f"Datetime columns detected: {', '.join(datetime_names)}\n"
 
    # Missing report — only columns with issues
    high_missing = [r for r in missing_report if r["flag"] == "HIGH"]
    low_missing  = [r for r in missing_report if r["flag"] == "LOW"]
    clean_count  = sum(1 for r in missing_report if r["flag"] == "CLEAN")
 
    prompt += f"\nMissing values: {clean_count} columns fully clean\n"
    if high_missing:
        prompt += "HIGH missing (≥10%):\n"
        for r in high_missing:
            prompt += f"  - {r['column']}: {r['pct']}% missing\n"
    if low_missing:
        prompt += "LOW missing (<10%):\n"
        for r in low_missing:
            prompt += f"  - {r['column']}: {r['pct']}% missing\n"
 
    # Column stats — numeric distributions
    prompt += "\nColumn statistics:\n"
    for col_name, s in col_stats.items():
        if s.get("type") == "numeric":
            prompt += (
                f"  {col_name}: mean={s['mean']}, median={s['median']}, "
                f"std={s['std']}, min={s['min']}, max={s['max']}, "
                f"distribution={s.get('skew', 'unknown')}\n"
            )
        elif s.get("type") == "text":
            prompt += (
                f"  {col_name}: {s['unique_values']} unique values, "
                f"most common='{s['most_common']}' ({s.get('top_pct', '?')}% of rows)\n"
            )
        elif s.get("type") == "datetime":
            date_range = ""
            if "min" in s and "max" in s:
                date_range = f", range {s['min']} to {s['max']}"
            prompt += f"  {col_name}: datetime column{date_range}\n"
 
    prompt += (
        "\nWrite your initial analysis following the structure in your instructions. "
        "Be specific — use the actual numbers above, not vague descriptions."
    )
    return prompt
 
 
def build_followup_prompt(question, summary, col_stats):
    """Build context for a follow-up question."""
    rows = summary.get("rows")
    cols = summary.get("columns")
 
    context = f"Dataset context: {rows} rows × {cols} columns\n"
    context += "Column stats available:\n"
    for col_name, s in col_stats.items():
        if s.get("type") == "numeric":
            context += (
                f"  {col_name} (numeric): mean={s['mean']}, "
                f"median={s['median']}, min={s['min']}, max={s['max']}\n"
            )
        elif s.get("type") == "text":
            context += (
                f"  {col_name} (text): {s['unique_values']} unique, "
                f"top='{s['most_common']}'\n"
            )
        elif s.get("type") == "datetime":
            date_range = f", {s.get('min','')} to {s.get('max','')}" if "min" in s else ""
            context += f"  {col_name} (datetime{date_range})\n"
 
    return f"{context}\nUser question: {question}"
 
 
# ── API calls ──────────────────────────────────────────────────────────────────
 
def call_llm_api(messages: list, max_tokens: int = 800) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    return response.content[0].text
 
 
# ── Public interface ───────────────────────────────────────────────────────────
 
def generate_narrative(summary, missing_report, col_stats=None):
    """Generate the initial AI analysis. col_stats improves specificity."""
    if col_stats is None:
        col_stats = {}
    prompt = build_initial_prompt(summary, missing_report, col_stats)
    return call_llm_api([{"role": "user", "content": prompt}], max_tokens=800)
 
 
def answer_question(question: str, summary: dict, col_stats: dict, history: list) -> str:
    """
    Answer a follow-up question using conversation history.
 
    history: list of {"role": "user"|"assistant", "content": str}
             — the full conversation so far, NOT including the current question.
    """
    context_prompt = build_followup_prompt(question, summary, col_stats)
 
    messages = history + [{"role": "user", "content": context_prompt}]
    return call_llm_api(messages, max_tokens=500)
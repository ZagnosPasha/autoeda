import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are Perceiv, an AI data analyst. Give sharp, specific, bullet-point analysis. No paragraphs.

FORMAT for initial analysis — use exactly these four sections with emoji headers:

📋 **Overview**
- [dataset size, what it contains, time range if applicable]
- [key identifier column if present]

⚠️ **Data Quality**
- [each missing value issue with exact %, flagged as HIGH/LOW]
- [any invalid values, wrong types, anomalies]
- If no issues: "All columns clean ✓"

📊 **Key Patterns**
- [dominant category values with %]
- [skewed distributions with mean vs median]
- [notable correlations or concentrations]

🔍 **Investigate First**
- [most important thing to fix/explore, specific action]
- [second priority]
- [third priority]

RULES:
- Every bullet uses actual column names and real numbers from the data
- Max 2-3 bullets per section — ruthlessly prioritise
- No paragraphs, no preamble, no "this dataset contains..."
- Bold column names with **column_name**
- Keep each bullet under 15 words

For follow-up questions:
- Answer in 2-4 bullets maximum
- Lead with the number/fact, then explain
- Bold any column names referenced"""


def build_initial_prompt(summary, missing_report, col_stats):
    rows = summary.get("rows")
    cols = summary.get("columns")
    missing_pct = summary.get("missing_pct")
    numeric_cols = summary.get("numeric_cols")
    text_cols = summary.get("text_cols")
    datetime_cols = summary.get("datetime_cols", 0)
    datetime_names = summary.get("datetime_col_names", [])

    prompt = f"Dataset: {rows:,} rows × {cols} columns\n"
    prompt += f"Types: {numeric_cols} numeric, {text_cols} text, {datetime_cols} datetime\n"
    prompt += f"Overall missing: {missing_pct}%\n"

    if datetime_names:
        prompt += f"Datetime columns: {', '.join(datetime_names)}\n"

    high_missing = [r for r in missing_report if r["flag"] == "HIGH"]
    low_missing  = [r for r in missing_report if r["flag"] == "LOW"]
    clean_count  = sum(1 for r in missing_report if r["flag"] == "CLEAN")

    prompt += f"Clean columns: {clean_count}/{cols}\n"
    if high_missing:
        prompt += "HIGH missing:\n" + "".join(f"  {r['column']}: {r['pct']}%\n" for r in high_missing)
    if low_missing:
        prompt += "LOW missing:\n" + "".join(f"  {r['column']}: {r['pct']}%\n" for r in low_missing)

    prompt += "\nColumn stats:\n"
    for col_name, s in col_stats.items():
        if s.get("type") == "numeric":
            prompt += (f"  {col_name}: mean={s['mean']}, median={s['median']}, "
                       f"min={s['min']}, max={s['max']}, {s.get('skew','')}\n")
        elif s.get("type") == "text":
            prompt += (f"  {col_name}: {s['unique_values']} unique, "
                       f"top='{s['most_common']}' ({s.get('top_pct','?')}%)\n")
        elif s.get("type") == "datetime":
            rng = f" [{s['min']} → {s['max']}]" if "min" in s else ""
            prompt += f"  {col_name}: datetime{rng}\n"

    prompt += "\nWrite the analysis following your format instructions exactly."
    return prompt


def build_followup_prompt(question, summary, col_stats):
    rows = summary.get("rows")
    cols = summary.get("columns")
    context = f"Dataset: {rows:,} rows × {cols} columns\nStats:\n"
    for col_name, s in col_stats.items():
        if s.get("type") == "numeric":
            context += f"  {col_name}: mean={s['mean']}, median={s['median']}, min={s['min']}, max={s['max']}\n"
        elif s.get("type") == "text":
            context += f"  {col_name}: {s['unique_values']} unique, top='{s['most_common']}'\n"
        elif s.get("type") == "datetime":
            rng = f" [{s.get('min','')} → {s.get('max','')}]" if "min" in s else ""
            context += f"  {col_name}: datetime{rng}\n"
    return f"{context}\nQuestion: {question}"


def call_llm_api(messages: list, max_tokens: int = 600) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    return response.content[0].text


def generate_narrative(summary, missing_report, col_stats=None):
    if col_stats is None:
        col_stats = {}
    prompt = build_initial_prompt(summary, missing_report, col_stats)
    return call_llm_api([{"role": "user", "content": prompt}], max_tokens=600)


def answer_question(question: str, summary: dict, col_stats: dict, history: list) -> str:
    context_prompt = build_followup_prompt(question, summary, col_stats)
    messages = history + [{"role": "user", "content": context_prompt}]
    return call_llm_api(messages, max_tokens=400)
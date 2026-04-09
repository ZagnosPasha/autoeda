import anthropic
import os
from dotenv import load_dotenv
from analyser import load_data, get_missing_report,get_summary

load_dotenv()

def build_prompt(summary,missing_report):
    row = summary.get("rows","No such field")
    cols = summary.get("columns","No such field")
    missing_pcnt = summary.get("missing_pct","No such field")

    prompt = f"Here is my dataset information: \n"
    prompt += f"-{row} rows, {cols} columns \n"
    prompt += f"-{missing_pcnt}% is missing overall \n"
    

    for stats in missing_report:
        categry = stats.get("column","No such field")
        misng_prcnt_catgry = stats.get("pct","No such field")
        flag = stats.get("flag","No such field")

        prompt += f"{categry} is {misng_prcnt_catgry}% missing - flagged {flag}\n"
        
    prompt += "\nPlease write a plain-English paragraph explaining what this data looks like and what a data science student should pay attention to. "
    return prompt

def call_llm_api(prompt):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text

def generate_narrative(summary, missing_report):
    prompt = build_prompt(summary, missing_report)
    narrative = call_llm_api(prompt)
    return narrative


# openai_integration.py
import os
from utils import verbose_print

# Read benchmarking year and engine model from environment
YEAR = os.getenv("YEAR", "2025")
ENGINE_MODEL = os.getenv("ENGINE_MODEL", "gpt-4o")

def generate_full_explanation(client, data_description, chart_type):
    """
    Generates a three-part explanation:
      1. "Why this chart matters" – a brief explanation.
      2. "Industry Standards" – obtains benchmarks for the year from web search.
      3. "AI Insights" – uses the industry standards as context to provide positively biased insights.
    Returns the combined explanation text.
    """
    if not client:
        return "AI client not available. No explanation generated."
    
    # Part 1: Why this chart matters
    why_prompt = f"""
You are a marketing analytics expert in email marketing.
Based on the following data context and chart type:
Data Context: {data_description}
Chart Type: {chart_type}
Explain briefly why this chart is important for understanding email marketing performance.
Respond in plain text.
    """.strip()
    try:
        why_response = client.responses.create(
            model=ENGINE_MODEL,
            input=why_prompt
        )
        why_text = why_response.output_text.strip()
    except Exception as e:
        why_text = f"Error in 'Why this chart matters': {e}"
    
    # Part 2: Industry Standards via web search
    industry_prompt = f"""
You are a marketing analytics expert.
Using web search, provide industry standards and benchmarks for email marketing performance for the year {YEAR} related to the following chart:
Data Context: {data_description}
Chart Type: {chart_type}
Respond in plain text and include at least one source citation with a URL.
    """.strip()
    try:
        industry_response = client.responses.create(
            model=ENGINE_MODEL,
            tools=[{"type": "web_search_preview"}],
            input=industry_prompt
        )
        industry_text = industry_response.output_text.strip()
    except Exception as e:
        industry_text = f"Error in 'Industry Standards': {e}"
    
    # Part 3: AI Insights using industry standards as context
    insights_prompt = f"""
You are a marketing analytics expert.
Given the following industry standards and benchmarks:
{industry_text}
And based on the data context:
{data_description}
And the chart type:
{chart_type}
Provide exactly 3 bullet points summarizing key insights, highlighting how our performance compares positively to industry standards.
Avoid stating obvious conclusions.
Respond in plain text.
    """.strip()
    try:
        insights_response = client.responses.create(
            model=ENGINE_MODEL,
            input=insights_prompt
        )
        insights_text = insights_response.output_text.strip()
    except Exception as e:
        insights_text = f"Error in 'AI Insights': {e}"
    
    final_output = (
        f"Why this chart matters:\n{why_text}\n\n"
        f"Industry Standards:\n{industry_text}\n\n"
        f"AI Insights:\n{insights_text}"
    )
    return final_output

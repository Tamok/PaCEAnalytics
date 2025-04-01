# openai_integration.py
import os
import json
import hashlib
from utils import verbose_print

CACHE_FILE = "ai_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def get_cache_key(data_description, chart_type):
    key = data_description + chart_type
    return hashlib.md5(key.encode("utf-8")).hexdigest()

def generate_full_explanation(client, data_description, chart_type):
    """
    Generates an explanation with the following structure:
      - Overview: one short paragraph explaining what the chart shows.
      - AI Insights: three bullet points.
      - Recommendations: two bullet points.
      - Industry Standards: web-sourced 2025 statistics with embedded links.
    
    This function first checks if a cached result exists for the given data_description and chart_type.
    If so, it returns the cached response; otherwise, it calls the AI, caches the result, and returns it.
    """
    cache = load_cache()
    key = get_cache_key(data_description, chart_type)
    if key in cache:
        verbose_print("Using cached AI explanation.")
        return cache[key]
    
    prompt = f"""
You are a marketing analytics expert. Analyze the following data context and chart type.
Data Context: {data_description}
Chart Type: {chart_type}
Generate an explanation that includes:
1. An overview in one short paragraph explaining what the chart shows.
2. Three bullet points with AI Insights.
3. Two bullet points with Recommendations.
4. Industry Standards: Use web search to source relevant 2025 statistics and embed the source link.
Format your response exactly as follows:

Overview: <your overview>

AI Insights:
- <bullet point 1>
- <bullet point 2>
- <bullet point 3>

Recommendations:
- <bullet point 1>
- <bullet point 2>

Industry Standards:
<your sourced statistics with citation>

Respond in plain text.
    """.strip()
    try:
        response = client.responses.create(
            model="gpt-4o",
            input=prompt
        )
        explanation = response.output_text.strip()
    except Exception as e:
        explanation = f"Error in generating explanation: {e}"
    
    cache[key] = explanation
    save_cache(cache)
    return explanation

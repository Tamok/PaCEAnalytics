# visualization.py
import matplotlib.pyplot as plt
import seaborn as sns
import dataframe_image as dfi
from utils import UCSB_BLUE, PACE_LINKS, add_slide_number, place_logo_on_figure
from openai_integration import generate_full_explanation
import os

# Use letter-size landscape (11 x 8.5 inches)
FIGSIZE = (11, 8.5)

def create_summary_table_slide(summary_df, pdf):
    """
    Exports the summary table as a high-resolution, centered image and inserts it into the PDF.
    Adjusts styling to match branding.
    """
    table_png = "summary_table.png"
    styled = (
        summary_df.style
        .set_caption("Overall Email Marketing KPIs")
        .set_table_styles([
            {
                'selector': 'caption',
                'props': [('color', UCSB_BLUE),
                          ('font-size', '18px'),
                          ('text-align', 'center'),
                          ('font-weight', 'bold')]
            },
            {
                'selector': 'th',
                'props': [('text-align', 'center'), ('background-color', PACE_LINKS), ('color', 'white')]
            }
        ])
        .set_properties(**{'text-align': 'center', 'font-size': '10pt', 'width': '80px'})
        .background_gradient(cmap="Blues")
    )
    dfi.export(styled, table_png, dpi=200)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    ax.axis('off')
    img = plt.imread(table_png)
    ax.imshow(img, aspect='auto')
    add_slide_number(fig)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_correlation_heatmap(df_rates, pdf, client):
    """
    Creates a correlation heatmap of the key rate metrics and a text slide with a full explanation.
    """
    rate_cols = ["Delivery Rate", "Open Rate", "Click Rate", "Bounce Rate", "Unsubscribe Rate"]
    corr = df_rates[rate_cols].corr()

    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Correlation Heatmap for Key Email Marketing Rates", fontsize=16, color=UCSB_BLUE)
    add_slide_number(fig)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    raw_data_text = corr.to_string()
    explanation = ("This heatmap displays the correlation between key email marketing rate metrics. "
                   "It shows how one metric may relate to another.")
    full_explanation = generate_full_explanation(client, f"Correlation Data:\n{raw_data_text}", "Heatmap")
    text_content = (
        f"Why this chart matters:\n{explanation}\n\n"
        f"Industry Standards:\n(Referenced benchmarks for {os.getenv('YEAR', '2025')})\n\n"
        f"AI Insights:\n{full_explanation}"
    )
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    ax.axis('off')
    ax.text(0.01, 0.95, text_content, ha='left', va='top', wrap=True, fontsize=11)
    add_slide_number(fig)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_distribution_histogram(df_rates, metric, pdf, client):
    """
    Creates a histogram for the given rate metric and a text slide with a full explanation.
    """
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    sns.histplot(df_rates[metric].dropna(), kde=True, color=PACE_LINKS, ax=ax)
    ax.set_title(f"Distribution of {metric}", fontsize=16, color=UCSB_BLUE)
    ax.set_xlabel(metric)
    ax.set_ylabel("Frequency (Count per bin)")
    add_slide_number(fig)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    summary_text = df_rates[metric].describe().to_string()
    explanation = f"This histogram shows the distribution of {metric} (in %). Frequency indicates how many records fall into each bin."
    full_explanation = generate_full_explanation(client, f"Distribution Summary for {metric}:\n{summary_text}", f"Histogram for {metric}")
    text_content = (
        f"Why this chart matters:\n{explanation}\n\n"
        f"Industry Standards:\n(Referenced benchmarks for {os.getenv('YEAR', '2025')})\n\n"
        f"AI Insights:\n{full_explanation}"
    )
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    ax.axis('off')
    ax.text(0.01, 0.95, text_content, ha='left', va='top', wrap=True, fontsize=11)
    add_slide_number(fig)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_definitions_slide(pdf):
    """
    Creates a definitions slide that explains key terms such as "Frequency" and the rate metrics.
    """
    definitions = (
        "Definitions:\n\n"
        "Frequency: The number of records (email campaigns) that fall within a specific range (bin) in a histogram. "
        "It indicates how common a particular performance range is.\n\n"
        "Delivery Rate: (Delivered/Sent) * 100\n"
        "Open Rate: (Opened/Delivered) * 100\n"
        "Click Rate: (Clicked/Delivered) * 100\n"
        "Bounce Rate: (Bounced/Sent) * 100\n"
        "Unsubscribe Rate: (Unsubscribes/Sent) * 100\n"
    )
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    ax.axis('off')
    ax.text(0.05, 0.9, definitions, ha='left', va='top', fontsize=12, color=UCSB_BLUE)
    add_slide_number(fig)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_overall_conclusion(summary_df, pdf, client):
    """
    Generates a final overall conclusion slide by feeding the raw summary table data to the AI,
    comparing our KPIs to industry benchmarks for the defined YEAR.
    """
    raw_summary = summary_df.to_string(index=False)
    prompt = f"""
We have the following summary of our email marketing KPIs:
{raw_summary}

As a marketing analytics expert, provide 3 high-level bullet points summarizing our overall performance trends,
comparing our numbers to industry benchmarks for {os.getenv('YEAR', '2025')}, and highlighting our positive results.
Avoid trivial observations.
Respond in plain text.
    """.strip()
    if client:
        try:
            initial_response = client.responses.create(
                model=os.getenv("ENGINE_MODEL", "gpt-4o"),
                input=prompt
            )
            initial_conclusion = initial_response.output_text.strip()
        except Exception as e:
            initial_conclusion = f"Error in initial AI call: {e}"
        
        corroboration_prompt = f"""
You are a marketing analytics expert. The initial overall conclusion is:
{initial_conclusion}

Now, using web search, corroborate these conclusions by referencing industry standards for {os.getenv('YEAR', '2025')},
and clearly state if our performance is above those standards (include at least one citation with a URL).
Append your findings without removing any original content.
Respond in plain text.
    """.strip()
        try:
            corroboration_response = client.responses.create(
                model=os.getenv("ENGINE_MODEL", "gpt-4o"),
                tools=[{"type": "web_search_preview"}],
                input=corroboration_prompt
            )
            corroboration_text = corroboration_response.output_text.strip()
        except Exception as e:
            corroboration_text = f"Error in corroboration AI call: {e}"
        final_conclusion = initial_conclusion + "\n\n" + corroboration_text
    else:
        final_conclusion = "AI client not available. No overall conclusion generated."

    text_content = f"Overall Conclusions:\n{final_conclusion}"
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    ax.axis('off')
    ax.text(0.01, 0.95, text_content, ha='left', va='top', wrap=True, fontsize=11)
    add_slide_number(fig)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

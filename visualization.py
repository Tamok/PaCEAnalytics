# visualization.py
import matplotlib.pyplot as plt
import seaborn as sns
import dataframe_image as dfi
from utils import UCSB_BLUE, PACE_LINKS, add_slide_number, place_logo_on_figure, process_markdown
from openai_integration import generate_full_explanation
import os

# Use uniform letter-size landscape (11 x 8.5 inches)
FIGSIZE = (11, 8.5)

def create_summary_table_slide(summary_df, pdf):
    """
    Generates a slide with a styled table of key email marketing metrics.
    """
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.axis('tight')
    ax.axis('off')
    ax.set_title("Key Email Marketing Metrics", fontsize=24, color=UCSB_BLUE, pad=20)
    
    table = ax.table(cellText=summary_df.values,
                     colLabels=summary_df.columns,
                     loc='center',
                     cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    # Style header cells with UCSB Blue font on a PaCE Links background
    for key, cell in table.get_celld().items():
        if key[0] == 0:
            cell.set_text_props(color="white", weight="bold")
            cell.set_facecolor(PACE_LINKS)
    table.scale(1, 2)
    
    place_logo_on_figure(fig)
    add_slide_number(fig)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_correlation_heatmap(df_rates, pdf, client):
    """
    Creates a correlation heatmap slide and an insights text slide.
    """
    rate_cols = ["Delivery Rate", "Open Rate", "Click Rate", "Bounce Rate", "Unsubscribe Rate"]
    corr = df_rates[rate_cols].corr()

    # Heatmap slide
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Correlation Heatmap for Key Email Marketing Rates", fontsize=18, color=UCSB_BLUE)
    add_slide_number(fig)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    # Insights text slide
    raw_data_text = corr.to_string()
    ai_explanation = generate_full_explanation(client, f"Correlation Data:\n{raw_data_text}", "Correlation Heatmap")
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    ax.axis('off')
    # Consistent title and positioning for text slides:
    ax.text(0.05, 0.90, "Insights for Correlation Heatmap", fontsize=20, color=UCSB_BLUE)
    add_slide_number(fig)
    ax.text(0.05, 0.80, ai_explanation, ha='left', va='top', wrap=True, fontsize=12, color=UCSB_BLUE)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_distribution_histogram(df_rates, metric, pdf, client):
    """
    Creates a histogram slide for a given metric and an insights text slide.
    """
    # Histogram slide
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    sns.histplot(df_rates[metric].dropna(), kde=True, color=PACE_LINKS, ax=ax)
    ax.set_title(f"Distribution of {metric}", fontsize=18, color=UCSB_BLUE)
    ax.set_xlabel(metric, fontsize=14, color=UCSB_BLUE)
    ax.set_ylabel("Frequency (Count per bin)", fontsize=14, color=UCSB_BLUE)
    add_slide_number(fig)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    # Insights text slide
    summary_text = df_rates[metric].describe().to_string()
    ai_explanation = generate_full_explanation(client, f"Distribution Summary for {metric}:\n{summary_text}", f"Histogram for {metric}")
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    ax.axis('off')
    ax.text(0.05, 0.90, f"Insights for Distribution of {metric}", fontsize=20, color=UCSB_BLUE)
    add_slide_number(fig)
    ax.text(0.05, 0.80, ai_explanation, ha='left', va='top', wrap=True, fontsize=12, color=UCSB_BLUE)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_definitions_additional_slide(pdf, note):
    """
    Combines Key Definitions and Additional Information into a single slide.
    """
    definitions = (
        "Key Definitions:\n\n"
        "• Frequency: Number of campaigns in a specific performance range.\n"
        "• Delivery Rate: (Delivered / Sent) * 100\n"
        "• Open Rate: (Opened / Delivered) * 100\n"
        "• Click Rate: (Clicked / Delivered) * 100\n"
        "• Bounce Rate: (Bounced / Sent) * 100\n"
        "• Unsubscribe Rate: (Unsubscribes / Sent) * 100\n\n"
        "Additional Information:\n" + note
    )
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    ax.axis('off')
    ax.text(0.05, 0.90, "Key Definitions & Additional Information", fontsize=24, color=UCSB_BLUE)
    add_slide_number(fig)
    ax.text(0.05, 0.75, definitions, ha='left', va='top', wrap=True, fontsize=14, color=UCSB_BLUE)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_overall_conclusion(summary_df, pdf, client):
    """
    Generates the overall conclusions slide using AI-generated insights.
    Processes markdown so that any formatting is interpreted as plain text.
    """
    raw_summary = summary_df.to_string(index=False)
    prompt = f"""
We have the following summary of our email marketing KPIs:
{raw_summary}

As a marketing analytics expert, provide an overall conclusion with:
- An overview paragraph.
- Three bullet points for AI Insights.
- Two bullet points for Recommendations.
- Industry Standards with embedded source links.
Respond in plain text with the order: Overview, AI Insights, Recommendations, Industry Standards.
    """.strip()
    if client:
        try:
            initial_response = client.responses.create(
                model=os.getenv("ENGINE_MODEL", "gpt-4o"),
                input=prompt
            )
            overall_text = initial_response.output_text.strip()
        except Exception as e:
            overall_text = f"Error in AI call: {e}"
    else:
        overall_text = "AI client not available. No overall conclusion generated."
    
    # Process markdown to interpret headings and links
    overall_text = process_markdown(overall_text)
    
    fig, ax = plt.subplots(figsize=FIGSIZE)
    place_logo_on_figure(fig)
    ax.axis('off')
    ax.text(0.05, 0.90, "Overall Performance Conclusions", fontsize=24, color=UCSB_BLUE)
    add_slide_number(fig)
    ax.text(0.05, 0.75, overall_text, ha='left', va='top', wrap=True, fontsize=12, color=UCSB_BLUE)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

# main.py
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from dotenv import load_dotenv

# Import modules from our project
import utils
import analysis
import visualization
import openai

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Import the OpenAI module (if installed)
try:
    import openai
except ImportError:
    openai = None

def main():
    parser = argparse.ArgumentParser(
        description="Generate a modular Zoho Campaign Performance PDF report focused on email marketing KPIs with AI comments."
    )
    parser.add_argument('--file', type=str, default="CampaignReports2025.csv",
                        help="Path to the CSV file (default: CampaignReports2025.csv)")
    parser.add_argument('--output', type=str, default="zoho_campaign_performance.pdf",
                        help="Output PDF file name (default: zoho_campaign_performance.pdf)")
    args = parser.parse_args()

    utils.verbose_print("Initializing OpenAI client...")
    client = utils.init_openai_client(openai, OPENAI_API_KEY)

    utils.verbose_print(f"Reading CSV file: {args.file}")
    try:
        df = pd.read_csv(args.file)
        utils.verbose_print("CSV file loaded successfully.")
    except Exception as e:
        utils.verbose_print(f"Error reading file {args.file}: {e}")
        return

    # Drop negligible columns if present
    cols_to_drop = ["Forwards", "Marked as spam"]
    dropped = []
    for col in cols_to_drop:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            dropped.append(col)
    if dropped:
        note = f"Note: The following metrics were dropped due to negligible impact: {', '.join(dropped)}."
    else:
        note = "Note: No negligible metrics were dropped."
    utils.verbose_print(note)

    with PdfPages(args.output) as pdf:
        # Title Slide
        utils.verbose_print("Generating title slide...")
        fig, ax = plt.subplots(figsize=(11, 8.5))
        utils.place_logo_on_figure(fig)
        ax.axis('off')
        ax.text(0.5, 0.6, "Zoho Campaign Performance", fontsize=30, ha='center', va='center', color=utils.UCSB_BLUE)
        ax.text(0.5, 0.45, "A Data-Driven Look at Email Marketing Results", fontsize=16, ha='center', va='center', color=utils.PACE_LINKS)
        utils.add_slide_number(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # Definitions Slide
        utils.verbose_print("Generating definitions slide...")
        visualization.create_definitions_slide(pdf)

        # Dropped Metrics Note Slide
        utils.verbose_print("Adding dropped metrics note slide...")
        fig, ax = plt.subplots(figsize=(11, 8.5))
        utils.place_logo_on_figure(fig)
        ax.axis('off')
        ax.text(0.05, 0.9, note, ha='left', va='top', fontsize=14, color=utils.UCSB_BLUE)
        utils.add_slide_number(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # Summary Table Slide (Overall KPIs)
        utils.verbose_print("Generating summary table slide...")
        summary_df = analysis.create_summary_table(df)
        visualization.create_summary_table_slide(summary_df, pdf)

        # Compute rate columns for further analysis
        df_rates = analysis.compute_rate_columns(df)

        # Correlation Heatmap Slide
        utils.verbose_print("Generating correlation heatmap slide...")
        visualization.create_correlation_heatmap(df_rates, pdf, client)

        # Distribution Histograms for key rate metrics
        for metric in ["Delivery Rate", "Open Rate", "Click Rate", "Bounce Rate", "Unsubscribe Rate"]:
            utils.verbose_print(f"Generating distribution histogram for {metric}...")
            visualization.create_distribution_histogram(df_rates, metric, pdf, client)

        # Final Overall Conclusion Slide
        utils.verbose_print("Generating final overall conclusion slide...")
        visualization.create_overall_conclusion(summary_df, pdf, client)

    utils.verbose_print(f"PDF report successfully created: {args.output}")

if __name__ == "__main__":
    main()

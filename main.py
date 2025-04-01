# main.py
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from dotenv import load_dotenv

# Import project modules
import utils
import analysis
import visualization
import openai

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

try:
    import openai
except ImportError:
    openai = None

def main():
    parser = argparse.ArgumentParser(
        description="Generate a modular Zoho Campaign Performance PDF report with AI comments."
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
    note = (f"Note: Dropped metrics: {', '.join(dropped)}." 
            if dropped else "Note: No negligible metrics were dropped.")
    utils.verbose_print(note)

    with PdfPages(args.output) as pdf:
        # Title Slide
        utils.verbose_print("Generating title slide...")
        fig, ax = plt.subplots(figsize=(11, 8.5))
        utils.place_logo_on_figure(fig)
        ax.axis('off')
        ax.set_title("Zoho Campaign Performance", fontsize=30, color=utils.UCSB_BLUE, pad=20)
        ax.text(0.5, 0.55, "A Data-Driven Look at Email Marketing Results", fontsize=18, ha='center', color=utils.PACE_LINKS)
        utils.add_slide_number(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # Definitions Slide
        utils.verbose_print("Generating definitions slide...")
        visualization.create_definitions_additional_slide(pdf, note)

        # Dropped Metrics Note Slide
        utils.verbose_print("Adding dropped metrics note slide...")
        fig, ax = plt.subplots(figsize=(11, 8.5))
        utils.place_logo_on_figure(fig)
        ax.axis('off')
        ax.set_title("Additional Information", fontsize=22, color=utils.UCSB_BLUE, pad=20)
        ax.text(0.05, 0.85, note, ha='left', va='top', fontsize=16, color=utils.UCSB_BLUE)
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

        # Distribution Histograms for key metrics
        for metric in ["Delivery Rate", "Open Rate", "Click Rate", "Bounce Rate", "Unsubscribe Rate"]:
            utils.verbose_print(f"Generating distribution histogram for {metric}...")
            visualization.create_distribution_histogram(df_rates, metric, pdf, client)

        # Final Overall Conclusion Slide
        utils.verbose_print("Generating final overall conclusion slide...")
        visualization.create_overall_conclusion(summary_df, pdf, client)

    utils.verbose_print(f"PDF report successfully created: {args.output}")

if __name__ == "__main__":
    main()

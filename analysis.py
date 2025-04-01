# analysis.py
import numpy as np
import pandas as pd
import markdown

def create_summary_table(df):
    """
    Computes a summary table with key email marketing KPIs and descriptions:
      - Sent: Total emails sent.
      - Delivered: Emails delivered to inbox.
      - Delivery Rate: Percentage of sent emails delivered.
      - Opened: Emails opened by recipients.
      - Open Rate: Percentage of delivered emails opened.
      - Clicked: Emails that resulted in clicks.
      - Click Rate: Percentage of delivered emails clicked.
      - Bounced: Emails that bounced.
      - Bounce Rate: Percentage of sent emails bounced.
      - Unsubscribes: Emails unsubscribed.
      - Unsubscribe Rate: Percentage of sent emails unsubscribed.
    Returns the summary table as a DataFrame with columns: Metric, Value, Description.
    """
    total_sent = df["Sent"].sum() if "Sent" in df.columns else 0
    total_delivered = df["Delivered"].sum() if "Delivered" in df.columns else 0
    total_opened = df["Opened"].sum() if "Opened" in df.columns else 0
    total_clicked = df["Clicked"].sum() if "Clicked" in df.columns else 0
    total_bounced = df["Bounced"].sum() if "Bounced" in df.columns else 0
    total_unsubscribes = df["Unsubscribes"].sum() if "Unsubscribes" in df.columns else 0

    delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
    open_rate = (total_opened / total_delivered * 100) if total_delivered > 0 else 0
    click_rate = (total_clicked / total_delivered * 100) if total_delivered > 0 else 0
    bounce_rate = (total_bounced / total_sent * 100) if total_sent > 0 else 0
    unsubscribe_rate = (total_unsubscribes / total_sent * 100) if total_sent > 0 else 0

    data = {
        "Metric": ["Sent", "Delivered", "Delivery Rate", "Opened", "Open Rate", 
                   "Clicked", "Click Rate", "Bounced", "Bounce Rate", "Unsubscribes", "Unsubscribe Rate"],
        "Value": [total_sent,
                  total_delivered,
                  f"{delivery_rate:.2f}%",
                  total_opened,
                  f"{open_rate:.2f}%",
                  total_clicked,
                  f"{click_rate:.2f}%",
                  total_bounced,
                  f"{bounce_rate:.2f}%",
                  total_unsubscribes,
                  f"{unsubscribe_rate:.2f}%"],
        "Description": [
            "Total emails sent",
            "Emails delivered to inbox",
            "Percentage of sent emails delivered",
            "Total emails opened",
            "Percentage of delivered emails opened",
            "Emails with clicks",
            "Percentage of delivered emails clicked",
            "Emails that bounced",
            "Percentage of sent emails bounced",
            "Total unsubscribes",
            "Percentage of sent emails unsubscribed"
        ]
    }
    summary_df = pd.DataFrame(data)
    return summary_df

def compute_rate_columns(df):
    """
    Computes per-campaign rate columns.
    """
    df = df.copy()
    df["Delivery Rate"] = np.where(df["Sent"] > 0, df["Delivered"] / df["Sent"] * 100, 0)
    df["Open Rate"] = np.where(df["Delivered"] > 0, df["Opened"] / df["Delivered"] * 100, 0)
    df["Click Rate"] = np.where(df["Delivered"] > 0, df["Clicked"] / df["Delivered"] * 100, 0)
    df["Bounce Rate"] = np.where(df["Sent"] > 0, df["Bounced"] / df["Sent"] * 100, 0)
    df["Unsubscribe Rate"] = np.where(df["Sent"] > 0, df["Unsubscribes"] / df["Sent"] * 100, 0)
    return df

def process_markdown(text):
    """
    Converts markdown text to HTML.
    """
    try:
        html = markdown.markdown(text)
        return html
    except Exception as e:
        return text

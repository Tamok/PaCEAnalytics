# utils.py
import os
import matplotlib.pyplot as plt

# Branding and global configuration
UCSB_BLUE = "#003660"
UCSB_GOLD = "#febc11"
PACE_LINKS = "#1178b5"

# Global slide counter
SLIDE_NUMBER = 1

def verbose_print(message):
    print("[INFO] " + message)

def process_markdown(text):
    """
    In this version, we output plain text directly.
    (Further markdown-to-plain conversion could be added if needed.)
    """
    return text

def add_slide_number(fig):
    """
    Adds the current slide number to the figure (bottom-right) and increments the global counter.
    """
    global SLIDE_NUMBER
    fig.text(0.95, 0.02, f"Slide {SLIDE_NUMBER}", ha="right", va="bottom", fontsize=10, color=UCSB_BLUE)
    SLIDE_NUMBER += 1

def init_openai_client(openai_module, api_key):
    """
    Initializes and returns the OpenAI client if available; otherwise returns None.
    """
    if openai_module is None or not api_key:
        verbose_print("OpenAI client not configured. Comments will be skipped.")
        return None
    client = openai_module.OpenAI(api_key=api_key)
    return client

def place_logo_on_figure(fig, logo_path="logo.png"):
    """
    Places a small logo in the top-right corner of the figure.
    Coordinates are fixed to ensure visibility.
    """
    try:
        logo_img = plt.imread(logo_path)
        new_ax = fig.add_axes([0.85, 0.85, 0.1, 0.1], anchor='NE', zorder=1)
        new_ax.imshow(logo_img)
        new_ax.axis('off')
    except FileNotFoundError:
        verbose_print(f"Logo file not found: {logo_path}")

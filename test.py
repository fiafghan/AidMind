# Works with refugee camps, neighborhoods, health zones, etc.

import html
from aidmind import analyze_needs
analyze_needs(
    country_name="Afghanistan",
    admin_level="ADM1",
    dataset_path="sample_data/provinces.csv",
    admin_col="province",   
    fixed_thresholds=(0.25, 0.50, 0.75),  # Optional: fixed thresholds
    output_html_path="output/provinces2025.html",
)
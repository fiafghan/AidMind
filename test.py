# Works with refugee camps, neighborhoods, health zones, etc.

import html
from aidmind import analyze_needs
analyze_needs(
    "afghanistan_needs_sample.csv",
    local_geojson="refugees.geojson",
    admin_col="camp_name",
    fixed_thresholds=(0.25, 0.50, 0.75),  # Optional: fixed thresholds
    output_html_path="output/needs_map_custom.html"
)
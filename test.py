from aidmind import analyze_needs

out_html = analyze_needs(
    dataset_path="afghanistan_needs_sample.csv",
    country_name="Afghanistan",
    admin_level="ADM1",         # province-level boundaries
    admin_col=None,             # auto-detects 'province'
    local_geojson=None,         # or path to a local GeoJSON
    output_html_path="output/afghanistan_needs_sample.html",
)
print("Map saved to:", out_html)
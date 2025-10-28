from aidmind import analyze_needs

output = analyze_needs(
    "afghanistan_needs.csv",
    "Afghanistan",
    admin_col="province"
)
print(f"Map: {output}")
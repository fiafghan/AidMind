from aidmind import analyze_needs

out = analyze_needs("afghanistan_needs.csv", "Afghanistan", admin_col="province", local_geojson="afghanistan_admin1.geojson")
print("Map saved to:", out)








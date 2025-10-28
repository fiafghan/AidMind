from aidmind import analyze_needs

# Test 1: Province-level analysis
print("=" * 60)
print("Test 1: Province-level analysis")
print("=" * 60)
output = analyze_needs(
    "afghanistan_needs.csv",
    "Afghanistan",
    admin_level="ADM1",
    admin_col="province"
)
print(f"✅ Province map: {output}\n")

# Test 2: District-level analysis (if you have district data and boundaries)
# Uncomment when you have district-level data
# print("=" * 60)
# print("Test 2: District-level analysis")
# print("=" * 60)
# output = analyze_needs(
#     "afghanistan_districts.csv",
#     "Afghanistan",
#     admin_level="ADM2",
#     admin_col="district"
# )
# print(f"✅ District map: {output}\n")

# Test 3: Village-level with custom boundaries (example)
# Uncomment when you have village data and boundaries
# print("=" * 60)
# print("Test 3: Village-level with custom GeoJSON")
# print("=" * 60)
# output = analyze_needs(
#     "villages.csv",
#     local_geojson="village_boundaries.geojson",
#     admin_col="village_name"
# )
# print(f"✅ Village map: {output}\n")

print("=" * 60)
print("All tests completed!")
print("=" * 60)
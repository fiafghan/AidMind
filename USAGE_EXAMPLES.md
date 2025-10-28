# AidMind Usage Examples

Complete guide for using AidMind with provinces, districts, villages, and custom geographic units.

---

## Table of Contents

1. [Province-Level Analysis (ADM1)](#1-province-level-analysis-adm1)
2. [District-Level Analysis (ADM2)](#2-district-level-analysis-adm2)
3. [Village-Level Analysis (Custom)](#3-village-level-analysis-custom)
4. [Custom Geographic Units](#4-custom-geographic-units)
5. [Working with Any CSV Structure](#5-working-with-any-csv-structure)

---

## 1. Province-Level Analysis (ADM1)

### With GeoBoundaries (Online)

```python
from aidmind import analyze_needs

# Basic province-level analysis
output = analyze_needs(
    "provinces.csv",
    "Afghanistan",
    admin_level="ADM1"
)
```

### Dataset Example (`provinces.csv`)
```csv
province,health_index,education_index,food_security,water_access
Kabul,0.75,0.80,0.70,0.85
Kandahar,0.45,0.40,0.50,0.35
Herat,0.60,0.65,0.55,0.60
Balkh,0.55,0.52,0.54,0.49
```

---

## 2. District-Level Analysis (ADM2)

### With GeoBoundaries

```python
from aidmind import analyze_needs

# District-level analysis
output = analyze_needs(
    "districts.csv",
    "Afghanistan",
    admin_level="ADM2",
    admin_col="district"
)
```

### Dataset Example (`districts.csv`)
```csv
district,health_score,education_score,food_insecurity,water_scarcity,population
Kabul City,0.78,0.85,0.22,0.15,5000000
Bagrami,0.45,0.38,0.55,0.62,120000
Char Asiab,0.32,0.28,0.68,0.75,85000
Paghman,0.50,0.45,0.50,0.55,150000
```

### CLI Usage
```bash
python -m aidmind districts.csv "Afghanistan" \
  --admin-level ADM2 \
  --admin-col district \
  --output districts_needs.html
```

---

## 3. Village-Level Analysis (Custom)

### With Custom GeoJSON Boundaries

Villages are not available in GeoBoundaries, so you need a custom GeoJSON file with village boundaries.

```python
from aidmind import analyze_needs

# Village-level analysis with custom boundaries
output = analyze_needs(
    "villages.csv",
    local_geojson="village_boundaries.geojson",
    admin_col="village_name"
)
```

### Dataset Example (`villages.csv`)
```csv
village_name,health_access,school_access,food_availability,water_quality,households
Qala-e-Fatullah,0.30,0.25,0.35,0.40,250
Deh-e-Bagh,0.45,0.40,0.50,0.55,180
Karez-e-Mir,0.25,0.20,0.30,0.35,120
Qarabagh Village,0.60,0.65,0.70,0.75,400
```

### GeoJSON Requirements

Your `village_boundaries.geojson` must have features with properties that include village names:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Qala-e-Fatullah",
        "district": "Kabul",
        "province": "Kabul"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[...]]
      }
    },
    ...
  ]
}
```

### CLI Usage
```bash
python -m aidmind villages.csv \
  --geojson village_boundaries.geojson \
  --admin-col village_name \
  --output villages_needs.html
```

---

## 4. Custom Geographic Units

AidMind works with **any** geographic unit you define, not just administrative boundaries.

### Examples

#### Refugee Camps
```python
output = analyze_needs(
    "refugee_camps.csv",
    local_geojson="camp_boundaries.geojson",
    admin_col="camp_name"
)
```

**Dataset** (`refugee_camps.csv`):
```csv
camp_name,shelter_quality,water_access,sanitation,food_distribution,health_services
Camp Dadaab 1,0.40,0.35,0.30,0.45,0.50
Camp Kakuma,0.55,0.50,0.45,0.60,0.65
Camp Nyarugusu,0.30,0.25,0.20,0.35,0.40
```

#### Urban Neighborhoods
```python
output = analyze_needs(
    "neighborhoods.csv",
    local_geojson="neighborhood_boundaries.geojson",
    admin_col="neighborhood"
)
```

**Dataset** (`neighborhoods.csv`):
```csv
neighborhood,poverty_rate,unemployment,housing_quality,public_services
Shar-e-Naw,0.20,0.15,0.85,0.90
Khair Khana,0.65,0.70,0.35,0.30
Dasht-e-Barchi,0.75,0.80,0.25,0.20
```

#### Health Facilities Coverage Zones
```python
output = analyze_needs(
    "health_zones.csv",
    local_geojson="health_zone_boundaries.geojson",
    admin_col="zone_id"
)
```

---

## 5. Working with Any CSV Structure

AidMind automatically:
- ✅ Detects your geographic unit column
- ✅ Uses all numeric columns as indicators
- ✅ Handles any column names
- ✅ Aggregates duplicate rows

### Example: Completely Custom Column Names

```csv
geo_unit,metric_a,metric_b,metric_c,metric_d,metric_e
Unit_001,0.23,0.45,0.67,0.89,0.12
Unit_002,0.56,0.78,0.34,0.23,0.45
Unit_003,0.89,0.12,0.56,0.78,0.34
```

```python
output = analyze_needs(
    "custom_data.csv",
    local_geojson="custom_boundaries.geojson",
    admin_col="geo_unit"
)
```

---

## 6. Advanced Options

### Fixed Thresholds for Cross-Region Comparison

```python
# Use same thresholds across all analyses
output = analyze_needs(
    "region_a.csv",
    local_geojson="region_a.geojson",
    fixed_thresholds=(0.25, 0.50, 0.75)
)

output = analyze_needs(
    "region_b.csv",
    local_geojson="region_b.geojson",
    fixed_thresholds=(0.25, 0.50, 0.75)  # Same thresholds for comparison
)
```

### Offline Analysis (No Internet)

```python
# Pre-download boundaries once (with internet)
from aidmind import _fetch_admin1_geojson, _country_to_iso3
iso3 = _country_to_iso3("Afghanistan")
geojson = _fetch_admin1_geojson(iso3, admin_level="ADM2")
# Boundaries now cached in cache/geoboundaries/

# Later, works offline (uses cached boundaries)
output = analyze_needs("data.csv", "Afghanistan", admin_level="ADM2")
```

### Batch Processing

```python
import glob
from aidmind import analyze_needs

# Process multiple datasets
for csv_file in glob.glob("data/*.csv"):
    country = csv_file.split("/")[-1].split("_")[0]  # Extract country from filename
    output = analyze_needs(
        csv_file,
        country,
        admin_level="ADM1"
    )
    print(f"Processed: {output}")
```

---

## 7. Interpreting Results

### HTML Map
- **Interactive choropleth** with 4 color levels
- **Hover tooltips** show: Geographic Unit, Need Score, Rank, Level
- **Legend** explains color coding

### CSV Export

Example output (`needs_scores_custom.csv`):

```csv
district,need_score,need_rank,cluster,need_level
Nuristan,0.92,0,0,high
Badakhshan,0.87,1,0,high
Kandahar,0.78,2,1,medium
Herat,0.45,15,2,low
Kabul,0.12,20,3,lowest
```

**Columns:**
- `district` (or your geo unit): Geographic unit name
- `need_score`: Composite need score (0-1, higher = more need)
- `need_rank`: Rank (0 = highest need)
- `cluster`: Cluster ID from KMeans
- `need_level`: Discrete level (high/medium/low/lowest)

---

## 8. Troubleshooting

### Low Match Rate

```
WARNING: Low admin name match rate: 45%
```

**Solution**: Ensure names in your CSV match names in your GeoJSON properties. Check for:
- Spelling differences
- Extra spaces or characters
- Case sensitivity

### No Boundaries Available

**Problem**: GeoBoundaries doesn't have village or custom unit boundaries.

**Solution**: Create or obtain a GeoJSON file with your boundaries and use `local_geojson` parameter.

### Custom GeoJSON Not Matching

**Problem**: Your CSV names don't match GeoJSON property names.

**Solution**: Check your GeoJSON properties. The tool looks for common name fields:
- `name`
- `shapeName`
- `NAME_1`
- `adm1_name`

Ensure your GeoJSON uses one of these, or the same names as your CSV.

---

## 9. Real-World Example: Multi-Level Analysis

### Scenario: Complete Afghanistan Assessment

```python
from aidmind import analyze_needs

# 1. National overview (provinces)
province_output = analyze_needs(
    "afghanistan_provinces.csv",
    "Afghanistan",
    admin_level="ADM1",
    output_html_path="maps/afghanistan_provinces.html"
)

# 2. Drill-down to districts in high-need province
district_output = analyze_needs(
    "kandahar_districts.csv",
    "Afghanistan",
    admin_level="ADM2",
    output_html_path="maps/kandahar_districts.html"
)

# 3. Village-level in highest-need district
village_output = analyze_needs(
    "spin_boldak_villages.csv",
    local_geojson="spin_boldak_villages.geojson",
    admin_col="village",
    output_html_path="maps/spin_boldak_villages.html"
)

print(f"Province map: {province_output}")
print(f"District map: {district_output}")
print(f"Village map: {village_output}")
```

---

## 10. Summary

AidMind is fully generalized and works with:

✅ **Any administrative level**: ADM1, ADM2, ADM3, or custom  
✅ **Any geographic unit**: Provinces, districts, villages, camps, neighborhoods, zones  
✅ **Any CSV structure**: Auto-detects columns, uses all numeric indicators  
✅ **Online or offline**: GeoBoundaries or custom GeoJSON  
✅ **Flexible naming**: Any column names for units and indicators  

**Key principle**: If you have a CSV with geographic units + indicators, and a GeoJSON with boundaries, AidMind will analyze it.

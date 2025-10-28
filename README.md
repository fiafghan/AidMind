# AidMind

**Unsupervised machine learning for humanitarian needs assessment at ANY geographic level**

AidMind is a production-ready Python tool that enables humanitarian data analysts to quickly identify areas with the highest need for aid using unsupervised machine learning. Works with **provinces, districts, villages, refugee camps, neighborhoods, or any custom geographic units**. It automatically clusters geographic units, ranks them by need level, and generates interactive choropleth maps with discrete color-coded need levels.

**Fully generalized**: Works with any CSV structure and any GeoJSON boundaries.

---

## Features

- **Works at ANY geographic level**: Provinces, districts, villages, refugee camps, neighborhoods, or any custom zones
- **Completely generalized**: Works with ANY CSV structure and ANY column names
- **Easy to use**: Single function call with dataset path
- **Flexible inputs**: Works with any numeric indicators (any column names accepted)
- **Custom boundaries**: Use your own GeoJSON for villages or custom units
- **Automatic preprocessing**: Handles missing values, duplicates, and name variations
- **Intelligent clustering**: Uses KMeans to identify need patterns across indicators
- **Geographic visualization**: Generates interactive HTML maps with 4 discrete need levels (high, medium, low, lowest)
- **Online or offline**: Use GeoBoundaries or custom GeoJSON files
- **International ready**: Works with any country, any admin level (ADM1, ADM2, ADM3, custom)
- **CSV export**: Outputs structured data with need scores, ranks, and levels
- **Professional logging**: Transparent processing with diagnostic information

---

## Installation

### Option 1: Pip install (recommended)

```bash
pip install aidmind
```

### Option 2: From source

```bash
git clone https://github.com/yourorg/aidmind.git
cd aidmind
pip install -r requirements.txt
pip install -e .
```

### Requirements

- Python 3.8+
- pandas >= 2.0
- numpy >= 1.24
- scikit-learn >= 1.3
- folium >= 0.15
- requests >= 2.31
- pycountry >= 22.3.5
- branca >= 0.7
- shapely >= 2.0

---

## Quick Start

### Province-level (with GeoBoundaries)

```python
from aidmind import analyze_needs

# Analyze provinces
output = analyze_needs("provinces.csv", "Afghanistan", admin_level="ADM1")
print(f"Map saved to: {output}")
```

### District-level (with GeoBoundaries)

```python
# Analyze districts
output = analyze_needs(
    "districts.csv",
    "Afghanistan",
    admin_level="ADM2",
    admin_col="district"
)
```

### Village-level (with custom boundaries)

```python
# Analyze villages using your own GeoJSON
output = analyze_needs(
    "villages.csv",
    local_geojson="village_boundaries.geojson",
    admin_col="village_name"
)
```

### Any custom geographic unit

```python
# Works with refugee camps, neighborhoods, health zones, etc.
output = analyze_needs(
    "refugee_camps.csv",
    local_geojson="camp_boundaries.geojson",
    admin_col="camp_name",
    fixed_thresholds=(0.25, 0.50, 0.75)  # Optional: fixed thresholds
)
```

### Command line

```bash
# Province-level
python -m aidmind provinces.csv "Afghanistan" --admin-level ADM1

# District-level
python -m aidmind districts.csv "Kenya" --admin-level ADM2 --admin-col district

# Village-level with custom boundaries
python -m aidmind villages.csv --geojson villages.geojson --admin-col village_name
```

**See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for complete documentation with 10+ examples.**

---

## Data Requirements

### Required

- **One geographic unit column**: Any column with location names (province, district, village, camp, zone, etc.)
- **At least one numeric indicator**: Any metric columns with numeric values

### Supported formats

- **CSV files** with UTF-8 encoding
- **ANY column names**: Tool auto-detects geographic column and uses all numeric columns
- **GeoJSON boundaries**: Either from GeoBoundaries or your own custom file

### Example: Province-level

```csv
province,health_index,education_index,income_index,food_security,water_access
Kabul,0.75,0.80,0.70,0.85,0.78
Kandahar,0.45,0.40,0.50,0.35,0.44
Herat,0.60,0.65,0.55,0.60,0.63
```

### Example: Village-level

```csv
village_name,health_access,school_access,water_quality,food_availability
Qala-e-Fatullah,0.30,0.25,0.40,0.35
Deh-e-Bagh,0.45,0.40,0.55,0.50
Karez-e-Mir,0.25,0.20,0.35,0.30
```

### Example: Refugee camps

```csv
camp_name,shelter,water,sanitation,food,health
Camp Dadaab 1,0.40,0.35,0.30,0.45,0.50
Camp Kakuma,0.55,0.50,0.45,0.60,0.65
Camp Nyarugusu,0.30,0.25,0.20,0.35,0.40
```

### Handling duplicates

If you have multiple records per unit (e.g., `Kabul_1`, `Kabul_2`), the tool automatically:
- Strips trailing numeric suffixes
- Aggregates by averaging indicators

---

## How It Works

### 1. **Preprocessing**
   - Auto-detects admin column or uses specified `admin_col`
   - Aggregates duplicate admin records by averaging
   - Imputes missing numeric values with median
   - Standardizes all indicators (zero mean, unit variance)

### 2. **Need Assessment**
   - Computes composite need score (mean of standardized indicators)
   - Applies KMeans clustering (3-5 clusters depending on data size)
   - Ranks clusters by mean need score

### 3. **Name Harmonization**
   - Normalizes admin names (lowercase, remove special characters)
   - Applies fuzzy matching to align with GeoBoundaries names
   - Logs match rate and coverage improvements

### 4. **Visualization**
   - Fetches admin boundaries from GeoBoundaries (or uses local file)
   - Assigns discrete color levels based on quartiles or fixed thresholds:
     - **High** (red-700): Top 25% need scores
     - **Medium** (red-400): 50th-75th percentile
     - **Low** (green-300): 25th-50th percentile
     - **Lowest** (green-600): Bottom 25%
   - Generates interactive Folium map with tooltips

### 5. **Output**
   - HTML map: `output/needs_map_<ISO3>.html`
   - CSV scores: `output/needs_scores_<ISO3>.csv`

---

## Outputs

### Interactive HTML Map

- Choropleth with 4 discrete color levels
- Hover tooltips showing: Province, Need Score, Need Rank, Level
- Legend with color key
- Highlight on hover

### CSV Export

Example `needs_scores_AFG.csv`:

```csv
admin1,need_score,need_rank,cluster,need_level
Kabul,0.142,3,2,lowest
Kandahar,0.856,0,0,high
Herat,0.487,2,1,medium
```

---

## Advanced Usage

### Fixed thresholds for cross-country comparison

```python
# Use consistent cutoffs across all countries
output = analyze_needs(
    "country1.csv",
    "Afghanistan",
    fixed_thresholds=(0.25, 0.50, 0.75)
)
```

### Offline mode with local boundaries

```python
# No internet required after initial download
output = analyze_needs(
    "data.csv",
    "Kenya",
    local_geojson="boundaries/kenya_adm1.geojson"
)
```

### ADM2 (district-level) analysis

```python
output = analyze_needs(
    "district_data.csv",
    "Ethiopia",
    admin_level="ADM2",
    admin_col="district"
)
```

---

## Troubleshooting

### Low match rate warning

**Problem**: `WARNING: Low admin name match rate: 45%`

**Solution**:
- Ensure admin names in your dataset match official names in GeoBoundaries
- Check for typos, spelling variations, or extra characters
- Use official admin names from [GeoBoundaries](https://www.geoboundaries.org/)
- Or provide a local GeoJSON with matching name properties

### No numeric columns found

**Problem**: `ValueError: No numeric feature columns found`

**Solution**:
- Ensure at least one column contains numeric values
- Check for non-numeric characters in indicator columns
- Remove or fix text values in numeric columns

### Admin column not detected

**Problem**: `ValueError: Could not detect an admin name column`

**Solution**:
- Rename your admin column to: `province`, `admin1`, `region`, or `state`
- Or specify it explicitly: `admin_col="your_column_name"`

### Empty or very small dataset

**Problem**: `WARNING: Dataset has only 2 rows`

**Solution**:
- AidMind requires at least 3 rows for clustering
- For reliable results, use datasets with 10+ admin units

---

## API Reference

### `analyze_needs()`

```python
def analyze_needs(
    dataset_path: str,
    country_name: Optional[str] = None,
    output_html_path: Optional[str] = None,
    *,
    admin_level: Optional[str] = None,
    admin_col: Optional[str] = None,
    local_geojson: Optional[str] = None,
    fixed_thresholds: Optional[Tuple[float, float, float]] = None,
) -> str
```

**Parameters**:
- `dataset_path` (str): Path to CSV file with geographic units and indicators
- `country_name` (str, optional): Country name (e.g., "Afghanistan", "Kenya"). Required only if using GeoBoundaries. Can be None if providing `local_geojson`
- `output_html_path` (str, optional): Custom output path for HTML
- `admin_level` (str, optional): Admin level ("ADM1", "ADM2", "ADM3", or any custom). Only used with GeoBoundaries
- `admin_col` (str, optional): Name of geographic unit column (auto-detected if None)
- `local_geojson` (str, optional): Path to local GeoJSON boundaries. Use this for villages or custom units
- `fixed_thresholds` (tuple, optional): (q25, q50, q75) for color levels

**Returns**:
- `str`: Path to generated HTML file

**Raises**:
- `FileNotFoundError`: If dataset or local_geojson not found
- `ValueError`: If invalid inputs, empty dataset, or both country_name and local_geojson missing

**Examples**:
```python
# Province-level with GeoBoundaries
analyze_needs("provinces.csv", "Afghanistan", admin_level="ADM1")

# District-level with GeoBoundaries
analyze_needs("districts.csv", "Kenya", admin_level="ADM2")

# Village-level with custom boundaries
analyze_needs("villages.csv", local_geojson="villages.geojson")

# Custom zones
analyze_needs("camps.csv", local_geojson="camps.geojson", admin_col="camp_name")
```

---

## Use Cases

### Humanitarian Organizations

- **Rapid needs assessment**: Identify priority areas for intervention
- **Resource allocation**: Visualize where aid is most needed
- **Monitoring & evaluation**: Track changes in need levels over time
- **Reporting**: Generate maps and data exports for donors

### Example Organizations

- UN agencies (UNHCR, UNICEF, WFP)
- International NGOs (MSF, Oxfam, Save the Children)
- National disaster management agencies
- Research institutions studying humanitarian crises

---

## Best Practices

### Data Quality

1. **Use official admin names** from GeoBoundaries or national sources
2. **Include multiple indicators** (3-5+) for robust assessment
3. **Check for outliers** and data quality issues before analysis
4. **Document data sources** and collection methodology

### Interpretation

1. **Need scores are relative** within the dataset (0-1 scale)
2. **Clustering is unsupervised**: No ground truth labels used
3. **Combine with qualitative data** for complete picture
4. **Validate results** with local experts and stakeholders

### Production Deployment

1. **Use fixed thresholds** for consistent cross-country comparison
2. **Cache boundaries locally** for offline or restricted environments
3. **Version control datasets** and track changes over time
4. **Automate workflows** with CI/CD pipelines

---

## Examples

See `examples/` directory for:
- `basic_usage.ipynb`: Step-by-step tutorial
- `multi_country.py`: Batch processing multiple countries
- `custom_config.py`: Advanced configuration options

---

## Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

See `CONTRIBUTING.md` for detailed guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Citation

If you use AidMind in your research or reports, please cite:

```
AidMind: Unsupervised Machine Learning for Humanitarian Needs Assessment
Version 1.0.0
https://github.com/yourorg/aidmind
```

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourorg/aidmind/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourorg/aidmind/discussions)
- **Email**: support@aidmind.org

---

## Acknowledgments

- **GeoBoundaries**: For providing open administrative boundary data
- **Humanitarian Data Exchange**: For inspiring accessible data tools
- **Open-source community**: For the amazing libraries this tool builds on

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

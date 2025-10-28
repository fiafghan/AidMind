# AidMind

**Unsupervised machine learning for humanitarian needs assessment and visualization**

AidMind is a production-ready Python tool that enables humanitarian data analysts to quickly identify provinces/regions with the highest need for aid using unsupervised machine learning. It automatically clusters geographic units, ranks them by need level, and generates interactive choropleth maps with discrete color-coded need levels.

---

## Features

- **Easy to use**: Single function call with dataset path and country name
- **Flexible inputs**: Works with any numeric indicators (health, education, income, food security, water access, etc.)
- **Automatic preprocessing**: Handles missing values, duplicates, and name variations
- **Intelligent clustering**: Uses KMeans to identify need patterns across indicators
- **Geographic visualization**: Generates interactive HTML maps with 4 discrete need levels (high, medium, low, lowest)
- **Offline capable**: Cache boundaries locally or provide custom GeoJSON files
- **International ready**: Works with any country supported by GeoBoundaries
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

### Basic usage

```python
from aidmind import analyze_needs

# Generate need assessment map
output_path = analyze_needs("my_data.csv", "Afghanistan")
print(f"Map saved to: {output_path}")
```

### With options

```python
output_path = analyze_needs(
    dataset_path="humanitarian_indicators.csv",
    country_name="Kenya",
    admin_col="county",                           # Specify admin column name
    admin_level="ADM1",                           # Or "ADM2" if available
    local_geojson="kenya_boundaries.geojson",     # Use local boundaries
    fixed_thresholds=(0.25, 0.50, 0.75),          # Fixed color thresholds
    output_html_path="output/kenya_needs.html"    # Custom output path
)
```

### Command line

```bash
python -m aidmind my_data.csv "Afghanistan" --output results/map.html
```

---

## Data Requirements

### Required

- **One admin column**: Province/state/county names (e.g., `province`, `admin1`, `region`, `state`)
- **At least one numeric indicator**: Any humanitarian metrics (e.g., `health_index`, `poverty_rate`, `food_security`)

### Supported formats

- CSV files with UTF-8 encoding
- Column names can be anything; the tool auto-detects admin names and uses all numeric columns

### Example dataset structure

```csv
province,health_index,education_index,income_index,food_security,water_access
Kabul,0.75,0.80,0.70,0.85,0.78
Kandahar,0.45,0.40,0.50,0.35,0.44
Herat,0.60,0.65,0.55,0.60,0.63
```

### Handling duplicates

If you have multiple records per admin unit (e.g., `Kabul_1`, `Kabul_2`), the tool automatically:
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
    country_name: str,
    output_html_path: Optional[str] = None,
    *,
    admin_level: str = "ADM1",
    admin_col: Optional[str] = None,
    local_geojson: Optional[str] = None,
    fixed_thresholds: Optional[Tuple[float, float, float]] = None,
) -> str
```

**Parameters**:
- `dataset_path` (str): Path to CSV file with indicators
- `country_name` (str): Country name (e.g., "Afghanistan", "Kenya")
- `output_html_path` (str, optional): Custom output path for HTML
- `admin_level` (str): "ADM1" (default) or "ADM2"
- `admin_col` (str, optional): Name of admin column (auto-detected if None)
- `local_geojson` (str, optional): Path to local GeoJSON boundaries
- `fixed_thresholds` (tuple, optional): (q25, q50, q75) for color levels

**Returns**:
- `str`: Path to generated HTML file

**Raises**:
- `FileNotFoundError`: If dataset or local_geojson not found
- `ValueError`: If invalid inputs, empty dataset, or no numeric columns

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

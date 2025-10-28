# Changelog

All notable changes to AidMind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-28

### Added
- Initial production release
- Core `analyze_needs()` function with unsupervised clustering
- Automatic admin column detection
- Median imputation for missing values
- Admin name aggregation (strips trailing numeric suffixes)
- Fuzzy name harmonization using difflib
- GeoBoundaries API integration with local caching
- Support for local GeoJSON boundaries (offline mode)
- Discrete 4-level color scheme (high, medium, low, lowest)
- Interactive Folium choropleth maps with tooltips
- CSV export with need scores, ranks, clusters, and levels
- Comprehensive input validation and error messages
- Structured logging with INFO-level diagnostics
- Match rate reporting for name alignment
- Support for both ADM1 and ADM2 administrative levels
- Optional fixed thresholds for cross-country comparison
- Command-line interface
- Full API documentation
- Professional README with examples and troubleshooting
- MIT License
- Setup.py for pip installation
- Requirements.txt with pinned versions
- Example datasets (Afghanistan 200+ records)
- Unit tests for core functionality
- Dockerfile for containerized deployment
- .gitignore for clean repository

### Technical Details
- Python 3.8+ support
- Dependencies: pandas, numpy, scikit-learn, folium, requests, pycountry, branca, shapely
- Clustering: KMeans (3-5 clusters based on sample size)
- Need score: Mean of standardized indicators (0-1 scale)
- Color mapping: Quartile-based or fixed thresholds
- Boundary source: GeoBoundaries gbOpen API
- Output formats: HTML (interactive map), CSV (structured data)

### Documentation
- Comprehensive README with quick start, API reference, troubleshooting
- Inline code documentation and type hints
- Example Jupyter notebook
- Use case descriptions for humanitarian organizations

### Quality Assurance
- Input validation for all parameters
- Graceful error handling with actionable messages
- Small sample size warnings
- Low match rate warnings
- Logging for transparency and debugging
- Unit tests with pytest
- Type hints throughout

## [Unreleased]

### Planned Features
- Support for custom indicator weights
- PCA-based composite indicators (optional)
- Multi-language support for outputs
- Interactive Streamlit/Dash dashboard
- Batch processing for multiple countries
- Time-series analysis and trend detection
- Integration with Humanitarian Data Exchange (HDX)
- Support for additional boundary sources
- Enhanced fuzzy matching with phonetic algorithms
- Automated data quality reports
- Export to additional formats (PDF, GeoJSON, Shapefile)
- API wrapper for web services
- More example notebooks and datasets

### Future Enhancements
- Performance optimization for large datasets (>10k rows)
- GPU acceleration for clustering (optional)
- Advanced visualization options (3D maps, animations)
- Integration with popular BI tools (Power BI, Tableau)
- Custom color schemes and branding
- Multi-modal indicators (categorical + numeric)
- Hierarchical clustering option
- Ensemble methods for robust scoring

---

## Version History

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| 1.0.0   | 2025-10-28   | Initial production release with full ML pipeline |

---

## Migration Guide

### From Pre-release to 1.0.0

If you used development versions:

1. **Update imports**: No changes needed
2. **API changes**: None (backwards compatible)
3. **New features**: All optional parameters are backward compatible
4. **Breaking changes**: None

### Recommended Workflow Update

```python
# Old (still works)
from aidmind import analyze_needs
analyze_needs("data.csv", "Country")

# New (recommended with validation)
from aidmind import analyze_needs
try:
    output = analyze_needs(
        "data.csv",
        "Country",
        admin_col="province",  # explicit is better
    )
    print(f"Success: {output}")
except ValueError as e:
    print(f"Data issue: {e}")
except FileNotFoundError as e:
    print(f"File issue: {e}")
```

---

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/yourorg/aidmind/issues
- GitHub Discussions: https://github.com/yourorg/aidmind/discussions
- Email: support@aidmind.org

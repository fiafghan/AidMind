# AidMind Deployment Guide

This guide will help you deploy AidMind for use by international humanitarian organizations.

## Quick Start (5 minutes)

### Option 1: Local Installation

```bash
cd /home/fardin-ibrahimi/Desktop/AidMind
pip install -e .
```

Test it:
```bash
python -m aidmind afghanistan_needs_200.csv "Afghanistan"
```

### Option 2: Docker Deployment

```bash
cd /home/fardin-ibrahimi/Desktop/AidMind
docker build -t aidmind:1.0.0 .

# Run
docker run -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output \
  aidmind:1.0.0 python -m aidmind /app/data/afghanistan_needs_200.csv "Afghanistan"
```

## Complete Package Structure

```
AidMind/
├── aidmind.py                    # Main module
├── setup.py                      # Package configuration
├── requirements.txt              # Dependencies
├── README.md                     # Documentation
├── LICENSE                       # MIT License
├── CHANGELOG.md                  # Version history
├── CONTRIBUTING.md               # Contribution guidelines
├── MANIFEST.in                   # Package data
├── Dockerfile                    # Container image
├── .gitignore                    # Git exclusions
├── example.py                    # Usage examples
├── test_aidmind.py              # Unit tests
├── afghanistan_needs_200.csv     # Sample data
└── test.py                       # Quick test script
```

## Installation Methods

### Method 1: pip install (Local)

```bash
cd AidMind
pip install -e .
```

**Pros**: Fast, easy for development  
**Cons**: Requires Python environment setup

### Method 2: pip install (from PyPI - future)

```bash
pip install aidmind
```

**Note**: Not yet published to PyPI. To publish:
```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

### Method 3: Docker

```bash
docker build -t aidmind:1.0.0 .
docker run -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output \
  aidmind:1.0.0 python -m aidmind /app/data/your_data.csv "YourCountry"
```

**Pros**: Consistent environment, no local setup  
**Cons**: Requires Docker

## Testing the Installation

### Run unit tests:

```bash
pytest test_aidmind.py -v
```

Expected output:
```
test_aidmind.py::TestAdminDetection::test_detect_standard_columns PASSED
test_aidmind.py::TestAdminDetection::test_detect_case_insensitive PASSED
...
=================== XX passed in X.XXs ===================
```

### Run example:

```bash
python example.py
```

### Manual test:

```python
from aidmind import analyze_needs
output = analyze_needs("afghanistan_needs_200.csv", "Afghanistan")
print(f"Success: {output}")
```

## Deployment for NGOs

### Scenario 1: Single Analyst Workstation

**Setup:**
```bash
# Create dedicated environment
python -m venv aidmind_env
source aidmind_env/bin/activate  # Windows: aidmind_env\Scripts\activate

# Install
cd AidMind
pip install -e .
```

**Usage:**
```python
from aidmind import analyze_needs
output = analyze_needs("my_data.csv", "Kenya")
```

### Scenario 2: Shared Team Server

**Setup (Ubuntu/Debian):**
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv git

# Clone/copy AidMind
cd /opt
sudo git clone https://github.com/yourorg/aidmind.git
cd aidmind

# Install globally
sudo pip3 install -e .
```

**Usage:**
```bash
# Any user can run
aidmind /data/humanitarian_data.csv "Afghanistan" --output /reports/
```

### Scenario 3: Restricted/Offline Environment

**Preparation (with internet):**
```bash
# Download all dependencies
pip download -r requirements.txt -d packages/

# Cache boundaries for key countries
python -c "
from aidmind import _fetch_admin1_geojson, _country_to_iso3
for country in ['Afghanistan', 'Kenya', 'Somalia', 'Yemen']:
    iso3 = _country_to_iso3(country)
    _fetch_admin1_geojson(iso3)
"
```

**Transfer to offline environment:**
```bash
# Copy entire AidMind directory including cache/
rsync -avz AidMind/ offline-machine:/opt/aidmind/
```

**Install offline:**
```bash
cd /opt/aidmind
pip install --no-index --find-links=packages/ -r requirements.txt
pip install -e .
```

### Scenario 4: Docker in Production

**Build:**
```bash
docker build -t aidmind:1.0.0 .
docker tag aidmind:1.0.0 yourregistry.com/aidmind:1.0.0
docker push yourregistry.com/aidmind:1.0.0
```

**Deploy:**
```bash
# Create persistent volumes
docker volume create aidmind_cache
docker volume create aidmind_data
docker volume create aidmind_output

# Run
docker run -d \
  --name aidmind_service \
  -v aidmind_data:/app/data \
  -v aidmind_output:/app/output \
  -v aidmind_cache:/app/cache \
  --restart unless-stopped \
  yourregistry.com/aidmind:1.0.0
```

## Configuration

### Fixed Thresholds (Recommended for Multi-Country)

Create `config.py`:
```python
# Organization-standard thresholds
THRESHOLDS = (0.25, 0.50, 0.75)

from aidmind import analyze_needs

def analyze_with_org_standards(dataset, country):
    return analyze_needs(
        dataset,
        country,
        fixed_thresholds=THRESHOLDS
    )
```

### Country-Specific Boundary Files

```python
# Store local boundaries
BOUNDARIES = {
    "Afghanistan": "/data/boundaries/afg_adm1.geojson",
    "Kenya": "/data/boundaries/ken_adm1.geojson",
}

from aidmind import analyze_needs

def analyze_with_local_boundaries(dataset, country):
    return analyze_needs(
        dataset,
        country,
        local_geojson=BOUNDARIES.get(country)
    )
```

## Troubleshooting

### Common Issues

**1. Import Error**
```
ImportError: No module named 'aidmind'
```
**Solution:**
```bash
pip install -e /path/to/AidMind
```

**2. Missing Dependencies**
```
ModuleNotFoundError: No module named 'pandas'
```
**Solution:**
```bash
pip install -r requirements.txt
```

**3. Permission Denied (cache/output)**
```
PermissionError: [Errno 13] Permission denied: '/app/cache'
```
**Solution:**
```bash
mkdir -p cache output
chmod 755 cache output
```

**4. Low Match Rate**
```
WARNING: Low admin name match rate: 45%
```
**Solution:**
- Check admin names match GeoBoundaries official names
- Use `admin_col` parameter to specify correct column
- Provide `local_geojson` with matching names

## Monitoring & Logging

### Enable Detailed Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from aidmind import analyze_needs
output = analyze_needs("data.csv", "Country")
```

### Log to File

```python
import logging
logging.basicConfig(
    filename='aidmind.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
```

## Support

- **Documentation**: See README.md
- **Issues**: GitHub Issues (https://github.com/yourorg/aidmind/issues)
- **Email**: support@aidmind.org

## Next Steps

1. ✅ Test with your own humanitarian datasets
2. ✅ Set up fixed thresholds for your organization
3. ✅ Cache boundaries for your countries of operation
4. ✅ Train your team on usage and interpretation
5. ✅ Integrate into your reporting workflows
6. ✅ Contribute improvements back to the project

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-28  
**Status**: Production Ready ✅

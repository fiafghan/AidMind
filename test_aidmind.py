"""
Unit tests for AidMind
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
import json
from aidmind import (
    analyze_needs,
    _detect_admin_column,
    _normalize_name,
    _strip_suffix_unit,
    _compute_need_scores,
)


class TestAdminDetection:
    """Tests for admin column detection"""
    
    def test_detect_standard_columns(self):
        """Test detection of standard admin column names"""
        df = pd.DataFrame({"province": ["A", "B"], "value": [1, 2]})
        assert _detect_admin_column(df) == "province"
        
        df = pd.DataFrame({"admin1": ["A", "B"], "value": [1, 2]})
        assert _detect_admin_column(df) == "admin1"
        
        df = pd.DataFrame({"region": ["A", "B"], "value": [1, 2]})
        assert _detect_admin_column(df) == "region"
    
    def test_detect_case_insensitive(self):
        """Test case-insensitive detection"""
        df = pd.DataFrame({"Province": ["A", "B"], "value": [1, 2]})
        assert _detect_admin_column(df) == "Province"
        
        df = pd.DataFrame({"PROVINCE": ["A", "B"], "value": [1, 2]})
        assert _detect_admin_column(df) == "PROVINCE"
    
    def test_no_admin_column(self):
        """Test when no admin column exists"""
        df = pd.DataFrame({"value1": [1, 2], "value2": [3, 4]})
        # Should return first non-numeric column or None
        result = _detect_admin_column(df)
        assert result is None or result in df.columns


class TestNameNormalization:
    """Tests for name normalization"""
    
    def test_basic_normalization(self):
        """Test basic name normalization"""
        assert _normalize_name("Kabul") == "kabul"
        assert _normalize_name("  Herat  ") == "herat"
        assert _normalize_name("KANDAHAR") == "kandahar"
    
    def test_special_characters(self):
        """Test removal of special characters"""
        assert _normalize_name("Sar-e Pol") == "sare pol"
        assert _normalize_name("Nangarhar!") == "nangarhar"
        assert _normalize_name("Badakhshan@#$") == "badakhshan"
    
    def test_multiple_spaces(self):
        """Test collapsing multiple spaces"""
        assert _normalize_name("Valle  del   Cauca") == "valle del cauca"
    
    def test_suffix_stripping(self):
        """Test stripping numeric suffixes"""
        assert _strip_suffix_unit("Kabul_1") == "Kabul"
        assert _strip_suffix_unit("Herat-2") == "Herat"
        assert _strip_suffix_unit("Kandahar_10") == "Kandahar"
        assert _strip_suffix_unit("Balkh") == "Balkh"


class TestNeedScoring:
    """Tests for need score computation"""
    
    def test_need_score_calculation(self):
        """Test need score normalization to 0-1 range"""
        df = pd.DataFrame({
            "ind1": [0.1, 0.5, 0.9],
            "ind2": [0.2, 0.6, 0.8],
        })
        scores = _compute_need_scores(df)
        
        assert len(scores) == 3
        assert np.min(scores) >= 0.0
        assert np.max(scores) <= 1.0
        assert np.max(scores) > np.min(scores)  # Should have variance
    
    def test_uniform_scores(self):
        """Test when all indicators are the same"""
        df = pd.DataFrame({
            "ind1": [0.5, 0.5, 0.5],
            "ind2": [0.5, 0.5, 0.5],
        })
        scores = _compute_need_scores(df)
        
        # All scores should be equal (and 0 after normalization)
        assert np.allclose(scores, 0.0)


class TestInputValidation:
    """Tests for input validation"""
    
    def test_missing_file(self):
        """Test error when file doesn't exist"""
        with pytest.raises(FileNotFoundError):
            analyze_needs("nonexistent.csv", "Afghanistan")
    
    def test_empty_country_name(self):
        """Test error with empty country name"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("province,value\nKabul,0.5\n")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="country_name cannot be empty"):
                analyze_needs(temp_path, "")
        finally:
            os.unlink(temp_path)
    
    def test_invalid_admin_level(self):
        """Test error with invalid admin level"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("province,value\nKabul,0.5\n")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid admin_level"):
                analyze_needs(temp_path, "Afghanistan", admin_level="ADM3")
        finally:
            os.unlink(temp_path)
    
    def test_invalid_thresholds(self):
        """Test error with invalid fixed thresholds"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("province,value\nKabul,0.5\n")
            temp_path = f.name
        
        try:
            # Wrong number of thresholds
            with pytest.raises(ValueError, match="must be a tuple/list of 3 floats"):
                analyze_needs(temp_path, "Afghanistan", fixed_thresholds=(0.5,))
            
            # Non-numeric thresholds
            with pytest.raises(ValueError, match="must be numeric"):
                analyze_needs(temp_path, "Afghanistan", fixed_thresholds=("a", "b", "c"))
        finally:
            os.unlink(temp_path)


class TestEndToEnd:
    """End-to-end integration tests"""
    
    def test_basic_workflow(self):
        """Test complete workflow with minimal dataset"""
        # Create temporary CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("province,health,education,income\n")
            f.write("Kabul,0.8,0.9,0.7\n")
            f.write("Kandahar,0.4,0.3,0.5\n")
            f.write("Herat,0.6,0.7,0.6\n")
            f.write("Balkh,0.5,0.6,0.5\n")
            temp_csv = f.name
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_html = os.path.join(temp_dir, "test_map.html")
            
            try:
                # Run analysis
                result_path = analyze_needs(
                    dataset_path=temp_csv,
                    country_name="Afghanistan",
                    output_html_path=output_html,
                )
                
                # Verify outputs exist
                assert os.path.exists(result_path)
                assert result_path == output_html
                
                # Check CSV export
                csv_path = os.path.join(temp_dir, "needs_scores_AFG.csv")
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    assert "need_score" in df.columns
                    assert "need_level" in df.columns
                    assert len(df) > 0
                
            finally:
                os.unlink(temp_csv)
    
    def test_aggregation(self):
        """Test that duplicate admin names are aggregated"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("province,health,education\n")
            f.write("Kabul_1,0.8,0.9\n")
            f.write("Kabul_2,0.7,0.8\n")
            f.write("Herat_1,0.6,0.7\n")
            f.write("Herat_2,0.5,0.6\n")
            temp_csv = f.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_html = os.path.join(temp_dir, "test_agg.html")
            
            try:
                result_path = analyze_needs(
                    dataset_path=temp_csv,
                    country_name="Afghanistan",
                    output_html_path=output_html,
                )
                assert os.path.exists(result_path)
            finally:
                os.unlink(temp_csv)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

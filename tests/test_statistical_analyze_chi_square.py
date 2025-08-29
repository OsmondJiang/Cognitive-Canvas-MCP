#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Chi-Square Functionality in Statistical Analyzer Tool
Updated to test JSON output format
"""
import sys
import os
import unittest
import json
import math

# Add the parent directory to Python path to import tools
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from tools.statistical_analyzer import StatisticalAnalyzer

class TestChiSquareBasic(unittest.TestCase):
    """Test basic chi-square functionality with JSON output"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalAnalyzer()
    
    def _validate_json_structure(self, result, analysis_name):
        """Helper method to validate JSON structure"""
        try:
            result_data = json.loads(result)
            self.assertIsInstance(result_data, dict, f"{analysis_name}: Result should be a JSON object")
            self.assertIn("analysis_report", result_data, f"{analysis_name}: Missing 'analysis_report' key")
            return result_data
        except json.JSONDecodeError as e:
            self.fail(f"{analysis_name}: Invalid JSON format - {e}")
    
    def test_chi_square_calculation_simple(self):
        """Test basic chi-square calculation with known result"""
        data = {
            "device": ["Mobile", "Desktop", "Mobile", "Desktop", "Mobile"],
            "conversion": ["Yes", "No", "Yes", "No", "Yes"]
        }
        
        result = self.tool.analyze("test_chi_simple", data=data, analysis_type="chi_square_test")
        result_data = self._validate_json_structure(result, "Basic Chi-Square")
        
        # Check analysis type
        self.assertEqual(result_data["analysis_report"]["analysis_type"], "chi_square_test")
        self.assertEqual(result_data["analysis_report"]["output_format"], "json")
        
        # Check results structure
        results = result_data["analysis_report"]["results"]
        self.assertIn("chi_square", results)
        
        chi_square = results["chi_square"]
        self.assertIn("statistical_results", chi_square)
        self.assertIn("effect_size", chi_square)
        self.assertIn("contingency_table", chi_square)
        
        # Check specific metrics
        stats = chi_square["statistical_results"]
        self.assertIn("chi_square_statistic", stats)
        self.assertIn("p_value", stats)
        self.assertIn("degrees_of_freedom", stats)
        
        # Value validation
        self.assertEqual(stats["degrees_of_freedom"]["value"], 1)  # (2-1) * (2-1)
        self.assertGreaterEqual(stats["chi_square_statistic"]["value"], 0)
        self.assertGreaterEqual(stats["p_value"]["value"], 0)
        self.assertLessEqual(stats["p_value"]["value"], 1)
    
    def test_chi_square_perfect_independence(self):
        """Test chi-square with perfectly independent variables"""
        # Perfect independence: equal distribution across all cells
        data = {
            "group": ["A", "A", "B", "B"] * 4,
            "outcome": ["Success", "Failure", "Success", "Failure"] * 4
        }
        
        result = self.tool.analyze("test_chi_independence", data=data, analysis_type="chi_square_test")
        result_data = self._validate_json_structure(result, "Perfect Independence")
        
        # Check chi-square should be close to 0 for perfect independence
        chi_square = result_data["analysis_report"]["results"]["chi_square"]
        chi_stat = chi_square["statistical_results"]["chi_square_statistic"]["value"]
        cramers_v = chi_square["effect_size"]["cramers_v"]["value"]
        
        self.assertAlmostEqual(chi_stat, 0, places=3)
        self.assertAlmostEqual(cramers_v, 0, places=3)
    
    def test_chi_square_strong_association(self):
        """Test chi-square with strong association"""
        # Strong association: A always goes with Success, B always goes with Failure
        data = {
            "treatment": ["Treatment"] * 10 + ["Control"] * 10,
            "outcome": ["Success"] * 10 + ["Failure"] * 10
        }
        
        result = self.tool.analyze("test_chi_strong", data=data, analysis_type="chi_square_test")
        result_data = self._validate_json_structure(result, "Strong Association")
        
        chi_square = result_data["analysis_report"]["results"]["chi_square"]
        chi_stat = chi_square["statistical_results"]["chi_square_statistic"]["value"]
        cramers_v = chi_square["effect_size"]["cramers_v"]["value"]
        association_strength = chi_square["effect_size"]["association_strength"]
        
        # Chi-square should be high for perfect association
        self.assertGreater(chi_stat, 10)
        # Cramér's V should be close to 1 for perfect association
        self.assertGreater(cramers_v, 0.8)
        self.assertEqual(association_strength, "Large association")

class TestChiSquareEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalAnalyzer()
    
    def _validate_json_structure(self, result, analysis_name):
        """Helper method to validate JSON structure"""
        try:
            result_data = json.loads(result)
            self.assertIsInstance(result_data, dict, f"{analysis_name}: Result should be a JSON object")
            return result_data
        except json.JSONDecodeError as e:
            self.fail(f"{analysis_name}: Invalid JSON format - {e}")
    
    def test_insufficient_data(self):
        """Test with insufficient data"""
        data = {
            "group": ["A", "B"],
            "outcome": ["X", "Y"]
        }
        
        result = self.tool.analyze("test_chi_insufficient", data=data, analysis_type="chi_square_test")
        result_data = self._validate_json_structure(result, "Insufficient Data")
        
        # Should still return proper JSON structure
        if "analysis_report" in result_data:
            self.assertEqual(result_data["analysis_report"]["analysis_type"], "chi_square_test")
        # Or might return error format
        elif "error" in result_data:
            self.assertIn("at least 5 observations", result_data["error"])
    
    def test_single_category_variable(self):
        """Test with one variable having only one category"""
        data = {
            "treatment": ["Same"] * 10,
            "outcome": ["Success", "Failure"] * 5
        }
        
        result = self.tool.analyze("test_chi_single_cat", data=data, analysis_type="chi_square_test")
        result_data = self._validate_json_structure(result, "Single Category")
        
        # Should handle gracefully in JSON format
        if "analysis_report" in result_data and "results" in result_data["analysis_report"]:
            results = result_data["analysis_report"]["results"]
            if "chi_square" in results:
                chi_square = results["chi_square"]
                # Should have an error due to division by zero with single category
                if "error" in chi_square:
                    self.assertIn("division by zero", chi_square["error"])
                elif "statistical_results" in chi_square:
                    # If it did compute, degrees of freedom should be 0
                    df = chi_square["statistical_results"]["degrees_of_freedom"]["value"]
                    self.assertEqual(df, 0)

class TestChiSquareContingencyTable(unittest.TestCase):
    """Test contingency table creation and validation in JSON output"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalAnalyzer()
    
    def _validate_json_structure(self, result, analysis_name):
        """Helper method to validate JSON structure"""
        try:
            result_data = json.loads(result)
            self.assertIsInstance(result_data, dict, f"{analysis_name}: Result should be a JSON object")
            self.assertIn("analysis_report", result_data, f"{analysis_name}: Missing 'analysis_report' key")
            return result_data
        except json.JSONDecodeError as e:
            self.fail(f"{analysis_name}: Invalid JSON format - {e}")
    
    def test_contingency_table_structure(self):
        """Test contingency table structure in JSON output"""
        data = {
            "browser": ["Chrome", "Chrome", "Firefox", "Firefox", "Safari", "Safari"],
            "conversion": ["Yes", "No", "Yes", "No", "Yes", "No"]
        }
        
        result = self.tool.analyze("test_contingency", data=data, analysis_type="chi_square_test")
        result_data = self._validate_json_structure(result, "Contingency Table")
        
        chi_square = result_data["analysis_report"]["results"]["chi_square"]
        contingency = chi_square["contingency_table"]
        
        # Validate contingency table structure
        self.assertIn("table_data", contingency)
        self.assertIn("categories_1", contingency)
        self.assertIn("categories_2", contingency)
        self.assertIn("note", contingency)
        
        # Check table dimensions
        table_data = contingency["table_data"]
        categories_1 = contingency["categories_1"]
        categories_2 = contingency["categories_2"]
        
        self.assertEqual(len(table_data), len(categories_1))
        for row in table_data:
            self.assertEqual(len(row), len(categories_2))
    
    def test_contingency_table_values(self):
        """Test contingency table values are correct"""
        data = {
            "category": ["A", "A", "B", "B", "A", "B"],
            "response": ["X", "Y", "X", "Y", "X", "Y"]
        }
        
        result = self.tool.analyze("test_contingency_values", data=data, analysis_type="chi_square_test")
        result_data = self._validate_json_structure(result, "Contingency Values")
        
        contingency = result_data["analysis_report"]["results"]["chi_square"]["contingency_table"]
        table_data = contingency["table_data"]
        
        # Verify the total count matches the data length
        total_count = sum(sum(row) for row in table_data)
        self.assertEqual(total_count, len(data["category"]))
        
        # Check that all counts are non-negative integers
        for row in table_data:
            for count in row:
                self.assertGreaterEqual(count, 0)
                self.assertIsInstance(count, int)

class TestChiSquareIntegration(unittest.TestCase):
    """Test integration with the main analyze method"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalAnalyzer()
    
    def _validate_json_structure(self, result, analysis_name):
        """Helper method to validate JSON structure"""
        try:
            result_data = json.loads(result)
            self.assertIsInstance(result_data, dict, f"{analysis_name}: Result should be a JSON object")
            self.assertIn("analysis_report", result_data, f"{analysis_name}: Missing 'analysis_report' key")
            return result_data
        except json.JSONDecodeError as e:
            self.fail(f"{analysis_name}: Invalid JSON format - {e}")
    
    def test_analyze_method_chi_square(self):
        """Test chi-square through main analyze method"""
        data = {
            "category": ["A", "B", "A", "B", "A", "B"],
            "response": ["Yes", "No", "Yes", "No", "Yes", "No"]
        }
        
        result = self.tool.analyze("test_analyze_chi", data=data, analysis_type="chi_square_test")
        result_data = self._validate_json_structure(result, "Analyze Method")
        
        # Verify complete analysis structure
        self.assertEqual(result_data["analysis_report"]["analysis_type"], "chi_square_test")
        results = result_data["analysis_report"]["results"]
        
        # Should have frequency analysis for both variables
        freq_keys = [k for k in results.keys() if "frequency_analysis" in k]
        self.assertTrue(len(freq_keys) >= 2)
        
        # Should have chi-square test results
        self.assertIn("chi_square", results)
        
        chi_square = results["chi_square"]
        self.assertIn("test_information", chi_square)
        self.assertIn("statistical_results", chi_square)
        self.assertIn("effect_size", chi_square)
        self.assertIn("contingency_table", chi_square)
    
    def test_auto_detection_categorical(self):
        """Test auto detection chooses chi-square for two categorical variables"""
        data = {
            "treatment": ["A", "B", "A", "B", "A"],
            "outcome": ["Success", "Failure", "Success", "Failure", "Success"]
        }
        
        result = self.tool.analyze("test_auto_chi", data=data, analysis_type="auto")
        result_data = self._validate_json_structure(result, "Auto Detection")
        
        # Should auto-detect chi_square_test for two categorical variables
        self.assertEqual(result_data["analysis_report"]["analysis_type"], "chi_square_test")

class TestChiSquareFrequencyAnalysis(unittest.TestCase):
    """Test frequency analysis integration with chi-square"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalAnalyzer()
    
    def _validate_json_structure(self, result, analysis_name):
        """Helper method to validate JSON structure"""
        try:
            result_data = json.loads(result)
            self.assertIsInstance(result_data, dict, f"{analysis_name}: Result should be a JSON object")
            self.assertIn("analysis_report", result_data, f"{analysis_name}: Missing 'analysis_report' key")
            return result_data
        except json.JSONDecodeError as e:
            self.fail(f"{analysis_name}: Invalid JSON format - {e}")
    
    def test_frequency_analysis_included(self):
        """Test that chi-square includes frequency analysis for both variables"""
        data = {
            "device_type": ["Mobile", "Desktop", "Tablet", "Mobile", "Desktop"],
            "user_action": ["Click", "View", "Click", "View", "Click"]
        }
        
        result = self.tool.analyze("test_freq_chi", data=data, analysis_type="chi_square_test")
        result_data = self._validate_json_structure(result, "Frequency Analysis")
        
        results = result_data["analysis_report"]["results"]
        
        # Should have frequency analysis for both variables
        self.assertIn("frequency_analysis_device_type", results)
        self.assertIn("frequency_analysis_user_action", results)
        
        # Check frequency analysis structure
        freq_device = results["frequency_analysis_device_type"]
        self.assertIn("summary_statistics", freq_device)
        self.assertIn("frequency_distribution", freq_device)
        self.assertIn("diversity_metrics", freq_device)
        
        freq_action = results["frequency_analysis_user_action"]
        self.assertIn("summary_statistics", freq_action)
        self.assertIn("frequency_distribution", freq_action)
        self.assertIn("diversity_metrics", freq_action)

if __name__ == '__main__':
    unittest.main(verbosity=2)

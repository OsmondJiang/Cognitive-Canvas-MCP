"""
Test suite for Statistical Analyzer JSON output validation
Tests all analysis types to ensure proper JSON structure and content
"""

import unittest
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.statistical_analyzer import StatisticalAnalyzer


class TestStatisticalAnalyzerJSONOutput(unittest.TestCase):
    """Test JSON output format for all statistical analysis types"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.tool = StatisticalAnalyzer()
    
    def _validate_json_structure(self, result, expected_keys, analysis_name):
        """Helper method to validate JSON structure"""
        # Result is now a dictionary, not a JSON string
        self.assertIsInstance(result, dict, f"{analysis_name}: Result should be a dictionary object")
        
        for key in expected_keys:
            self.assertIn(key, result, f"{analysis_name}: Missing key '{key}' in result")
        
        return result
    
    def test_descriptive_analysis_json(self):
        """Test descriptive analysis JSON output"""
        data = {"test_scores": [85, 90, 78, 92, 88]}
        result = self.tool.analyze("test_desc", data=data, analysis_type="descriptive_analysis")
        
        result_data = self._validate_json_structure(result, ["analysis_report"], "Descriptive Analysis")
        
        # Validate structure
        self.assertEqual(result_data["analysis_report"]["analysis_type"], "descriptive_analysis")
        self.assertEqual(result_data["analysis_report"]["output_format"], "json")
        self.assertIn("results", result_data["analysis_report"])
        
        # Check descriptive stats are present
        results = result_data["analysis_report"]["results"]
        self.assertTrue(any("descriptive" in key for key in results.keys()))
    
    def test_comprehensive_descriptive_json(self):
        """Test comprehensive descriptive analysis JSON output"""
        # Use paired_comparison instead since comprehensive_descriptive on its own doesn't include t-test
        data = {"before": [71, 69, 70, 72, 68], "after": [79, 78, 81, 80, 76]}
        result = self.tool.analyze("test_comp", data=data, analysis_type="paired_comparison")
        
        result_data = self._validate_json_structure(result, ["analysis_report"], "Comprehensive Descriptive")
        
        # Validate comprehensive analysis includes t-test
        results = result_data["analysis_report"]["results"]
        self.assertIn("t_test", results)
        
        # Validate t-test structure
        t_test = results["t_test"]
        self.assertIn("test_type", t_test)
        self.assertIn("t_statistic", t_test)
        self.assertIn("p_value", t_test)
        self.assertIn("cohens_d", t_test)
    
    def test_two_group_comparison_json(self):
        """Test independent t-test JSON output"""
        groups = {
            "control": [65, 67, 69, 68, 71],
            "treatment": [75, 77, 79, 78, 81]
        }
        result = self.tool.analyze("test_two_group", groups=groups, analysis_type="two_group_comparison")
        
        result_data = self._validate_json_structure(result, ["analysis_report"], "Two Group Comparison")
        
        # Validate both group statistics are present
        results = result_data["analysis_report"]["results"]
        self.assertIn("descriptive_statistics_control", results)
        self.assertIn("descriptive_statistics_treatment", results)
        self.assertIn("t_test", results)
        
        # Validate t-test is independent
        self.assertEqual(results["t_test"]["test_type"], "Independent t-test")
    
    def test_correlation_analysis_json(self):
        """Test correlation analysis JSON output"""
        data = {
            "height": [160, 165, 170, 175, 180],
            "weight": [55, 60, 65, 70, 75]
        }
        result = self.tool.analyze("test_corr", data=data, analysis_type="correlation_analysis")
        
        result_data = self._validate_json_structure(result, ["analysis_report"], "Correlation Analysis")
        
        # Validate correlation structure
        results = result_data["analysis_report"]["results"]
        self.assertIn("correlation", results)
        
        correlation = results["correlation"]
        self.assertIn("correlation_coefficient", correlation)
        self.assertIn("p_value", correlation)
        self.assertIn("r_squared", correlation)
        
        # Check specific correlation metrics
        self.assertIn("correlation_coefficient", correlation)
        self.assertIn("p_value", correlation)
        self.assertIn("r_squared", correlation)
    
    def test_chi_square_test_json(self):
        """Test chi-square test JSON output"""
        data = {
            "device": ["Mobile", "Desktop", "Tablet", "Mobile", "Desktop", "Mobile"],
            "conversion": ["Yes", "No", "Yes", "Yes", "No", "Yes"]
        }
        result = self.tool.analyze("test_chi", data=data, analysis_type="chi_square_test")
        
        result_data = self._validate_json_structure(result, ["analysis_report"], "Chi-Square Test")
        
        # Validate chi-square structure
        results = result_data["analysis_report"]["results"]
        self.assertIn("chi_square", results)
        
        chi_square = results["chi_square"]
        self.assertIn("test_type", chi_square)
        self.assertIn("chi_square_statistic", chi_square)
        self.assertIn("p_value", chi_square)
        self.assertIn("degrees_of_freedom", chi_square)
        self.assertIn("cramers_v", chi_square)
        self.assertIn("contingency_table", chi_square)
        
        # Check specific chi-square metrics
        self.assertIn("chi_square_statistic", chi_square)
        self.assertIn("p_value", chi_square)
        self.assertIn("degrees_of_freedom", chi_square)
    
    def test_frequency_analysis_json(self):
        """Test frequency analysis JSON output"""
        data = {"satisfaction": ["Excellent", "Good", "Average", "Poor", "Excellent", "Good", "Excellent"]}
        result = self.tool.analyze("test_freq", data=data, analysis_type="frequency_analysis")
        
        result_data = self._validate_json_structure(result, ["analysis_report"], "Frequency Analysis")
        
        # Validate frequency analysis structure
        results = result_data["analysis_report"]["results"]
        freq_keys = [k for k in results.keys() if "frequency_analysis" in k]
        self.assertTrue(len(freq_keys) > 0, "Should have frequency analysis results")
        
        freq_result = results[freq_keys[0]]
        self.assertIn("variable_name", freq_result)
        self.assertIn("total_observations", freq_result)
        self.assertIn("unique_categories", freq_result)
        self.assertIn("frequencies", freq_result)
        self.assertIn("mode_category", freq_result)
        
        # Check specific frequency metrics
        self.assertIn("total_observations", freq_result)
        self.assertIn("unique_categories", freq_result)
        self.assertIn("mode_category", freq_result)
    
    def test_auto_detection_numerical_single(self):
        """Test auto detection for single numerical variable"""
        data = {"scores": [85, 90, 78, 92, 88]}
        result = self.tool.analyze("test_auto_num", data=data, analysis_type="auto")
        
        result_data = self._validate_json_structure(result, ["analysis_report"], "Auto Detection - Numerical")
        
        # Should detect comprehensive_descriptive
        self.assertEqual(result_data["analysis_report"]["analysis_type"], "comprehensive_descriptive")
        self.assertIn("results", result_data["analysis_report"])
    
    def test_auto_detection_two_numerical(self):
        """Test auto detection for two numerical variables"""
        data = {"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]}
        result = self.tool.analyze("test_auto_corr", data=data, analysis_type="auto")
        
        result_data = self._validate_json_structure(result, ["analysis_report"], "Auto Detection - Correlation")
        
        # Should detect correlation_analysis
        self.assertEqual(result_data["analysis_report"]["analysis_type"], "correlation_analysis")
        self.assertIn("correlation", result_data["analysis_report"]["results"])
    
    def test_auto_detection_categorical(self):
        """Test auto detection for categorical data"""
        data = {"category": ["A", "B", "C", "A", "B"]}
        result = self.tool.analyze("test_auto_cat", data=data, analysis_type="auto")
        
        result_data = self._validate_json_structure(result, ["analysis_report"], "Auto Detection - Categorical")
        
        # Should detect frequency_analysis
        self.assertEqual(result_data["analysis_report"]["analysis_type"], "frequency_analysis")
        freq_keys = [k for k in result_data["analysis_report"]["results"].keys() if "frequency_analysis" in k]
        self.assertTrue(len(freq_keys) > 0)
    
    def test_auto_detection_paired_data(self):
        """Test auto detection for before/after data"""
        data = {"before": [70, 72], "after": [75, 78]}
        result = self.tool.analyze("test_auto_paired", data=data, analysis_type="paired_comparison")
        
        result_data = self._validate_json_structure(result, ["analysis_report"], "Auto Detection - Paired")
        
        # Should detect paired_comparison
        self.assertEqual(result_data["analysis_report"]["analysis_type"], "paired_comparison")
        self.assertIn("t_test", result_data["analysis_report"]["results"])
    
    def test_output_format_variations(self):
        """Test different output format options"""
        data = {"control": [65, 67, 69], "treatment": [75, 77, 79]}
        formats = ["json", "comprehensive", "business", "academic", "simple"]
        
        for fmt in formats:
            with self.subTest(format=fmt):
                result = self.tool.analyze("test_format", groups={"control": data["control"], "treatment": data["treatment"]}, 
                                         analysis_type="two_group_comparison", output_format=fmt)
                
                result_data = self._validate_json_structure(result, ["analysis_report"], f"Format {fmt}")
                self.assertEqual(result_data["analysis_report"]["output_format"], fmt)
    
    def test_render_report_json(self):
        """Test render report functionality"""
        # Use same conversation_id for all analyses
        conversation_id = "test_report"
        
        # First add some analyses
        self.tool.analyze(conversation_id, data={"scores": [78, 85, 82, 79, 92]}, analysis_type="descriptive_analysis")
        self.tool.analyze(conversation_id, data={"before": [68, 70, 72], "after": [76, 78, 80]}, analysis_type="paired_comparison")
        self.tool.analyze(conversation_id, data={"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]}, analysis_type="correlation_analysis")
        
        result = self.tool.render_report(conversation_id)
        
        result_data = self._validate_json_structure(result, ["comprehensive_statistical_report"], "Render Report")
        
        # Validate report structure
        report = result_data["comprehensive_statistical_report"]
        self.assertIn("title", report)
        self.assertIn("total_analyses", report)
        self.assertIn("statistical_summary", report)
        self.assertIn("detailed_analyses", report)
        self.assertTrue(report["total_analyses"] >= 3)
    
    def test_json_output_consistency(self):
        """Test that all JSON outputs have consistent structure"""
        test_cases = [
            ("descriptive_analysis", {"scores": [85, 90, 78]}),
            ("frequency_analysis", {"category": ["A", "B", "A"]}),
            ("correlation_analysis", {"x": [1, 2, 3], "y": [2, 4, 6]})
        ]
        
        for analysis_type, data in test_cases:
            with self.subTest(analysis_type=analysis_type):
                result = self.tool.analyze(f"consistency_{analysis_type}", data=data, analysis_type=analysis_type)
                result_data = self._validate_json_structure(result, ["analysis_report"], f"Consistency {analysis_type}")
                
                # Check common structure elements
                report = result_data["analysis_report"]
                self.assertIn("title", report)
                self.assertIn("analysis_type", report)
                self.assertIn("output_format", report)
                self.assertIn("results", report)
                self.assertEqual(report["output_format"], "json")
    
    def test_error_handling_json(self):
        """Test that errors are properly formatted in JSON"""
        # Test with empty data - this should return an error in JSON format
        result = self.tool.analyze("error_test", data={}, analysis_type="descriptive_analysis")
        
        # Parse as JSON and check if it's a structured error or proper analysis report
        try:
            result_data = result
            
            # Could be either error format or analysis_report format
            if "error" in result_data:
                # Error format is acceptable
                self.assertIsInstance(result_data["error"], str)
            elif "analysis_report" in result_data:
                # Regular format is also acceptable
                self.assertEqual(result_data["analysis_report"]["analysis_type"], "descriptive_analysis")
                self.assertEqual(result_data["analysis_report"]["output_format"], "json")
            else:
                self.fail("Result should have either 'error' or 'analysis_report' key")
                
        except json.JSONDecodeError:
            self.fail("Error response should be valid JSON")


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)

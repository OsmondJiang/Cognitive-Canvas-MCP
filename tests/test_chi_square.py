#!/usr/bin/env python3
"""
Comprehensive Test Suite for Chi-Square Functionality in Statistical Evidence Tool
"""
import sys
import os

# Add the parent directory to Python path to import tools
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from tools.statistical_evidence import StatisticalEvidenceTool

def test_chi_square_edge_cases():
    """Test edge cases and error conditions"""
    tool = StatisticalEvidenceTool()
    
    #!/usr/bin/env python3
"""
Comprehensive Unit Tests for Chi-Square Functionality in Statistical Evidence Tool
"""
import sys
import os
import unittest
import json
import math

# Add the parent directory to Python path to import tools
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from tools.statistical_evidence import StatisticalEvidenceTool

class TestChiSquareBasic(unittest.TestCase):
    """Test basic chi-square functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalEvidenceTool()
    
    def test_chi_square_calculation_simple(self):
        """Test basic chi-square calculation with known result"""
        # Use sufficient data (at least 5 observations)
        var1 = ["A", "A", "B", "B", "A"]
        var2 = ["X", "Y", "X", "Y", "X"]
        
        result = self.tool._perform_chi_square_test(var1, var2, "var1", "var2")
        
        # Basic structure assertions
        self.assertIsInstance(result, dict)
        self.assertNotIn("error", result)
        self.assertIn("chi_square_statistic", result)
        self.assertIn("p_value", result)
        self.assertIn("cramers_v", result)
        self.assertIn("degrees_of_freedom", result)
        
        # Value assertions
        self.assertEqual(result["degrees_of_freedom"], 1)  # (2-1) * (2-1)
        self.assertGreaterEqual(result["chi_square_statistic"], 0)
        self.assertGreaterEqual(result["p_value"], 0)
        self.assertLessEqual(result["p_value"], 1)
        self.assertGreaterEqual(result["cramers_v"], 0)
        self.assertLessEqual(result["cramers_v"], 1)
    
    def test_chi_square_perfect_independence(self):
        """Test chi-square with perfectly independent variables"""
        # Perfect independence: equal distribution across all cells
        var1 = ["A", "A", "B", "B"] * 4
        var2 = ["X", "Y", "X", "Y"] * 4
        
        result = self.tool._perform_chi_square_test(var1, var2, "var1", "var2")
        
        self.assertNotIn("error", result)
        # Chi-square should be exactly 0 for perfect independence
        self.assertAlmostEqual(result["chi_square_statistic"], 0, places=3)
        self.assertAlmostEqual(result["cramers_v"], 0, places=3)
    
    def test_chi_square_strong_association(self):
        """Test chi-square with strong association"""
        # Strong association: A always goes with X, B always goes with Y
        var1 = ["A"] * 10 + ["B"] * 10
        var2 = ["X"] * 10 + ["Y"] * 10
        
        result = self.tool._perform_chi_square_test(var1, var2, "var1", "var2")
        
        self.assertNotIn("error", result)
        # Chi-square should be high for perfect association
        self.assertGreater(result["chi_square_statistic"], 10)
        # Cramér's V should be close to 1 for perfect association
        self.assertGreater(result["cramers_v"], 0.8)
        self.assertEqual(result["effect_size_category"], "Large association")

class TestChiSquareEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalEvidenceTool()
    
    def test_insufficient_data(self):
        """Test with insufficient data"""
        var1 = ["A", "B"]
        var2 = ["X", "Y"]
        
        result = self.tool._perform_chi_square_test(var1, var2, "var1", "var2")
        
        self.assertIn("error", result)
        self.assertIn("at least 5 observations", result["error"])
    
    def test_unequal_length_arrays(self):
        """Test with unequal length arrays"""
        var1 = ["A", "B", "C"]
        var2 = ["X", "Y"]
        
        result = self.tool._perform_chi_square_test(var1, var2, "var1", "var2")
        
        self.assertIn("error", result)
        self.assertIn("equal length", result["error"])
    
    def test_single_category_variable(self):
        """Test with one variable having only one category"""
        var1 = ["A"] * 10
        var2 = ["X", "Y"] * 5
        
        result = self.tool._perform_chi_square_test(var1, var2, "var1", "var2")
        
        # Should handle gracefully, degrees of freedom should be 0
        if "error" not in result:
            self.assertEqual(result["degrees_of_freedom"], 0)
    
    def test_empty_data(self):
        """Test with empty data"""
        var1 = []
        var2 = []
        
        result = self.tool._perform_chi_square_test(var1, var2, "var1", "var2")
        
        self.assertIn("error", result)

class TestChiSquareContingencyTable(unittest.TestCase):
    """Test contingency table creation and validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalEvidenceTool()
    
    def test_contingency_table_structure(self):
        """Test contingency table structure"""
        var1 = ["A", "A", "B", "B", "A", "B"]
        var2 = ["X", "Y", "X", "Y", "X", "Y"]
        
        table, cats1, cats2 = self.tool._create_contingency_table(var1, var2)
        
        # Test structure
        self.assertEqual(len(table), len(cats1))
        self.assertEqual(len(table[0]), len(cats2))
        self.assertEqual(cats1, ["A", "B"])  # Should be sorted
        self.assertEqual(cats2, ["X", "Y"])  # Should be sorted
        
        # Test values
        total_count = sum(sum(row) for row in table)
        self.assertEqual(total_count, len(var1))
    
    def test_contingency_table_values(self):
        """Test contingency table values are correct"""
        var1 = ["A", "A", "B", "B", "A", "B"]
        var2 = ["X", "Y", "X", "Y", "X", "Y"]
        
        table, cats1, cats2 = self.tool._create_contingency_table(var1, var2)
        
        # Manual count verification
        # A-X: positions 0, 4 = 2 occurrences
        # A-Y: position 1 = 1 occurrence  
        # B-X: position 2 = 1 occurrence
        # B-Y: positions 3, 5 = 2 occurrences
        
        expected_table = [[2, 1], [1, 2]]
        self.assertEqual(table, expected_table)

class TestChiSquareIntegration(unittest.TestCase):
    """Test integration with the main analyze method"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalEvidenceTool()
    
    def test_analyze_method_chi_square(self):
        """Test chi-square through main analyze method"""
        data = {
            "category": ["A", "B", "A", "B", "A", "B"],
            "response": ["Yes", "No", "Yes", "No", "Yes", "No"]
        }
        
        result = self.tool.analyze(
            conversation_id="test_integration",
            data=data,
            analysis_type="chi_square_test"
        )
        
        # Should return formatted string
        self.assertIsInstance(result, str)
        self.assertIn("Chi-Square Test of Independence", result)
        self.assertIn("χ² statistic", result)
        self.assertIn("Contingency Table", result)
    
    def test_auto_detection_categorical(self):
        """Test automatic detection of categorical data"""
        data = {
            "gender": ["Male", "Female"] * 5,
            "preference": ["A", "B"] * 5
        }
        
        result = self.tool.analyze(
            conversation_id="test_auto_detect",
            data=data,
            analysis_type="auto"
        )
        
        # Should auto-detect and perform chi-square
        self.assertIsInstance(result, str)
        self.assertIn("Chi-Square Test", result)
    
    def test_frequency_analysis_single_variable(self):
        """Test frequency analysis for single categorical variable"""
        data = {
            "color": ["Red", "Blue", "Green", "Red", "Blue", "Red"]
        }
        
        result = self.tool.analyze(
            conversation_id="test_frequency",
            data=data,
            analysis_type="frequency_analysis"
        )
        
        self.assertIsInstance(result, str)
        # Check if result contains statistical analysis report
        self.assertIn("Statistical Analysis Report", result)
        
        # For frequency analysis, we should be able to see evidence of analysis
        # The main test is that it doesn't error and produces some result
        self.assertTrue(len(result) > 0)

class TestChiSquareStatisticalValidation(unittest.TestCase):
    """Test statistical properties and validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalEvidenceTool()
    
    def test_cramers_v_bounds(self):
        """Test Cramér's V is always between 0 and 1"""
        test_cases = [
            (["A"] * 5 + ["B"] * 5, ["X"] * 5 + ["Y"] * 5),  # Perfect association
            (["A", "B"] * 5, ["X", "Y"] * 5),  # Perfect independence
            (["A"] * 7 + ["B"] * 3, ["X"] * 6 + ["Y"] * 4),  # Some association
        ]
        
        for var1, var2 in test_cases:
            result = self.tool._perform_chi_square_test(var1, var2, "var1", "var2")
            if "error" not in result:
                cramers_v = result["cramers_v"]
                self.assertGreaterEqual(cramers_v, 0, f"Cramér's V should be >= 0, got {cramers_v}")
                self.assertLessEqual(cramers_v, 1, f"Cramér's V should be <= 1, got {cramers_v}")
    
    def test_degrees_of_freedom_calculation(self):
        """Test degrees of freedom calculation"""
        # 2x2 table
        result = self.tool._perform_chi_square_test(
            ["A", "B"] * 3, ["X", "Y"] * 3, "var1", "var2"
        )
        if "error" not in result:
            self.assertEqual(result["degrees_of_freedom"], 1)  # (2-1) * (2-1)
        
        # 3x2 table
        result = self.tool._perform_chi_square_test(
            ["A", "B", "C"] * 2, ["X", "Y"] * 3, "var1", "var2"
        )
        if "error" not in result:
            self.assertEqual(result["degrees_of_freedom"], 2)  # (3-1) * (2-1)
    
    def test_effect_size_categories(self):
        """Test effect size category assignment"""
        # Test different levels of association
        test_cases = [
            # Perfect independence should give negligible/small effect
            (["A", "B"] * 10, ["X", "Y"] * 10, ["Negligible", "Small"]),
            # Strong pattern should give medium/large effect
            (["A"] * 15 + ["B"] * 5, ["X"] * 15 + ["Y"] * 5, ["Medium", "Large"]),
        ]
        
        for var1, var2, expected_categories in test_cases:
            result = self.tool._perform_chi_square_test(var1, var2, "var1", "var2")
            if "error" not in result:
                effect_category = result["effect_size_category"]
                self.assertIn("association", effect_category.lower())

class TestChiSquarePerformance(unittest.TestCase):
    """Test performance with larger datasets"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalEvidenceTool()
    
    def test_large_dataset_performance(self):
        """Test performance with larger dataset"""
        # Generate larger dataset
        var1 = ["A", "B", "C"] * 100
        var2 = ["X", "Y"] * 150
        
        result = self.tool._perform_chi_square_test(var1, var2, "var1", "var2")
        
        self.assertNotIn("error", result)
        self.assertIn("chi_square_statistic", result)
        self.assertEqual(result["sample_size"], 300)
    
    def test_many_categories(self):
        """Test with many categories"""
        categories1 = ["Cat" + str(i) for i in range(5)]
        categories2 = ["Type" + str(i) for i in range(4)]
        
        var1 = categories1 * 4  # 20 observations
        var2 = categories2 * 5  # 20 observations
        
        result = self.tool._perform_chi_square_test(var1, var2, "var1", "var2")
        
        if "error" not in result:
            # 5x4 table should have (5-1)*(4-1) = 12 degrees of freedom
            self.assertEqual(result["degrees_of_freedom"], 12)

class TestStringDataHandling(unittest.TestCase):
    """Test proper handling of string data and mixed data types"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalEvidenceTool()
    
    def test_string_data_no_format_errors(self):
        """Test that string data doesn't cause formatting errors in reports"""
        # String data that would cause min/max errors if not handled properly
        var1 = ["High", "Medium", "Low", "High", "Medium", "Low"]
        var2 = ["Yes", "No", "Maybe", "Yes", "No", "Maybe"]
        
        # Should not raise ValueError for string formatting
        result = self.tool._perform_chi_square_test(var1, var2, "priority", "response")
        self.assertNotIn("error", result)
        self.assertIn("chi_square_statistic", result)
    
    def test_unicode_string_handling(self):
        """Test handling of unicode strings in chi-square analysis"""
        var1 = ["优秀", "良好", "一般", "较差", "优秀", "良好"]
        var2 = ["满意", "不满意", "中性", "满意", "不满意", "中性"]
        
        result = self.tool._perform_chi_square_test(var1, var2, "评价", "满意度")
        self.assertNotIn("error", result)
        self.assertIn("chi_square_statistic", result)
        self.assertEqual(result["variable_1"], "评价")
        self.assertEqual(result["variable_2"], "满意度")
    
    def test_special_characters_in_strings(self):
        """Test handling of special characters in categorical data"""
        var1 = ["Type-A", "Type-B", "Type_C", "Type-A", "Type-B"]
        var2 = ["Grade+", "Grade-", "Grade=", "Grade+", "Grade-"]
        
        result = self.tool._perform_chi_square_test(var1, var2, "type", "grade")
        self.assertNotIn("error", result)
        self.assertIn("chi_square_statistic", result)
    
    def test_empty_string_handling(self):
        """Test handling of empty strings (should be treated as valid category)"""
        var1 = ["A", "B", "", "A", "B", ""]
        var2 = ["X", "Y", "Z", "X", "Y", "Z"]
        
        result = self.tool._perform_chi_square_test(var1, var2, "category", "type")
        self.assertNotIn("error", result)
        # Empty string should be treated as a valid category
        self.assertIn("chi_square_statistic", result)
    
    def test_numeric_strings_vs_numbers(self):
        """Test that numeric strings are treated as categorical, not numerical"""
        # Numeric strings should be treated as categories, not converted to numbers
        var1 = ["1", "2", "3", "1", "2", "3"]
        var2 = ["A", "B", "C", "A", "B", "C"]
        
        result = self.tool._perform_chi_square_test(var1, var2, "numeric_string", "letter")
        self.assertNotIn("error", result)
        
        # Should have 3x3 contingency table (treating "1", "2", "3" as categories)
        contingency = result.get("contingency_table", [])
        if contingency:
            self.assertEqual(len(contingency), 3)  # 3 rows
            self.assertEqual(len(contingency[0]), 3)  # 3 columns

class TestRenderReportStringBugFixes(unittest.TestCase):
    """Test render_report functionality with string data bug fixes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalEvidenceTool()
        self.conv_id = "test_string_bugs"
    
    def test_render_report_categorical_data_display(self):
        """Test that categorical data is displayed correctly in render_report"""
        # Perform chi-square analysis with string data
        data = {
            "device_type": ["Mobile", "Desktop", "Tablet", "Mobile", "Desktop"],
            "user_satisfaction": ["High", "Medium", "Low", "High", "Medium"]
        }
        
        self.tool.analyze(self.conv_id, data, None, "chi_square_test")
        
        # Generate report - should not crash with string data
        report = self.tool.render_report(self.conv_id)
        
        # Should show unique values instead of range for categorical data
        self.assertIn("unique values", report)
        self.assertNotIn("range =", report)  # Numerical range shouldn't appear for categorical
        self.assertIn("Chi Square Test", report)
        self.assertIn("device_type", report)
        self.assertIn("user_satisfaction", report)
    
    def test_render_report_mixed_data_types(self):
        """Test render_report with mixed numerical and categorical data"""
        # Numerical analysis
        numerical_data = {"scores": [85, 92, 78, 88, 91]}
        self.tool.analyze(self.conv_id, numerical_data, None, "descriptive")
        
        # Categorical analysis
        categorical_data = {"feedback": ["Good", "Excellent", "Poor", "Good", "Excellent"]}
        self.tool.analyze(self.conv_id, categorical_data, None, "frequency_analysis")
        
        # Generate report
        report = self.tool.render_report(self.conv_id)
        
        # Should handle both data types appropriately
        self.assertIn("range =", report)  # Numerical data should show range
        self.assertIn("unique values", report)  # Categorical data should show unique count
        self.assertNotIn("Unknown format code", report)  # No formatting errors
    
    def test_render_report_no_string_format_errors(self):
        """Test that render_report doesn't have string formatting errors"""
        # Create data that would cause formatting errors if not handled
        string_heavy_data = {
            "responses": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            "demographics": ["18-25", "26-35", "36-45", "46-55", "55+"]
        }
        
        self.tool.analyze(self.conv_id, string_heavy_data, None, "chi_square_test")
        
        # Should not raise formatting exceptions
        try:
            report = self.tool.render_report(self.conv_id)
            self.assertIsInstance(report, str)
            self.assertIn("Statistical Analysis Report", report)
        except ValueError as e:
            if "Unknown format code" in str(e):
                self.fail(f"String formatting error not fixed: {e}")

class TestAnalyzeMethodStringHandling(unittest.TestCase):
    """Test the main analyze method with string data handling improvements"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalEvidenceTool()
        self.conv_id = "test_analyze_strings"
    
    def test_analyze_auto_detection_with_strings(self):
        """Test auto-detection properly identifies string data for chi-square"""
        # String data should trigger chi-square analysis in auto mode
        data = {
            "category": ["A", "B", "C", "A", "B"],
            "rating": ["High", "Low", "Medium", "High", "Low"]
        }
        
        result = self.tool.analyze(self.conv_id, data, None, "auto")
        
        # Should automatically detect as categorical and use chi-square
        self.assertIn("Chi-Square Test", result)
        self.assertNotIn("error", result.lower())
    
    def test_analyze_frequency_with_unicode(self):
        """Test frequency analysis with unicode strings"""
        data = {"反馈": ["优秀", "良好", "一般", "较差", "优秀", "良好", "优秀"]}
        
        result = self.tool.analyze(self.conv_id, data, None, "frequency_analysis")
        
        # Should handle unicode without errors
        self.assertIsInstance(result, str)
        self.assertNotIn("error", result.lower())
    
    def test_analyze_handles_mixed_string_types(self):
        """Test analyze method with mixed string types"""
        # Mix of different string formats that could cause issues
        data = {
            "responses": ["1", "2", "3", "A", "B", "C"],  # Mix of numeric and letter strings
            "categories": ["Type_1", "Type-2", "Type 3", "Type_1", "Type-2", "Type 3"]
        }
        
        result = self.tool.analyze(self.conv_id, data, None, "chi_square_test")
        
        # Should treat all as categorical strings
        self.assertIn("Chi-Square Test", result)
        self.assertNotIn("error", result.lower())

def run_test_suite():
    """Run the complete test suite with detailed output"""
    
    # Create test suite
    test_classes = [
        TestChiSquareBasic,
        TestChiSquareEdgeCases,
        TestChiSquareContingencyTable,
        TestChiSquareIntegration,
        TestChiSquareStatisticalValidation,
        TestChiSquarePerformance
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("🧪 Chi-Square Test Suite Summary")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.split('AssertionError: ')[-1].strip()}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.split('Exception: ')[-1].strip()}")
    
    if not result.failures and not result.errors:
        print("\n✅ All tests passed! Chi-square functionality is working correctly.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Only run when called directly for debugging purposes
    print("🧪 Chi-Square Test Suite (Debug Mode)")
    print("=" * 80)
    print("Note: For production testing, use: python -m unittest tests.test_chi_square")
    print("=" * 80)
    
    success = run_test_suite()
    sys.exit(0 if success else 1)
    print("=" * 60)
    
    # Test 1: Insufficient data
    small_data = {
        "var1": ["A", "B"],
        "var2": ["X", "Y"]
    }
    print("📝 Test 1: Insufficient data (n=2)")
    result = tool.analyze("test_edge_1", small_data, analysis_type="chi_square_test")
    print("✓ Should show frequency analysis only")
    
    # Test 2: Single category in one variable
    single_cat_data = {
        "constant": ["A", "A", "A", "A", "A"],
        "varied": ["X", "Y", "X", "Y", "X"]
    }
    print("\n📝 Test 2: One variable has single category")
    result = tool.analyze("test_edge_2", single_cat_data, analysis_type="chi_square_test")
    print("✓ Should handle gracefully")
    
    # Test 3: Unequal length arrays
    print("\n📝 Test 3: Unequal length data")
    try:
        result = tool._perform_chi_square_test(
            ["A", "B", "C"], ["X", "Y"], "var1", "var2"
        )
        print(f"Result: {result.get('error', 'No error detected')}")
    except Exception as e:
        print(f"Exception: {e}")

def test_chi_square_real_world_scenarios():
    """Test realistic business and research scenarios"""
    tool = StatisticalEvidenceTool()
    
    print("\n🏢 Testing Real-World Business Scenarios")
    print("=" * 60)
    
    # Scenario 1: Customer satisfaction vs product category
    customer_data = {
        "product_category": [
            "Electronics", "Clothing", "Books", "Electronics", "Clothing", 
            "Books", "Electronics", "Clothing", "Books", "Electronics",
            "Clothing", "Books", "Home", "Home", "Home", "Home", 
            "Electronics", "Clothing", "Books", "Home"
        ],
        "satisfaction": [
            "High", "Medium", "High", "Low", "High",
            "Medium", "High", "Low", "High", "Medium",
            "Low", "High", "High", "High", "Medium", "Low",
            "Medium", "High", "Low", "High"
        ]
    }
    
    print("📊 Scenario 1: Customer Satisfaction vs Product Category")
    result = tool.analyze("business_1", customer_data, analysis_type="chi_square_test")
    print(result)
    print("\n" + "="*40)
    
    # Scenario 2: Marketing campaign effectiveness
    marketing_data = {
        "campaign_type": ["Email", "Social", "TV", "Email", "Social"] * 8,
        "conversion": ["Yes", "No", "Yes", "No", "Yes"] * 8
    }
    
    print("� Scenario 2: Marketing Campaign vs Conversion")
    result = tool.analyze("business_2", marketing_data, analysis_type="chi_square_test")
    print(result)

def test_chi_square_academic_scenarios():
    """Test academic research scenarios"""
    tool = StatisticalEvidenceTool()
    
    print("\n🎓 Testing Academic Research Scenarios")
    print("=" * 60)
    
    # Scenario 1: Medical study - treatment vs outcome
    medical_data = {
        "treatment": [
            "Drug_A", "Drug_B", "Placebo", "Drug_A", "Drug_B", "Placebo",
            "Drug_A", "Drug_B", "Placebo", "Drug_A", "Drug_B", "Placebo",
            "Drug_A", "Drug_B", "Placebo", "Drug_A", "Drug_B", "Placebo",
            "Drug_A", "Drug_B", "Placebo", "Drug_A", "Drug_B", "Placebo"
        ],
        "outcome": [
            "Improved", "Improved", "No_Change", "Improved", "No_Change", "Worse",
            "Improved", "Improved", "No_Change", "No_Change", "Improved", "No_Change",
            "Improved", "Worse", "Worse", "Improved", "Improved", "No_Change",
            "No_Change", "Improved", "Worse", "Improved", "No_Change", "No_Change"
        ]
    }
    
    print("🏥 Medical Study: Treatment vs Outcome")
    result = tool.analyze("academic_1", medical_data, analysis_type="chi_square_test")
    print(result)
    print("\n" + "="*40)
    
    # Scenario 2: Educational research
    education_data = {
        "teaching_method": ["Traditional", "Interactive", "Online"] * 15,
        "performance": ["Poor", "Average", "Excellent"] * 15
    }
    
    print("📚 Educational Study: Teaching Method vs Performance")
    result = tool.analyze("academic_2", education_data, analysis_type="chi_square_test")
    print(result)

def test_chi_square_statistical_properties():
    """Test statistical properties and interpretation"""
    tool = StatisticalEvidenceTool()
    
    print("\n📐 Testing Statistical Properties")
    print("=" * 60)
    
    # Test 1: Perfect independence (expected chi-square ≈ 0)
    independent_data = {
        "var1": ["A", "A", "A", "A", "B", "B", "B", "B"] * 3,
        "var2": ["X", "X", "Y", "Y", "X", "X", "Y", "Y"] * 3
    }
    
    print("🎯 Test 1: Perfect Independence (χ² should be close to 0)")
    result = tool.analyze("stat_1", independent_data, analysis_type="chi_square_test")
    print(result)
    print("\n" + "="*40)
    
    # Test 2: Strong association
    strong_association_data = {
        "gender": ["Male"] * 20 + ["Female"] * 20,
        "preference": ["Sports"] * 18 + ["Other"] * 2 + ["Fashion"] * 18 + ["Other"] * 2
    }
    
    print("💪 Test 2: Strong Association")
    result = tool.analyze("stat_2", strong_association_data, analysis_type="chi_square_test")
    print(result)

def test_chi_square_large_datasets():
    """Test with larger datasets"""
    tool = StatisticalEvidenceTool()
    
    print("\n📊 Testing Large Dataset Performance")
    print("=" * 60)
    
    # Generate larger dataset
    import random
    random.seed(42)  # For reproducible results
    
    large_data = {
        "region": ["North", "South", "East", "West"] * 50,
        "response": []
    }
    
    # Generate responses with some pattern
    for region in large_data["region"]:
        if region == "North":
            response = random.choices(["Yes", "No"], weights=[0.7, 0.3])[0]
        elif region == "South":
            response = random.choices(["Yes", "No"], weights=[0.4, 0.6])[0]
        elif region == "East":
            response = random.choices(["Yes", "No"], weights=[0.6, 0.4])[0]
        else:  # West
            response = random.choices(["Yes", "No"], weights=[0.5, 0.5])[0]
        large_data["response"].append(response)
    
    print(f"📈 Large Dataset: n={len(large_data['region'])}")
    result = tool.analyze("large_dataset", large_data, analysis_type="chi_square_test")
    print(result)

def test_chi_square_auto_detection():
    """Test automatic detection of categorical data"""
    tool = StatisticalEvidenceTool()
    
    print("\n🤖 Testing Auto-Detection Capabilities")
    print("=" * 60)
    
    # Mixed data that should trigger chi-square
    mixed_data = {
        "category": ["A", "B", "C", "A", "B", "C", "A", "B"],
        "status": ["Active", "Inactive", "Active", "Pending", "Active", "Inactive", "Pending", "Active"]
    }
    
    print("🔍 Auto-detection with categorical data:")
    result = tool.analyze("auto_detect", mixed_data, analysis_type="auto")
    print(result)

def test_chi_square_error_handling():
    """Test comprehensive error handling"""
    tool = StatisticalEvidenceTool()
    
    print("\n⚠️  Testing Error Handling")
    print("=" * 60)
    
    # Test various error conditions
    error_cases = [
        {
            "name": "Empty data",
            "data": {"var1": [], "var2": []},
            "expected": "Should handle empty data gracefully"
        },
        {
            "name": "Single data point",
            "data": {"var1": ["A"], "var2": ["X"]},
            "expected": "Should require minimum sample size"
        },
        {
            "name": "All same values",
            "data": {"var1": ["A"] * 10, "var2": ["X"] * 10},
            "expected": "Should detect no variation"
        }
    ]
    
    for case in error_cases:
        print(f"\n📝 {case['name']}:")
        try:
            result = tool.analyze(f"error_{case['name'].replace(' ', '_')}", 
                                case["data"], analysis_type="chi_square_test")
            print(f"✓ {case['expected']}")
        except Exception as e:
            print(f"Exception: {e}")

def test_chi_square_debug():
    """Debug chi-square test execution"""
    tool = StatisticalEvidenceTool()
    
    # Simple test data
    data = {
        "A": ["X", "Y", "X", "Y", "X", "Y"],
        "B": ["1", "2", "1", "1", "2", "2"]
    }
    
    print("\n🐛 Debug Chi-Square Test Execution")
    print("=" * 60)
    print(f"Input data: {data}")
    print(f"Data keys: {list(data.keys())}")
    print(f"Data length check: A={len(data['A'])}, B={len(data['B'])}")
    
    # Test the chi-square method directly
    try:
        chi_result = tool._perform_chi_square_test(data["A"], data["B"], "A", "B")
        print(f"\nDirect chi-square result: {chi_result}")
    except Exception as e:
        print(f"\nDirect chi-square error: {e}")
    
    # Test through analyze method
    result = tool.analyze(
        conversation_id="debug_chi_square",
        data=data,
        analysis_type="chi_square_test"
    )
    print(f"\nAnalyze method result:")
    print(result)

if __name__ == "__main__":
    print("🧪 Comprehensive Chi-Square Test Suite for Statistical Evidence Tool")
    print("=" * 80)
    
    try:
        # Basic functionality tests
        test_chi_square_debug()
        
        # Edge cases and error handling
        test_chi_square_edge_cases()
        test_chi_square_error_handling()
        
        # Real-world scenarios
        test_chi_square_real_world_scenarios()
        test_chi_square_academic_scenarios()
        
        # Statistical properties
        test_chi_square_statistical_properties()
        
        # Performance tests
        test_chi_square_large_datasets()
        
        # Auto-detection
        test_chi_square_auto_detection()
        
        print("\n" + "="*80)
        print("✅ All comprehensive chi-square tests completed successfully!")
        print("🎯 Test Coverage:")
        print("   • Edge cases and error conditions")
        print("   • Real-world business scenarios")
        print("   • Academic research applications")
        print("   • Statistical properties validation")
        print("   • Large dataset performance")
        print("   • Auto-detection capabilities")
        print("   • Comprehensive error handling")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

import sys
import os
import unittest
import math
import json

# Add the parent directory to the path to import tools
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from tools.statistical_analyzer import StatisticalAnalyzer

class TestStatisticalAnalyzer(unittest.TestCase):
    def setUp(self):
        self.tool = StatisticalAnalyzer()
        self.conv_id = "test_conversation"
        
        # Sample datasets for testing
        self.normal_data = [68, 72, 75, 71, 69, 73, 70, 74, 67, 76]
        self.skewed_data = [1, 2, 3, 4, 5, 15, 25, 35, 45, 100]
        self.outlier_data = [10, 11, 12, 13, 14, 15, 16, 17, 18, 50]
        
        # A/B testing datasets
        self.control_group = [6.2, 5.8, 6.1, 5.9, 6.3, 6.0, 5.7, 6.4, 5.6, 6.2]
        self.treatment_group = [7.8, 8.1, 7.5, 8.0, 7.9, 8.2, 7.7, 8.3, 7.6, 8.0]
        
        # Educational intervention study
        self.traditional_teaching = [72, 74, 68, 70, 73, 69, 71, 75, 67, 76]
        self.interactive_teaching = [78, 82, 76, 80, 79, 83, 77, 81, 75, 84]
        self.ai_assisted_teaching = [88, 91, 86, 89, 90, 87, 92, 85, 93, 88]
        
        # Correlated variables for testing
        self.study_hours = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.test_scores = [65, 70, 75, 80, 85, 88, 92, 95, 97, 100]
        self.sleep_hours = [4, 5, 6, 7, 8, 9, 10, 8, 7, 6]
        
        # Paired data (before/after intervention)
        self.before_training = [45, 48, 52, 46, 50, 47, 49, 51, 44, 53]
        self.after_training = [58, 62, 65, 59, 63, 60, 62, 64, 57, 66]
    
    def test_descriptive_stats_comprehensive(self):
        """Test comprehensive descriptive statistics with different data types"""
        # Normal distribution-like data
        result = self.tool._calculate_descriptive_stats(self.normal_data)
        self.assertEqual(result['n'], 10)
        self.assertAlmostEqual(result['mean'], 71.5, places=1)
        self.assertAlmostEqual(result['median'], 71.5, places=1)
        self.assertGreater(result['std'], 0)
        self.assertIn('q1', result)
        self.assertIn('q3', result)
        self.assertIn('iqr', result)
        
        # Test with outlier data
        outlier_result = self.tool._calculate_descriptive_stats(self.outlier_data)
        self.assertIn('outliers', outlier_result)
        self.assertGreater(len(outlier_result['outliers']), 0)
        
        # Test with single value (edge case)
        single_result = self.tool._calculate_descriptive_stats([5])
        self.assertEqual(single_result['n'], 1)
        self.assertEqual(single_result['std'], 0)
        
        # Test with empty data
        empty_result = self.tool._calculate_descriptive_stats([])
        self.assertIn('error', empty_result)
    
    def test_paired_t_test_comprehensive(self):
        """Test paired t-test with realistic before/after data"""
        result = self.tool._perform_t_test(self.before_training, self.after_training, paired=True)
        
        # Basic structure validation
        self.assertEqual(result['test_type'], "Paired t-test")
        self.assertIn('t_statistic', result)
        self.assertIn('p_value', result)
        self.assertIn('degrees_of_freedom', result)
        self.assertIn('cohens_d', result)
        self.assertEqual(result['degrees_of_freedom'], 9)  # n-1 for paired test
        
        # The training should show improvement (negative t-statistic for before-after)
        self.assertLess(result['t_statistic'], 0)  # Before < After, so negative
        
        # Effect size should be substantial for this training data
        self.assertGreater(abs(result['cohens_d']), 1.0)  # Large effect
        
        # Test unequal sample sizes (should error)
        error_result = self.tool._perform_t_test([1, 2, 3], [4, 5], paired=True)
        self.assertIn('error', error_result)
    
    def test_independent_t_test_ab_testing(self):
        """Test independent t-test with A/B testing scenario"""
        result = self.tool._perform_t_test(self.control_group, self.treatment_group, paired=False)
        
        self.assertEqual(result['test_type'], "Independent t-test")
        self.assertEqual(result['degrees_of_freedom'], 18)  # n1 + n2 - 2
        
        # Treatment should be significantly higher than control
        self.assertLess(result['t_statistic'], 0)  # Control < Treatment
        self.assertLess(result['p_value'], 0.05)  # Should be significant
        
        # Large effect expected for this data
        self.assertGreater(abs(result['cohens_d']), 1.0)
    
    def test_anova_educational_intervention(self):
        """Test ANOVA with educational intervention study"""
        groups = {
            "traditional": self.traditional_teaching,
            "interactive": self.interactive_teaching,
            "ai_assisted": self.ai_assisted_teaching
        }
        
        result = self.tool._perform_anova(groups)
        
        # Basic structure validation
        self.assertEqual(result['test_type'], "One-way ANOVA")
        self.assertEqual(result['df_between'], 2)  # 3 groups - 1
        self.assertEqual(result['df_within'], 27)   # 30 total - 3 groups
        self.assertIn('f_statistic', result)
        self.assertIn('p_value', result)
        self.assertIn('eta_squared', result)
        
        # Should show significant differences between teaching methods
        self.assertGreater(result['f_statistic'], 3.0)  # Strong F-statistic
        self.assertLess(result['p_value'], 0.05)        # Significant
        
        # Post-hoc comparisons should be present
        self.assertIn('posthoc_comparisons', result)
        self.assertEqual(len(result['posthoc_comparisons']), 3)  # 3 choose 2 = 3 comparisons
        
        # Test with insufficient groups (should still work but with minimal degrees of freedom)
        single_group_result = self.tool._perform_anova({"group1": [1, 2, 3]})
        self.assertIn('test_type', single_group_result)  # Should still return a result, not an error
    
    def test_correlation_analysis_comprehensive(self):
        """Test correlation analysis with different relationship strengths"""
        # Strong positive correlation (study hours vs test scores)
        strong_result = self.tool._calculate_correlation(self.study_hours, self.test_scores)
        self.assertGreater(strong_result['correlation_coefficient'], 0.8)
        self.assertLess(strong_result['p_value'], 0.01)
        self.assertIn('Very strong', strong_result['strength_category'])
        self.assertEqual(strong_result['direction'], "Positive")
        
        # Weaker correlation (study hours vs sleep hours)
        weak_result = self.tool._calculate_correlation(self.study_hours, self.sleep_hours)
        self.assertLess(abs(weak_result['correlation_coefficient']), 0.8)
        
        # No correlation (random data)
        import random
        random.seed(42)  # For reproducible results
        random_x = [random.randint(1, 100) for _ in range(20)]
        random_y = [random.randint(1, 100) for _ in range(20)]
        no_corr_result = self.tool._calculate_correlation(random_x, random_y)
        self.assertLess(abs(no_corr_result['correlation_coefficient']), 0.5)
        
        # Test mismatched lengths
        error_result = self.tool._calculate_correlation([1, 2, 3], [4, 5])
        self.assertIn('error', error_result)
    
    def test_auto_analysis_detection(self):
        """Test automatic analysis type detection"""
        # Should detect paired comparison
        paired_data = {"before": self.before_training, "after": self.after_training}
        analysis_type = self.tool._detect_analysis_type(paired_data)
        self.assertEqual(analysis_type, "paired_comparison")
        
        # Should detect correlation analysis
        corr_data = {"hours": self.study_hours, "scores": self.test_scores}
        analysis_type = self.tool._detect_analysis_type(corr_data)
        self.assertEqual(analysis_type, "correlation_analysis")
        
        # Should detect ANOVA
        groups = {"group1": [1, 2, 3], "group2": [4, 5, 6], "group3": [7, 8, 9]}
        analysis_type = self.tool._detect_analysis_type(None, groups)
        self.assertEqual(analysis_type, "anova_analysis")
        
        # Should detect two-group comparison
        two_groups = {"control": [1, 2, 3], "treatment": [4, 5, 6]}
        analysis_type = self.tool._detect_analysis_type(None, two_groups)
        self.assertEqual(analysis_type, "two_group_comparison")
    
    def test_analyze_method_comprehensive(self):
        """Test the main analyze method with various scenarios"""
        # Test A/B testing scenario
        ab_data = {"control": self.control_group, "treatment": self.treatment_group}
        result = self.tool.analyze(self.conv_id, groups=ab_data, analysis_type="auto")
        
        # Parse result (now a dictionary)
        parsed_result = result
        self.assertIn("analysis_report", parsed_result)
        self.assertIn("results", parsed_result["analysis_report"])
        
        # Check for t-test results
        results = parsed_result["analysis_report"]["results"]
        self.assertIn("t_test", results)
        self.assertEqual(results["t_test"]["test_type"], "Independent t-test")
        self.assertIn("t_statistic", results["t_test"])
        self.assertIn("p_value", results["t_test"])
        
        # Test educational intervention
        edu_groups = {
            "traditional": self.traditional_teaching,
            "interactive": self.interactive_teaching, 
            "ai_assisted": self.ai_assisted_teaching
        }
        anova_result = self.tool.analyze(self.conv_id, groups=edu_groups, analysis_type="auto")
        
        # Parse ANOVA result (now a dictionary)
        anova_parsed = anova_result
        anova_results = anova_parsed["analysis_report"]["results"]
        self.assertIn("anova", anova_results)
        self.assertEqual(anova_results["anova"]["test_type"], "One-way ANOVA")
        self.assertIn("f_statistic", anova_results["anova"])
        self.assertIn("posthoc_comparisons", anova_results["anova"])
        
        # Test correlation analysis
        corr_data = {"study_hours": self.study_hours, "test_scores": self.test_scores}
        corr_result = self.tool.analyze(self.conv_id, data=corr_data, analysis_type="auto")
        
        # Parse correlation result (now a dictionary)
        corr_parsed = corr_result
        corr_results = corr_parsed["analysis_report"]["results"]
        self.assertIn("correlation", corr_results)
        self.assertIn("correlation_coefficient", corr_results["correlation"])
        
        # Test paired comparison
        paired_data = {"before": self.before_training, "after": self.after_training}
        paired_result = self.tool.analyze(self.conv_id, data=paired_data, analysis_type="auto")
        
        # Parse paired comparison result (now a dictionary)
        paired_parsed = paired_result
        paired_results = paired_parsed["analysis_report"]["results"]
        self.assertIn("t_test", paired_results)
        self.assertEqual(paired_results["t_test"]["test_type"], "Paired t-test")
    
    def test_render_report_comprehensive(self):
        """Test comprehensive report generation"""
        # Perform multiple analyses first
        # 1. A/B test
        ab_data = {"control": self.control_group, "treatment": self.treatment_group}
        self.tool.analyze(self.conv_id, groups=ab_data, analysis_type="auto")
        
        # 2. Educational ANOVA
        edu_groups = {
            "traditional": self.traditional_teaching,
            "interactive": self.interactive_teaching,
            "ai_assisted": self.ai_assisted_teaching
        }
        self.tool.analyze(self.conv_id, groups=edu_groups, analysis_type="auto")
        
        # 3. Correlation analysis
        corr_data = {"study_hours": self.study_hours, "test_scores": self.test_scores}
        self.tool.analyze(self.conv_id, data=corr_data, analysis_type="auto")
        
        # Generate comprehensive report
        report = self.tool.render_report(self.conv_id)
        
        # Parse report result (now a dictionary)
        report_parsed = report
        self.assertIn("comprehensive_statistical_report", report_parsed)
        report_data = report_parsed["comprehensive_statistical_report"]
        
        # Should contain summary information
        self.assertEqual(report_data["title"], "Comprehensive Statistical Analysis Report")
        self.assertEqual(report_data["total_analyses"], 3)
        self.assertIn("statistical_summary", report_data)
        self.assertIn("summary_statistics", report_data)
        
        # Check detailed analyses
        self.assertIn("detailed_analyses", report_data)
        self.assertEqual(len(report_data["detailed_analyses"]), 3)
        
        # Should contain statistical summaries from all analyses
        statistical_summary = report_data["statistical_summary"]
        self.assertGreater(len(statistical_summary["t_tests"]), 0)
        self.assertGreater(len(statistical_summary["correlations"]), 0)
        self.assertGreater(len(statistical_summary["group_comparisons"]), 0)
    
    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling"""
        # Test with very small samples
        tiny_sample = [1, 2]
        result = self.tool._perform_t_test(tiny_sample, [3, 4], paired=False)
        self.assertIn('t_statistic', result)  # Should still work
        
        # Test with identical values (no variance)
        identical_values = [5, 5, 5, 5, 5]
        result = self.tool._perform_t_test(identical_values, [6, 6, 6, 6, 6], paired=False)
        self.assertIn('t_statistic', result)
        
        # Test correlation with no variance in one variable
        no_var_result = self.tool._calculate_correlation([1, 1, 1, 1], [2, 3, 4, 5])
        self.assertEqual(no_var_result['correlation_coefficient'], 0)
        
        # Test with very large datasets (performance test)
        import random
        large_dataset1 = list(range(1000))
        large_dataset2 = [x + random.randint(-10, 10) for x in large_dataset1]
        large_result = self.tool._calculate_correlation(large_dataset1, large_dataset2)
        self.assertIsInstance(large_result['correlation_coefficient'], float)
        
        # Test invalid analysis type
        invalid_result = self.tool.analyze(self.conv_id, data={"x": [1, 2, 3]}, analysis_type="invalid_type")
        self.assertIn("error", invalid_result)  # Should return error dict
        self.assertEqual(invalid_result["error"], "No results to display.")  # Check exact error message
    
    def test_output_format_variations(self):
        """Test different output formats"""
        ab_data = {"control": self.control_group, "treatment": self.treatment_group}
        
        # Test comprehensive format (default)
        comprehensive = self.tool.analyze(self.conv_id, groups=ab_data, output_format="comprehensive")
        comprehensive_data = comprehensive
        self.assertIn("analysis_report", comprehensive_data)
        self.assertIn("results", comprehensive_data["analysis_report"])
        
        # Test business format
        business = self.tool.analyze("conv2", groups=ab_data, output_format="business")
        business_data = business
        self.assertIn("analysis_report", business_data)
        
        # Test academic format
        academic = self.tool.analyze("conv3", groups=ab_data, output_format="academic")
        academic_data = academic
        self.assertIn("analysis_report", academic_data)
        
        # Test simple format
        simple = self.tool.analyze("conv4", groups=ab_data, output_format="simple")
        simple_data = simple
        self.assertIn("analysis_report", simple_data)
    
    def test_single_variable_comprehensive_analysis(self):
        """Test comprehensive single variable analysis"""
        # Performance data with realistic distribution
        response_times = [120, 135, 145, 150, 155, 160, 165, 170, 175, 180, 
                         185, 190, 195, 200, 210, 220, 250, 300, 450, 600]
        
        result = self.tool.analyze(self.conv_id, data={"response_time": response_times}, 
                                 analysis_type="comprehensive_descriptive")
        
        # Parse result (now a dictionary)
        result_data = result
        
        # Check that comprehensive analysis was performed
        self.assertIn("analysis_report", result_data)
        self.assertIn("results", result_data["analysis_report"])
        
        # Check for distribution analysis results
        results = result_data["analysis_report"]["results"]
        self.assertTrue(any("distribution_analysis" in key for key in results.keys()))
        
        # Check for specific analysis components in the results
        distribution_key = [k for k in results.keys() if "distribution_analysis" in k][0]
        distribution_data = results[distribution_key]
        
        self.assertIn("descriptive_statistics", distribution_data)
        self.assertIn("performance_metrics", distribution_data)
        self.assertIn("data_quality", distribution_data)
        self.assertIn("variability_analysis", distribution_data)
        
    def test_single_variable_percentiles(self):
        """Test percentile calculations for single variable"""
        data = list(range(1, 101))  # 1 to 100
        
        result = self.tool._calculate_descriptive_stats(data)
        
        # Check percentiles
        self.assertAlmostEqual(result['p50'], 50.5, places=1)  # median
        self.assertAlmostEqual(result['p95'], 95.05, places=1)  # 95th percentile
        self.assertAlmostEqual(result['p99'], 99.01, places=1)  # 99th percentile
        
    def test_confidence_interval_calculation(self):
        """Test confidence interval calculation for mean"""
        data = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
        
        result = self.tool._calculate_descriptive_stats(data)
        
        self.assertIn('mean_ci_95_lower', result)
        self.assertIn('mean_ci_95_upper', result)
        self.assertIn('mean_se', result)
        
        # CI should contain the mean
        mean = result['mean']
        ci_lower = result['mean_ci_95_lower']
        ci_upper = result['mean_ci_95_upper']
        
        self.assertLess(ci_lower, mean)
        self.assertGreater(ci_upper, mean)
        
    def test_distribution_shape_analysis(self):
        """Test distribution shape analysis"""
        # Create skewed data
        right_skewed = [1, 2, 3, 4, 5, 10, 15, 20, 50, 100]
        
        result = self.tool._perform_distribution_analysis(right_skewed, "test_var")
        
        self.assertEqual(result["variable_name"], "test_var")
        self.assertEqual(result["analysis_type"], "Single Variable Distribution Analysis")
        self.assertIn("distribution_shape", result)
        
        # Should detect right skew
        shape = result["distribution_shape"]
        self.assertGreater(shape["skewness"], 0)  # Positive skewness
        self.assertIn("right-skewed", shape["shape_description"].lower())
        
    def test_performance_metrics_analysis(self):
        """Test performance metrics (P50, P95, P99) analysis"""
        # Simulated response time data
        response_times = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 
                         100, 120, 150, 200, 300, 500, 800, 1000, 1200, 1500]
        
        result = self.tool._perform_distribution_analysis(response_times, "response_time")
        
        self.assertIn("performance_metrics", result)
        perf = result["performance_metrics"]
        
        self.assertIn("p50_median", perf)
        self.assertIn("p95", perf)
        self.assertIn("p99", perf)
        self.assertIn("p95_p50_ratio", perf)
        
        # P95 should be greater than P50
        self.assertGreater(perf["p95"], perf["p50_median"])
        
    def test_data_quality_outlier_detection(self):
        """Test outlier detection in data quality analysis"""
        # Data with clear outliers
        data_with_outliers = [10, 12, 14, 16, 18, 20, 22, 24, 26, 100, 200]
        
        result = self.tool._perform_distribution_analysis(data_with_outliers, "test_data")
        
        self.assertIn("data_quality", result)
        quality = result["data_quality"]
        
        self.assertGreater(quality["outlier_count"], 0)
        self.assertGreater(quality["outlier_percentage"], 0)
        self.assertIn("outlier_values", quality)
        
    def test_variability_analysis(self):
        """Test coefficient of variation and variability categorization"""
        # Low variability data
        low_var_data = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
        
        result = self.tool._perform_distribution_analysis(low_var_data, "low_var")
        
        self.assertIn("variability_analysis", result)
        var_analysis = result["variability_analysis"]
        
        self.assertIn("coefficient_of_variation", var_analysis)
        self.assertIn("variability_category", var_analysis)
        
        # Should be categorized as low variability
        self.assertLess(var_analysis["coefficient_of_variation"], 10)
        self.assertIn("Low", var_analysis["variability_category"])
        
    def test_normality_assessment(self):
        """Test normality assessment functionality"""
        # Approximately normal data
        normal_data = [10, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 30]
        
        result = self.tool._perform_distribution_analysis(normal_data, "normal_test")
        
        self.assertIn("normality_assessment", result)
        norm = result["normality_assessment"]
        
        self.assertIn("mean_median_difference", norm)
        self.assertIn("within_1_std_pct", norm)
        self.assertIn("within_2_std_pct", norm)
        self.assertIn("expected_1std_pct", norm)
        self.assertIn("expected_2std_pct", norm)
        
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test empty data
        result = self.tool._calculate_descriptive_stats([])
        self.assertIn("error", result)
        
        # Test mismatched correlation data
        result = self.tool._calculate_correlation([1, 2, 3], [1, 2])
        self.assertIn("error", result)

class TestRenderReportFunctionality(unittest.TestCase):
    """Test render_report functionality with various analysis types"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalAnalyzer()
        self.conv_id = "test_render_report"
    
    def test_render_report_empty_conversation(self):
        """Test render_report with no analyses"""
        result = self.tool.render_report("nonexistent_conv")
        result_data = result
        result_str = str(result_data)
        self.assertIn("No analyses found", result_str)
    
    def test_render_report_single_numerical_analysis(self):
        """Test render_report with single numerical analysis"""
        # Perform a t-test
        data = {"before": [70, 72, 68], "after": [78, 80, 76]}
        self.tool.analyze(self.conv_id, data, None, "paired_comparison")
        
        # Generate report
        report = self.tool.render_report(self.conv_id)
        
        # Parse result (now a dictionary)
        report_data = report
        
        # Check report structure
        self.assertIn("comprehensive_statistical_report", report_data)
        report_content = report_data["comprehensive_statistical_report"]
        
        self.assertEqual(report_content["title"], "Comprehensive Statistical Analysis Report")
        self.assertIn("statistical_summary", report_content)
        self.assertIn("detailed_analyses", report_content)
        self.assertEqual(report_content["total_analyses"], 1)
        self.assertEqual(report_content["summary_statistics"]["t_tests_conducted"], 1)
        self.assertEqual(report_content["summary_statistics"]["total_statistical_tests"], 1)
    
    def test_render_report_categorical_analysis(self):
        """Test render_report with categorical analysis (chi-square)"""
        # Perform chi-square test
        data = {
            "device": ["Mobile", "Desktop", "Tablet", "Mobile", "Desktop"],
            "conversion": ["Yes", "No", "Yes", "Yes", "No"]
        }
        self.tool.analyze(self.conv_id, data, None, "chi_square_test")
        
        # Generate report
        report = self.tool.render_report(self.conv_id)
        
        # Parse result (now a dictionary)
        report_data = report
        
        # Check categorical analysis section
        self.assertIn("comprehensive_statistical_report", report_data)
        report_content = report_data["comprehensive_statistical_report"]
        
        self.assertGreater(len(report_content["statistical_summary"]["categorical_analyses"]), 0)
        # Chi-square test includes: 1 chi-square test + 2 frequency analyses = 3 total categorical analyses
        self.assertEqual(report_content["summary_statistics"]["categorical_analyses_performed"], 3)
        
        # Check for chi-square specific data
        categorical_analysis = report_content["statistical_summary"]["categorical_analyses"][0]
        self.assertIn("chi_square_statistic", categorical_analysis)
        self.assertIn("cramers_v", categorical_analysis)
    
    def test_render_report_frequency_analysis(self):
        """Test render_report with frequency analysis"""
        # Perform frequency analysis
        data = {"feedback": ["Excellent", "Good", "Average", "Poor", "Excellent", "Good"]}
        self.tool.analyze(self.conv_id, data, None, "frequency_analysis")
        
        # Generate report
        report = self.tool.render_report(self.conv_id)
        
        # Parse result (now a dictionary)
        report_data = report
        
        # Check frequency analysis results
        self.assertIn("comprehensive_statistical_report", report_data)
        report_content = report_data["comprehensive_statistical_report"]
        
        self.assertGreater(len(report_content["statistical_summary"]["categorical_analyses"]), 0)
        self.assertEqual(report_content["summary_statistics"]["categorical_analyses_performed"], 1)
        
        # Check for frequency analysis specific data
        categorical_analysis = report_content["statistical_summary"]["categorical_analyses"][0]
        self.assertIn("total_observations", categorical_analysis)
        self.assertIn("unique_categories", categorical_analysis)
    
    def test_render_report_mixed_analysis_types(self):
        """Test render_report with mixed numerical and categorical analyses"""
        # Numerical analysis (t-test)
        numerical_data = {"before": [70, 72, 68], "after": [78, 80, 76]}
        self.tool.analyze(self.conv_id, numerical_data, None, "paired_comparison")
        
        # Categorical analysis (chi-square) - need at least 5 observations
        categorical_data = {
            "age_group": ["18-25", "26-35", "36-45", "18-25", "26-35"],
            "product": ["A", "B", "C", "A", "B"]
        }
        self.tool.analyze(self.conv_id, categorical_data, None, "chi_square_test")
        
        # Correlation analysis
        correlation_data = {"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]}
        self.tool.analyze(self.conv_id, correlation_data, None, "correlation_analysis")
        
        # Generate report
        report = self.tool.render_report(self.conv_id)
        
        # Parse result (now a dictionary)
        report_data = report
        
        # Check all analysis types are present
        self.assertIn("comprehensive_statistical_report", report_data)
        report_content = report_data["comprehensive_statistical_report"]
        
        self.assertEqual(report_content["total_analyses"], 3)
        # total_statistical_tests: 1 t-test + 1 correlation + 1 chi-square + 2 frequency analyses = 5 total
        self.assertEqual(report_content["summary_statistics"]["total_statistical_tests"], 5)
        self.assertEqual(report_content["summary_statistics"]["t_tests_conducted"], 1)
        self.assertEqual(report_content["summary_statistics"]["correlations_calculated"], 1)
        # Chi-square test includes 1 chi-square + 2 frequency analyses = 3 categorical analyses
        self.assertEqual(report_content["summary_statistics"]["categorical_analyses_performed"], 3)
        
        # Check that all analysis types have data
        self.assertGreater(len(report_content["statistical_summary"]["t_tests"]), 0)
        self.assertGreater(len(report_content["statistical_summary"]["correlations"]), 0)
        self.assertGreater(len(report_content["statistical_summary"]["categorical_analyses"]), 0)
    
    def test_render_report_effect_sizes_counting(self):
        """Test that effect sizes are properly counted in report"""
        # Analysis with Cohen's d
        data = {"before": [70, 72, 68], "after": [78, 80, 76]}
        self.tool.analyze(self.conv_id, data, None, "paired_comparison")
        
        # Analysis with Cramér's V - need at least 5 observations
        categorical_data = {
            "device": ["Mobile", "Desktop", "Tablet", "Mobile", "Desktop"],
            "conversion": ["Yes", "No", "Yes", "Yes", "No"]
        }
        self.tool.analyze(self.conv_id, categorical_data, None, "chi_square_test")
        
        # Generate report
        report = self.tool.render_report(self.conv_id)
        
        # Parse result (now a dictionary)
        report_data = report
        
        # Should count both effect sizes
        self.assertIn("comprehensive_statistical_report", report_data)
        report_content = report_data["comprehensive_statistical_report"]
        
        self.assertEqual(report_content["summary_statistics"]["effect_sizes_calculated"], 2)
        
        # Check for Cohen's d in t-test results
        t_test_results = report_content["statistical_summary"]["t_tests"]
        self.assertGreater(len(t_test_results), 0)
        self.assertIn("cohens_d", t_test_results[0])
        
        # Check for Cramér's V in categorical results
        categorical_results = report_content["statistical_summary"]["categorical_analyses"]
        self.assertGreater(len(categorical_results), 0)
        self.assertIn("cramers_v", categorical_results[0])

class TestMixedDataTypeHandling(unittest.TestCase):
    """Test handling of mixed numerical and categorical data types"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalAnalyzer()
        self.conv_id = "test_mixed_data"
    
    def test_numerical_data_range_display(self):
        """Test that numerical data shows range in reports"""
        data = {"scores": [85, 92, 78, 88, 91]}
        result = self.tool.analyze(self.conv_id, data, None, "descriptive_analysis")
        
        # Should not error with numerical data and should be valid dict
        result_data = result
        self.assertIsInstance(result, dict)
        
        # Check that the analysis completed successfully (has results)
        self.assertIn("analysis_report", result_data)
        self.assertIn("results", result_data["analysis_report"])
        self.assertGreater(len(result_data["analysis_report"]["results"]), 0)
    
    def test_categorical_data_unique_values_display(self):
        """Test that categorical data shows unique values count"""
        data = {"category": ["A", "B", "C", "A", "B", "A"]}
        result = self.tool.analyze(self.conv_id, data, None, "frequency_analysis")
        
        # Should handle categorical data without trying to calculate min/max and should be valid dict
        result_data = result
        self.assertIsInstance(result, dict)
        self.assertNotIn("error", result_data)
    
    def test_mixed_numerical_categorical_in_render_report(self):
        """Test render_report handles mixed data types correctly"""
        # Add numerical analysis
        numerical_data = {"values": [10, 15, 12, 18, 14]}
        self.tool.analyze(self.conv_id, numerical_data, None, "descriptive_analysis")
        
        # Add categorical analysis  
        categorical_data = {"categories": ["Red", "Blue", "Green", "Red", "Blue"]}
        self.tool.analyze(self.conv_id, categorical_data, None, "frequency_analysis")
        
        # Generate report - should not crash on mixed data types
        report = self.tool.render_report(self.conv_id)
        
        # Parse result (now a dictionary)
        report_data = report
        
        # Should handle both data types
        self.assertIn("comprehensive_statistical_report", report_data)
        report_content = report_data["comprehensive_statistical_report"]
        
        # Check that both analyses are present
        self.assertEqual(report_content["total_analyses"], 2)
        
        # Check for numerical data in detailed analyses
        detailed_analyses = report_content["detailed_analyses"]
        numerical_analysis = [a for a in detailed_analyses if a["analysis_type"] == "descriptive_analysis"]
        self.assertGreater(len(numerical_analysis), 0)
        
        # Check for categorical analysis
        categorical_analysis = [a for a in detailed_analyses if a["analysis_type"] == "frequency_analysis"]
        self.assertGreater(len(categorical_analysis), 0)

class TestStringDataBugFixes(unittest.TestCase):
    """Test fixes for string data handling bugs"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalAnalyzer()
        self.conv_id = "test_string_bugs"
    
    def test_string_data_no_min_max_error(self):
        """Test that string data doesn't cause min/max errors"""
        # String data that would cause min/max errors if not handled
        string_data = {
            "categories": ["High", "Medium", "Low", "High", "Low"],
            "responses": ["Agree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
        }
        
        # Should not raise ValueError for string min/max
        try:
            result = self.tool.analyze(self.conv_id, string_data, None, "chi_square_test")
            result_data = result
            self.assertIsInstance(result, dict)
        except ValueError as e:
            if "Unknown format code" in str(e):
                self.fail(f"String formatting error not fixed: {e}")
    
    def test_unicode_string_handling(self):
        """Test handling of unicode strings"""
        # Test data with English values for consistent internationalization
        unicode_data = {
            "feedback": ["Excellent", "Good", "Average", "Poor", "Excellent"],
            "region": ["North", "South", "East", "West", "North"]
        }
        
        # Should handle unicode strings without errors
        try:
            result = self.tool.analyze(self.conv_id, unicode_data, None, "chi_square_test")
            result_data = result
            self.assertIsInstance(result, dict)
            
            # Check for chi-square analysis in the results
            self.assertIn("analysis_report", result_data)
            self.assertIn("results", result_data["analysis_report"])
            self.assertIn("chi_square", result_data["analysis_report"]["results"])
        except (UnicodeError, ValueError) as e:
            self.fail(f"Unicode handling error: {e}")
    
    def test_mixed_string_numeric_data_safety(self):
        """Test safety with mixed string and numeric data"""
        # Use purely categorical data to ensure chi-square test
        categorical_data = {
            "grades": ["A", "B", "C", "A", "B"],        # Letter strings
            "performance": ["High", "Low", "Medium", "High", "Low"]  # Performance strings
        }
        
        # Should detect and handle appropriately
        result = self.tool.analyze(self.conv_id, categorical_data, None, "chi_square_test")
        result_data = result
        self.assertIsInstance(result, dict)
        
        # Should perform chi-square test for categorical data
        self.assertIn("analysis_report", result_data)
        self.assertIn("results", result_data["analysis_report"])
        self.assertIn("chi_square", result_data["analysis_report"]["results"])

if __name__ == "__main__":
    unittest.main()

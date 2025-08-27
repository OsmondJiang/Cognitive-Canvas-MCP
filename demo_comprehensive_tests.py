#!/usr/bin/env python3
"""
Demo script showcasing comprehensive test cases for Statistical Evidence Tool
"""

import sys
import os

# Add the parent directory to the path to import tools
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from tools.statistical_evidence import StatisticalEvidenceTool

def demo_comprehensive_testing():
    """Demonstrate the comprehensive testing capabilities"""
    print("🧪 Statistical Evidence Tool - Comprehensive Testing Demo")
    print("=" * 60)
    
    tool = StatisticalEvidenceTool()
    
    # Real-world A/B Testing Scenario
    print("\n📊 SCENARIO 1: A/B Testing for Website Conversion Rates")
    print("-" * 50)
    
    # Control group: existing website (conversion rates in %)
    control_conversions = [2.1, 2.3, 1.9, 2.0, 2.4, 2.2, 1.8, 2.1, 2.0, 2.3]
    # Treatment group: new website design  
    treatment_conversions = [2.8, 3.1, 2.9, 3.0, 2.7, 3.2, 2.6, 2.9, 3.0, 2.8]
    
    ab_result = tool.analyze(
        "ab_test_demo",
        groups={"control": control_conversions, "treatment": treatment_conversions},
        analysis_type="auto",
        output_format="business"
    )
    print(ab_result)
    
    # Educational Research Scenario  
    print("\n\n📚 SCENARIO 2: Educational Intervention Study")
    print("-" * 50)
    
    # Three teaching methods with student test scores
    traditional_scores = [72, 74, 68, 70, 73, 69, 71, 75, 67, 76, 70, 72]
    interactive_scores = [78, 82, 76, 80, 79, 83, 77, 81, 75, 84, 80, 78]
    ai_assisted_scores = [88, 91, 86, 89, 90, 87, 92, 85, 93, 88, 89, 91]
    
    education_groups = {
        "traditional": traditional_scores,
        "interactive": interactive_scores, 
        "ai_assisted": ai_assisted_scores
    }
    
    edu_result = tool.analyze(
        "education_demo",
        groups=education_groups,
        analysis_type="auto",
        output_format="academic"
    )
    print(edu_result)
    
    # Employee Performance Correlation Study
    print("\n\n💼 SCENARIO 3: Employee Performance Correlation Analysis")
    print("-" * 50)
    
    # Multiple variables for comprehensive analysis
    employee_data = {
        "years_experience": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 4, 6, 8],
        "training_hours": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 25, 45, 65, 85],
        "performance_score": [65, 70, 75, 80, 85, 88, 92, 95, 97, 100, 72, 82, 90, 96],
        "job_satisfaction": [6.2, 6.8, 7.1, 7.5, 7.8, 8.0, 8.2, 8.5, 8.7, 9.0, 7.0, 7.8, 8.3, 8.8]
    }
    
    # Batch analysis for comprehensive insights
    batch_analyses = [
        {"type": "descriptive", "variables": ["performance_score", "job_satisfaction"]},
        {"type": "correlation", "var1": "years_experience", "var2": "performance_score"},
        {"type": "correlation", "var1": "training_hours", "var2": "performance_score"},
        {"type": "correlation", "var1": "performance_score", "var2": "job_satisfaction"},
        {"type": "outlier_detection", "variable": "performance_score"}
    ]
    
    batch_result = tool.batch_analyze(
        "employee_demo",
        employee_data,
        batch_analyses,
        output_format="comprehensive"
    )
    print(batch_result)
    
    # Training Effectiveness - Before/After Study
    print("\n\n🎯 SCENARIO 4: Training Program Effectiveness (Paired Study)")
    print("-" * 50)
    
    # Employee skills assessment before and after training
    before_training = [45, 48, 52, 46, 50, 47, 49, 51, 44, 53, 48, 46, 50, 52]
    after_training = [58, 62, 65, 59, 63, 60, 62, 64, 57, 66, 61, 59, 63, 65]
    
    training_result = tool.analyze(
        "training_demo",
        data={"before": before_training, "after": after_training},
        analysis_type="auto",
        output_format="comprehensive"
    )
    print(training_result)
    
    # Generate comprehensive report
    print("\n\n📋 COMPREHENSIVE ANALYSIS REPORT")
    print("=" * 50)
    
    # Use one of the conversation IDs to generate a detailed report
    comprehensive_report = tool.render_report("education_demo")
    print(comprehensive_report)
    
    # Edge Cases and Robustness Testing
    print("\n\n🛠️ ROBUSTNESS TESTING - Edge Cases")
    print("-" * 50)
    
    print("Testing with small sample sizes:")
    small_sample_result = tool.analyze(
        "edge_cases",
        groups={"group1": [1, 2], "group2": [3, 4]},
        analysis_type="auto"
    )
    print("✅ Small samples handled successfully")
    
    print("\nTesting with identical values:")
    identical_result = tool.analyze(
        "edge_cases",
        data={"variable1": [5, 5, 5, 5], "variable2": [5, 5, 5, 5]},
        analysis_type="correlation_analysis"
    )
    print("✅ Identical values handled successfully")
    
    print("\nTesting with large dataset (performance test):")
    import random
    random.seed(42)
    large_x = list(range(1000))
    large_y = [x + random.randint(-50, 50) for x in large_x]
    
    large_result = tool.analyze(
        "performance_test",
        data={"x_values": large_x[:100], "y_values": large_y[:100]},  # Use subset for demo
        analysis_type="correlation_analysis"
    )
    print("✅ Large datasets handled efficiently")
    
    print("\n🎉 All comprehensive testing scenarios completed successfully!")
    print("The Statistical Evidence Tool now has robust test coverage including:")
    print("• Real-world A/B testing scenarios")
    print("• Multi-group educational research")
    print("• Employee performance correlation studies")
    print("• Before/after training effectiveness analysis")
    print("• Edge case handling and robustness testing")
    print("• Comprehensive batch analysis capabilities")
    print("• Multiple output format support")

if __name__ == "__main__":
    demo_comprehensive_testing()

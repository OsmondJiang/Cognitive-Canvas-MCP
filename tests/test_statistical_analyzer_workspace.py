#!/usr/bin/env python3

import unittest
from tools.statistical_analyzer import StatisticalAnalyzer

class TestStatisticalAnalyzerWorkspace(unittest.TestCase):
    """Test workspace functionality for StatisticalAnalyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = StatisticalAnalyzer()
        self.conv_id = "test_workspace_conv"
        
        # Sample data for testing
        self.numerical_data = {"scores": [85, 90, 78, 92, 88, 76, 94]}
        self.categorical_data = {"category": ["A", "B", "A", "C", "B", "A", "C"]}
        self.paired_data = {"before": [70, 72, 68], "after": [78, 80, 76]}
        self.groups_data = {
            "control": [75, 78, 82, 79, 85],
            "treatment": [88, 92, 86, 94, 90]
        }

    def test_auto_workspace_creation(self):
        """Test that workspaces are auto-created on first analysis"""
        workspace_id = "analysis_workspace_1"
        
        # Perform analysis - should auto-create workspace
        result = self.tool.analyze(self.conv_id, workspace_id, data=self.numerical_data, analysis_type="descriptive_analysis")
        
        # Verify workspace was created and analysis succeeded
        self.assertIn("analysis_report", result)
        self.assertIn(self.conv_id, self.tool.conversations)
        self.assertIn("workspaces", self.tool.conversations[self.conv_id])
        self.assertIn(workspace_id, self.tool.conversations[self.conv_id]["workspaces"])
        self.assertIn("analyses", self.tool.conversations[self.conv_id]["workspaces"][workspace_id])
        
        # Check that analysis was stored in correct workspace
        analyses = self.tool.conversations[self.conv_id]["workspaces"][workspace_id]["analyses"]
        self.assertEqual(len(analyses), 1)
        self.assertEqual(analyses[0]["workspace_id"], workspace_id)

    def test_workspace_isolation(self):
        """Test that analyses are isolated between workspaces"""
        workspace_a = "workspace_a"
        workspace_b = "workspace_b"
        
        # Perform different analyses in different workspaces
        result_a = self.tool.analyze(self.conv_id, workspace_a, data=self.numerical_data, analysis_type="descriptive_analysis")
        result_b = self.tool.analyze(self.conv_id, workspace_b, data=self.categorical_data, analysis_type="frequency_analysis")
        
        # Verify both analyses succeeded
        self.assertIn("analysis_report", result_a)
        self.assertIn("analysis_report", result_b)
        
        # Verify workspaces are isolated
        workspace_a_analyses = self.tool.conversations[self.conv_id]["workspaces"][workspace_a]["analyses"]
        workspace_b_analyses = self.tool.conversations[self.conv_id]["workspaces"][workspace_b]["analyses"]
        
        self.assertEqual(len(workspace_a_analyses), 1)
        self.assertEqual(len(workspace_b_analyses), 1)
        
        # Verify analysis types are different
        self.assertEqual(workspace_a_analyses[0]["analysis_type"], "descriptive_analysis")
        self.assertEqual(workspace_b_analyses[0]["analysis_type"], "frequency_analysis")
        
        # Verify workspace IDs are correctly stored
        self.assertEqual(workspace_a_analyses[0]["workspace_id"], workspace_a)
        self.assertEqual(workspace_b_analyses[0]["workspace_id"], workspace_b)

    def test_multiple_analyses_same_workspace(self):
        """Test multiple analyses within the same workspace"""
        workspace_id = "multi_analysis_workspace"
        
        # Perform multiple analyses in same workspace
        result1 = self.tool.analyze(self.conv_id, workspace_id, data=self.paired_data, analysis_type="paired_comparison")
        result2 = self.tool.analyze(self.conv_id, workspace_id, groups=self.groups_data, analysis_type="two_group_comparison")
        result3 = self.tool.analyze(self.conv_id, workspace_id, data=self.categorical_data, analysis_type="frequency_analysis")
        
        # Verify all analyses succeeded
        self.assertIn("analysis_report", result1)
        self.assertIn("analysis_report", result2)
        self.assertIn("analysis_report", result3)
        
        # Verify all analyses are in the same workspace
        analyses = self.tool.conversations[self.conv_id]["workspaces"][workspace_id]["analyses"]
        self.assertEqual(len(analyses), 3)
        
        # Verify analysis types
        analysis_types = [analysis["analysis_type"] for analysis in analyses]
        self.assertIn("paired_comparison", analysis_types)
        self.assertIn("two_group_comparison", analysis_types)
        self.assertIn("frequency_analysis", analysis_types)
        
        # Verify all have correct workspace_id
        for analysis in analyses:
            self.assertEqual(analysis["workspace_id"], workspace_id)

    def test_get_analysis_report_workspace_specific(self):
        """Test that analysis reports are workspace-specific"""
        workspace_a = "report_workspace_a"
        workspace_b = "report_workspace_b"
        
        # Perform analyses in different workspaces
        self.tool.analyze(self.conv_id, workspace_a, data=self.numerical_data, analysis_type="descriptive_analysis")
        self.tool.analyze(self.conv_id, workspace_a, data=self.paired_data, analysis_type="paired_comparison")
        
        self.tool.analyze(self.conv_id, workspace_b, data=self.categorical_data, analysis_type="frequency_analysis")
        
        # Get reports for each workspace
        report_a = self.tool.get_analysis_report(self.conv_id, workspace_a)
        report_b = self.tool.get_analysis_report(self.conv_id, workspace_b)
        
        # Verify both reports are successful
        self.assertIn("comprehensive_statistical_report", report_a)
        self.assertIn("comprehensive_statistical_report", report_b)
        
        # Verify workspace IDs are correct
        self.assertEqual(report_a["comprehensive_statistical_report"]["workspace_id"], workspace_a)
        self.assertEqual(report_b["comprehensive_statistical_report"]["workspace_id"], workspace_b)
        
        # Verify different analysis counts
        self.assertEqual(report_a["comprehensive_statistical_report"]["total_analyses"], 2)
        self.assertEqual(report_b["comprehensive_statistical_report"]["total_analyses"], 1)

    def test_nonexistent_workspace_report(self):
        """Test getting report for non-existent workspace"""
        # First create conversation with some data to ensure conversation exists
        self.tool.analyze(self.conv_id, "existing_workspace", data=self.numerical_data, analysis_type="descriptive_analysis")
        
        # Try to get report for workspace that doesn't exist in the conversation
        result = self.tool.get_analysis_report(self.conv_id, "nonexistent_workspace")
        
        # Should return error
        self.assertIn("error", result)
        self.assertIn("No analyses found for workspace", result["error"])

    def test_conversation_isolation_with_workspaces(self):
        """Test that workspaces are isolated between conversations"""
        conv_id_a = "conversation_a"
        conv_id_b = "conversation_b"
        workspace_id = "same_workspace_name"
        
        # Perform analyses in same-named workspaces but different conversations
        result_a = self.tool.analyze(conv_id_a, workspace_id, data=self.numerical_data, analysis_type="descriptive_analysis")
        result_b = self.tool.analyze(conv_id_b, workspace_id, data=self.categorical_data, analysis_type="frequency_analysis")
        
        # Verify both succeeded
        self.assertIn("analysis_report", result_a)
        self.assertIn("analysis_report", result_b)
        
        # Verify conversations are isolated
        self.assertIn(conv_id_a, self.tool.conversations)
        self.assertIn(conv_id_b, self.tool.conversations)
        
        # Verify workspaces exist in both conversations
        self.assertIn(workspace_id, self.tool.conversations[conv_id_a]["workspaces"])
        self.assertIn(workspace_id, self.tool.conversations[conv_id_b]["workspaces"])
        
        # Verify different analyses
        analyses_a = self.tool.conversations[conv_id_a]["workspaces"][workspace_id]["analyses"]
        analyses_b = self.tool.conversations[conv_id_b]["workspaces"][workspace_id]["analyses"]
        
        self.assertEqual(len(analyses_a), 1)
        self.assertEqual(len(analyses_b), 1)
        self.assertNotEqual(analyses_a[0]["analysis_type"], analyses_b[0]["analysis_type"])

    def test_workspace_backward_compatibility(self):
        """Test that old tests still work with default workspace behavior"""
        # This simulates how existing code should still work
        default_workspace = "default"
        
        # Perform analysis using default workspace
        result = self.tool.analyze(self.conv_id, default_workspace, data=self.numerical_data, analysis_type="descriptive_analysis")
        
        # Verify it works as expected
        self.assertIn("analysis_report", result)
        self.assertIn(default_workspace, self.tool.conversations[self.conv_id]["workspaces"])
        
        # Get report using default workspace
        report = self.tool.get_analysis_report(self.conv_id, default_workspace)
        self.assertIn("comprehensive_statistical_report", report)
        self.assertEqual(report["comprehensive_statistical_report"]["workspace_id"], default_workspace)

    def test_workspace_edge_cases(self):
        """Test edge cases for workspace functionality"""
        # Test with special characters in workspace names
        special_workspace = "workspace-with_special.chars123"
        result = self.tool.analyze(self.conv_id, special_workspace, data=self.numerical_data, analysis_type="descriptive_analysis")
        self.assertIn("analysis_report", result)
        
        # Test with empty workspace name (should still work)
        empty_workspace = ""
        result = self.tool.analyze(self.conv_id, empty_workspace, data=self.numerical_data, analysis_type="descriptive_analysis")
        self.assertIn("analysis_report", result)
        
        # Verify both workspaces exist
        self.assertIn(special_workspace, self.tool.conversations[self.conv_id]["workspaces"])
        self.assertIn(empty_workspace, self.tool.conversations[self.conv_id]["workspaces"])

    def test_workspace_data_structure_integrity(self):
        """Test that workspace data structure maintains integrity"""
        workspace_id = "structure_test_workspace"
        
        # Perform analysis
        self.tool.analyze(self.conv_id, workspace_id, data=self.numerical_data, analysis_type="descriptive_analysis")
        
        # Verify correct nested structure
        conv_data = self.tool.conversations[self.conv_id]
        self.assertIn("workspaces", conv_data)
        
        workspace_data = conv_data["workspaces"][workspace_id]
        self.assertIn("analyses", workspace_data)
        self.assertIn("data_history", workspace_data)
        
        # Verify analyses structure
        analysis = workspace_data["analyses"][0]
        required_fields = ["analysis_type", "results", "data", "groups", "workspace_id"]
        for field in required_fields:
            self.assertIn(field, analysis)
        
        self.assertEqual(analysis["workspace_id"], workspace_id)

    def test_complex_workflow_across_workspaces(self):
        """Test complex workflow using multiple workspaces"""
        # Simulate a research project with different analysis phases
        exploratory_workspace = "exploratory_analysis"
        confirmatory_workspace = "confirmatory_analysis"
        final_workspace = "final_results"
        
        # Phase 1: Exploratory analysis
        self.tool.analyze(self.conv_id, exploratory_workspace, data=self.numerical_data, analysis_type="descriptive_analysis")
        self.tool.analyze(self.conv_id, exploratory_workspace, data=self.numerical_data, analysis_type="comprehensive_descriptive")
        
        # Phase 2: Confirmatory analysis
        self.tool.analyze(self.conv_id, confirmatory_workspace, data=self.paired_data, analysis_type="paired_comparison")
        self.tool.analyze(self.conv_id, confirmatory_workspace, groups=self.groups_data, analysis_type="two_group_comparison")
        
        # Phase 3: Final analysis
        correlation_data = {"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]}
        self.tool.analyze(self.conv_id, final_workspace, data=correlation_data, analysis_type="correlation_analysis")
        
        # Verify all phases have correct number of analyses
        exploratory_analyses = self.tool.conversations[self.conv_id]["workspaces"][exploratory_workspace]["analyses"]
        confirmatory_analyses = self.tool.conversations[self.conv_id]["workspaces"][confirmatory_workspace]["analyses"]
        final_analyses = self.tool.conversations[self.conv_id]["workspaces"][final_workspace]["analyses"]
        
        self.assertEqual(len(exploratory_analyses), 2)
        self.assertEqual(len(confirmatory_analyses), 2)
        self.assertEqual(len(final_analyses), 1)
        
        # Generate reports for each phase
        exploratory_report = self.tool.get_analysis_report(self.conv_id, exploratory_workspace)
        confirmatory_report = self.tool.get_analysis_report(self.conv_id, confirmatory_workspace)
        final_report = self.tool.get_analysis_report(self.conv_id, final_workspace)
        
        # Verify all reports are generated successfully
        self.assertIn("comprehensive_statistical_report", exploratory_report)
        self.assertIn("comprehensive_statistical_report", confirmatory_report)
        self.assertIn("comprehensive_statistical_report", final_report)
        
        # Verify workspace IDs in reports
        self.assertEqual(exploratory_report["comprehensive_statistical_report"]["workspace_id"], exploratory_workspace)
        self.assertEqual(confirmatory_report["comprehensive_statistical_report"]["workspace_id"], confirmatory_workspace)
        self.assertEqual(final_report["comprehensive_statistical_report"]["workspace_id"], final_workspace)


if __name__ == "__main__":
    unittest.main()

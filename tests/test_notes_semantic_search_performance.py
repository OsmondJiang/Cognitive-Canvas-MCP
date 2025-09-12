#!/usr/bin/env python3
"""
Performance benchmark tests for semantic search functionality
"""
import unittest
import sys
import os
import time
from typing import List, Dict

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.notes import NotesManager


class TestSemanticSearchPerformance(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up a large dataset for performance testing"""
        cls.manager = NotesManager()
        cls.conversation_id = "performance_test_conversation"
        
        # Create a large dataset of varied notes
        cls.large_dataset = [
            {
                "title": f"Machine Learning Research {i}",
                "content": f"Research on neural networks, deep learning architectures, and artificial intelligence applications in domain {i}. "
                          f"This includes supervised learning, unsupervised learning, reinforcement learning, and transfer learning techniques.",
                "tags": ["ml", "ai", "research", f"domain_{i}"],
                "note_type": "research"
            } for i in range(20)
        ] + [
            {
                "title": f"Software Development Practice {i}",
                "content": f"Best practices for software engineering, code review, testing frameworks, and deployment strategies in project {i}. "
                          f"Includes version control, continuous integration, and software architecture patterns.",
                "tags": ["development", "software", "engineering", f"project_{i}"],
                "note_type": "experience"
            } for i in range(20)
        ] + [
            {
                "title": f"Database Performance Issue {i}",
                "content": f"Query optimization, indexing strategies, and database performance tuning for system {i}. "
                          f"Includes connection pooling, query analysis, and database schema optimization.",
                "tags": ["database", "performance", "optimization", f"system_{i}"],
                "note_type": "problem"
            } for i in range(20)
        ] + [
            {
                "title": f"Cloud Infrastructure Solution {i}",
                "content": f"Cloud deployment, microservices architecture, and scalability solutions for environment {i}. "
                          f"Includes containerization, orchestration, monitoring, and cost optimization.",
                "tags": ["cloud", "infrastructure", "scalability", f"env_{i}"],
                "note_type": "solution"
            } for i in range(20)
        ] + [
            {
                "title": f"User Experience Design {i}",
                "content": f"UX research, user interface design, and usability testing for application {i}. "
                          f"Includes user personas, journey mapping, wireframing, and accessibility considerations.",
                "tags": ["ux", "design", "usability", f"app_{i}"],
                "note_type": "general"
            } for i in range(20)
        ]
        
        # Record all test notes
        print(f"Setting up {len(cls.large_dataset)} test notes...")
        for note_data in cls.large_dataset:
            cls.manager.record_note(
                conversation_id=cls.conversation_id,
                content=note_data["content"],
                title=note_data["title"],
                note_type=note_data["note_type"],
                tags=note_data["tags"]
            )
        print("Setup completed.")
    
    def test_single_search_performance(self):
        """Test performance of single semantic search"""
        queries = [
            "machine learning neural networks",
            "database query optimization",
            "cloud microservices architecture", 
            "user interface design",
            "software development best practices"
        ]
        
        performance_results = []
        
        for query in queries:
            start_time = time.time()
            
            result = self.manager.search_notes(
                conversation_id=self.conversation_id,
                query=query,
                search_type="semantic",
                limit=10
            )
            
            end_time = time.time()
            search_time = end_time - start_time
            
            # Verify search succeeded
            self.assertTrue(result["success"], f"Search failed for query: {query}")
            self.assertGreater(len(result["results"]), 0, f"No results for query: {query}")
            
            performance_results.append({
                "query": query,
                "time": search_time,
                "results_count": len(result["results"]),
                "total_matches": result["total_count"]
            })
            
            # Performance assertions
            self.assertLess(search_time, 1.0, f"Search took too long ({search_time:.3f}s) for query: {query}")
            self.assertGreater(result["total_count"], 0, f"No matches found for query: {query}")
        
        # Calculate average performance
        avg_time = sum(r["time"] for r in performance_results) / len(performance_results)
        self.assertLess(avg_time, 0.5, f"Average search time too high: {avg_time:.3f}s")
    
    def test_batch_search_performance(self):
        """Test performance of multiple searches in sequence"""
        queries = [
            "artificial intelligence",
            "software engineering",
            "database performance", 
            "cloud computing",
            "user experience",
            "neural networks",
            "query optimization",
            "microservices",
            "interface design",
            "code review"
        ]
        
        start_time = time.time()
        
        results = []
        for query in queries:
            result = self.manager.search_notes(
                conversation_id=self.conversation_id,
                query=query,
                search_type="semantic",
                limit=5
            )
            self.assertTrue(result["success"])
            results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_search = total_time / len(queries)
        
        # Performance assertions
        self.assertLess(total_time, 5.0, f"Batch search took too long: {total_time:.3f}s")
        self.assertLess(avg_time_per_search, 0.5, f"Average search time too high: {avg_time_per_search:.3f}s")
        
        # Verify all searches returned results
        for i, result in enumerate(results):
            self.assertGreater(len(result["results"]), 0, 
                             f"No results for batch query {i}: {queries[i]}")
    
    def test_combined_search_performance(self):
        """Test performance of combined semantic + tag search"""
        test_cases = [
            {"query": "machine learning", "tags": ["ml", "ai"]},
            {"query": "database optimization", "tags": ["database", "performance"]},
            {"query": "cloud deployment", "tags": ["cloud", "infrastructure"]},
            {"query": "user interface", "tags": ["ux", "design"]},
        ]
        
        performance_results = []
        
        for case in test_cases:
            start_time = time.time()
            
            result = self.manager.search_notes(
                conversation_id=self.conversation_id,
                query=case["query"],
                search_tags=case["tags"],
                search_type="combined",
                limit=10
            )
            
            end_time = time.time()
            search_time = end_time - start_time
            
            # Verify search succeeded
            self.assertTrue(result["success"], 
                          f"Combined search failed for query: {case['query']} with tags: {case['tags']}")
            
            performance_results.append({
                "query": case["query"],
                "tags": case["tags"],
                "time": search_time,
                "results_count": len(result["results"]),
                "search_method": result.get("search_method")
            })
            
            # Performance assertions
            self.assertLess(search_time, 1.0, 
                          f"Combined search took too long ({search_time:.3f}s) for {case}")
            
            # Verify search method
            self.assertEqual(result.get("search_method"), "semantic + tag",
                           "Combined search should use 'semantic + tag' method")
        
        # Overall performance check
        avg_time = sum(r["time"] for r in performance_results) / len(performance_results)
        self.assertLess(avg_time, 0.6, f"Average combined search time too high: {avg_time:.3f}s")
    
    def test_search_result_quality_consistency(self):
        """Test that search results are consistent across multiple runs"""
        query = "machine learning neural networks"
        
        # Run the same search multiple times
        results = []
        for i in range(5):
            result = self.manager.search_notes(
                conversation_id=self.conversation_id,
                query=query,
                search_type="semantic",
                limit=5
            )
            self.assertTrue(result["success"])
            results.append(result)
        
        # Verify consistency in top results
        if len(results) > 1:
            first_result_titles = [note["title"] for note in results[0]["results"]]
            
            for i, result in enumerate(results[1:], 1):
                current_titles = [note["title"] for note in result["results"]]
                
                # Should have significant overlap in top results
                overlap = len(set(first_result_titles[:3]).intersection(set(current_titles[:3])))
                self.assertGreaterEqual(overlap, 2, 
                                      f"Inconsistent results between run 0 and run {i}. "
                                      f"Expected at least 2 overlapping top results, got {overlap}")
                
                # Verify scores are reasonable and consistent
                for note in result["results"]:
                    score = note.get("relevance_score", 0)
                    self.assertGreater(score, 0, "All results should have positive relevance scores")
                    self.assertLessEqual(score, 2.0, "Relevance scores should be reasonable (≤2.0)")
    
    def test_large_result_set_performance(self):
        """Test performance when requesting many results"""
        query = "software development"
        
        start_time = time.time()
        
        result = self.manager.search_notes(
            conversation_id=self.conversation_id,
            query=query,
            search_type="semantic",
            limit=50  # Request many results
        )
        
        end_time = time.time()
        search_time = end_time - start_time
        
        # Verify search succeeded
        self.assertTrue(result["success"])
        
        # Performance assertions
        self.assertLess(search_time, 2.0, f"Large result search took too long: {search_time:.3f}s")
        
        # Verify result quality
        self.assertGreater(len(result["results"]), 10, "Should return substantial results for broad query")
        
        # Verify ranking quality - scores should be in descending order
        scores = [note.get("relevance_score", 0) for note in result["results"]]
        self.assertEqual(scores, sorted(scores, reverse=True),
                        "Large result set should be properly ranked")
        
        # Verify all results have required fields
        for note in result["results"]:
            self.assertIn("title", note)
            self.assertIn("content", note) 
            self.assertIn("relevance_score", note)
            self.assertIn("tags", note)


def run_performance_tests():
    """Run performance benchmark tests"""
    print("⚡ Running Semantic Search Performance Tests")
    print("=" * 60)
    
    # Run performance tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSemanticSearchPerformance)
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("📊 Performance Test Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All performance tests passed!")
        print("🚀 Semantic search performance is acceptable")
    else:
        print(f"\n⚠️  {len(result.failures + result.errors)} performance test(s) failed")
        
        if result.failures:
            print("\n❌ Performance Issues:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print("\n💥 Performance Errors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)

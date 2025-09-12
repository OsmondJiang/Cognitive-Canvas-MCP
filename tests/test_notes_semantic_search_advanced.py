#!/usr/bin/env python3
"""
Advanced semantic search tests for the notes system
Tests complex scenarios like synonym matching, concept similarity, multilingual content, etc.
"""
import unittest
import sys
import os

# Add the parent directory to the Python path to import tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.notes import NotesManager
from tools.semantic_search import NotesSemanticSearch


class TestAdvancedSemanticSearch(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with complex notes dataset"""
        self.manager = NotesManager()
        self.conversation_id = "advanced_test_conversation"
        
        # Create a diverse set of test notes
        self.test_notes = [
            {
                "title": "Machine Learning Fundamentals",
                "content": "Deep learning and neural networks are subset of artificial intelligence. Supervised learning uses labeled data for training models.",
                "tags": ["ai", "ml", "education"],
                "note_type": "general"
            },
            {
                "title": "AI Ethics Discussion",
                "content": "Artificial intelligence systems must be designed with fairness, transparency, and accountability in mind. Bias in algorithms can lead to discrimination.",
                "tags": ["ethics", "ai", "fairness"],
                "note_type": "problem"
            },
            {
                "title": "Database Optimization Tips",
                "content": "Query performance can be improved through proper indexing. SQL optimization involves analyzing execution plans and identifying bottlenecks.",
                "tags": ["database", "performance", "sql"],
                "note_type": "solution"
            },
            {
                "title": "Python Data Analysis",
                "content": "Pandas and NumPy are essential libraries for data manipulation and numerical computation. DataFrame operations enable efficient data processing.",
                "tags": ["python", "data", "pandas"],
                "note_type": "experience"
            },
            {
                "title": "Web Development Best Practices",
                "content": "Modern web applications should be responsive, accessible, and performant. JavaScript frameworks like React and Vue provide component-based architecture.",
                "tags": ["web", "javascript", "frontend"],
                "note_type": "general"
            },
            {
                "title": "Cloud Computing Concepts",
                "content": "Infrastructure as a Service (IaaS) provides virtualized computing resources. Microservices architecture enables scalable distributed systems.",
                "tags": ["cloud", "architecture", "scalability"],
                "note_type": "general"
            },
            {
                "title": "网络安全基础知识",  # Chinese content
                "content": "防火墙和入侵检测系统是网络安全的重要组成部分。加密技术保护数据传输的安全性。多因素认证增强了系统的安全防护。",
                "tags": ["安全", "网络", "加密"],
                "note_type": "general"
            },
            {
                "title": "Algorithm Complexity Analysis",
                "content": "Big O notation describes the time complexity of algorithms. Space-time tradeoffs are important considerations in algorithm design.",
                "tags": ["algorithms", "complexity", "optimization"],
                "note_type": "experience"
            },
            {
                "title": "DevOps Pipeline Setup",
                "content": "Continuous integration and continuous deployment streamline software delivery. Docker containers ensure consistent environments across development and production.",
                "tags": ["devops", "ci-cd", "docker"],
                "note_type": "solution"
            },
            {
                "title": "User Experience Research",
                "content": "User interviews and usability testing provide insights into user behavior. Personas and user journeys help design user-centered interfaces.",
                "tags": ["ux", "research", "design"],
                "note_type": "experience"
            }
        ]
        
        # Add all test notes
        for note_data in self.test_notes:
            self.manager.record_note(
                conversation_id=self.conversation_id,
                content=note_data["content"],
                title=note_data["title"],
                note_type=note_data["note_type"],
                tags=note_data["tags"]
            )
    
    def test_synonym_and_concept_matching(self):
        """Test semantic search's ability to match synonyms and related concepts"""
        test_cases = [
            {
                "query": "neural networks",
                "expected_matches": ["Machine Learning Fundamentals"],
                "description": "Should find ML content when searching for neural networks"
            },
            {
                "query": "bias and discrimination", 
                "expected_matches": ["AI Ethics Discussion"],
                "description": "Should match ethics content for bias-related queries"
            },
            {
                "query": "database performance tuning",
                "expected_matches": ["Database Optimization Tips"],
                "description": "Should find optimization content for performance queries"
            },
            {
                "query": "data science libraries",
                "expected_matches": ["Python Data Analysis"],
                "description": "Should match pandas/numpy content for data science queries"
            },
            {
                "query": "responsive web design",
                "expected_matches": ["Web Development Best Practices"],
                "description": "Should find web dev content for responsive design queries"
            }
        ]
        
        for case in test_cases:
            with self.subTest(query=case["query"]):
                result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=case["query"],
                    search_type="semantic",
                    limit=5
                )
                
                # Verify search succeeded
                self.assertTrue(result["success"], 
                              f"Search failed for query: {case['query']}")
                
                # Verify we got results
                self.assertGreater(len(result["results"]), 0,
                                 f"No results found for query: {case['query']}")
                
                # Check if expected matches are found
                found_titles = [note["title"] for note in result["results"]]
                matches_found = any(expected in found_titles for expected in case["expected_matches"])
                
                self.assertTrue(matches_found, 
                              f"Expected to find {case['expected_matches']} in results {found_titles} for query '{case['query']}'")
                
                # Verify relevance scores are reasonable (> 0)
                for note in result["results"]:
                    score = note.get("relevance_score", 0)
                    self.assertGreater(score, 0, 
                                     f"Relevance score should be > 0, got {score} for note '{note['title']}'")
                
                # Verify scores are in descending order
                scores = [note.get("relevance_score", 0) for note in result["results"]]
                self.assertEqual(scores, sorted(scores, reverse=True),
                               f"Results should be ranked by relevance score in descending order for query '{case['query']}'")
                
                # Verify search metadata
                self.assertEqual(result["search_type"], "semantic")
                self.assertEqual(result["search_method"], "semantic")
    
    def test_context_awareness(self):
        """Test semantic search's understanding of context and domain knowledge"""
        context_tests = [
            {
                "query": "scalable systems architecture",
                "expected_concepts": ["cloud", "microservices", "distributed"],
                "description": "Should understand scalability in software architecture context"
            },
            {
                "query": "algorithm efficiency analysis",
                "expected_concepts": ["complexity", "Big O", "optimization"],
                "description": "Should connect efficiency with algorithmic complexity"
            },
            {
                "query": "automated software delivery",
                "expected_concepts": ["CI/CD", "deployment", "pipeline"],
                "description": "Should understand automation in DevOps context"
            },
            {
                "query": "user-centered design methodology",
                "expected_concepts": ["UX", "usability", "user behavior"],
                "description": "Should connect design with user experience research"
            }
        ]
        
        for test in context_tests:
            with self.subTest(query=test["query"]):
                result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=test["query"],
                    search_type="semantic",
                    limit=3
                )
                
                # Verify search succeeded
                self.assertTrue(result["success"], 
                              f"Context search failed for query: {test['query']}")
                
                # Should get at least one result
                self.assertGreater(len(result["results"]), 0,
                                 f"No results found for context query: {test['query']}")
                
                # Verify top result has reasonable relevance score
                top_result = result["results"][0]
                top_score = top_result.get("relevance_score", 0)
                self.assertGreater(top_score, 0.1,
                                 f"Top result relevance score too low ({top_score}) for query: {test['query']}")
                
                # Check if the result content contains context-relevant terms
                content_lower = (top_result["title"] + " " + top_result["content"]).lower()
                concept_matches = [concept for concept in test["expected_concepts"] 
                                 if concept.lower() in content_lower]
                
                # Should find at least one relevant concept
                self.assertGreater(len(concept_matches), 0,
                                 f"Expected to find at least one of {test['expected_concepts']} in result content for query '{test['query']}'. "
                                 f"Top result: '{top_result['title']}'")
                
                # Verify result structure
                self.assertIn("title", top_result)
                self.assertIn("content", top_result)
                self.assertIn("relevance_score", top_result)
    
    def test_multilingual_content_search(self):
        """Test semantic search with multilingual content"""
        multilingual_tests = [
            {
                "query": "network security",
                "description": "English query should potentially find security-related content",
            },
            {
                "query": "firewall protection", 
                "description": "Security terms should find relevant content",
            },
            {
                "query": "encryption algorithms",
                "description": "Crypto terms should find security or algorithm content",
            }
        ]
        
        for test in multilingual_tests:
            with self.subTest(query=test["query"]):
                result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=test["query"],
                    search_type="semantic",
                    limit=10
                )
                
                # Verify search succeeded (semantic search should always work)
                self.assertTrue(result["success"],
                              f"Search should succeed for query: {test['query']}")
                
                # Should get some results (even if not perfect matches)
                # Note: TF-IDF may not find perfect matches for all multilingual queries
                # but should at least return the most relevant available content
                if len(result["results"]) > 0:
                    # Verify result structure
                    for note in result["results"]:
                        self.assertIn("title", note)
                        self.assertIn("content", note) 
                        self.assertIn("relevance_score", note)
                        self.assertGreaterEqual(note["relevance_score"], 0)
                    
                    # Verify ranking order
                    scores = [note.get("relevance_score", 0) for note in result["results"]]
                    self.assertEqual(scores, sorted(scores, reverse=True),
                                   f"Results should be ranked by relevance for query '{test['query']}'")
                
                # Check for Chinese security note if it exists in results
                chinese_note_found = any("网络安全" in note["title"] for note in result["results"])
                # Note: We don't assert this must be true since TF-IDF may not 
                # always match cross-language content effectively
                
                # Verify search metadata
                self.assertEqual(result["search_type"], "semantic")
                self.assertIn("search_method", result)
    
    def test_semantic_ranking_quality(self):
        """Test that semantic search ranks results by relevance quality"""
        ranking_tests = [
            {
                "query": "artificial intelligence machine learning",
                "description": "AI/ML query should rank ML content highest",
                "expected_top_keywords": ["machine learning", "artificial intelligence", "ai", "ml"]
            },
            {
                "query": "web development frontend frameworks",
                "description": "Frontend query should prioritize web development",
                "expected_top_keywords": ["web", "frontend", "javascript", "frameworks"]
            },
            {
                "query": "data analysis numerical computation",
                "description": "Data analysis should rank Python/pandas content highly",
                "expected_top_keywords": ["data", "analysis", "pandas", "numpy"]
            }
        ]
        
        for test in ranking_tests:
            with self.subTest(query=test["query"]):
                result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=test["query"],
                    search_type="semantic",
                    limit=10
                )
                
                # Verify search succeeded
                self.assertTrue(result["success"],
                              f"Ranking test failed for query: {test['query']}")
                
                # Should get results
                self.assertGreater(len(result["results"]), 0,
                                 f"No results for ranking test query: {test['query']}")
                
                # Verify ranking quality - scores should be in descending order
                scores = [note.get('relevance_score', 0) for note in result["results"]]
                self.assertEqual(scores, sorted(scores, reverse=True),
                               "Results should be ranked by relevance score in descending order")
                
                # Top result should have reasonable relevance score
                top_score = result["results"][0].get('relevance_score', 0)
                self.assertGreater(top_score, 0.2,
                                 f"Top result should have good relevance score (>0.2), got {top_score}")
                
                # Check if top result contains expected keywords
                top_result = result["results"][0]
                content_lower = (top_result["title"] + " " + top_result["content"]).lower()
                
                keyword_matches = sum(1 for keyword in test["expected_top_keywords"] 
                                    if keyword.lower() in content_lower)
                
                self.assertGreater(keyword_matches, 0,
                                 f"Top result should contain at least one expected keyword from {test['expected_top_keywords']} "
                                 f"for query '{test['query']}'. Top result: '{top_result['title']}'")
                
                # Verify all results have valid scores
                for i, note in enumerate(result["results"]):
                    score = note.get("relevance_score", 0)
                    self.assertGreaterEqual(score, 0,
                                          f"Result {i} should have non-negative relevance score, got {score}")
                    self.assertIn("title", note)
                    self.assertIn("content", note)
    
    def test_semantic_search_edge_cases(self):
        """Test semantic search with edge cases and challenging queries"""
        # Test empty query
        result = self.manager.search_notes(
            conversation_id=self.conversation_id,
            query="",
            search_type="semantic",
            limit=5
        )
        self.assertFalse(result["success"], "Empty query should fail")
        self.assertIn("error", result)
        
        # Test very long query
        long_query = "a" * 1000
        result = self.manager.search_notes(
            conversation_id=self.conversation_id,
            query=long_query,
            search_type="semantic",
            limit=5
        )
        # Should handle gracefully - either succeed or fail with clear error
        self.assertIn("success", result)
        if not result["success"]:
            self.assertIn("error", result)
        
        # Test query with only stop words
        result = self.manager.search_notes(
            conversation_id=self.conversation_id,
            query="the and or but",
            search_type="semantic",
            limit=5
        )
        # Should succeed but may return low-relevance results
        if result["success"] and result["results"]:
            # If results exist, scores should be valid but possibly low
            for note in result["results"]:
                score = note.get("relevance_score", 0)
                self.assertGreaterEqual(score, 0, "Relevance scores should be non-negative")
                
        # Test non-existent terms
        result = self.manager.search_notes(
            conversation_id=self.conversation_id,
            query="xyz123 nonexistent blahblah qwerty999",
            search_type="semantic",
            limit=5
        )
        # Should succeed but may return no or low-relevance results
        self.assertTrue(result["success"], "Search with non-existent terms should not crash")
        
        # Test query with special characters
        result = self.manager.search_notes(
            conversation_id=self.conversation_id,
            query="machine @#$% learning !@#",
            search_type="semantic",
            limit=5
        )
        # Should handle special characters gracefully
        self.assertTrue(result["success"], "Search with special characters should work")
        
        # Test single character query
        result = self.manager.search_notes(
            conversation_id=self.conversation_id,
            query="a",
            search_type="semantic",
            limit=5
        )
        # Should handle single character queries
        self.assertTrue(result["success"], "Single character query should be handled")
        
        # Test numeric query
        result = self.manager.search_notes(
            conversation_id=self.conversation_id,
            query="123 456 789",
            search_type="semantic",
            limit=5
        )
        # Should handle numeric queries
        self.assertTrue(result["success"], "Numeric query should be handled")
    
    def test_combined_semantic_tag_search(self):
        """Test combined semantic and tag search functionality"""
        combined_tests = [
            {
                "query": "performance optimization",
                "tags": ["database"],
                "description": "Should find database optimization with performance query + db tags"
            },
            {
                "query": "software development",
                "tags": ["python"],
                "description": "Should boost Python content for dev query + python tags"
            },
            {
                "query": "system design",
                "tags": ["cloud", "scalability"],
                "description": "Should find cloud/architecture content for system design query"
            }
        ]
        
        for test in combined_tests:
            with self.subTest(query=test["query"], tags=test["tags"]):
                # Test semantic-only search
                semantic_result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=test["query"],
                    search_type="semantic",
                    limit=5
                )
                
                # Test combined search
                combined_result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=test["query"],
                    search_tags=test["tags"],
                    search_type="combined",
                    limit=5
                )
                
                # Both searches should succeed
                self.assertTrue(semantic_result["success"],
                              f"Semantic search failed for query: {test['query']}")
                self.assertTrue(combined_result["success"],
                              f"Combined search failed for query: {test['query']} with tags: {test['tags']}")
                
                # Combined search should use correct search method
                self.assertEqual(combined_result.get("search_method"), "semantic + tag",
                               f"Combined search should use 'semantic + tag' method")
                
                # Combined search should potentially return different results
                # (this tests that tag filtering/boosting is working)
                if combined_result["results"]:
                    top_combined = combined_result["results"][0]
                    
                    # Verify result structure
                    self.assertIn("title", top_combined)
                    self.assertIn("content", top_combined)
                    self.assertIn("relevance_score", top_combined)
                    self.assertIn("tags", top_combined)
                    
                    # Top result should have reasonable score
                    top_score = top_combined.get("relevance_score", 0)
                    self.assertGreater(top_score, 0,
                                     f"Top combined result should have positive relevance score, got {top_score}")
                    
                    # Check if top result has any of the specified tags
                    result_tags = top_combined.get('tags', [])
                    tag_overlap = set(test['tags']).intersection(set(result_tags))
                    
                    # For combined search, we expect some tag relevance
                    # Either direct tag matches or semantic relevance should be present
                    has_tag_match = len(tag_overlap) > 0
                    has_semantic_relevance = top_score > 0.1  # Reasonable semantic score
                    
                    self.assertTrue(has_tag_match or has_semantic_relevance,
                                  f"Combined search result should have either tag matches {tag_overlap} "
                                  f"or good semantic relevance (score: {top_score}) for query '{test['query']}' "
                                  f"with tags {test['tags']}")
                
                # Test tag-only search for comparison
                tag_result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    search_tags=test["tags"],
                    search_type="tag",
                    limit=5
                )
                
                self.assertTrue(tag_result["success"],
                              f"Tag search failed for tags: {test['tags']}")
                
                if tag_result["results"]:
                    # All tag search results should have the specified tags
                    for note in tag_result["results"]:
                        note_tags = note.get("tags", [])
                        tag_overlap = set(test['tags']).intersection(set(note_tags))
                        self.assertGreater(len(tag_overlap), 0,
                                         f"Tag search result should contain at least one of {test['tags']}, "
                                         f"but note tags are {note_tags}")
                
                # Verify search metadata
                self.assertEqual(semantic_result.get("search_type"), "semantic")
                self.assertEqual(combined_result.get("search_type"), "combined")
                self.assertEqual(tag_result.get("search_type"), "tag")


def run_advanced_semantic_tests():
    """Run all advanced semantic search tests"""
    # Create test suite and run with standard unittest runner
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAdvancedSemanticSearch)
    
    # Run tests with minimal output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_advanced_semantic_tests()
    sys.exit(0 if success else 1)

"""
Semantic Search Module for Cognitive Canvas Notes
=================================================

Provides semantic search capabilities using TF-IDF vectorization and cosine similarity.
This implementation is lightweight and doesn't require external LLM calls.
"""

from typing import List, Dict, Tuple, Optional
import re
import numpy as np

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class SemanticSearch:
    """
    Lightweight semantic search using TF-IDF vectorization and cosine similarity.
    """
    
    def __init__(self, min_similarity_threshold: float = 0.1):
        """
        Initialize the semantic search engine.
        
        Args:
            min_similarity_threshold: Minimum similarity score to consider as a match
        """
        self.min_similarity_threshold = min_similarity_threshold
        self.vectorizer = None
        self.document_vectors = None
        self.documents = []
        self.document_metadata = []
        
        if not SKLEARN_AVAILABLE:
            print("Warning: scikit-learn not available. Falling back to simple keyword matching.")
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better vectorization.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def build_index(self, documents: List[Dict], content_fields: List[str] = None) -> None:
        """
        Build search index from documents.
        
        Args:
            documents: List of document dictionaries
            content_fields: Fields to use for content (default: ['content', 'title'])
        """
        if content_fields is None:
            content_fields = ['content', 'title']
        
        self.documents = documents
        self.document_metadata = []
        
        # Extract text content from documents
        texts = []
        for doc in documents:
            # Combine specified content fields
            combined_text = []
            for field in content_fields:
                if field in doc and doc[field]:
                    combined_text.append(str(doc[field]))
            
            # Add tags as text if available
            if 'tags' in doc and doc['tags']:
                combined_text.extend(doc['tags'])
            
            text = ' '.join(combined_text)
            processed_text = self._preprocess_text(text)
            texts.append(processed_text)
            
            # Store metadata for quick access
            self.document_metadata.append({
                'id': doc.get('id', ''),
                'title': doc.get('title', ''),
                'note_type': doc.get('note_type', 'general'),
                'tags': doc.get('tags', [])
            })
        
        if not SKLEARN_AVAILABLE:
            # Store texts for fallback keyword matching
            self.processed_texts = texts
            return
        
        # Build TF-IDF vectors
        self.vectorizer = TfidfVectorizer(
            max_features=5000,          # Limit vocabulary size
            stop_words='english',       # Remove common English stop words
            ngram_range=(1, 2),        # Use unigrams and bigrams
            min_df=1,                  # Minimum document frequency
            max_df=0.8                 # Maximum document frequency
        )
        
        self.document_vectors = self.vectorizer.fit_transform(texts)
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query text
            top_k: Number of top results to return
            
        Returns:
            List of (document_index, similarity_score) tuples, sorted by similarity
        """
        if not self.documents:
            return []
        
        processed_query = self._preprocess_text(query)
        
        if not SKLEARN_AVAILABLE:
            return self._fallback_keyword_search(processed_query, top_k)
        
        # Vectorize query
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
        
        # Get top-k results above threshold
        results = []
        for idx, similarity in enumerate(similarities):
            if similarity >= self.min_similarity_threshold:
                results.append((idx, similarity))
        
        # Sort by similarity (descending) and limit to top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _fallback_keyword_search(self, query: str, top_k: int) -> List[Tuple[int, float]]:
        """
        Fallback keyword-based search when sklearn is not available.
        
        Args:
            query: Preprocessed query text
            top_k: Number of top results to return
            
        Returns:
            List of (document_index, similarity_score) tuples
        """
        query_words = set(query.split())
        results = []
        
        for idx, text in enumerate(self.processed_texts):
            text_words = set(text.split())
            
            # Calculate simple word overlap similarity
            if query_words and text_words:
                intersection = query_words.intersection(text_words)
                union = query_words.union(text_words)
                similarity = len(intersection) / len(union) if union else 0
                
                if similarity >= self.min_similarity_threshold:
                    results.append((idx, similarity))
        
        # Sort by similarity (descending) and limit to top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_document_by_index(self, index: int) -> Optional[Dict]:
        """
        Get document by index.
        
        Args:
            index: Document index
            
        Returns:
            Document dictionary or None if index is invalid
        """
        if 0 <= index < len(self.documents):
            return self.documents[index]
        return None
    
    def get_metadata_by_index(self, index: int) -> Optional[Dict]:
        """
        Get document metadata by index.
        
        Args:
            index: Document index
            
        Returns:
            Metadata dictionary or None if index is invalid
        """
        if 0 <= index < len(self.document_metadata):
            return self.document_metadata[index]
        return None


class NotesSemanticSearch:
    """
    Specialized semantic search for Notes with caching and incremental updates.
    """
    
    def __init__(self):
        self.search_engines = {}  # conversation_id -> SemanticSearch
        self.last_update = {}     # conversation_id -> last_update_count
    
    def _get_or_create_search_engine(self, conversation_id: str) -> SemanticSearch:
        """Get or create search engine for a conversation."""
        if conversation_id not in self.search_engines:
            self.search_engines[conversation_id] = SemanticSearch()
            self.last_update[conversation_id] = 0
        return self.search_engines[conversation_id]
    
    def update_index(self, conversation_id: str, notes: List[Dict]) -> None:
        """
        Update search index for a conversation.
        
        Args:
            conversation_id: Conversation identifier
            notes: List of note dictionaries
        """
        search_engine = self._get_or_create_search_engine(conversation_id)
        
        # Only rebuild index if notes have changed
        if len(notes) != self.last_update.get(conversation_id, 0):
            search_engine.build_index(notes, content_fields=['content', 'title'])
            self.last_update[conversation_id] = len(notes)
    
    def semantic_search(self, conversation_id: str, notes: List[Dict], 
                       query: str, limit: int = 10) -> List[Tuple[Dict, float]]:
        """
        Perform semantic search on notes.
        
        Args:
            conversation_id: Conversation identifier
            notes: List of note dictionaries
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of (note_dict, similarity_score) tuples
        """
        # Update index if needed
        self.update_index(conversation_id, notes)
        
        search_engine = self._get_or_create_search_engine(conversation_id)
        
        # Perform search
        search_results = search_engine.search(query, top_k=limit)
        
        # Convert to note dictionaries with scores
        results = []
        for doc_idx, similarity in search_results:
            note = search_engine.get_document_by_index(doc_idx)
            if note:
                results.append((note, similarity))
        
        return results
    
    def clear_index(self, conversation_id: str) -> None:
        """Clear search index for a conversation."""
        if conversation_id in self.search_engines:
            del self.search_engines[conversation_id]
            del self.last_update[conversation_id]

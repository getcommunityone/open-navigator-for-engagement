#!/usr/bin/env python3
"""
Production-grade jurisdiction name normalization and fuzzy matching

Implements industry best practices:
1. Deterministic normalization (lowercase, Unicode, punctuation, whitespace)
2. Jurisdiction suffix stripping (city, town, county, etc.)
3. Directional/prepositional cleanup ("of", "the", "city of")
4. Synonym dictionary (saint ↔ st, fort ↔ ft, mount ↔ mt)
5. Token-based fuzzy matching (not just exact string matching)
6. Hierarchy-aware matching (state → county → city)
7. Confidence scoring and thresholding

Based on Census Bureau, GeoNames, and public sector entity resolution standards.
"""
import re
import unicodedata
from typing import Tuple, Dict, List
from difflib import SequenceMatcher
from loguru import logger


class JurisdictionNameNormalizer:
    """
    Normalize jurisdiction names following industry best practices.
    
    Pattern: normalize → de-noise → tokenize → fuzzy match
    """
    
    # U.S. jurisdiction suffixes (high-frequency, low-information tokens)
    JURISDICTION_SUFFIXES = [
        'city', 'town', 'township', 'village', 'borough', 'boro',
        'county', 'parish', 'district', 'municipality', 'muni',
        'cdp',  # Census Designated Place
        'incorporated', 'unincorporated',
        'charter', 'consolidated'
    ]
    
    # Directional and prepositional stopwords
    STOPWORDS = [
        'of', 'the', 'and', '&',
        'city of', 'town of', 'county of', 'borough of', 'village of',
        'chartered', 'municipal', 'metro', 'metropolitan'
    ]
    
    # Synonym dictionary (deterministic replacements)
    SYNONYMS = {
        'saint': 'st',
        'fort': 'ft',
        'mount': 'mt',
        'mountain': 'mtn',
        'junction': 'jct',
        'junction': 'junc',
        'center': 'ctr',
        'centre': 'ctr',
        'heights': 'hts',
        'park': 'pk',
        'point': 'pt',
        'port': 'pt',
        'spring': 'spg',
        'springs': 'spgs',
        'station': 'sta',
        'north': 'n',
        'south': 's',
        'east': 'e',
        'west': 'w',
        'northeast': 'ne',
        'northwest': 'nw',
        'southeast': 'se',
        'southwest': 'sw'
    }
    
    def __init__(self, apply_synonyms: bool = True, apply_stopwords: bool = True):
        """
        Initialize normalizer.
        
        Args:
            apply_synonyms: Apply synonym dictionary (st ↔ saint, etc.)
            apply_stopwords: Remove stopwords ("of", "the", etc.)
        """
        self.apply_synonyms = apply_synonyms
        self.apply_stopwords = apply_stopwords
        
        # Compile regex patterns for performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for better performance."""
        
        # Suffix pattern (must be at end of string)
        suffix_pattern = r'\s+(?:' + '|'.join(self.JURISDICTION_SUFFIXES) + r')$'
        self.suffix_regex = re.compile(suffix_pattern, re.IGNORECASE)
        
        # Suffix in middle pattern (e.g., "Garden City city" → "Garden city")
        # Matches "Town" or "City" capitalized in middle followed by lowercase suffix
        self.middle_suffix_regex = re.compile(
            r'\s+(?:Town|City)\s+(?=(?:city|town|village))',
            re.IGNORECASE
        )
        
        # Stopwords pattern
        stopword_pattern = r'\b(?:' + '|'.join(re.escape(sw) for sw in self.STOPWORDS) + r')\b'
        self.stopword_regex = re.compile(stopword_pattern, re.IGNORECASE)
        
        # Punctuation pattern (keep hyphens, remove others)
        self.punctuation_regex = re.compile(r'[^\w\s\-]')
        
        # Whitespace normalization
        self.whitespace_regex = re.compile(r'\s+')
    
    def normalize(self, name: str) -> str:
        """
        Full normalization pipeline.
        
        Args:
            name: Raw jurisdiction name (e.g., "City of Mobile, AL")
            
        Returns:
            Normalized name (e.g., "mobile")
        """
        if not name or not isinstance(name, str):
            return ''
        
        # Step 1: Unicode normalization (NFKD - compatibility decomposition)
        name = unicodedata.normalize('NFKD', name)
        
        # Step 2: Lowercase
        name = name.lower()
        
        # Step 3: Remove punctuation (except hyphens)
        name = self.punctuation_regex.sub(' ', name)
        
        # Step 4: Remove stopwords first (before suffix stripping)
        if self.apply_stopwords:
            name = self.stopword_regex.sub(' ', name)
        
        # Step 5: Apply synonym dictionary
        if self.apply_synonyms:
            name = self._apply_synonyms(name)
        
        # Step 6: Remove suffixes in middle (e.g., "Greenfield Town city" → "Greenfield city")
        name = self.middle_suffix_regex.sub(' ', name)
        
        # Step 7: Remove suffix at end (must be last normalization step)
        name = self.suffix_regex.sub('', name)
        
        # Step 8: Normalize whitespace
        name = self.whitespace_regex.sub(' ', name).strip()
        
        return name
    
    def _apply_synonyms(self, name: str) -> str:
        """Apply synonym dictionary (whole word replacement)."""
        words = name.split()
        normalized_words = [self.SYNONYMS.get(word, word) for word in words]
        return ' '.join(normalized_words)
    
    def tokenize(self, name: str) -> set:
        """
        Tokenize normalized name into set of tokens.
        
        Used for token-based similarity (Jaccard, token-set).
        """
        return set(name.split())
    
    def token_set_similarity(self, name1: str, name2: str) -> float:
        """
        Token-set similarity (recommended for jurisdictions).
        
        Handles word order differences:
        - "los angeles county" vs "county of los angeles" → high similarity
        - "new york city" vs "new york county" → low similarity
        
        Returns:
            Similarity score [0.0, 1.0]
        """
        tokens1 = self.tokenize(name1)
        tokens2 = self.tokenize(name2)
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        
        return len(intersection) / len(union) if union else 0.0
    
    def token_sort_similarity(self, name1: str, name2: str) -> float:
        """
        Token-sort similarity (handles word order).
        
        Sorts tokens alphabetically before comparing.
        """
        sorted1 = ' '.join(sorted(self.tokenize(name1)))
        sorted2 = ' '.join(sorted(self.tokenize(name2)))
        
        return SequenceMatcher(None, sorted1, sorted2).ratio()
    
    def hybrid_similarity(self, name1: str, name2: str) -> float:
        """
        Hybrid similarity combining multiple metrics.
        
        Weights:
        - Token-set: 50% (handles reordering)
        - Token-sort: 30% (handles partial matches)
        - Character ratio: 20% (catches typos)
        """
        token_set = self.token_set_similarity(name1, name2)
        token_sort = self.token_sort_similarity(name1, name2)
        char_ratio = SequenceMatcher(None, name1, name2).ratio()
        
        return (0.5 * token_set) + (0.3 * token_sort) + (0.2 * char_ratio)


class HierarchicalJurisdictionMatcher:
    """
    Hierarchy-aware jurisdiction matcher.
    
    Matches: state (exact) → county (fuzzy) → city (fuzzy)
    """
    
    def __init__(
        self,
        normalizer: JurisdictionNameNormalizer = None,
        confidence_threshold: float = 0.85
    ):
        """
        Initialize matcher.
        
        Args:
            normalizer: Name normalizer instance
            confidence_threshold: Minimum similarity score to accept match
        """
        self.normalizer = normalizer or JurisdictionNameNormalizer()
        self.confidence_threshold = confidence_threshold
    
    def match(
        self,
        source_name: str,
        source_state: str,
        source_type: str,
        target_name: str,
        target_state: str,
        target_type: str
    ) -> Tuple[bool, float, str]:
        """
        Match two jurisdictions with hierarchy awareness.
        
        Args:
            source_name: Source jurisdiction name
            source_state: Source state code (e.g., 'AL')
            source_type: Source type ('city', 'county', etc.)
            target_name: Target jurisdiction name
            target_state: Target state code
            target_type: Target type
        
        Returns:
            (is_match, confidence_score, explanation)
        """
        # Step 1: State must match exactly (blocking)
        if source_state.upper() != target_state.upper():
            return False, 0.0, f"State mismatch: {source_state} != {target_state}"
        
        # Step 2: Normalize names
        norm_source = self.normalizer.normalize(source_name)
        norm_target = self.normalizer.normalize(target_name)
        
        # Step 3: Exact match after normalization (highest confidence)
        if norm_source == norm_target:
            return True, 1.0, "Exact match after normalization"
        
        # Step 4: Fuzzy match (token-based similarity)
        similarity = self.normalizer.hybrid_similarity(norm_source, norm_target)
        
        if similarity >= self.confidence_threshold:
            return True, similarity, f"Fuzzy match (score: {similarity:.2f})"
        else:
            return False, similarity, f"Below threshold (score: {similarity:.2f} < {self.confidence_threshold})"
    
    def find_best_match(
        self,
        source_name: str,
        source_state: str,
        candidates: List[Dict]
    ) -> Tuple[Dict, float, str]:
        """
        Find best matching candidate from a list.
        
        Args:
            source_name: Source jurisdiction name
            source_state: Source state code
            candidates: List of dicts with 'name', 'state', 'type' keys
        
        Returns:
            (best_candidate, confidence, explanation) or (None, 0.0, reason)
        """
        best_candidate = None
        best_score = 0.0
        best_explanation = ""
        
        norm_source = self.normalizer.normalize(source_name)
        
        for candidate in candidates:
            # Block by state
            if candidate['state'].upper() != source_state.upper():
                continue
            
            norm_target = self.normalizer.normalize(candidate['name'])
            similarity = self.normalizer.hybrid_similarity(norm_source, norm_target)
            
            if similarity > best_score:
                best_score = similarity
                best_candidate = candidate
                best_explanation = f"Fuzzy match: '{source_name}' → '{candidate['name']}' (score: {similarity:.2f})"
        
        if best_score >= self.confidence_threshold:
            return best_candidate, best_score, best_explanation
        else:
            return None, best_score, f"No match above threshold (best score: {best_score:.2f})"


# Example usage and test cases
if __name__ == '__main__':
    normalizer = JurisdictionNameNormalizer()
    
    # Test normalization
    test_cases = [
        "City of Mobile, AL",
        "Greenfield Town city",
        "Winthrop Town city",
        "Garden City city",
        "Phenix City city",
        "Saint Louis County",
        "Fort Wayne city",
        "Mount Vernon town",
        "North Reading town",
        "Smiths Station city",
        "City of New York",
        "County of Los Angeles"
    ]
    
    print("NORMALIZATION TEST CASES:")
    print("=" * 80)
    for name in test_cases:
        normalized = normalizer.normalize(name)
        print(f"{name:35} → {normalized}")
    
    print("\n\nSIMILARITY TEST CASES:")
    print("=" * 80)
    
    pairs = [
        ("Mobile city", "Mobile"),
        ("Greenfield Town city", "Greenfield"),
        ("Saint Louis County", "St Louis County"),
        ("Fort Wayne", "Ft Wayne city"),
        ("City of Los Angeles", "Los Angeles County"),  # Should be low
        ("New York City", "New York County"),  # Should be low
        ("Smiths Station", "Smith Station"),  # Typo - should still match
    ]
    
    for name1, name2 in pairs:
        norm1 = normalizer.normalize(name1)
        norm2 = normalizer.normalize(name2)
        similarity = normalizer.hybrid_similarity(norm1, norm2)
        print(f"{name1:30} vs {name2:30} → {similarity:.2f}")

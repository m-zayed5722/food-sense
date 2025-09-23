#!/usr/bin/env python3
"""
Debug Modification Detection
Detailed debugging of why certain modifications aren't detected
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.order_schema import ModificationType

def debug_modification_patterns():
    """Debug the modification pattern matching"""
    
    print("🔍 DEBUGGING MODIFICATION PATTERNS")
    print("="*50)
    
    test_text = "big mac no pickles with large fries extra salt"
    print(f"Test text: '{test_text}'")
    print()
    
    # Test each pattern individually
    patterns = [
        (r'\bno\s+([\w\s]{2,15}?)(?:\s+(?:with|large|medium|small|extra|and|$))', "REMOVE"),
        (r'\bextra\s+([\w\s]{2,15}?)(?:\s+(?:with|large|medium|small|no|and|$))', "EXTRA"),
        (r'\bwith\s+([\w\s,]+?)(?:\s+(?:and|,)\s+[\w\s,]+)*(?:\s*$|[.]|\s+(?:large|medium|small|extra|no|with)|\s+[A-Z])', "ADD"),
    ]
    
    for i, (pattern, mod_type) in enumerate(patterns, 1):
        print(f"Pattern {i} ({mod_type}):")
        print(f"  Regex: {pattern}")
        
        matches = re.finditer(pattern, test_text, re.IGNORECASE)
        found_matches = list(matches)
        
        if found_matches:
            for j, match in enumerate(found_matches):
                print(f"  Match {j+1}: '{match.group(1)}' at position {match.start()}-{match.end()}")
                print(f"    Full match: '{match.group()}'")
        else:
            print(f"  No matches found")
        print()
    
    # Test the sequential patterns
    print("Sequential patterns:")
    
    # Check for multiple no/extra patterns
    no_pattern = r'\bno\s+(\w+(?:\s+\w+)*)\s+no\s+((?:\w+(?:\s+\w+)*(?:\s+no\s+\w+(?:\s+\w+)*)*)+)'
    extra_pattern = r'\bextra\s+(\w+(?:\s+\w+)*)\s+extra\s+((?:\w+(?:\s+\w+)*(?:\s+extra\s+\w+(?:\s+\w+)*)*)+)'
    
    no_matches = re.finditer(no_pattern, test_text, re.IGNORECASE)
    extra_matches = re.finditer(extra_pattern, test_text, re.IGNORECASE)
    
    print(f"Sequential 'no' matches: {len(list(no_matches))}")
    print(f"Sequential 'extra' matches: {len(list(extra_matches))}")
    
    print()
    print("="*50)

def test_simple_patterns():
    """Test with simplified patterns"""
    print("🧪 TESTING SIMPLIFIED PATTERNS")
    print("="*50)
    
    test_cases = [
        "big mac no pickles with large fries extra salt",
        "mcchicken no mayo with medium sprite", 
        "pizza extra cheese with garlic bread",
    ]
    
    # Simplified patterns
    simple_patterns = [
        (r'\bno\s+(\w+)', "REMOVE"),
        (r'\bextra\s+(\w+)', "EXTRA"), 
        (r'\bwith\s+([\w\s]+?)(?=\s+(?:large|medium|small|and|\d|$))', "ADD"),
    ]
    
    for test_text in test_cases:
        print(f"Testing: '{test_text}'")
        
        for pattern, mod_type in simple_patterns:
            matches = re.finditer(pattern, test_text, re.IGNORECASE)
            for match in matches:
                print(f"  {mod_type}: '{match.group(1).strip()}'")
        print()

if __name__ == "__main__":
    debug_modification_patterns()
    print()
    test_simple_patterns()
#!/usr/bin/env python3
"""
Direct Pattern Test
Test the patterns directly to see what's being matched
"""

import re

def test_direct_patterns():
    test_cases = [
        "mcchicken no mayo with medium sprite",
        "pizza extra cheese with garlic bread", 
        "chicken wings extra sauce"
    ]
    
    patterns = [
        (r'\bno\s+(\w+)', "REMOVE"),
        (r'\bextra\s+(\w+)', "EXTRA"), 
        (r'\bwith\s+([\w\s]+?)(?=\s+(?:large|medium|small|and|\d|$))', "ADD"),
        (r'\bwith\s+([\w\s]+)$', "ADD"),
    ]
    
    print("🔍 DIRECT PATTERN TESTING")
    print("="*50)
    
    for text in test_cases:
        print(f"\nTesting: '{text}'")
        print("-" * 30)
        
        for pattern, mod_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            matches_list = list(matches)
            
            if matches_list:
                for match in matches_list:
                    print(f"  {mod_type}: '{match.group(1).strip()}'")
            else:
                print(f"  {mod_type}: No match")

if __name__ == "__main__":
    test_direct_patterns()
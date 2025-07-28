#!/usr/bin/env python3
"""
Test script for standalone due date extraction functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from utils.due_date_extractor import extract_due_date_from_text

def test_due_date_extraction():
    """Test the standalone due date extraction function"""
    
    test_cases = [
        # Test cases with due dates
        ("I have to pay my insurance before 29 jul 2025", ("I have to pay my insurance", "2025-07-29")),
        ("Pay rent by 15 jan 2025", ("Pay rent", "2025-01-15")),
        ("Submit report due 30 dec 2024", ("Submit report", "2024-12-30")),
        ("Meeting notes for 25th march 2025", ("Meeting notes for", "2025-03-25")),
        ("Project deadline until 10th april 2025", ("Project deadline", "2025-04-10")),
        ("Review documents by 5th may 2025", ("Review documents", "2025-05-05")),
        ("Call client on 2025-06-15", ("Call client on", "2025-06-15")),
        ("Send email by 15-06-2025", ("Send email", "2025-06-15")),
        
        # Test cases without due dates
        ("Just a regular note", ("Just a regular note", None)),
        ("Meeting with John tomorrow", ("Meeting with John tomorrow", None)),
        ("Remember to buy groceries", ("Remember to buy groceries", None)),
        ("Project status update", ("Project status update", None)),
    ]
    
    print("Testing standalone due date extraction...")
    print("=" * 50)
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        cleaned_text, due_date = extract_due_date_from_text(input_text)
        
        print(f"Test {i}:")
        print(f"  Input: '{input_text}'")
        print(f"  Expected: {expected}")
        print(f"  Actual: ('{cleaned_text}', {due_date})")
        
        if (cleaned_text.strip(), due_date) == expected:
            print("  ✓ PASS")
        else:
            print("  ✗ FAIL")
        print()

if __name__ == "__main__":
    test_due_date_extraction() 
#!/usr/bin/env python3
"""
Simple test for jhi.py functionality.
"""

import subprocess
import sys
import os

def test_jhi_output():
    """Test that jhi.py outputs 'jhi'."""
    try:
        # Run the jhi.py script and capture output
        result = subprocess.run([sys.executable, 'jhi.py'], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Check that it ran successfully
        if result.returncode != 0:
            print(f"ERROR: jhi.py failed with return code {result.returncode}")
            print(f"STDERR: {result.stderr}")
            return False
        
        # Check the output
        expected_output = "jhi\n"
        if result.stdout == expected_output:
            print("PASS: jhi.py outputs 'jhi' correctly")
            return True
        else:
            print(f"FAIL: Expected '{expected_output.strip()}', got '{result.stdout.strip()}'")
            return False
    
    except Exception as e:
        print(f"ERROR: Failed to run test: {e}")
        return False

def main():
    """Run the test."""
    print("Running jhi functionality test...")
    success = test_jhi_output()
    
    if success:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Main test runner for Omani-Therapist-Voice system.

This script runs all test suites and generates a comprehensive report.
"""

import os
import sys
import time
import logging
import unittest
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import test modules
from test_speech_recognition import SpeechRecognitionTests
from test_emotion_understanding import EmotionUnderstandingTests
from test_therapeutic_response import TherapeuticResponseTests
from test_crisis_handling import CrisisHandlingTests
from test_performance import PerformanceTests


def run_all_tests():
    """Run all test suites and generate report."""
    # Start timing
    start_time = datetime.now()
    logger.info(f"Starting test run at {start_time}")
    
    # Create results directory
    results_dir = Path(__file__).parent / "test_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(SpeechRecognitionTests))
    test_suite.addTest(unittest.makeSuite(EmotionUnderstandingTests))
    test_suite.addTest(unittest.makeSuite(TherapeuticResponseTests))
    test_suite.addTest(unittest.makeSuite(CrisisHandlingTests))
    test_suite.addTest(unittest.makeSuite(PerformanceTests))
    
    # Set up test result collection
    test_results = {}
    
    # Create result collector
    class TestResultCollector(unittest.TextTestResult):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.results = {
                "success": [],
                "failure": [],
                "error": [],
                "skipped": []
            }
        
        def addSuccess(self, test):
            super().addSuccess(test)
            self.results["success"].append(str(test))
        
        def addFailure(self, test, err):
            super().addFailure(test, err)
            self.results["failure"].append({
                "test": str(test),
                "error": str(err[1])
            })
        
        def addError(self, test, err):
            super().addError(test, err)
            self.results["error"].append({
                "test": str(test),
                "error": str(err[1])
            })
        
        def addSkip(self, test, reason):
            super().addSkip(test, reason)
            self.results["skipped"].append({
                "test": str(test),
                "reason": reason
            })
    
    # Run the tests
    runner = unittest.TextTestRunner(
        verbosity=2,
        resultclass=TestResultCollector
    )
    result = runner.run(test_suite)
    
    # End timing
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Generate summary
    summary = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration,
        "total_tests": result.testsRun,
        "successful_tests": len(result.results["success"]),
        "failed_tests": len(result.results["failure"]),
        "error_tests": len(result.results["error"]),
        "skipped_tests": len(result.results["skipped"]),
        "details": result.results
    }
    
    # Calculate pass rate
    total_run = result.testsRun - len(result.results["skipped"])
    if total_run > 0:
        pass_rate = len(result.results["success"]) / total_run * 100
    else:
        pass_rate = 0
    
    summary["pass_rate"] = pass_rate
    
    # Determine overall result
    if pass_rate >= 85:
        summary["overall_result"] = "PASSED"
    elif pass_rate >= 70:
        summary["overall_result"] = "PARTIALLY PASSED"
    else:
        summary["overall_result"] = "FAILED"
    
    # Save results to JSON file
    result_file = results_dir / f"test_results_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    logger.info(f"\n{'='*80}\nTEST RUN SUMMARY\n{'='*80}")
    logger.info(f"Duration: {duration:.2f} seconds")
    logger.info(f"Total tests: {result.testsRun}")
    logger.info(f"Successful: {len(result.results['success'])}")
    logger.info(f"Failed: {len(result.results['failure'])}")
    logger.info(f"Errors: {len(result.results['error'])}")
    logger.info(f"Skipped: {len(result.results['skipped'])}")
    logger.info(f"Pass rate: {pass_rate:.2f}%")
    logger.info(f"Overall result: {summary['overall_result']}")
    logger.info(f"Detailed results saved to: {result_file}")
    
    return summary


if __name__ == "__main__":
    run_all_tests()

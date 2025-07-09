"""
Performance Tests for Omani-Therapist-Voice

This module contains test cases to validate the system's real-time
performance capabilities and end-to-end latency.
"""

import os
import sys
import time
import logging
import unittest
import tempfile
import asyncio
import threading
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import required modules
try:
    from speech_to_Text.whisper import create_omani_stt
    from llm.openai_client import create_azure_omani_llm
    from Text_to_Speech.arabic_tts import OmaniTTS
    from api.main import app  # FastAPI app
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    raise


class PerformanceTests(unittest.TestCase):
    """Test suite for system performance and latency."""
    
    def setUp(self):
        """Set up the test environment."""
        # Initialize components
        self.stt = create_omani_stt()
        self.llm = create_azure_omani_llm()
        self.tts = OmaniTTS()
        
        # Test data - audio files and text inputs
        self.test_data = {
            # Audio inputs (paths to audio files)
            "audio_inputs": {
                "short": "test_data/audio/short_input.mp3",  # ~3 seconds
                "medium": "test_data/audio/medium_input.mp3",  # ~10 seconds
                "long": "test_data/audio/long_input.mp3",  # ~20 seconds
            },
            
            # Text inputs for different complexity levels
            "text_inputs": {
                "simple": "أشعر بالقلق اليوم.",  # Simple statement
                "medium": "أواجه صعوبة في التركيز في العمل. أفكاري مشتتة وأشعر بالتوتر.",  # Medium complexity
                "complex": """أواجه مشكلة معقدة في علاقتي مع زوجتي وأهلها. يتدخلون في قراراتنا المالية ويضغطون علينا 
                لاتخاذ خيارات لا نرغب فيها. أشعر بالإحباط والغضب لكنني لا أريد أن أتسبب في مشكلة عائلية. 
                كيف يمكنني التعامل مع هذا الموقف بطريقة تحترم الجميع؟"""  # Complex scenario
            }
        }
        
        # Create test data directory if it doesn't exist
        os.makedirs(Path(__file__).parent / "test_results", exist_ok=True)
    
    def test_response_time(self):
        """Test PT-01: End-to-end response time for a conversation turn."""
        # Use medium complexity text input
        text_input = self.test_data["text_inputs"]["medium"]
        
        # Measure complete processing pipeline time
        start_time = time.time()
        
        # Step 1: Generate LLM response
        llm_response = self.llm.generate_response(text_input)
        
        # Step 2: Generate speech from response
        audio_output = self.tts.synthesize_speech(llm_response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Log results
        logger.info(f"End-to-End Response Time Test:")
        logger.info(f"User input: {text_input}")
        logger.info(f"LLM response: {llm_response}")
        logger.info(f"Total processing time: {total_time:.2f} seconds")
        
        # Assert maximum end-to-end time (20 seconds as per requirements)
        self.assertLessEqual(total_time, 20, 
                           "End-to-end response time exceeded 20 seconds limit")
    
    def test_long_session(self):
        """Test PT-02: Performance during a long conversation session."""
        # Simulate a 30+ minute conversation with multiple turns
        conversation_duration = 0
        turn_count = 0
        max_duration = 30 * 60  # 30 minutes in seconds
        
        test_inputs = [
            self.test_data["text_inputs"]["simple"],
            self.test_data["text_inputs"]["medium"],
            self.test_data["text_inputs"]["complex"]
        ]
        
        # Metrics to track
        response_times = []
        memory_usage = []
        
        # Log start
        logger.info(f"Long Session Test: Starting")
        session_start = time.time()
        
        # Run conversation turns until we reach desired duration
        while conversation_duration < max_duration and turn_count < 20:  # Cap at 20 turns for test practicality
            # Select input (rotating through available inputs)
            text_input = test_inputs[turn_count % len(test_inputs)]
            
            # Measure turn time
            turn_start = time.time()
            
            # Process turn
            llm_response = self.llm.generate_response(text_input)
            audio_output = self.tts.synthesize_speech(llm_response)
            
            # Calculate turn time
            turn_time = time.time() - turn_start
            response_times.append(turn_time)
            
            # Get memory usage (simplified)
            # In a real test, use a proper memory profiler
            memory_usage.append(self._get_memory_usage())
            
            # Log turn details
            logger.info(f"Turn {turn_count + 1} - Time: {turn_time:.2f}s - Response length: {len(llm_response)}")
            
            # Update tracking variables
            conversation_duration = time.time() - session_start
            turn_count += 1
            
            # Add simulated user thinking time between turns
            time.sleep(1)
        
        # Calculate metrics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # Calculate performance degradation
        initial_times = response_times[:3]
        final_times = response_times[-3:]
        avg_initial = sum(initial_times) / len(initial_times)
        avg_final = sum(final_times) / len(final_times)
        degradation = (avg_final - avg_initial) / avg_initial * 100 if avg_initial > 0 else 0
        
        # Log results
        logger.info(f"Long Session Results:")
        logger.info(f"Total duration: {conversation_duration:.2f} seconds")
        logger.info(f"Total turns: {turn_count}")
        logger.info(f"Average response time: {avg_response_time:.2f} seconds")
        logger.info(f"Maximum response time: {max_response_time:.2f} seconds")
        logger.info(f"Performance degradation: {degradation:.2f}%")
        
        # Assert performance stability
        self.assertLessEqual(degradation, 20, 
                           "Performance degradation exceeds 20% threshold")
        self.assertLessEqual(max_response_time, 30, 
                           "Maximum response time exceeded 30 seconds")
    
    def test_stress_testing(self):
        """Test PT-03: System behavior under rapid sequential inputs."""
        # Define rapid inputs (multiple queries in quick succession)
        rapid_inputs = [
            self.test_data["text_inputs"]["simple"],
            self.test_data["text_inputs"]["simple"],
            self.test_data["text_inputs"]["medium"],
            self.test_data["text_inputs"]["simple"],
            self.test_data["text_inputs"]["complex"],
        ]
        
        # Metrics to track
        success_count = 0
        failure_count = 0
        response_times = []
        
        # Log start
        logger.info(f"Stress Test: Starting with {len(rapid_inputs)} rapid inputs")
        
        # Process all inputs with minimal delay
        for i, text_input in enumerate(rapid_inputs):
            try:
                # Measure processing time
                start_time = time.time()
                
                # Process input
                llm_response = self.llm.generate_response(text_input)
                
                # Ensure we got a valid response
                if llm_response and len(llm_response) > 10:
                    success_count += 1
                else:
                    failure_count += 1
                    logger.warning(f"Input {i+1} produced insufficient response")
                
                # Calculate processing time
                process_time = time.time() - start_time
                response_times.append(process_time)
                
                # Log result
                logger.info(f"Input {i+1} - Time: {process_time:.2f}s - Success: {bool(llm_response)}")
                
                # Minimal delay between requests (250ms)
                time.sleep(0.25)
                
            except Exception as e:
                failure_count += 1
                logger.error(f"Input {i+1} failed with error: {e}")
        
        # Calculate success rate
        success_rate = success_count / len(rapid_inputs) * 100
        
        # Log results
        logger.info(f"Stress Test Results:")
        logger.info(f"Success rate: {success_rate:.2f}%")
        logger.info(f"Average response time: {sum(response_times) / len(response_times):.2f}s")
        
        # Assert minimum success rate
        self.assertGreaterEqual(success_rate, 90, 
                              "Stress test success rate below 90%")
    
    def test_network_variation(self):
        """Test PT-04: Performance under varied network conditions."""
        # This test simulates different network conditions
        # In a real test environment, use network throttling tools
        
        # Define network conditions to simulate
        network_conditions = [
            {"name": "Good", "latency": 0, "packet_loss": 0},  # Good connection
            {"name": "Average", "latency": 0.1, "packet_loss": 0.01},  # Average connection
            {"name": "Poor", "latency": 0.3, "packet_loss": 0.05},  # Poor connection
        ]
        
        text_input = self.test_data["text_inputs"]["medium"]
        results = []
        
        # Test under each network condition
        for condition in network_conditions:
            logger.info(f"Testing under {condition['name']} network conditions")
            
            # Apply simulated network condition
            self._simulate_network_condition(condition["latency"], condition["packet_loss"])
            
            # Measure response time
            try:
                start_time = time.time()
                
                # Process request
                llm_response = self.llm.generate_response(text_input)
                
                # Calculate time
                total_time = time.time() - start_time
                
                # Store result
                results.append({
                    "condition": condition["name"],
                    "time": total_time,
                    "success": bool(llm_response and len(llm_response) > 10),
                    "response_length": len(llm_response) if llm_response else 0
                })
                
                # Log result
                logger.info(f"{condition['name']} condition - Time: {total_time:.2f}s - Success: {results[-1]['success']}")
                
            except Exception as e:
                logger.error(f"Failed under {condition['name']} condition: {e}")
                results.append({
                    "condition": condition["name"],
                    "time": None,
                    "success": False,
                    "error": str(e)
                })
        
        # Reset network simulation
        self._simulate_network_condition(0, 0)
        
        # Log overall results
        logger.info(f"Network Variation Results:")
        for result in results:
            time_str = f"{result['time']:.2f}s" if result['time'] is not None else "N/A"
            logger.info(f"{result['condition']}: {time_str} - Success: {result['success']}")
        
        # Assert minimum success requirements
        successful_conditions = sum(1 for r in results if r["success"])
        self.assertGreaterEqual(successful_conditions, 2, 
                              "Failed to handle at least 2 network conditions")
    
    def test_error_recovery(self):
        """Test PT-05: Recovery from system interruptions."""
        text_input = self.test_data["text_inputs"]["complex"]
        
        # First, establish baseline with normal operation
        logger.info("Establishing baseline response")
        try:
            baseline_response = self.llm.generate_response(text_input)
            logger.info(f"Baseline response length: {len(baseline_response)}")
        except Exception as e:
            logger.error(f"Baseline failed: {e}")
            self.fail("Could not establish baseline response")
        
        # Now test with forced interruption
        logger.info("Testing with forced interruption")
        
        # Set up async interruption
        async def force_interruption():
            # Start normal processing
            process_task = asyncio.create_task(
                self._async_process_response(text_input)
            )
            
            # Wait briefly then interrupt
            await asyncio.sleep(1.0)
            
            # Simulate interruption by canceling task
            process_task.cancel()
            
            try:
                await process_task
            except asyncio.CancelledError:
                logger.info("Task successfully cancelled")
                
            # Attempt recovery
            recovery_start = time.time()
            recovery_response = self.llm.generate_response(text_input, 
                                                         recovery_mode=True)
            recovery_time = time.time() - recovery_start
            
            return {
                "success": bool(recovery_response and len(recovery_response) > 10),
                "time": recovery_time,
                "response_length": len(recovery_response) if recovery_response else 0
            }
        
        # Run the interruption test
        try:
            # Use asyncio.run or get_event_loop depending on Python version
            try:
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(force_interruption())
            except RuntimeError:
                result = asyncio.run(force_interruption())
                
            # Log results
            logger.info(f"Error Recovery Results:")
            logger.info(f"Recovery success: {result['success']}")
            logger.info(f"Recovery time: {result['time']:.2f}s")
            logger.info(f"Response length: {result['response_length']}")
            
            # Assert successful recovery
            self.assertTrue(result["success"], "Failed to recover from interruption")
            self.assertLessEqual(result["time"], 25, 
                               "Recovery time exceeded 25 seconds")
            
        except Exception as e:
            logger.error(f"Interruption test failed: {e}")
            self.fail(f"Error during interruption test: {e}")
    
    async def _async_process_response(self, text_input):
        """Process a response asynchronously for interruption testing."""
        return self.llm.generate_response(text_input)
    
    def _get_memory_usage(self) -> float:
        """
        Get current memory usage in MB.
        
        Returns:
            Memory usage in MB
        """
        # This is a simplified placeholder
        # In real implementation, use proper memory profiling
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0.0
    
    def _simulate_network_condition(self, latency: float, packet_loss: float):
        """
        Simulate network conditions by adding latency and packet loss.
        
        Args:
            latency: Latency in seconds to add per request
            packet_loss: Probability (0-1) of packet loss
        """
        # This is a mock implementation
        # In a real test environment, use network throttling tools
        
        # Store original methods
        if not hasattr(self, '_original_send'):
            # Save original methods only on first call
            import httpx
            self._original_send = httpx.Client.send
        
        # Apply network condition simulation by monkey patching
        if latency > 0 or packet_loss > 0:
            def delayed_send(self, request, **kwargs):
                # Simulate latency
                if latency > 0:
                    time.sleep(latency)
                
                # Simulate packet loss
                if packet_loss > 0 and random.random() < packet_loss:
                    raise Exception("Simulated packet loss")
                
                # Call original method
                return self._original_send(request, **kwargs)
            
            # Apply monkey patch
            import httpx
            httpx.Client.send = delayed_send
        else:
            # Restore original method
            import httpx
            httpx.Client.send = self._original_send


if __name__ == "__main__":
    unittest.main()

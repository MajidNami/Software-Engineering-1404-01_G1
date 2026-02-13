#!/usr/bin/env python
"""
Test script for Team7 Speaking Assessment API
Tests the complete workflow: Audio Upload -> ASR -> LLM -> Evaluation
"""

import requests
import json
import os
import sys

# Configuration
BASE_URL = "http://localhost:8000/team7"
API_KEY = "test-api-key"  # Replace with actual API key

def test_ping():
    """Test health check endpoint"""
    print("\n=== Testing Ping Endpoint ===")
    try:
        response = requests.get(
            f"{BASE_URL}/ping/",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_speaking_submission(audio_file_path, user_id, question_id):
    """Test speaking evaluation endpoint"""
    print("\n=== Testing Speaking Submission ===")
    
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found: {audio_file_path}")
        return False
    
    try:
        # Prepare multipart/form-data
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'audio_file': (os.path.basename(audio_file_path), audio_file, 'audio/wav')
            }
            data = {
                'user_id': user_id,
                'question_id': question_id
            }
            
            print(f"Uploading: {audio_file_path}")
            print(f"File size: {os.path.getsize(audio_file_path) / 1024:.2f} KB")
            
            response = requests.post(
                f"{BASE_URL}/api/v1/evaluate/speaking/",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {API_KEY}"}
            )
        
        print(f"\nStatus: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("\n✓ Speaking evaluation successful!")
            print(f"  Evaluation ID: {result.get('evaluation_id')}")
            print(f"  Overall Score: {result.get('overall_score')}")
            print(f"  Transcript: {result.get('transcript', '')[:100]}...")
            print(f"  Criteria: {len(result.get('criteria', []))} metrics")
            return True
        else:
            print(f"\n✗ Error: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_invalid_file():
    """Test validation with invalid file"""
    print("\n=== Testing Invalid File Validation ===")
    
    try:
        # Create a fake large file (>10MB)
        files = {
            'audio_file': ('test.wav', b'X' * (11 * 1024 * 1024), 'audio/wav')  # 11MB
        }
        data = {
            'user_id': 'test-user-123',
            'question_id': 'test-question-123'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/evaluate/speaking/",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Should return 400 error
        if response.status_code == 400:
            print("\n✓ File size validation working correctly")
            return True
        else:
            print("\n✗ Expected 400 error for oversized file")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_missing_audio():
    """Test error handling when audio file is missing"""
    print("\n=== Testing Missing Audio File ===")
    
    try:
        data = {
            'user_id': 'test-user-123',
            'question_id': 'test-question-123'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/evaluate/speaking/",
            data=data,
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 400:
            print("\n✓ Missing audio file validation working correctly")
            return True
        else:
            print("\n✗ Expected 400 error for missing audio")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Team7 Speaking Assessment API Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Ping
    results.append(("Ping", test_ping()))
    
    # Test 2: Missing audio file
    results.append(("Missing Audio", test_missing_audio()))
    
    # Test 3: Invalid file size
    results.append(("File Size Validation", test_invalid_file()))
    
    # Test 4: Valid speaking submission (if audio file provided)
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
        user_id = sys.argv[2] if len(sys.argv) > 2 else "test-user-123"
        question_id = sys.argv[3] if len(sys.argv) > 3 else "test-question-123"
        results.append(("Speaking Submission", test_speaking_submission(audio_path, user_id, question_id)))
    else:
        print("\nSkipping speaking submission test (no audio file provided)")
        print("Usage: python test_speaking_api.py <audio_file.wav> [user_id] [question_id]")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

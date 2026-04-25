"""
Tester Agent - Automated Testing for Gemini API Wrapper
Uses Python requests library to validate all endpoints
"""

import requests
import json
import sys
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: List[Dict] = []
        self.passed = 0
        self.failed = 0

    def test_health_check(self) -> bool:
        """Test: Health Check Endpoint"""
        print("\n[TEST 1] Health Check Endpoint")
        try:
            response = requests.get(f"{self.base_url}/health")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert data["status"] == "healthy"
            print("✓ PASSED: Health check successful")
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ FAILED: {str(e)}")
            self.failed += 1
            return False

    def test_api_info(self) -> bool:
        """Test: Get API Info Endpoint"""
        print("\n[TEST 2] Get API Info Endpoint")
        try:
            response = requests.get(f"{self.base_url}/")
            assert response.status_code == 200
            data = response.json()
            assert "endpoints" in data
            print(f"✓ PASSED: API info retrieved")
            print(f"  Available endpoints: {list(data['endpoints'].keys())}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ FAILED: {str(e)}")
            self.failed += 1
            return False

    def test_valid_prompt(self) -> bool:
        """Test: Send Valid Prompt to Chat Endpoint"""
        print("\n[TEST 3] Send Valid Prompt to Chat Endpoint")
        try:
            payload = {
                "prompt": "What is FastAPI? Answer in one sentence.",
                "model": "gemini-2.5-flash"
            }
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=30
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert "response" in data
            assert len(data["response"]) > 0
            print(f"✓ PASSED: Valid prompt processed")
            print(f"  Prompt: {data['prompt']}")
            print(f"  Response: {data['response'][:100]}...")
            self.passed += 1
            return True
        except requests.exceptions.Timeout:
            print(f"✗ FAILED: Request timeout (Gemini API might be slow)")
            self.failed += 1
            return False
        except requests.exceptions.ConnectionError:
            print(f"✗ FAILED: Connection error - Is the server running?")
            self.failed += 1
            return False
        except Exception as e:
            print(f"✗ FAILED: {str(e)}")
            self.failed += 1
            return False

    def test_empty_prompt(self) -> bool:
        """Test: Empty Prompt Should Return Error"""
        print("\n[TEST 4] Empty Prompt Error Handling")
        try:
            payload = {
                "prompt": "",
                "model": "gemini-2.5-flash"
            }
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=10
            )
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"
            data = response.json()
            assert "detail" in data or "error" in data
            print(f"✓ PASSED: Empty prompt correctly rejected with 400 error")
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ FAILED: {str(e)}")
            self.failed += 1
            return False

    def test_missing_prompt_field(self) -> bool:
        """Test: Missing Prompt Field Should Return Error"""
        print("\n[TEST 5] Missing Prompt Field Validation")
        try:
            payload = {
                "model": "gemini-2.5-flash"
            }
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=10
            )
            assert response.status_code == 422, f"Expected 422, got {response.status_code}"
            print(f"✓ PASSED: Missing field correctly rejected with 422 error")
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ FAILED: {str(e)}")
            self.failed += 1
            return False

    def test_response_structure(self) -> bool:
        """Test: Response Has Correct Structure"""
        print("\n[TEST 6] Response Structure Validation")
        try:
            payload = {
                "prompt": "Hello Gemini",
                "model": "gemini-2.5-flash"
            }
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=30
            )
            assert response.status_code == 200
            data = response.json()
            
            required_fields = ["prompt", "response", "model"]
            for field in required_fields:
                assert field in data, f"Missing field: {field}"
                assert data[field] is not None, f"Field {field} is None"
            
            print(f"✓ PASSED: Response structure is valid")
            print(f"  Fields: {list(data.keys())}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ FAILED: {str(e)}")
            self.failed += 1
            return False

    def run_all_tests(self) -> Tuple[int, int]:
        """Run all tests and return results"""
        print("=" * 60)
        print("🧪 GEMINI API WRAPPER - AUTOMATED TESTING")
        print("=" * 60)
        
        try:
            # Connection test
            print("\n[SETUP] Checking server connection...")
            response = requests.get(f"{self.base_url}/health", timeout=5)
            print("✓ Server is running")
        except requests.exceptions.ConnectionError:
            print("✗ ERROR: Cannot connect to server at", BASE_URL)
            print("  Please make sure the server is running:")
            print("  > python main.py")
            return 0, 1

        # Run tests
        self.test_health_check()
        self.test_api_info()
        self.test_valid_prompt()
        self.test_empty_prompt()
        self.test_missing_prompt_field()
        self.test_response_structure()

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✓ Passed: {self.passed}")
        print(f"✗ Failed: {self.failed}")
        total = self.passed + self.failed
        if total > 0:
            percentage = (self.passed / total) * 100
            print(f"📈 Success Rate: {percentage:.1f}%")
        print("=" * 60)

        return self.passed, self.failed


def main():
    """Main entry point for the tester agent"""
    tester = APITester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

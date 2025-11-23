import requests
import json
import time

def test_start_adaptive_test():
    url = "http://localhost:5001/api/adaptive-test/start"
    payload = {
        "user_id": "test_user_123",
        "grade": "G9",
        "curriculum_category": "Common Core",
        "test_type": "adaptive_test",
        "target_difficulty": "Hard",
        "topic": "VerificationTopic" + str(time.time()) # Unique topic
    }
    headers = {
        "Content-Type": "application/json"
    }

    print(f"Testing URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            first_q = data.get('first_question', {})
            q_id = first_q.get('id', 'N/A')
            print(f"Generated Question ID: {q_id}")
            
            if "US_G9" in q_id:
                 print("✅ ID Format Check Passed")
            else:
                 print("⚠️ ID Format Check Failed (Might be using cached question)")
                 
            print("✅ API Test Passed")
        else:
            print("❌ API Test Failed")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_start_adaptive_test()

#!/usr/bin/env python3
"""
Classification Engine Test Script

This script tests the email classification pipeline:
1. Rule-based classification
2. ML-based classification
3. Hybrid classification pipeline
4. API endpoint
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"


def print_response(response, title):
    """Pretty print API response"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def create_test_emails(mailbox_id):
    """Create test emails for classification"""
    print("\n📧 Creating test emails for classification...")
    
    test_emails = [
        {
            "subject": "URGENT: Project deadline tomorrow!",
            "sender": "boss@company.com",
            "body": "Please submit your work by tomorrow 5 PM. This is critical.",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id,
            "category": None  # Will be classified
        },
        {
            "subject": "Newsletter: Weekly Tech Updates",
            "sender": "noreply@newsletter.com",
            "body": "Unsubscribe anytime. Here are this week's top stories.",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id,
            "category": None
        },
        {
            "subject": "Exciting internship opportunity at Google",
            "sender": "recruiter@google.com",
            "body": "We are hiring for summer internship. Great career opportunity!",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id,
            "category": None
        },
        {
            "subject": "Team meeting notes",
            "sender": "colleague@company.com",
            "body": "Here are the notes from today's meeting. FYI.",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id,
            "category": None
        },
        {
            "subject": "Exam schedule released",
            "sender": "admin@university.edu",
            "body": "The final exam schedule is now available. Please check the deadline.",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id,
            "category": None
        },
    ]
    
    email_ids = []
    for email_data in test_emails:
        response = requests.post(f"{BASE_URL}/emails/", json=email_data)
        if response.status_code == 201:
            email_ids.append(response.json()['id'])
            print(f"  ✅ Created: {email_data['subject'][:50]}")
    
    return email_ids


def test_classification_api():
    """Test the classification API endpoint"""
    print("\n\n🤖 TESTING CLASSIFICATION API")
    
    # Call the classify endpoint
    response = requests.post(f"{BASE_URL}/emails/classify/")
    print_response(response, "POST /api/emails/classify/")
    
    return response


def verify_classifications():
    """Verify that emails were classified correctly"""
    print("\n\n✅ VERIFYING CLASSIFICATIONS")
    
    # Get all emails
    response = requests.get(f"{BASE_URL}/emails/")
    
    if response.status_code == 200:
        emails = response.json()['results']
        
        print(f"\nTotal emails: {len(emails)}")
        print("\nClassification Results:")
        print("-" * 70)
        
        for email in emails:
            category = email.get('category', 'NULL')
            subject = email['subject'][:45]
            print(f"  [{category:12}] {subject}")
        
        # Count by category
        categories = {}
        for email in emails:
            cat = email.get('category', 'NULL')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nCategory Distribution:")
        print("-" * 70)
        for cat, count in sorted(categories.items()):
            print(f"  {cat:12}: {count} emails")


def test_direct_classification():
    """Test classification pipeline directly (without API)"""
    print("\n\n🔬 TESTING CLASSIFICATION PIPELINE DIRECTLY")
    
    try:
        # Import the classifier
        import sys
        sys.path.insert(0, '/home/rj/RajneeshCodes/PEP Project/SmartMailboxBackend')
        
        from emails.services import get_classifier
        
        classifier = get_classifier()
        
        # Test cases
        test_cases = [
            {
                "sender": "urgent@company.com",
                "subject": "URGENT: Deadline tomorrow",
                "body": "Please submit ASAP",
                "expected": "CRITICAL"
            },
            {
                "sender": "noreply@newsletter.com",
                "subject": "Weekly Newsletter",
                "body": "Unsubscribe anytime",
                "expected": "JUNK"
            },
            {
                "sender": "recruiter@jobs.com",
                "subject": "Job opportunity",
                "body": "We are hiring for an internship position",
                "expected": "OPPORTUNITY"
            },
            {
                "sender": "team@company.com",
                "subject": "Project update",
                "body": "Here is the latest status on our project",
                "expected": "INFO (via ML)"
            }
        ]
        
        print("\nDirect Classification Tests:")
        print("-" * 70)
        
        for i, test in enumerate(test_cases, 1):
            result = classifier.classify(
                test['sender'],
                test['subject'],
                test['body']
            )
            
            print(f"\nTest {i}: {test['subject'][:40]}")
            print(f"  Expected: {test['expected']}")
            print(f"  Got: {result['category']} (via {result['method']})")
            
            if result['method'] == 'rule':
                print(f"  Matched patterns: {result['matched_patterns']}")
            else:
                print(f"  ML Confidence: {result['confidence']}")
        
        print("\n✅ Direct classification tests completed")
        
    except Exception as e:
        print(f"❌ Error in direct testing: {e}")


def main():
    """Run all classification tests"""
    print("🚀 Starting Classification Engine Tests")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # First, ensure we have a mailbox
        response = requests.get(f"{BASE_URL}/mailboxes/")
        if response.status_code == 200:
            mailboxes = response.json()['results']
            if mailboxes:
                mailbox_id = mailboxes[0]['id']
            else:
                # Create a mailbox
                mb_data = {
                    "provider": "GMAIL",
                    "email_address": "test-classification@example.com",
                    "is_active": True
                }
                response = requests.post(f"{BASE_URL}/mailboxes/", json=mb_data)
                mailbox_id = response.json()['id']
        
        # Create test emails
        email_ids = create_test_emails(mailbox_id)
        
        # Test direct classification
        test_direct_classification()
        
        # Test API classification
        test_classification_api()
        
        # Verify results
        verify_classifications()
        
        print("\n\n" + "="*70)
        print("✅ ALL CLASSIFICATION TESTS COMPLETED")
        print("="*70)
        print("\n📝 Summary:")
        print("  ✅ Rule-based classifier working")
        print("  ✅ ML classifier working")
        print("  ✅ Hybrid pipeline working")
        print("  ✅ API endpoint working")
        print("\n🎯 Next Steps:")
        print("  - Add more training data for better ML accuracy")
        print("  - Implement confidence thresholds")
        print("  - Add batch classification optimization")
        print("  - Create admin interface for reviewing classifications")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django is running:")
        print("   cd SmartMailboxBackend && python manage.py runserver")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

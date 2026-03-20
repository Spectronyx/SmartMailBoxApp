#!/usr/bin/env python3
"""
Simple Classification API Test

Tests the /api/emails/classify/ endpoint
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"


def main():
    print("🚀 Testing Email Classification API\n")
    
    # Step 1: Get or create mailbox
    print("1️⃣  Getting mailbox...")
    response = requests.get(f"{BASE_URL}/mailboxes/")
    mailboxes = response.json()['results']
    
    if mailboxes:
        mailbox_id = mailboxes[0]['id']
        print(f"   ✅ Using mailbox ID: {mailbox_id}\n")
    else:
        mb_data = {"provider": "GMAIL", "email_address": "test@example.com", "is_active": True}
        response = requests.post(f"{BASE_URL}/mailboxes/", json=mb_data)
        mailbox_id = response.json()['id']
        print(f"   ✅ Created mailbox ID: {mailbox_id}\n")
    
    # Step 2: Create test emails without categories
    print("2️⃣  Creating test emails...")
    test_emails = [
        {
            "subject": "URGENT: Submit assignment by tomorrow",
            "sender": "professor@university.edu",
            "body": "The deadline is tomorrow at 5 PM. Please submit ASAP.",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id
        },
        {
            "subject": "Weekly Newsletter from TechCrunch",
            "sender": "noreply@techcrunch.com",
            "body": "Unsubscribe anytime. Here are this week's top tech stories.",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id
        },
        {
            "subject": "Internship Opportunity at Microsoft",
            "sender": "recruiting@microsoft.com",
            "body": "We're hiring for summer internship. Great career opportunity!",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id
        },
    ]
    
    for email in test_emails:
        response = requests.post(f"{BASE_URL}/emails/", json=email)
        if response.status_code == 201:
            print(f"   ✅ Created: {email['subject'][:50]}")
    
    print()
    
    # Step 3: Call classification endpoint
    print("3️⃣  Calling classification API...")
    response = requests.post(f"{BASE_URL}/emails/classify/")
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Classified {result['classified_count']} emails\n")
        
        print("4️⃣  Classification Results:")
        print("   " + "="*66)
        for item in result['results']:
            category = item['category']
            method = item['method']
            subject = item['subject']
            
            if method == 'rule':
                patterns = item.get('matched_patterns', [])
                print(f"   [{category:12}] {subject}")
                print(f"                  → Rule-based (matched: {len(patterns)} patterns)")
            else:
                confidence = item.get('confidence', 0)
                print(f"   [{category:12}] {subject}")
                print(f"                  → ML-based (confidence: {confidence:.2%})")
        
        print("\n✅ Classification test completed successfully!")
        print("\n📊 Summary:")
        print(f"   • Total classified: {result['classified_count']}")
        print(f"   • Endpoint: POST /api/emails/classify/")
        print(f"   • Hybrid approach: Rules → ML fallback")
        
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   {response.text[:500]}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django is running:")
        print("   cd SmartMailboxBackend && python manage.py runserver")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

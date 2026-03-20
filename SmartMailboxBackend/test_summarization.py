#!/usr/bin/env python3
"""
Summarization API Test

Tests the /api/emails/summarize/ endpoint
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"


def main():
    print("🚀 Testing Email Summarization API\n")
    
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
    
    # Step 2: Create test emails with long content
    print("2️⃣  Creating test emails (long content)...")
    
    # Long text about Python (from Wikipedia intro)
    python_text = """
    Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation. Python is dynamically typed and garbage-collected. It supports multiple programming paradigms, including structured (particularly procedural), object-oriented and functional programming. It is often described as a "batteries included" language due to its comprehensive standard library.
    Guido van Rossum began working on Python in the late 1980s as a successor to the ABC programming language and first released it in 1991 as Python 0.9.0. Python 2.0 was released in 2000. Python 3.0, released in 2008, was a major revision not completely backward-compatible with earlier versions. Python 2.7.18, released in 2020, was the last release of Python 2.
    Python consistently ranks as one of the most popular programming languages. It is widely used in machine learning, data science, web development, automation, and many other fields. The language is managed by the Python Software Foundation.
    Detailed description of features include easy syntax, extensive libraries, community support, and cross-platform compatibility. Many large organizations use Python, including Wikipedia, Google, Yahoo!, CERN, NASA, Facebook, Amazon, Instagram, Spotify, and Reddit.
    """
    
    # Short text (should be skipped)
    short_text = "This is a very short email. It should not be summarized."
    
    test_emails = [
        {
            "subject": "Article: History of Python",
            "sender": "news@techhistory.com",
            "body": python_text,
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id,
            "category": "INFO"  # Pre-classified
        },
        {
            "subject": "Short Note",
            "sender": "friend@email.com",
            "body": short_text,
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id,
            "category": "INFO"
        },
    ]
    
    for email in test_emails:
        response = requests.post(f"{BASE_URL}/emails/", json=email)
        if response.status_code == 201:
            print(f"   ✅ Created: {email['subject'][:50]}")
    
    print()
    
    # Step 3: Call summarization endpoint
    print("3️⃣  Calling summarization API...")
    response = requests.post(f"{BASE_URL}/emails/summarize/")
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Summarized {result['summarized_count']} emails\n")
        
        print("4️⃣  Summarization Results:")
        print("   " + "="*80)
        
        for item in result['results']:
            subject = item['subject']
            summary = item['summary']
            
            print(f"   Subject: {subject}")
            print(f"   Summary: {summary}\n")
            print("   " + "-"*80)
            
        print("\n✅ Summarization test completed successfully!")
        print("\n📊 Summary:")
        print(f"   • Total summarized: {result['summarized_count']}")
        print(f"   • Endpoint: POST /api/emails/summarize/")
        print(f"   • Method: Extractive (Frequency-based)")
        
        if result['summarized_count'] == 1:
            print("   • Note: Short email was correctly skipped!")
        
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

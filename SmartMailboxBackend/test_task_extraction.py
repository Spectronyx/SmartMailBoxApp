#!/usr/bin/env python3
"""
Task Extraction API Test

Tests the /api/emails/extract-tasks/ endpoint
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"


def main():
    print("🚀 Testing Email Task Extraction API\n")
    
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
    
    # Step 2: Create test emails with actionable content
    print("2️⃣  Creating test emails with actions and deadlines...")
    
    test_emails = [
        {
            "subject": "Assignment Submission Reminder",
            "sender": "professor@university.edu",
            "body": "Please submit your final project report by next Friday at 5 PM. "
                    "Make sure to include all the required sections.",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id,
            "category": "CRITICAL"
        },
        {
            "subject": "Internship Application",
            "sender": "hr@techcorp.com",
            "body": "We're excited about your interest! Please apply through our portal "
                    "before January 31, 2026. Upload your resume and cover letter.",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id,
            "category": "OPPORTUNITY"
        },
        {
            "subject": "Meeting Tomorrow",
            "sender": "manager@company.com",
            "body": "Don't forget to attend the team meeting tomorrow at 10 AM. "
                    "We'll discuss the Q1 roadmap.",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id,
            "category": "INFO"
        },
        {
            "subject": "Conference Registration",
            "sender": "events@conference.org",
            "body": "Register for the AI Summit 2026 by February 15. "
                    "Early bird discount available!",
            "received_at": datetime.now().isoformat(),
            "mailbox": mailbox_id,
            "category": "OPPORTUNITY"
        },
    ]
    
    for email in test_emails:
        response = requests.post(f"{BASE_URL}/emails/", json=email)
        if response.status_code == 201:
            print(f"   ✅ Created: {email['subject'][:50]}")
    
    print()
    
    # Step 3: Call task extraction endpoint
    print("3️⃣  Calling task extraction API...")
    response = requests.post(f"{BASE_URL}/emails/extract-tasks/")
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Created {result['tasks_created']} tasks\n")
        
        print("4️⃣  Extraction Results:")
        print("   " + "="*80)
        
        for item in result['results']:
            subject = item['subject']
            action = item['action_text']
            deadline = item.get('deadline')
            
            print(f"   Subject: {subject}")
            print(f"   Action: {action}")
            if deadline:
                print(f"   Deadline: {deadline}")
            else:
                print(f"   Deadline: No specific deadline found")
            print("   " + "-"*80)
        
        print("\n✅ Task extraction test completed successfully!")
        print("\n📊 Summary:")
        print(f"   • Tasks created: {result['tasks_created']}")
        print(f"   • Endpoint: POST /api/emails/extract-tasks/")
        print(f"   • Date Parser: dateparser (handles relative dates)")
        print(f"   • Action Detection: Rule-based verb matching")
        
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

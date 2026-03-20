#!/usr/bin/env python3
"""
API Test Script for Smart Mailbox Summarizer Backend

This script tests the core API endpoints to verify functionality.
Run this after starting the Django development server.
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"


def print_response(response, title):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_mailbox_api():
    """Test Mailbox CRUD operations"""
    print("\n\n🔧 TESTING MAILBOX API")
    
    # Create a mailbox
    mailbox_data = {
        "provider": "GMAIL",
        "email_address": "test@example.com",
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/mailboxes/", json=mailbox_data)
    print_response(response, "CREATE MAILBOX")
    
    if response.status_code == 201:
        mailbox_id = response.json()['id']
        
        # List mailboxes
        response = requests.get(f"{BASE_URL}/mailboxes/")
        print_response(response, "LIST MAILBOXES")
        
        # Get specific mailbox
        response = requests.get(f"{BASE_URL}/mailboxes/{mailbox_id}/")
        print_response(response, "GET MAILBOX DETAIL")
        
        return mailbox_id
    return None


def test_email_api(mailbox_id):
    """Test Email API operations"""
    print("\n\n📧 TESTING EMAIL API")
    
    # Create test emails
    emails_data = [
        {
            "subject": "Urgent: Project Deadline Tomorrow",
            "sender": "boss@company.com",
            "body": "Please submit the quarterly report by tomorrow 5 PM.",
            "received_at": datetime.now().isoformat(),
            "category": "CRITICAL",
            "mailbox": mailbox_id
        },
        {
            "subject": "New Job Opportunity",
            "sender": "recruiter@jobs.com",
            "body": "We have an exciting opportunity for you.",
            "received_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "category": "OPPORTUNITY",
            "mailbox": mailbox_id
        },
        {
            "subject": "Newsletter: Tech Updates",
            "sender": "newsletter@tech.com",
            "body": "Here are this week's top tech stories.",
            "received_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "category": "INFO",
            "mailbox": mailbox_id
        }
    ]
    
    email_ids = []
    for email_data in emails_data:
        response = requests.post(f"{BASE_URL}/emails/", json=email_data)
        if response.status_code == 201:
            email_ids.append(response.json()['id'])
    
    print(f"✅ Created {len(email_ids)} test emails")
    
    # Test unified inbox
    response = requests.get(f"{BASE_URL}/emails/")
    print_response(response, "UNIFIED INBOX (All Emails)")
    
    # Test mailbox-specific emails
    response = requests.get(f"{BASE_URL}/emails/mailbox/{mailbox_id}/")
    print_response(response, f"EMAILS FOR MAILBOX {mailbox_id}")
    
    # Test filtering by category
    response = requests.get(f"{BASE_URL}/emails/?category=CRITICAL")
    print_response(response, "FILTER: CRITICAL EMAILS")
    
    return email_ids


def test_task_api(email_ids):
    """Test Task API operations"""
    print("\n\n✅ TESTING TASK API")
    
    if not email_ids:
        print("⚠️  No emails available to create tasks")
        return
    
    # Create a task
    task_data = {
        "action_text": "Submit quarterly report",
        "deadline": (datetime.now() + timedelta(days=1)).isoformat(),
        "reminder_sent": False,
        "email": email_ids[0]
    }
    
    response = requests.post(f"{BASE_URL}/tasks/", json=task_data)
    print_response(response, "CREATE TASK")
    
    # List tasks
    response = requests.get(f"{BASE_URL}/tasks/")
    print_response(response, "LIST ALL TASKS")


def main():
    """Run all tests"""
    print("🚀 Starting API Tests for Smart Mailbox Summarizer")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/mailboxes/")
        if response.status_code != 200:
            print("❌ Server not responding correctly. Is it running?")
            return
        
        # Run tests
        mailbox_id = test_mailbox_api()
        
        if mailbox_id:
            email_ids = test_email_api(mailbox_id)
            test_task_api(email_ids)
        
        print("\n\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        print("\n📝 Next Steps:")
        print("  - Visit http://localhost:8000/admin/ to see Django Admin")
        print("  - Visit http://localhost:8000/api/mailboxes/ for browsable API")
        print("  - Integrate ML/NLP modules for email categorization")
        print("  - Add authentication in Sprint 2")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django is running:")
        print("   cd SmartMailboxBackend && python manage.py runserver")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

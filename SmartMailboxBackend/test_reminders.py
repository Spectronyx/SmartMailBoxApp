#!/usr/bin/env python3
"""
Reminder Engine Test

Tests the task reminder functionality via management command and API
"""

import requests
import json
from datetime import datetime, timedelta, timezone

BASE_URL = "http://localhost:8000/api"


def create_test_tasks_with_deadlines():
    """Create tasks with various deadlines for testing reminders."""
    print("📝 Creating test tasks with upcoming deadlines...\n")
    
    # Get mailbox
    response = requests.get(f"{BASE_URL}/mailboxes/")
    mailboxes = response.json()['results']
    
    if not mailboxes:
        mb_data = {"provider": "GMAIL", "email_address": "test@example.com", "is_active": True}
        response = requests.post(f"{BASE_URL}/mailboxes/", json=mb_data)
        mailbox_id = response.json()['id']
    else:
        mailbox_id = mailboxes[0]['id']
    
    now = datetime.now(timezone.utc)
    
    # Create test emails and tasks
    test_scenarios = [
        {
            "name": "Task due in 2 days",
            "deadline": now + timedelta(days=2),
            "should_trigger": "3_days window"
        },
        {
            "name": "Task due in 12 hours",
            "deadline": now + timedelta(hours=12),
            "should_trigger": "1_day window"
        },
        {
            "name": "Task due in 2 hours",
            "deadline": now + timedelta(hours=2),
            "should_trigger": "3_hours window (FINAL)"
        },
        {
            "name": "Task due in 10 days",
            "deadline": now + timedelta(days=10),
            "should_trigger": "None (too far out)"
        },
    ]
    
    created_tasks = []
    
    for scenario in test_scenarios:
        # Create email
        email_data = {
            "subject": scenario["name"],
            "sender": "test@example.com",
            "body": f"This is a test task: {scenario['name']}",
            "received_at": now.isoformat(),
            "mailbox": mailbox_id,
            "category": "CRITICAL"
        }
        
        email_response = requests.post(f"{BASE_URL}/emails/", json=email_data)
        if email_response.status_code != 201:
            print(f"   ❌ Failed to create email for {scenario['name']}")
            continue
        
        email_id = email_response.json()['id']
        
        # Create task
        task_data = {
            "email": email_id,
            "action_text": f"Complete {scenario['name']}",
            "deadline": scenario["deadline"].isoformat(),
            "reminder_sent": False
        }
        
        task_response = requests.post(f"{BASE_URL}/tasks/", json=task_data)
        if task_response.status_code == 201:
            task = task_response.json()
            created_tasks.append(task)
            print(f"   ✅ Created: {scenario['name']}")
            print(f"      Deadline: {scenario['deadline'].strftime('%Y-%m-%d %H:%M %Z')}")
            print(f"      Expected: {scenario['should_trigger']}\n")
        else:
            print(f"   ❌ Failed to create task for {scenario['name']}")
    
    return created_tasks


def test_api_endpoint():
    """Test the /api/tasks/run-reminders/ endpoint."""
    print("\n🔔 Testing Reminder API Endpoint\n")
    print("="*70)
    
    response = requests.post(f"{BASE_URL}/tasks/run-reminders/")
    
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        print("API Response:")
        print(json.dumps(result, indent=2))
        print("\n" + "="*70)
        
        stats = result.get('stats', {})
        print(f"\n📊 Statistics:")
        print(f"   • Tasks Checked: {stats.get('total_checked', 0)}")
        print(f"   • Reminders Sent: {stats.get('reminders_sent', 0)}")
        print(f"   • Final Reminders: {stats.get('final_reminders', 0)}")
        print(f"   • Errors: {stats.get('errors', 0)}")
        
        return stats
    else:
        print(f"❌ Error: {response.text}")
        return None


def verify_reminder_flags():
    """Verify that reminder_sent flags were updated correctly."""
    print("\n\n✅ Verifying Reminder Flags\n")
    
    response = requests.get(f"{BASE_URL}/tasks/")
    if response.status_code == 200:
        tasks = response.json()['results']
        
        print("Task Status:")
        print("-"*70)
        for task in tasks:
            deadline = task.get('deadline')
            if deadline:
                reminder_sent = task.get('reminder_sent', False)
                status = "📧 FINAL SENT" if reminder_sent else "⏰ PENDING"
                print(f"   {status} | Task {task['id']}: {task['action_text'][:40]}")
        print("-"*70)


def main():
    print("🚀 Testing Task Reminder System\n")
    print("="*70 + "\n")
    
    try:
        # Create test tasks
        tasks = create_test_tasks_with_deadlines()
        
        if not tasks:
            print("❌ No tasks created. Cannot test reminders.")
            return
        
        # Test API endpoint
        stats = test_api_endpoint()
        
        # Verify flags
        verify_reminder_flags()
        
        print("\n\n" + "="*70)
        print("✅ REMINDER SYSTEM TEST COMPLETE")
        print("="*70)
        
        print("\n📝 Next Steps:")
        print("   • Test management command: python manage.py send_reminders")
        print("   • Schedule periodic execution (cron/systemd/Celery)")
        print("   • Extend notifications (email/SMS/push)")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django is running:")
        print("   cd SmartMailboxBackend && python manage.py runserver")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

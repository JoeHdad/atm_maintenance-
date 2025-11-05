"""
Test script to verify device status isolation between technicians.

This script tests that when a supervisor approves or rejects a submission
from one technician, it does NOT affect the same device under another technician's account.
"""

import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from core.models import User, Device, TechnicianDevice, Submission
from django.db import transaction


def cleanup_test_data():
    """Clean up test data from previous runs."""
    print("\n🧹 Cleaning up previous test data...")
    
    # Delete test users
    User.objects.filter(username__startswith='test_tech_').delete()
    
    # Delete test devices
    Device.objects.filter(interaction_id__startswith='TEST-').delete()
    
    print("✅ Cleanup complete")


def create_test_data():
    """Create test technicians and devices."""
    print("\n📝 Creating test data...")
    
    # Create two test technicians
    tech_a = User.objects.create_user(
        username='test_tech_a',
        password='TestPass123!',
        role='technician',
        city='Cairo'
    )
    print(f"✅ Created Technician A: {tech_a.username} (ID: {tech_a.id})")
    
    tech_b = User.objects.create_user(
        username='test_tech_b',
        password='TestPass123!',
        role='technician',
        city='Cairo'
    )
    print(f"✅ Created Technician B: {tech_b.username} (ID: {tech_b.id})")
    
    # Create a test device
    device = Device.objects.create(
        interaction_id='TEST-ATM-001',
        gfm_cost_center='CC-001',
        region='Downtown',
        gfm_problem_type='Cleaning',
        gfm_problem_date='2025-10-29',
        city='Cairo',
        type='Cleaning1'
    )
    print(f"✅ Created Device: {device.interaction_id} (ID: {device.id})")
    
    # Assign device to both technicians
    TechnicianDevice.objects.create(technician=tech_a, device=device)
    TechnicianDevice.objects.create(technician=tech_b, device=device)
    print(f"✅ Assigned device to both technicians")
    
    return tech_a, tech_b, device


def create_submissions(tech_a, tech_b, device):
    """Create submissions from both technicians for the same device."""
    print("\n📤 Creating submissions...")
    
    # Create submission from Technician A
    submission_a = Submission.objects.create(
        technician=tech_a,
        device=device,
        type='Cleaning1',
        visit_date=date.today(),
        half_month=1,
        job_status='Ok',
        status='Pending'
    )
    print(f"✅ Created Submission A: ID {submission_a.id} (Tech A, Device {device.interaction_id})")
    print(f"   Status: {submission_a.status}")
    
    # Create submission from Technician B
    submission_b = Submission.objects.create(
        technician=tech_b,
        device=device,
        type='Cleaning1',
        visit_date=date.today(),
        half_month=1,
        job_status='Ok',
        status='Pending'
    )
    print(f"✅ Created Submission B: ID {submission_b.id} (Tech B, Device {device.interaction_id})")
    print(f"   Status: {submission_b.status}")
    
    return submission_a, submission_b


def test_independent_submissions(tech_a, tech_b, device, submission_a, submission_b):
    """Test that both submissions exist independently."""
    print("\n🧪 TEST 1: Verify both submissions exist independently")
    print("=" * 60)
    
    # Verify both submissions exist
    count = Submission.objects.filter(device=device).count()
    print(f"Total submissions for device: {count}")
    
    if count != 2:
        print(f"❌ FAILED: Expected 2 submissions, got {count}")
        return False
    
    print(f"✅ PASSED: Both submissions exist independently")
    return True


def test_approve_one_submission(submission_a, submission_b, tech_a, tech_b, device):
    """Test that approving one submission doesn't affect the other."""
    print("\n🧪 TEST 2: Approve Submission A and verify Submission B is unaffected")
    print("=" * 60)
    
    # Approve submission from Technician A
    submission_a.status = 'Approved'
    submission_a.remarks = 'Good work'
    submission_a.save()
    print(f"✅ Approved Submission A (Tech A)")
    
    # Refresh from database
    submission_a.refresh_from_db()
    submission_b.refresh_from_db()
    
    print(f"\nAfter approval:")
    print(f"  Submission A status: {submission_a.status}")
    print(f"  Submission B status: {submission_b.status}")
    
    # Verify Submission A is approved
    if submission_a.status != 'Approved':
        print(f"❌ FAILED: Submission A should be Approved, got {submission_a.status}")
        return False
    
    # Verify Submission B is still Pending (NOT affected)
    if submission_b.status != 'Pending':
        print(f"❌ FAILED: Submission B should still be Pending, got {submission_b.status}")
        return False
    
    print(f"✅ PASSED: Submission B status unchanged (still Pending)")
    return True


def test_reject_other_submission(submission_a, submission_b, tech_a, tech_b, device):
    """Test that rejecting another submission doesn't affect the approved one."""
    print("\n🧪 TEST 3: Reject Submission B and verify Submission A stays Approved")
    print("=" * 60)
    
    # Reject submission from Technician B
    submission_b.status = 'Rejected'
    submission_b.remarks = 'Missing photos'
    submission_b.save()
    print(f"✅ Rejected Submission B (Tech B)")
    
    # Refresh from database
    submission_a.refresh_from_db()
    submission_b.refresh_from_db()
    
    print(f"\nAfter rejection:")
    print(f"  Submission A status: {submission_a.status}")
    print(f"  Submission B status: {submission_b.status}")
    
    # Verify Submission A is still Approved
    if submission_a.status != 'Approved':
        print(f"❌ FAILED: Submission A should still be Approved, got {submission_a.status}")
        return False
    
    # Verify Submission B is Rejected
    if submission_b.status != 'Rejected':
        print(f"❌ FAILED: Submission B should be Rejected, got {submission_b.status}")
        return False
    
    print(f"✅ PASSED: Submission A status unchanged (still Approved)")
    return True


def test_technician_views_own_status(tech_a, tech_b, device, submission_a, submission_b):
    """Test that each technician only sees their own submission status."""
    print("\n🧪 TEST 4: Verify each technician sees only their own submission status")
    print("=" * 60)
    
    # Get submissions for Tech A
    tech_a_submissions = Submission.objects.filter(
        technician=tech_a,
        device=device
    )
    
    # Get submissions for Tech B
    tech_b_submissions = Submission.objects.filter(
        technician=tech_b,
        device=device
    )
    
    print(f"Tech A submissions for device: {tech_a_submissions.count()}")
    print(f"Tech B submissions for device: {tech_b_submissions.count()}")
    
    if tech_a_submissions.count() != 1:
        print(f"❌ FAILED: Tech A should have 1 submission, got {tech_a_submissions.count()}")
        return False
    
    if tech_b_submissions.count() != 1:
        print(f"❌ FAILED: Tech B should have 1 submission, got {tech_b_submissions.count()}")
        return False
    
    # Verify statuses
    tech_a_status = tech_a_submissions.first().status
    tech_b_status = tech_b_submissions.first().status
    
    print(f"\nTech A sees status: {tech_a_status}")
    print(f"Tech B sees status: {tech_b_status}")
    
    if tech_a_status != 'Approved':
        print(f"❌ FAILED: Tech A should see Approved, got {tech_a_status}")
        return False
    
    if tech_b_status != 'Rejected':
        print(f"❌ FAILED: Tech B should see Rejected, got {tech_b_status}")
        return False
    
    print(f"✅ PASSED: Each technician sees only their own submission status")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 DEVICE STATUS ISOLATION TEST SUITE")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # Setup
            cleanup_test_data()
            tech_a, tech_b, device = create_test_data()
            submission_a, submission_b = create_submissions(tech_a, tech_b, device)
            
            # Run tests
            results = []
            results.append(("Test 1: Independent Submissions", test_independent_submissions(tech_a, tech_b, device, submission_a, submission_b)))
            results.append(("Test 2: Approve One Submission", test_approve_one_submission(submission_a, submission_b, tech_a, tech_b, device)))
            results.append(("Test 3: Reject Other Submission", test_reject_other_submission(submission_a, submission_b, tech_a, tech_b, device)))
            results.append(("Test 4: Technician Views Own Status", test_technician_views_own_status(tech_a, tech_b, device, submission_a, submission_b)))
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 TEST SUMMARY")
            print("=" * 60)
            
            passed = sum(1 for _, result in results if result)
            total = len(results)
            
            for test_name, result in results:
                status_icon = "✅" if result else "❌"
                print(f"{status_icon} {test_name}")
            
            print(f"\nTotal: {passed}/{total} tests passed")
            
            if passed == total:
                print("\n🎉 ALL TESTS PASSED! Device status isolation is working correctly.")
                return True
            else:
                print(f"\n⚠️  {total - passed} test(s) failed. Device status isolation has issues.")
                return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        cleanup_test_data()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

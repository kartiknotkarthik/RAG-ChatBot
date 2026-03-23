import pytest
import os
import sys

# Add scheduler directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scheduler.main import MFScheduler

def test_nav_update_job_execution():
    # Verify the daily job function returns success and increments counter
    mf_s = MFScheduler()
    assert mf_s.jobs_count == 0
    
    result = mf_s.daily_nav_update()
    assert result == True
    assert mf_s.jobs_count == 1

def test_full_sync_job_execution():
    # Verify the monthly full sync function behaves correctly
    mf_s = MFScheduler()
    assert mf_s.jobs_count == 0
    
    result = mf_s.monthly_full_sync()
    assert result == True
    assert mf_s.jobs_count == 1

def test_job_registration_counts():
    # Verify that we've correctly registered the 2 main jobs
    import schedule
    # Clear any previous runs
    schedule.clear()
    
    mf_s = MFScheduler()
    mf_s.start()
    
    # Check current pending jobs in the schedule registry
    jobs = schedule.get_jobs()
    assert len(jobs) == 2 # 1 daily + 1 monthly (every 30 days)

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__]))

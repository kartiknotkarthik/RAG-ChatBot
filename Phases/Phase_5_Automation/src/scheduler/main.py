import schedule
import time
import os

class MFScheduler:
    def __init__(self):
        self.jobs_count = 0
    
    def daily_nav_update(self):
        print("Running job: Daily NAV update from AMFI...")
        # Placeholder for calling Phase 1 extractor
        # os.system("python Phase_1_Extraction/src/extractors/downloader.py --nav-only")
        self.jobs_count += 1
        return True

    def monthly_full_sync(self):
        print("Running job: Monthly full AMC Facts re-scrape & re-indexing...")
        # Placeholder for full Phase 1 -> Phase 2 pipeline
        # os.system("python Phase_1_Extraction/src/extractors/merger.py")
        # os.system("python Phase_2_RAG/src/database/populate_db.py")
        self.jobs_count += 1
        return True

    def start(self):
        # Register the jobs as per architectural requirements
        schedule.every().day.at("09:00").do(self.daily_nav_update)
        schedule.every(30).days.do(self.monthly_full_sync)
        
        print("Mutual Fund RAG Scheduler is now RUNNING...")
        # This loop normally runs indefinitely in production
        # while True:
        #    schedule.run_pending()
        #    time.sleep(1)

if __name__ == "__main__":
    mf_s = MFScheduler()
    mf_s.start()

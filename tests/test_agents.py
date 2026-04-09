from utils.cv_extractor import get_cv_summary
from utils.job_scraper import manual_job_entry, clean_text, detect_source

def test_manual_job_entry():
    """Manual job entry builds a balid JobPosting. """
    job = manual_job_entry(
        title="Data Scientist",
        company="Test Corp",
        description="Looking for a Python expert with ML experience. "
    )

    assert job.title == "Data Scientist"
    assert job.company == "Test Corp"
    assert job.source == "manual"
    assert len(job.description) > 10

def test_clean_text():
    """clean_text removes excess whitespace"""
    messy = "Hello world\n\n\nThis is a test"
    result = clean_text(messy)
    assert " " not in result
    assert result.count("\n\n\n") == 0

def test_detetect_source():
    """detect_source identifies platforms correctly. """
    assert detect_source("https://www/linkedin.com/jobs/123") == "linkedin"
    assert detect_source("https://www/indeed.com/jobs/abc") == "indeed"
    assert detect_source("https://www/pnet.com/jobs/456") == "pnet"
    assert detect_source("https://www/somecompany.co.za/careers") == "other"
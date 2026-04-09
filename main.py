from dotenv import load_dotenv
import os
from agents.base_agent import BaseAgent, Message
from utils.cv_extractor import extract_text_from_pdf, get_cv_summary
from utils.job_scraper import scrape_job, manual_job_entry


load_dotenv()



def test_cv_extractor():
    print("=" * 50)
    print("TEST 1: CV Extractor")
    print("=" * 50)

    # Put your actual CV PDF in the project root and update this path
    cv_path = ""

    try:
        text = extract_text_from_pdf(cv_path)
        print(f"Extracted {len(text)} characters from CV .")
        print("\n First 500 characters:")
        print("-" * 40)
        print(text[:500])
        print("-" * 40)
        print("CV extractor: PASSED\n")
    except FileNotFoundError:
        print(
            "CV PDF not found. Add your CV to the project root as chuene-mosomane and rerun"
        )

def test_job_scraper_manual():
    print("=" * 50)
    print("TEST 2: CV Manual Job Entry (no URL needed)")
    print("=" * 50)

    job = manual_job_entry(
        title = "Senior Data Scientist",
        company="Nedbank",
        description=""",
        We are looking for a Senior Data Scientist to join our team.
        Requiremets: Python, machine learning, deep learning, MLOps. 
        Experience with cloud platforms (AWS or GCP) required.
        PhD and Masters in a quantitative field preferred.
        Responsibilities: Build predictive models, lead a small team,
        present findings to executive stakeholders
        """
    )

    print(f"Title: {job.title}")
    print(f"Company: {job.company}")
    print(f"Source: {job.source}")
    print(f"Description length: {len(job.description)} chars")
    print("Manual job entry: PASSED\n")

   

def test_job_scraper_url():
    print("=" * 50)
    print("TEST 3: URL Scraper (live request)")
    print("=" * 50)

    # Using a publicly accessible job board
    url = "https: www.pnet.co.za/job/data-scientist"

    print(f"Scraping: {url}")
    job = scrape_job(url)

    print(f"Title: {job.title}")
    print(f"Company: {job.company}")
    print(f"Description length: {len(job.description)} chars")

    if len(job.description) > 200:
        print("URL scraping: PASSED\n")
    else:
        print(
            "URL scraping returned thin content -- site may block scrapers. \n" \
            "This is expected for gated platforms. Manual fallback will be handle it. \n"
        )

if __name__ == "__main__":
    test_cv_extractor()
    test_job_scraper_manual()
    test_job_scraper_url()



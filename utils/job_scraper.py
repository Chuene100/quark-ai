import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
import re




@dataclass
class JobPosting:
    """
    Structured representation of a job posting.
    Agents receive this object - not raw HTML.
    """

    url: str
    title: str
    company: str
    description: str
    source: str              #e.g. "LinkedIn", "Indeed", "pnet", "manual"
    raw_html: str = ""      # kept for debugging, not sent to agents


def clean_text(text: str) -> str:
    """
    Removes excessive whitespaces and non-printable characters.
    Raw scraped text is messy -  this makes it readable
    """
    # collapse multiple newlines into two
    text = re.sub(r"\n{3,}", "\n\n", text)

    # collapse multiple spaces
    text = re.sub(r"[^\x20-\x7E\n]", "", text)
    return text.strip()


def detect_source(url: str) -> str:
    """Identifies the job platform from the URL."""
    url_lower = url.lower()

    if "linkedin.com" in url_lower:
        return "linkedin"
    
    elif "indeed.com" in url_lower:
        return "indeed"
    
    elif "pnet.co.za" in url_lower:
        return "pnet"
    
    elif "careers24.com" in url_lower:
        return "careers24"
    
    elif "jobplacements.com" in url_lower:
        return "jobplacements"
    
    else:
        return "other"
    

def scrape_job(url: str, manual_decription: str = "") -> JobPosting:
    """
    Scrapes a job posting from a URL.

    Many platforms (LinkedIn especially) block scrapers or require login.
    We handle this with a manual_description fallback - the user pastes 
    the JD text themselves if the scrape returns too little content.

    Args:
        url: the job posting URL
        manual_description: user-paseted JD text (fallback)

    Returns:
        JobPosting dataclass
    """

    source = detect_source(url)

    headers = {
        "User-Agent":(
        "Mozilla/5.0 (Windows NT 10.0; WIn64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/120.0.0.0 Safari/537.36"
        
        )
    }

    raw_html = ""
    
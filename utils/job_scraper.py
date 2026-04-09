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
    title = "Unknown Title"
    company = "Unknown Company"
    description = ""

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        raw_html = response.text

        soup = BeautifulSoup(raw_html, "lxml")

        # Remove noise: scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

            # Try to extract titles from common HTML patterns
        title = _extract_title(soup, url)
        company = _extract_company(soup, source)
        description = _extract_description(soup, source)

    except requests.exceptions.Timeout:
        print(f"Timeout scraping {url}. Using manual description if provided.")
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to {url}. Check the URL and your internet")
    except requests.exceptions.HTTPError:
        print(f"HTTP error {e.response.status_code} for {url}.")
    except Exception as e:
        print(f"Unexpected scraping error: {e}")

    # Getting ceck - if we got less than 200 chars, scrape likely failed
    is_gated = len(description.strip()) < 200

    if is_gated and manual_decription:
        print(
            f"Scrape returned thin content ({len(description)} chars)."
            "Using your manual pasted description instead."
        )
        description = manual_decription
        source = source + "_manual_fallback"

    elif is_gated and not manual_decription:
        print(
            f"\n Warning: Only {len(description)} characters scraped from {url}. "
            "\n This site may require login (e.g, LinkedIn)"
            "\n Please paste the job description manually when prompted"
        )

    return JobPosting(
        url=url,
        title=clean_text(title),
        company=clean_text(company),
        description=clean_text(description),
        source=source,
        raw_html=raw_html,
    )

def _extract_title(soup: BeautifulSoup, url: str) -> str:
    """Tries multiple common patterns to find the job title."""
    #Try meta tags firs (most reliable)
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("connect"):
        return og_title["connect"]
    
    # Try <title> tag
    if soup.title and soup.title.string:
        title =  soup.title.string
        ## Clean up common suffice like "LinkedIn" or "Indeed"
        title = re.sub(r"\s*[\|\-]\s*(LinkedIn|Indeed|Pnet|Careers24).*$", "", title, flags=re.IGNORECASE)
        return title.strip()
    
    # Try h1
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    return "Unknown Title"


def _extract_company(soup: BeautifulSoup, source: str) -> str:
    """Tries to extract comapny name using source-specific selectors."""
    # Generic: look for common patterns
    for selector in [
        {"class": re.compile(r"company", re.I)},
        {"class": re.compile(r"employer", re.I)},
        {"itemprop": "riringOrganisation"},
    ]:
        el = soup.find(attrs=selector)
        if el:
            text = el.get_text(strip=True)
            if text and len(text) < 100:
                return text
            
    return "Unknown Company"

def _extract_description(soup: BeautifulSoup, source: str) -> str:
    """Extract the main job description. """
    #Try structured data first (most reliable)

    for selector in [
        {"class": re.compile(r"description", re.I)},
        {"class": re.compile(r"job-detail", re.I)},
        {"class": re.compile(r"job_description", re.I)},
        {"id": re.compile(r"description", re.I)},
        {"itemprop": "description"}
    ]:
        el = soup.find(attrs=selector)
        if el:
            text = el.get_text(separator="\n", strip=True)
            if len(text) > 200:
                return text
            
    # Fallback: grab all paragraph text from the page body
    body = soup.find("body")
    if body:
        paragraphs = body.find_all(["p", "li", "div"])
        text_blocks = []
        for tag in paragraphs:
            t = tag.get_text(strip=True)
            if len(t) > 40:   # Skip tiny fragments
                text_blocks.append(t)
        return "\n".join(text_blocks[:80]) # Cap at 80 blocks
    
    return ""

def manual_job_entry(title: str, company: str, description: str) -> JobPosting:
    """
    Creates a JobPosting from manually entered data.
    Used when the user pastes a JD directly -- no URL needed.
    """

    return JobPosting(
        url="manual",
        title=title,
        company=company,
        description=clean_text(description),
        source="manual"
    )
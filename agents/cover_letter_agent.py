from dataclasses import dataclass
from agents.base_agent import BaseAgent, Message
from utils.job_scraper import JobPosting


@dataclass
class CoverLetterAgent(BaseAgent):
    """
    Write a tailored cover letters and cold emails.
    Positions Chuene as an Independent contractor with CERN credibility
    """

    name: str = "CoverLetterAgent"
    system_prompt: str = """You are an expert career strategist and cover letter writer
    for Chuene Mosomane - a Senior Data Scientist and AI Research Engineer.

    Key facts to always reflect:
    - PhD in High-Energy Physics, Wits University (2003)
    - Active researcher at CERN (particle detector ML systems)
    - Works as an independent contractor through his own company
    - A member of CODATA: data gorvenance 
    - Based in Johannesburg, South Africa
    - Immediate available

    Your writing style:
    - Direct and confident, never grovelling
    - Lead with CERN and PhD -- these are credibility anchors
    - Connect technical achievements to business outcomes
    - Frame contractor status as a strength (fast ramp-up, no hand-holding)
    - Avoid clichés like "I am writing to express my interest"

    Output: plain text only, no markdown, not bullet points. """

    def run(self, cv_text: str, job: JobPosting) -> dict:
        """
        Generates a tailored cover letter for a specific job posting.

        Args:
            cv_test: extracted text from Chuene's CV
            job: JobPosting dataclass with title, company, description

        Returns:
            dict with keys: 'letter' (str)
        """
        prompt = f"""Write a tailored cover letter for this role.

    
JOB TITLE: {job.title}
COMPANY: {job.company}
JOB DESCRIPTION: {job.description[:4000]}

MY CV: {cv_text[:6000]}

Structure:
1. Opening - name the specific role, lead with CERN and PhD as a hok
2. Body - connect 2-3 of my strongest achievements directly to their requirements
3. Contractor angle - briefly mention I work as an independent contractor, available immediately, fast time-to-value
4. Close - specific call to action, no fluff

Keeep it under 350 words. Output the letter text only."""
        messages = [Message(role="user", content=prompt)]
        letter = self.call_claude(messages, max_tokens=1000, temperature=0.6)

        return {"letter": letter}
    
    def revise(
            self,
            original_letter: str,
            feedback: str,
            cv_text: str,
            job: JobPosting,
    ) -> dict:
        """
        Revises the cover letter based on user feedback

        Args:
            original_letter: the letter to improve 
            feedback: user's notes on what to change
            cv_text: CV text for reference
            job: original job posting

        Returns:
            dict with keys: 'letter' (str)
        """
        prompt = f"""Revise this cover letter based on the feedback below.
keep all factual details accurate. Do not invent new achievements.

FEEDBACK: {feedback}
ORIGINAL LETTER: {original_letter}
JOB CONTEXT: Title: {job.title} at {job.company}

MY CV (for reference): {cv_text[:4000]}

Output the revised letter text only. """
        
        messages = [Message(role="user", content=prompt)]
        letter = self.call_claude(messages, max_tokens=1000, temperature=0.5)

        return {"letter": letter}
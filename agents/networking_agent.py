import json
import re
from dataclasses import dataclass
from agents.base_agent import BaseAgent, Message
from utils.job_scraper import JobPosting

@dataclass
class NetworkAgent(BaseAgent):
    """
    Generates LinkedIn DMs and cold emails to rectuiters
    and hiring managers. Relationship first approach - never
    beg for a job, always open a conversation
    """

    name: str = "NetworkingAgent"
    system_prompt: str = """You are a networking strategist for Chuene Mosomane
- a Senior Data Scientist and AI Research Engineer based in Johannesburg.

Chuene's positiong:
- PhD in High-Energy Physics (Wits University), CERN research and leadership experience
- Works as an independent contractor through his own company
- Seeking senior data science and AI engineering contract roles in South Africa

Message philosopy:
- Start a relationship, not a transaction
- One specific hook from thier company or roles (shows research)
- One concrete bridge from Chuene's background to their problems
- One low-friction CTA - a 15-minutes call or 2 specific questions
- Never: "I hope this finds you well", begging, excessive flatery

Output: JSON only with keys 'linkedin_dm' and 'cold_email'.
The cold_email must start with "Subject: ...". """


    def run(self, cv_text: str, job: JobPosting) -> dict:
        """
        Generate a LinkedIn DM and cold email for a target role.

        Returns:
        dict with keys: 'linked_dm' (str), 'cold_email' (str)
        """

        prompt = f"""Generate two outreach messages for this opportunity.

ROLE: {job.title} at {job.company}
JOB DESCRIPTION: {job.description[:3000]}
MY CV: {cv_text[:4000]}

Requirements:
- linkedin_dm: max 100 words, no subject line, opens a conversation
- cold_email: 150-200 words, start with Subject: line, references
a specific details from thier company or role. 

Use placeholders {{recipient_name}} where the name would go. 

Return valid JSON only: {{"linkedin_dm": "...", "cold_email": "Subject: ...\\n\\n..}} """
        
        messages = [Message(role="user", content=prompt)]
        raw = self.call_claude(messages, max_tokens=800, temperature=0.5)

        return self._parse_json_response(raw)
    
    def revise(
            self,
            original_messages: dict,
            feedback: str,
            cv_text: str,
            job: JobPosting,
    ) -> dict:
        """
        Revises networking messages based on user feedback.

        Returns:
            dict with keys: 'linked_dm' (str), 'cold_email' (str)
        """
        
        prompt = f"""Revise these outreach messages based on the feedback. 
Maintain relationship-first tone. No direct job requests. 

FEEDBACK: {feedback}

ORIGINAL MESSAGES: LinkedIn DM: {original_messages.get('linkedin_dm', '')}
Cold Email: {original_messages.get('cold_email', '')}

ROLE CONTEXT: {job.title} at {job.company}

Return valid JSON only: {{"linkein_dm": "...", "cold_email": "Subject: ...\\n\\n..."}}"""
        
        messages = [Message(role="user", content=prompt)]
        raw = self.call_claude(messages, max_tokens=800, temperature=0.5)

        return self._parse_json_response(raw)
    
    def _parse_json_response(self, raw: str) -> dict:
        """
        Safely parses JSON from Claude's response.
        Claude sometimes wrap JSON in markdown code blocks - we handle that
        
        """
        cleaned = re.sub(r"```json|```", "", raw).strip()

        try:
            data = json.loads(cleaned)
            return{
                "linkedin_dm": data.get("linked_dm", ""),
                "cold_email": data.get("cold_email", "")
            }
        except json.JSONDecodeError:
            # Fallback: return raw text in linkedin_dm so nothinf is lost
            print(f"JSON parse failed. Raw response: \n[:300]")
            return {
                "linkedin_dm": raw,
                "cold_email": ""
            }
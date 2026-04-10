import json
import re
from dataclasses import dataclass
from agents.base_agent import BaseAgent, Message
from utils.job_scraper import JobPosting


@dataclass
class CVReviewAgent(BaseAgent):
    """
    Analyses Chuene's CV against a specific job description.
    Returns a structured gap analysis with actionable edits.
    """

    name: str = "CVReviewAgent"
    system_prompt: str = """You are an executive rectuiter and career coach
with deep expertice in data science and AI engineering hiring in South Africa

You review CVs against job descriptions with two lenses:
1. ATS screen - keywork alignment, missing terms
2. Human screen - does the value proposition land in 6 seconds?

Your feedback is direct, specific, and prioritised.
You do not pad with generic advise.

Output: valid JSON only matching the exact schena requested. """

    def run(self, cv_text: str, job: JobPosting) -> dict:
        """
        Reviews CV against a job description. 


        Returns:
            dict with keys:
            - verdict (str)
            - confidence (float 0-1)
            - strenths (str)
            - weaknesses (str)
            - missing_keywords (list)
            - priority_edits (list of dicts)
        """
        prompt = f"""Review this CV against the job description. 


JOB TITLE: {job.title}
COMPANY: {job.company}
JOB DESCRIPTION: {job.description[:4000]}

CV: {cv_text[:6000]}

Return this exact JSON schema:
{{
    "verdict": "Strong Fit" | "Good Fit" | "Partial Fit" | "Weak Fit",
    "confidence": <float between 0.0 and 1.0>,
    "strengths": "<what works well for this specific role>",
    "weaknesses": "<what is holding the application back>",
    "missing_keywords": ["<keyword1>", "<keyword2>"],
    "Prioritiy_edits": [
        {{
            "priority": "High" | "Medium" | "Low",
            "section": "<CV section to edit>",
            "suggestion": "<specific actionable changes>",
            "reason": "<Why this matters for this role>"
        }}
    ]
}}

Result valid JSON only. No commentary. """ 

        messages = [Message(role="user", content=prompt)]
        raw = self.call_claude(messages, max_tokens=1500, temperature=0.2)

        return self._parse_json_response(raw)
    
    def _parse_json_response(self, raw: str) -> dict:
        """Parses Claude's JSON response with fallback."""
        cleaned = re.sub(r"```json|```", "", raw).strip()

        try:
            data = json.loads(cleaned)
            # Ensure confidence is a valid float
            data["confidence"] = max(
                0.0, min(1.0, float(data.get("confidence", 0.5)))
            )
            return data
        except (json.JSONDecodeError, ValueError):
            print(f"CV review JSON parse failed. Raw:\n{raw[:300]}")
            return {
                "verdict": "Parse Error",
                "confidence": 0.5,
                "strengths": raw[:500],
                "weaknesses": "",
                "missing_keywords": [],
                "priority_edits": [],
            }
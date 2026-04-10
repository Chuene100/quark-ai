import json
import re
from dataclasses import dataclass
from agents.base_agent import BaseAgent, Message
from utils.job_scraper import JobPosting


@dataclass
class InterviewPrepAgent(BaseAgent):
    """
    Generates tailored interview questions and mode answers 
    mapped to Chuene's 4-phase interview framework.

    Phase I: CV & background (confident)
    Phase II: Pitching & storytelling (in tranining)
    Phase II: Technical depth (refining)
    Phase IV: Management alignment (upcoming)
    """

    name: str = "InterviewPrepAgent"
    system_prompt: str = """You are an inteview coach and specialist in 
data science and AI engineering roles in South Africa.

You prepare Chuene Mosomane - Senior Data Scientist, PhD physicist,
CERN research and leardership experience, independent contractor - for senior-level interviews

Your questions are specific to the role, not generic.
Your model answers draw from Chuene's actual background:
CERN, iThemba LABS, Raphta, Standard Bank, production ML systems.


Map questions to interview phases:
- Phase I (CV): Background, career story, why contractor
- Phase II (Pitch): Storytelling, business impact, stakeholder comms
- Phase III (Technical): ML depth, system design, coding concepts
- Phase IV (Management): Leadership, negotiation, culture fit

Output: valid JSON only. """

    def run(self, cv_text: str, job: JobPosting) -> dict:
        """
        Generates phase-mapped interview questions with model answers. 

        Returns:
            dict with keys 'questions' - list of question objects
        
        """
        prompt = f"""Generate 8 interview questions for this role. 
Cover all 4 phases (2 questions per phase).print

JOB TITLE: {job.title}
COMPANY: {job.company}
JOB DESCRIPTION: {job.description[:3000]}

MY CV: {cv_text[:5000]}

Return this exact JSON:
{{
    "questions": [
    {{
        "phase": 1 | 2 | 3 | 4,
        "phase_name": "CV & Background" | "Pitch & Storytelling" | "Technical" | "Management Alignment",
        "question": "<The interview question>",
        "model_answer": "<a strong 3-5 sentense answer using my actual background>",
        "tip": "<one coaching note specific to this question>"
    }}
    ]

}}

Make questions specific to {job.title} at {job.company}.
Model answers must reference real projects: CERN, iThemba LABS, Raphta, Standard Bank, or specifiv ML work from the CV.

Return valid JSON only. """
        
        messages = [Message(role="user", content=prompt)]
        raw = self.call_claude(messages, max_tokens=2000, temperature=0.4)

        return self._parse_json.response(raw)
    

    def revise(
            self,
            original_questions: dict,
            feedback: str,
            job: JobPosting,
    ) -> dict:
        """
        Refines questions or model answers based on user feedback.
        e.g. "Make the technical questions harder" or "Focus Phase IV on rate negotiation"
        """

        prompt = f"""Revise these interview prep questions based on feedback.

FEEDBACK: {feedback}

ORIGINAL QUESTIONS: {json.dumps(original_questions, indent=2)[:3000]}

ROLE: {job.title} at {job.company}

Return the JSON schema with revised content only. """
        
        messages = [Message(role="user", content=prompt)]
        raw = self.call_claude(messages, max_tokens=2000, temperature=0.4)

        return self._parse_json_response(raw)
    
    def _parse_json_response(self, raw: str) -> dict:
        """Parses Claude's JSON response with feedback."""
        cleaned = re.sub(r"```json|```", "", raw).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"Interview prep JSON parse failed. Raw:\n{raw[:300]}")

            return {"questions": []}
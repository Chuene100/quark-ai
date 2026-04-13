import os 
from dataclasses import dataclass, field
from typing import Optional

from agents.base_agent import BaseAgent
from agents.cover_letter_agent import CoverLetterAgent
from agents.networking_agent import NetworkAgent
from agents.cv_review_agent import CVReviewAgent
from agents.interview_prep_agent import InterviewPrepAgent
from utils.cv_extractor import get_cv_summary
from utils.job_scraper import scrape_job, manual_job_entry, JobPosting


# Valid task names - used for routing and validation
VALID_TASKS = {
        "cover_letter",
        "networking",
        "cv_review",
        "interview_prep"
}

@dataclass
class OrchestrationResults:
    """
    Standardised result object returned by the Orchestrator.
    Every task returns this same structure - the UI only needs 
    to handle one result type regardless of which agent ran.
    
    """
    task: str                        # which taks was run
    job: JobPosting                  # the job posting used
    cv_text: str                     # the CV text used
    output: dict                     # the agent's raw output
    needs_manual_id: bool = False    # True if the URL was gated


class Orcherstrator:
    """
    Central router for Quark AI.

    Responsibilityes:
    1. Load and validate the CV
    2. Fetch and validate the job description
    3. Route to the correct specialist agent
    4. Return a standardised OrchestrationResult
    
    The Orcherstrator does not contain AI logic itself -
    it delegates everything to the specialist agents.
    This separation of concerns keeps each class testable
    and replaceable independently.
    """

    def __init__(self):
        # Initialise all agents once at startup
        # They are stateless -- safe to reuse across tasks
        self.cover_agent = CoverLetterAgent()
        self.networking_agent = NetworkAgent()
        self.cv_review_agent = CVReviewAgent()
        self.interview_prep_agent = InterviewPrepAgent()

        # Map task names to agent instances
        # Adding a new agent = aadd one line here
        self._agent_map = {
            "cover_letter": self.cover_agent,
            "networking": self.networking_agent,
            "cv_review": self.cv_review_agent,
            "interview_prep": self.interview_prep_agent,

        }

    def run(
        self,
        task: str,
        cv_path: str,
        job_url: Optional[str] = None,
        manual_title: Optional[str] = None,
        manual_company: Optional[str] = None,
        manual_description: Optional[str] = None,
    ) -> OrchestrationResults:
        """
        Main entry point for Quark AI.

        Args:
            task: one of 'coveer_letter', 'networking', 'cv_review', 'interview_prep'
            cv_path: path to the CV PDF file
            job_url: URL of the job posting (optional)
            manual_title: job title if entering manually
            manul_company: company name if entering manually
            manual_description: pasted JD text (fallback for gated URLs or manual entry)

        Returns:
            OrchestrationResult with all context and agent output

        Raises: 
            ValueError: for invalid task names or missing inputs
        """

        # --- Step 1: Validate taks ---
        task = task.strip().lower()
        if task not in VALID_TASKS:
            raise ValueError(
                f"Unknown task: '{task}'."
                f"Valid option: {', '.join(sorted(VALID_TASKS))}"
                )
        
        # -- Step 2: Load CV --
        cv_text = self._load_cv(cv_path)

        # -- Step 3: Build JobPosting ---
        job, needs_manual_id = self._build_job_posting(
            job_url=job_url,
            manual_title=manual_title,
            manual_company=manual_company,
            manual_description=manual_description,   
        )

        # --- Step 4: Route to agent --
        print(f"\nQuark AI - running task: {task}")
        print(f"Role: {job.title} at {job.company}")
        print(f"JD length: {len(job.description)} chars\n")

        agent = self._agent_map[task]
        output = agent.run(cv_text=cv_text, job=job)


        # --- Step 4: Return standardise result ---
        return Orcherstrator(
            task=task,
            job=job,
            cv_text=cv_text,
            output=output,
            needs_manual_id=needs_manual_id,
        )
    
    def revise(
            self,
            result:OrchestrationResults,
            feedback: str,
    ) -> OrchestrationResults:
        """
        Revises a  previous result based on user feedback.
        Passes the feedback to the dame agent that generated 
        the original output
        
        Args:
            result: the OrchestrationResults to improve
            feedback: user's revision instructions

        Returns:
            Updated OrchestrationResults with revised output
        """
        
        task = result.task
        agent = self._agent_map.get(task)

        if not agent:
            raise ValueError(
                f"Agent for '{task}' does not support revision"
            )
        print(f"\nQuark AI - revising: {task}")
        print(f"Feedback: {feedback[:100]}...\n")

        # Each agent's revise() signature differs slightly
        # We handle that with task-specific routing here
        if task == "cover_letter":
            revised_output = agent.revise(
                original_letter = result.output.get("letter", ""),
                feedback = feedback,
                cv_text = result.cv_text,
                job = result.job
            )

        elif task == "networking":
            revised_output= agent.revise(
                original_messages= result.output,
                feedback= feedback,
                cv_text= result.cv_text,
                job= result.job
            )

        elif task == "interview_prep":
            revised_output= agent.revise(
                original_questions= result.output,
                feedback= feedback,
                job= result.job,
            )
        else:
            # cv_review does not have a revise method
            # just re-run with the same inputs
            revised_output= agent.run(
                cv_text= result.cv_text,
                job= result.job 
            )

        # Return a new result with updated output
        #Original result is unchanged - immutable pattern
        return OrchestrationResults(
            task= result.task,
            job= result.job,
            cv_text= result.cv_text,
            output= revised_output,
            needs_manual_id= result.needs_manual_id,
        )
    
    def _load_cv(self, cv_path: str) -> str:
        """
        Loads and validates the CV PDF.
        Cerntralised here to every task benefints from
        the same validation logic.
        """
        if not cv_path:
            raise ValueError("CV path is required.")
        
        if not os.path.exists(cv_path):
            raise FileNotFoundError(
                f"CV not found at: {cv_path}\n"
                "Make sure the PDF is in your project folder."
            )
        cv_text = get_cv_summary(cv_path)

        if len(cv_text) < 100:
            raise ValueError(
                "CV appears to be empty or unreadable."
                "Try re-exporting it as a text-based PDF."
            )
        
        return cv_text
    
    def _build_job_posting(
            self,
            job_url: Optional[str],
            manual_title: Optional[str],
            manual_company: Optional[str],
            manual_description: Optional[str],
    ) -> tuple[JobPosting, bool]:
        """
        Builds a JobPosting from either a URL or manual input.

        Returns:
            tupel of (JobPosting, needs_manual_id: bool)
            needs_manual_id is True when scrapping returned
            thin conent and no manual fallback was provided
        """

        needs_manual_id = False
        
        # Manual entry - no URL provided
        if not job_url:
            if not all([manual_title, manual_company, manual_description]):
                raise ValueError(
                    "Provide either a job URL, or all three of: " \
                    "manual_title, manual_company, manual_description"
                )
            
            job = manual_job_entry(
                title= manual_title,
                company= manual_company,
                description= manual_description
            )

            return job, needs_manual_id
        
        # URL provided - attempt to scrape
        job= scrape_job(
            url= job_url,
            manual_decription= manual_description or "",
        )

        # Check if scrape returned thin content
        if len(job.description.strip()) < 200 and not manual_description:
            needs_manual_id = True

        return job, needs_manual_id
    

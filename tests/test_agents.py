from utils.cv_extractor import get_cv_summary
from utils.job_scraper import manual_job_entry, clean_text, detect_source
from unittest.mock import patch, MagicMock
from agents.orchestractor import Orcherstrator, OrchestrationResults, VALID_TASKS
from agents.review_coordinator import ReviewCoordinator, ReviewState
from utils.job_scraper import manual_job_entry
import pytest


MOCK_JOB = manual_job_entry("Senior DS", "TestCorp", "Python ML required.")
MOCK_CV= "PhD Physics. CERN. Python, PyTorch, AWS."
MOCK_RESULTS = Orcherstrator(
    task= "cover_letter",
    job= MOCK_JOB,
    cv_text= MOCK_CV,
    output= {"letter": "Dear Hiring Manager, test letter."}
)

def test_valid_tasks_sert():
    """VALID_TASKS contains the expected task names."""
    assert "cover_letter" in VALID_TASKS
    assert "networking" in VALID_TASKS
    assert "cv_review" in VALID_TASKS
    assert "interview_prep" in VALID_TASKS

def test_orchestrator_invalid_task():
    """Orchestrator raises ValueError for unknown tasks."""
    with patch("anthropic.Anthropic"):
        orch= Orcherstrator()
        with pytest.raises(ValueError, match= "Unknown task"):
            orch.run(task= "make_coffee", cv_path= "fake.pdf")

def test_orchestrator_missing_cv():
    """Orchestrator raises FileNotFoundError for missing CV."""
    with patch("anthropic.Anthropic"):
        orch= Orcherstrator()
        with pytest.raises(FileNotFoundError):
            orch.run(
                task= "cover_letter",
                cv_path= "does_not_exist.pdf",
                manual_title= "DS",
                manual_company= "Corp",
                manual_description= "Python ML"
            )

def test_review_coordinator_satisfied():
    """ReviewCoordinator ends loop whee user is satisfied."""
    with patch("anthropic.Anthropic"):
        orch = Orcherstrator()
        coordinator = ReviewCoordinator(orch)
        state = coordinator.start(MOCK_RESULTS)
        final = coordinator.handle(state, satisfied= True)
        assert final.done is True 
        assert final.message == "Output saved"

def test_review_coodinator_no_feedback():
    """ReviewCoodinator prompts for feedback when none given."""
    with patch("anthropic.Anthropic"):
        orch = Orcherstrator()
        coordinator = ReviewCoordinator(orch)
        state = coordinator.start(MOCK_RESULTS)
        updated = coordinator.handle(state, satisfied= False, feedback= "")
        assert updated.done is False
        assert "feedback" in updated.message.lower()

def test_review_coodinator_max_iterations():
    """ReviewCoodinator stops at MAX_ITERATIONS."""
    with patch("anthropic.Anthropic"):
        orch =  Orcherstrator()
        coordinator = ReviewCoordinator(orch)
        #Force state to max iterations
        state = ReviewState(
            result= MOCK_RESULTS,
            iteration=ReviewCoordinator.MAX_ITERATION,
        )
        final = coordinator.handle(state, satisfied=False, feedback="more details")
        assert final.done is True
        assert "Max revisions" in final.message









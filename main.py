from dotenv import load_dotenv
import os
from agents.base_agent import BaseAgent, Message
from utils.cv_extractor import extract_text_from_pdf, get_cv_summary
from utils.job_scraper import scrape_job, manual_job_entry
from agents.orchestractor import Orcherstrator
from agents.review_coordinator import ReviewCoordinator


load_dotenv()

CV_PATH = "chuene_mosomane-data_scientist.pdf"


# Test job -  manual entry so no network needed
JOB = dict(
    manual_titles= "Senior Data Scientist",
    manual_company= "Capitec Bank",
    manual_description= """
    Capitec is hiring a Senior Data Scientist to 
    lead credit risk modelling and fraud detection initiatives.
    Requirements: Python, scikit-learn, deep learning, AWS,
    SQL, strong communication with executive stakeholders.
    PhD or Masters in quatitative field preferred. 
    Contract position, 12 months renewable. 
    Lead a team of 3 junior data scientists.     


    
    """,
)


def test_orchestrator_cover_letter():
    print("\n" + "=" * 50)
    print("TEST : Orchestrator - cover letter")
    print("=" * 50)

    orch= Orcherstrator()
    result= orch.run(task="cover_letter", cv_path=CV_PATH, **JOB)

    print(result.output["letter"][:500])
    print(f"\nTask: {result.task}")
    print(f"Company: {result.job.company}")
    print("Orchestator cover letter: PASSED")
    

def test_orchestrator_cv_review():
    print("\n" + "=" * 50)
    print("TEST: Orchestrator - CV review")
    print("=" * 50)

    orch = Orcherstrator()
    result= orch.run(task="cv_review", cv_path=CV_PATH, **JOB)

    print(f"Verdict: {result.output.get('verdict')}")
    print(f"Confidence: {result.output.get('confidence')}")
    print(f"Keywords to add: {result.output.get('missing_keywords', [])}")
    print("Orchestrator CV review: PASSED")

def test_feedback_loop():
    print("\n" + "=" * 50)
    print("TEST : Feedback loop - cover letter")
    print("=" * 50)

    orch= Orcherstrator()
    coordinator= ReviewCoordinator(orch)

    # Initial generation
    result= orch.run(task= "cover_letter", cv_path=CV_PATH, **JOB)
    state= coordinator.start(result) 

    print("Initial letter (first 300 chars):")
    print(state.result.output["letter"][:300])

    # Simulate user asking for a revision
    state= coordinator.handle(
        state= state,
        satisfied= False,
        feedback= "Make it more direct. Cut the opening to one sentense. Emphasise the CERN work more"
    )

    print(f"\nAfter revision (iteration {state.iteration}):")
    print(state.result.output["letter"][:300])

    # Simulate user satisfied
    state= coordinator.handle(state=state, satisfied=True)
    print(f"\nDone: {state.done}")
    print(f"Message: {state.message}")
    print("Feedback loop: PASSED")

def test_invalid_task():
    print("\n" + "=" * 50)
    print("Test: Invalid task raises ValueError")
    print("=" * 50)

    orch= Orcherstrator()
    try:
        orch.run(task= "make_coffee", cv_path=CV_PATH, **JOB)
        print("Failed - should have raised ValueError")
    except ValueError as e:
        print(f"Correctly raised ValueError: {e}")
        print("Invalid task test: PASSED")

if __name__ == "__main__":
    test_invalid_task()
    test_orchestrator_cover_letter()
    test_orchestrator_cv_review()
    test_feedback_loop()



